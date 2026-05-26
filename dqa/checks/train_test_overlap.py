from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from dqa.domain import Finding, Severity
from dqa.domain.interfaces import AuditContext
from dqa.io import CSVDataLoader


@dataclass(frozen=True)
class TrainTestOverlapCheck:
    """
    Detect row overlap between train and test datasets (leakage risk).
    """

    name: str = "train_test_overlap"

    def run(self, df: pd.DataFrame, ctx: AuditContext) -> List[Finding]:
        train_path = ctx.params.get("train_path")
        test_path = ctx.params.get("test_path")
        key_columns = ctx.params.get("overlap_key_columns")  # optional list[str]

        if not train_path or not test_path:
            return []  # not configured -> skip

        loader = CSVDataLoader()
        train = loader.load(train_path).df
        test = loader.load(test_path).df

        # Use provided key columns if given; otherwise use common columns
        if key_columns:
            cols = [c for c in key_columns if c in train.columns and c in test.columns]
        else:
            cols = [c for c in train.columns if c in test.columns]

        if not cols:
            return [
                Finding(
                    id="TRAIN_TEST_OVERLAP_NO_COMMON_COLUMNS",
                    title="Cannot check train/test overlap (no common columns)",
                    description="Train and test datasets share no common columns to compare overlap.",
                    severity=Severity.MEDIUM,
                    columns=[],
                    metrics={
                        "train_columns": list(train.columns),
                        "test_columns": list(test.columns),
                    },
                    recommendation="Ensure train/test have same schema or set overlap_key_columns.",
                )
            ]

        # Hash row values to compare quickly
        train_sig = pd.util.hash_pandas_object(train[cols], index=False)
        test_sig = pd.util.hash_pandas_object(test[cols], index=False)

        overlap = set(train_sig.values.tolist()).intersection(
            set(test_sig.values.tolist())
        )
        overlap_count = len(overlap)

        train_rows = len(train)
        test_rows = len(test)
        overlap_test_ratio = overlap_count / test_rows if test_rows else 0.0
        overlap_train_ratio = overlap_count / train_rows if train_rows else 0.0

        if overlap_count == 0:
            return []

        if overlap_test_ratio >= 0.05:
            sev = Severity.HIGH
        elif overlap_test_ratio >= 0.01:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        return [
            Finding(
                id="TRAIN_TEST_OVERLAP",
                title="Train/Test overlap detected",
                description=(
                    f"Found {overlap_count} overlapping row(s) between train and test "
                    f"using {len(cols)} common column(s). This can inflate evaluation metrics."
                ),
                severity=sev,
                columns=cols,
                metrics={
                    "overlap_rows": overlap_count,
                    "train_rows": train_rows,
                    "test_rows": test_rows,
                    "overlap_ratio_test": round(overlap_test_ratio, 6),
                    "overlap_ratio_train": round(overlap_train_ratio, 6),
                    "columns_used": cols,
                    "train_path": str(Path(train_path).resolve()),
                    "test_path": str(Path(test_path).resolve()),
                },
                recommendation=(
                    "Deduplicate BEFORE splitting. Ensure train/test are disjoint. "
                    "Use stable keys or time-based splits if appropriate."
                ),
            )
        ]
