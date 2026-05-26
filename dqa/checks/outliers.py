from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


def _iqr_bounds(s: pd.Series, iqr_multiplier: float) -> Tuple[float, float]:
    """
    Compute Tukey IQR bounds for a numeric series (ignores NaNs).
    """
    s = pd.to_numeric(s, errors="coerce").dropna()
    if s.empty:
        return (float("nan"), float("nan"))

    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - iqr_multiplier * iqr
    upper = q3 + iqr_multiplier * iqr
    return lower, upper


def _outlier_stats(s: pd.Series, iqr_multiplier: float) -> Dict[str, float]:
    """
    Return outlier stats for a numeric series.
    """
    s_num = pd.to_numeric(s, errors="coerce")
    valid = s_num.dropna()
    if valid.empty:
        return {
            "outlier_count": 0.0,
            "outlier_ratio": 0.0,
            "lower_bound": float("nan"),
            "upper_bound": float("nan"),
            "n_valid": 0.0,
        }

    lower, upper = _iqr_bounds(valid, iqr_multiplier)
    mask = (valid < lower) | (valid > upper)
    outlier_count = int(mask.sum())
    outlier_ratio = float(outlier_count / len(valid)) if len(valid) else 0.0

    return {
        "outlier_count": float(outlier_count),
        "outlier_ratio": float(round(outlier_ratio, 6)),
        "lower_bound": float(round(lower, 6)) if np.isfinite(lower) else float("nan"),
        "upper_bound": float(round(upper, 6)) if np.isfinite(upper) else float("nan"),
        "n_valid": float(len(valid)),
    }


@dataclass(frozen=True)
class OutlierDetectionCheck:
    """
    Aggregate outlier detection across numeric features using IQR.

    Returns ONE Finding:
      - [] if no column exceeds threshold
      - OUTLIERS_DETECTED if any columns exceed threshold
    """

    name: str = "outlier_detection"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        iqr_multiplier = float(ctx.params.get("outlier_iqr_multiplier", 1.5))
        threshold = float(ctx.params.get("outlier_ratio_threshold", 0.05))

        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        if ctx.target and ctx.target in numeric_cols:
            # target usually shouldn't be treated like a feature for outliers
            numeric_cols = [c for c in numeric_cols if c != ctx.target]

        per_col: Dict[str, Dict[str, float]] = {}
        flagged: List[str] = []

        for c in numeric_cols:
            stats = _outlier_stats(df[c], iqr_multiplier)
            per_col[c] = stats
            if stats["outlier_ratio"] >= threshold:
                flagged.append(c)

        if not flagged:
            return []

        max_ratio = (
            max(per_col[c]["outlier_ratio"] for c in flagged) if flagged else 0.0
        )
        sev = Severity.HIGH if max_ratio >= 2 * threshold else Severity.MEDIUM

        return [
            Finding(
                id="OUTLIERS_DETECTED",
                title="Outliers detected in numeric features",
                description=(
                    f"Detected outliers using IQR method (multiplier={iqr_multiplier}). "
                    f"{len(flagged)} column(s) exceed outlier ratio threshold {threshold}."
                ),
                severity=sev,
                columns=flagged,
                metrics={
                    "threshold": threshold,
                    "iqr_multiplier": iqr_multiplier,
                    "columns": per_col,  # includes ratios for all numeric columns
                },
                recommendation=(
                    "Verify whether outliers are valid rare events or data errors. "
                    "Consider winsorization, robust scalers, clipping, log transforms, or removing bad rows."
                ),
            )
        ]
