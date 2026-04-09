from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class MissingValuesCheck:
    """
    Aggregate missing value detection across the dataset.

    Returns:
      - [] if no column exceeds the threshold AND overall ratio below threshold
      - One Finding (MISSING_VALUES) otherwise
    """
    name: str = "missing_values"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        threshold = float(ctx.params.get("missing_ratio_threshold", 0.05))

        total_cells = int(df.shape[0] * df.shape[1])
        total_missing = int(df.isna().sum().sum())
        overall_ratio = (total_missing / total_cells) if total_cells else 0.0

        per_col_counts = df.isna().sum()
        per_col_ratio = (per_col_counts / len(df)) if len(df) else per_col_counts * 0.0

        flagged_cols = [c for c in df.columns if float(per_col_ratio[c]) >= threshold]

        if overall_ratio < threshold and not flagged_cols:
            return []

        # Severity heuristic
        worst_col_ratio = float(max([per_col_ratio[c] for c in flagged_cols], default=0.0))
        if worst_col_ratio >= 0.30 or overall_ratio >= 0.20:
            sev = Severity.HIGH
        elif worst_col_ratio >= 0.10 or overall_ratio >= 0.05:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        # Build per-column metric dict (only for flagged columns to keep report readable)
        per_col_metrics: Dict[str, Dict[str, float]] = {}
        for c in flagged_cols:
            per_col_metrics[c] = {
                "missing_count": float(per_col_counts[c]),
                "missing_ratio": float(round(float(per_col_ratio[c]), 6)),
            }

        return [
            Finding(
                id="MISSING_VALUES",
                title="Missing values detected",
                description=(
                    f"Dataset contains missing values. Overall missing ratio is {overall_ratio:.4f}. "
                    f"{len(flagged_cols)} column(s) exceed threshold {threshold}."
                ),
                severity=sev,
                columns=flagged_cols,
                metrics={
                    "total_missing_cells": total_missing,
                    "total_cells": total_cells,
                    "overall_missing_ratio": float(round(overall_ratio, 6)),
                    "threshold": threshold,
                    "columns_over_threshold": int(len(flagged_cols)),
                    "per_column": per_col_metrics,
                },
                recommendation=(
                    "Inspect columns with missingness. Decide per feature whether to impute, drop rows, "
                    "drop the feature, or model missingness explicitly."
                ),
            )
        ]