from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext
from dqa.io import CSVDataLoader


def _psi(expected: np.ndarray, actual: np.ndarray, eps: float = 1e-6) -> float:
    expected = np.clip(expected, eps, None)
    actual = np.clip(actual, eps, None)
    return float(np.sum((actual - expected) * np.log(actual / expected)))


def _numeric_psi(ref: pd.Series, cur: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(ref, errors="coerce").dropna()
    cur = pd.to_numeric(cur, errors="coerce").dropna()
    if ref.empty or cur.empty:
        return 0.0

    # Special case: constant reference distribution
    ref_min = float(ref.min())
    ref_max = float(ref.max())

    if ref_min == ref_max:
        # Build a tiny interval around the constant value so pd.cut works
        eps = 1e-6 if ref_min == 0 else abs(ref_min) * 1e-6
        cut_points = np.array([ref_min - eps, ref_max + eps], dtype=float)
    else:
        qs = np.linspace(0, 1, bins + 1)
        cut_points = np.unique(ref.quantile(qs).to_numpy())

        # Fallback to equal-width bins if quantiles collapse too much
        if len(cut_points) < 3:
            cut_points = np.linspace(ref_min, ref_max, bins + 1)

        # Final safeguard: ensure unique, increasing edges
        cut_points = np.unique(cut_points)
        if len(cut_points) < 2:
            eps = 1e-6 if ref_min == 0 else abs(ref_min) * 1e-6
            cut_points = np.array([ref_min - eps, ref_max + eps], dtype=float)

    ref_bins = pd.cut(ref, bins=cut_points, include_lowest=True, duplicates="drop")
    cur_bins = pd.cut(cur, bins=cut_points, include_lowest=True, duplicates="drop")

    ref_p = ref_bins.value_counts(normalize=True, dropna=False).sort_index()
    cur_p = cur_bins.value_counts(normalize=True, dropna=False).sort_index()
    cur_p = cur_p.reindex(ref_p.index, fill_value=0.0)

    return _psi(ref_p.to_numpy(), cur_p.to_numpy())


def _categorical_psi(ref: pd.Series, cur: pd.Series, top_k: int = 50) -> float:
    ref = ref.astype("object").fillna("__MISSING__")
    cur = cur.astype("object").fillna("__MISSING__")

    ref_vc = ref.value_counts(normalize=True)
    top = list(ref_vc.head(top_k).index)

    def bucket(s: pd.Series) -> pd.Series:
        return s.where(s.isin(top), "__OTHER__")

    ref_b = bucket(ref)
    cur_b = bucket(cur)

    ref_p = ref_b.value_counts(normalize=True)
    cur_p = cur_b.value_counts(normalize=True)

    idx = sorted(set(ref_p.index).union(set(cur_p.index)))
    e = np.array([float(ref_p.get(k, 0.0)) for k in idx], dtype=float)
    a = np.array([float(cur_p.get(k, 0.0)) for k in idx], dtype=float)

    return _psi(e, a)


@dataclass(frozen=True)
class DataDriftCheck:
    """
    Drift between reference and current datasets.

    Always returns one finding when reference/current are provided:
    - DATA_DRIFT_DETECTED if drift is flagged
    - DATA_DRIFT_SUMMARY if comparison ran but nothing exceeded thresholds
    """
    name: str = "data_drift"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        ref_path = ctx.params.get("reference_path")
        cur_path = ctx.params.get("current_path")
        if not ref_path or not cur_path:
            return []

        psi_thr = float(ctx.params.get("drift_psi_threshold", 0.2))
        ks_alpha = float(ctx.params.get("drift_ks_alpha", 0.01))
        top_n = int(ctx.params.get("drift_top_n", 10))
        bins = int(ctx.params.get("drift_numeric_bins", 10))

        loader = CSVDataLoader()
        ref_df = loader.load(ref_path).df
        cur_df = loader.load(cur_path).df

        common_cols = [c for c in ref_df.columns if c in cur_df.columns]
        if ctx.target and ctx.target in common_cols:
            common_cols = [c for c in common_cols if c != ctx.target]

        if not common_cols:
            return [
                Finding(
                    id="DATA_DRIFT_NO_COMMON_COLUMNS",
                    title="Cannot compute drift (no common columns)",
                    description="Reference and current datasets share no common columns to compare drift.",
                    severity=Severity.MEDIUM,
                    columns=[],
                    metrics={
                        "reference_path": str(Path(ref_path).resolve()),
                        "current_path": str(Path(cur_path).resolve()),
                    },
                    recommendation="Ensure both datasets have the same schema.",
                )
            ]

        rows: List[Dict[str, object]] = []

        for c in common_cols:
            ref_s = ref_df[c]
            cur_s = cur_df[c]
            is_num = pd.api.types.is_numeric_dtype(ref_s) and pd.api.types.is_numeric_dtype(cur_s)

            if is_num:
                r = pd.to_numeric(ref_s, errors="coerce").dropna()
                u = pd.to_numeric(cur_s, errors="coerce").dropna()
                if r.empty or u.empty:
                    continue

                ks = ks_2samp(r.to_numpy(), u.to_numpy())
                psi = _numeric_psi(ref_s, cur_s, bins=bins)

                rows.append(
                    {
                        "column": c,
                        "type": "numeric",
                        "psi": float(psi),
                        "ks_stat": float(ks.statistic),
                        "ks_pvalue": float(ks.pvalue),
                        "flag_psi": bool(psi >= psi_thr),
                        "flag_ks": bool(ks.pvalue <= ks_alpha),
                    }
                )
            else:
                psi = _categorical_psi(ref_s, cur_s, top_k=50)
                rows.append(
                    {
                        "column": c,
                        "type": "categorical",
                        "psi": float(psi),
                        "ks_stat": 0.0,
                        "ks_pvalue": 1.0,
                        "flag_psi": bool(psi >= psi_thr),
                        "flag_ks": False,
                    }
                )

        if not rows:
            return [
                Finding(
                    id="DATA_DRIFT_SUMMARY",
                    title="Data drift summary (no comparable columns)",
                    description="Drift comparison ran, but no comparable numeric/categorical columns produced metrics.",
                    severity=Severity.LOW,
                    columns=[],
                    metrics={
                        "reference_path": str(Path(ref_path).resolve()),
                        "current_path": str(Path(cur_path).resolve()),
                        "psi_threshold": psi_thr,
                        "ks_alpha": ks_alpha,
                        "columns_compared": int(len(common_cols)),
                        "flagged_columns_count": 0,
                        "top_drifted_columns": [],
                    },
                    recommendation="Check schemas and data types of reference/current datasets.",
                )
            ]

        drift = pd.DataFrame(rows)

        for col, default in {
            "psi": 0.0,
            "ks_stat": 0.0,
            "ks_pvalue": 1.0,
            "flag_psi": False,
            "flag_ks": False,
        }.items():
            if col not in drift.columns:
                drift[col] = default
            drift[col] = drift[col].fillna(default)

        drift = drift.sort_values(by=["psi", "ks_stat"], ascending=False, na_position="last")

        flagged = drift[(drift["flag_psi"] == True) | (drift["flag_ks"] == True)]

        top = drift.head(top_n).copy()
        top["psi"] = top["psi"].round(6)
        top["ks_stat"] = top["ks_stat"].round(6)
        top["ks_pvalue"] = top["ks_pvalue"].round(8)

        metrics = {
            "reference_path": str(Path(ref_path).resolve()),
            "current_path": str(Path(cur_path).resolve()),
            "psi_threshold": psi_thr,
            "ks_alpha": ks_alpha,
            "columns_compared": int(len(common_cols)),
            "flagged_columns_count": int(flagged["column"].nunique()) if not flagged.empty else 0,
            "top_drifted_columns": top.to_dict(orient="records"),
        }

        if flagged.empty:
            return [
                Finding(
                    id="DATA_DRIFT_SUMMARY",
                    title="Data drift summary (no drift flagged)",
                    description="Drift comparison ran successfully, but no columns exceeded the configured thresholds.",
                    severity=Severity.LOW,
                    columns=[],
                    metrics=metrics,
                    recommendation=(
                        "If you expected drift, lower drift thresholds or verify reference/current inputs."
                    ),
                )
            ]

        max_psi = float(flagged["psi"].max())
        if max_psi >= 0.5:
            sev = Severity.HIGH
        elif max_psi >= 0.2:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        return [
            Finding(
                id="DATA_DRIFT_DETECTED",
                title="Data drift detected between reference and current datasets",
                description=(
                    f"Detected drift in {int(flagged['column'].nunique())} column(s) "
                    f"using PSI (>= {psi_thr}) and KS-test (p <= {ks_alpha})."
                ),
                severity=sev,
                columns=list(flagged["column"].unique()),
                metrics=metrics,
                recommendation=(
                    "Investigate source changes, seasonality, or pipeline issues. "
                    "Consider retraining and production monitoring."
                ),
            )
        ]