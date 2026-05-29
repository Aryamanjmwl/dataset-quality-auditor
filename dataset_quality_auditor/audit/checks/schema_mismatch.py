"""Train/test schema mismatch checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import (
    CRITICAL,
    HIGH,
    INFO,
    LOW,
    MEDIUM,
    WARNING,
)


def check_schema_mismatch(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Detect train/test column and dtype mismatches."""
    issues: list[Issue] = []
    train_columns = list(train_df.columns)
    test_columns = list(test_df.columns)
    missing_in_test = sorted(set(train_columns) - set(test_columns))
    extra_in_test = sorted(set(test_columns) - set(train_columns))
    shared_columns = sorted(set(train_columns) & set(test_columns))
    dtype_mismatches = {
        column: {
            "train_dtype": str(train_df[column].dtype),
            "test_dtype": str(test_df[column].dtype),
        }
        for column in shared_columns
        if str(train_df[column].dtype) != str(test_df[column].dtype)
    }
    type_kind_mismatches = {
        column: {
            "train_kind": _column_kind(train_profile, column),
            "test_kind": _column_kind(test_profile, column),
        }
        for column in shared_columns
        if _column_kind(train_profile, column) != _column_kind(test_profile, column)
    }
    details = {
        "train_columns": train_columns,
        "test_columns": test_columns,
        "missing_in_test": missing_in_test,
        "extra_in_test": extra_in_test,
        "dtype_mismatches": dtype_mismatches,
        "type_kind_mismatches": type_kind_mismatches,
    }

    for column in missing_in_test:
        severity = INFO if column == context.target_column else CRITICAL
        risk = LOW if column == context.target_column else HIGH
        issues.append(
            Issue(
                issue_id=issue_id("schema_missing_in_test", column),
                check_id="schema_mismatch",
                title="Train column missing from test dataset",
                severity=severity,
                risk_level=risk,
                status="failed",
                scope={"dataset": "test", "column": column, "column_role": "unknown"},
                evidence=Evidence(
                    metric="missing_in_test",
                    observed_value=True,
                    threshold=True,
                    comparison="observed_value == threshold",
                    details=details,
                ),
                ml_impact=(
                    "A feature missing from test data can break evaluation or "
                    "hide training-serving schema drift."
                ),
                recommendation=(
                    "Align train and test schemas before training and evaluation."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(context, {}),
            )
        )

    if extra_in_test:
        issues.append(
            Issue(
                issue_id=issue_id("schema_extra_in_test", "_".join(extra_in_test)),
                check_id="schema_mismatch",
                title="Extra columns detected in test dataset",
                severity=INFO,
                risk_level=LOW,
                status="failed",
                scope={"dataset": "test", "column": None, "column_role": None},
                evidence=Evidence(
                    metric="extra_in_test_count",
                    observed_value=len(extra_in_test),
                    threshold=0,
                    comparison="observed_value > threshold",
                    details=details,
                ),
                ml_impact=(
                    "Extra test columns may indicate inconsistent data extraction "
                    "or unused features."
                ),
                recommendation=(
                    "Review extra test columns and confirm they are expected."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(context, {}),
            )
        )

    for column, mismatch in dtype_mismatches.items():
        issues.append(
            Issue(
                issue_id=issue_id("schema_dtype_mismatch", column),
                check_id="schema_mismatch",
                title="Train/test dtype mismatch detected",
                severity=WARNING,
                risk_level=MEDIUM,
                status="failed",
                scope={
                    "dataset": "train_test",
                    "column": column,
                    "column_role": "unknown",
                },
                evidence=Evidence(
                    metric="dtype_mismatch",
                    observed_value=True,
                    threshold=True,
                    comparison="observed_value == threshold",
                    details={"column": column, **mismatch, **details},
                ),
                ml_impact=(
                    "Dtype mismatches can produce inconsistent preprocessing "
                    "between train and test data."
                ),
                recommendation="Apply explicit schema/type validation before modeling.",
                requires_human_review=False,
                reproducibility=reproducibility(context, {}),
            )
        )
    for column, mismatch in type_kind_mismatches.items():
        issues.append(
            Issue(
                issue_id=issue_id("schema_type_kind_mismatch", column),
                check_id="schema_mismatch",
                title="Train/test inferred type kind mismatch detected",
                severity=WARNING,
                risk_level=MEDIUM,
                status="failed",
                scope={
                    "dataset": "train_test",
                    "column": column,
                    "column_role": "unknown",
                },
                evidence=Evidence(
                    metric="type_kind_mismatch",
                    observed_value=True,
                    threshold=True,
                    comparison="observed_value == threshold",
                    details={"column": column, **mismatch, **details},
                ),
                ml_impact=(
                    "Inferred type-kind mismatches can produce inconsistent "
                    "preprocessing between train and test data."
                ),
                recommendation=(
                    "Review feature typing and apply explicit schema checks."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(context, {}),
            )
        )
    return issues


def _column_kind(profile: dict[str, object], column: str) -> str:
    columns = profile.get("columns", {})
    if not isinstance(columns, dict):
        return "unknown"
    metadata = columns.get(column, {})
    if not isinstance(metadata, dict):
        return "unknown"
    if metadata.get("is_numeric") is True:
        return "numeric"
    if metadata.get("inferred_role") == "datetime_candidate":
        return "datetime_candidate"
    if metadata.get("is_categorical") is True:
        return "categorical"
    return "other"
