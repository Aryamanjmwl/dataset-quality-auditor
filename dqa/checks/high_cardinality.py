from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class HighCardinalityCategoricalCheck:
    """
    Aggregate detection of high-cardinality categorical features.

    Flags a categorical column as high-cardinality if:
      - unique_count >= high_card_unique_count_threshold OR
      - unique_ratio >= high_card_unique_ratio_threshold

    Returns:
      - [] if no columns flagged
      - One Finding (HIGH_CARDINALITY_CATEGORICAL) listing all flagged columns
    """

    name: str = "high_cardinality_categorical"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        ratio_thr = float(ctx.params.get("high_card_unique_ratio_threshold", 0.50))
        count_thr = int(ctx.params.get("high_card_unique_count_threshold", 50))

        # treat object/category/bool as categorical-like
        cat_cols = list(
            df.select_dtypes(include=["object", "category", "bool"]).columns
        )

        flagged: List[str] = []
        per_col: Dict[str, Dict[str, float]] = {}

        n_rows = len(df) if len(df) else 1

        for c in cat_cols:
            nunique = int(df[c].nunique(dropna=True))
            unique_ratio = float(nunique / n_rows)

            per_col[c] = {
                "unique_count": float(nunique),
                "unique_ratio": float(round(unique_ratio, 6)),
                "count_threshold": float(count_thr),
                "ratio_threshold": float(ratio_thr),
            }

            if nunique >= count_thr or unique_ratio >= ratio_thr:
                flagged.append(c)

        if not flagged:
            return []

        # Severity heuristic: very high unique ratio or huge unique count -> HIGH
        max_ratio = max(per_col[c]["unique_ratio"] for c in flagged) if flagged else 0.0
        max_count = max(per_col[c]["unique_count"] for c in flagged) if flagged else 0.0

        if max_ratio >= 0.90 or max_count >= (count_thr * 5):
            sev = Severity.HIGH
        else:
            sev = Severity.MEDIUM

        # Only include metrics for flagged columns (keeps report smaller)
        flagged_metrics = {c: per_col[c] for c in flagged}

        return [
            Finding(
                id="HIGH_CARDINALITY_CATEGORICAL",
                title="High-cardinality categorical features detected",
                description=(
                    f"{len(flagged)} categorical feature(s) appear high-cardinality. "
                    "This can cause sparse one-hot encodings, overfitting, and memory/perf issues."
                ),
                severity=sev,
                columns=sorted(flagged),
                metrics={
                    "flagged_columns_count": int(len(flagged)),
                    "thresholds": {
                        "unique_ratio": ratio_thr,
                        "unique_count": count_thr,
                    },
                    "per_column": flagged_metrics,
                },
                recommendation=(
                    "Consider target encoding, frequency encoding, hashing, embeddings, "
                    "or grouping rare categories into an 'Other' bucket."
                ),
            )
        ]
