"""Constant column checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING


def check_constant_columns(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)

    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        non_null_count = int(df[column].notna().sum())
        unique_count = int(column_profile["unique_count"])
        if non_null_count == 0 or unique_count != 1:
            continue

        is_target = column == context.target_column
        severity = CRITICAL if is_target else WARNING
        risk_level = HIGH if is_target else MEDIUM
        issues.append(
            Issue(
                issue_id=issue_id("constant_column", str(column)),
                check_id="constant_columns",
                title=(
                    "Target column contains only one class"
                    if is_target
                    else "Constant feature column detected"
                ),
                severity=severity,
                risk_level=risk_level,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_profile["inferred_role"],
                },
                evidence=Evidence(
                    metric="unique_count",
                    observed_value=unique_count,
                    threshold=1,
                    comparison="observed_value == threshold",
                    details={
                        "unique_count": unique_count,
                        "non_null_count": non_null_count,
                    },
                ),
                ml_impact=(
                    "A constant target prevents supervised learning."
                    if is_target
                    else "Constant features do not provide useful model signal."
                ),
                recommendation=(
                    "Verify target extraction because a single target class is "
                    "not suitable for supervised training."
                    if is_target
                    else "Remove or ignore constant feature columns during modeling."
                ),
                requires_human_review=is_target,
                reproducibility=reproducibility(context, {"unique_count_threshold": 1}),
            )
        )

    return issues
