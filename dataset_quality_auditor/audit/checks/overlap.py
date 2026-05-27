"""Train/test overlap checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH


def check_train_test_overlap(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Detect exact duplicate rows across train and test."""
    shared_columns = list(train_df.columns.intersection(test_df.columns))
    if not shared_columns or test_df.empty:
        return []
    train_rows = set(map(tuple, train_df[shared_columns].astype(str).to_numpy()))
    test_rows = list(map(tuple, test_df[shared_columns].astype(str).to_numpy()))
    overlapping_count = sum(1 for row in test_rows if row in train_rows)
    if overlapping_count == 0:
        return []
    overlap_percent = float(overlapping_count / len(test_df))
    return [
        Issue(
            issue_id=issue_id("train_test_overlap", "rows"),
            check_id="train_test_overlap",
            title="Train/test row overlap detected",
            severity=CRITICAL,
            risk_level=HIGH,
            status="failed",
            scope={"dataset": "train_test", "column": None, "column_role": None},
            evidence=Evidence(
                metric="overlap_percent_of_test",
                observed_value=overlap_percent,
                threshold=0,
                comparison="observed_value > threshold",
                details={
                    "overlapping_row_count": overlapping_count,
                    "test_row_count": int(len(test_df)),
                    "overlap_percent_of_test": overlap_percent,
                },
            ),
            ml_impact=(
                "Test leakage from overlapping rows can inflate evaluation metrics."
            ),
            recommendation=(
                "Remove or review overlapping rows before evaluation; test leakage "
                "can make model metrics look better than they are."
            ),
            requires_human_review=False,
            reproducibility=reproducibility(context, {}),
        )
    ]
