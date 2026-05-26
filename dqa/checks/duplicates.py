from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext


@dataclass(frozen=True)
class DuplicateRowsCheck:
    """
    Detect exact duplicate rows.

    Duplicates can inflate model performance (data leakage) and bias metrics.
    """

    name: str = "duplicate_rows"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        dup_mask = df.duplicated(keep="first")
        dup_count = int(dup_mask.sum())
        n_rows = int(len(df))
        dup_ratio = (dup_count / n_rows) if n_rows > 0 else 0.0

        if dup_count == 0:
            return []

        # Severity heuristic
        if dup_ratio >= 0.10:
            sev = Severity.HIGH
        elif dup_ratio >= 0.02:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        return [
            Finding(
                id="DUPLICATE_ROWS",
                title="Duplicate rows detected",
                description=(
                    f"The dataset contains {dup_count} duplicate rows "
                    f"({dup_ratio:.2%} of rows)."
                ),
                severity=sev,
                columns=[],
                metrics={
                    "duplicate_rows": dup_count,
                    "n_rows": n_rows,
                    "duplicate_ratio": round(dup_ratio, 6),
                },
                recommendation=(
                    "Investigate why duplicates exist. If duplicates are accidental, "
                    "drop them before splitting train/test. If they are legitimate repeated events, "
                    "consider deduplication keys or time-based aggregation."
                ),
            )
        ]
