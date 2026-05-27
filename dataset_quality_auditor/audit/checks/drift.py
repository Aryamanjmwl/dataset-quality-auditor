"""Train/test drift checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import INFO, LOW, MEDIUM, WARNING


def check_numeric_drift(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    issues: list[Issue] = []
    shared = set(train_df.columns) & set(test_df.columns)
    for column in sorted(shared):
        if column == context.target_column:
            continue
        if not (
            pd.api.types.is_numeric_dtype(train_df[column])
            and pd.api.types.is_numeric_dtype(test_df[column])
        ):
            continue
        train_std = float(train_df[column].std())
        if train_std == 0 or pd.isna(train_std):
            continue
        train_mean = float(train_df[column].mean())
        test_mean = float(test_df[column].mean())
        test_std = float(test_df[column].std())
        mean_shift = abs(test_mean - train_mean) / train_std
        if mean_shift >= 1.0:
            severity, risk, threshold = WARNING, MEDIUM, 1.0
        elif mean_shift >= 0.5:
            severity, risk, threshold = INFO, LOW, 0.5
        else:
            continue
        issues.append(
            Issue(
                issue_id=issue_id("numeric_drift", column),
                check_id="numeric_drift",
                title="Numeric train/test drift detected",
                severity=severity,
                risk_level=risk,
                status="failed",
                scope={
                    "dataset": "train_test",
                    "column": column,
                    "column_role": "feature",
                },
                evidence=Evidence(
                    metric="mean_shift",
                    observed_value=float(mean_shift),
                    threshold=threshold,
                    comparison="observed_value >= threshold",
                    details={
                        "train_mean": train_mean,
                        "test_mean": test_mean,
                        "train_std": train_std,
                        "test_std": test_std,
                        "mean_shift": float(mean_shift),
                    },
                ),
                ml_impact=(
                    "Numeric distribution drift can make evaluation less "
                    "representative of training conditions."
                ),
                recommendation=(
                    "Review feature extraction and split logic; do not treat this "
                    "as statistical significance without a formal test."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(
                    context,
                    {"mean_shift_threshold": threshold},
                ),
            )
        )
    return issues


def check_categorical_drift(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    issues: list[Issue] = []
    shared = set(train_df.columns) & set(test_df.columns)
    for column in sorted(shared):
        if column == context.target_column:
            continue
        if pd.api.types.is_numeric_dtype(train_df[column]):
            continue
        train_values = {str(value) for value in train_df[column].dropna().unique()}
        test_values = {str(value) for value in test_df[column].dropna().unique()}
        unseen = sorted(test_values - train_values)
        missing = sorted(train_values - test_values)
        if unseen:
            severity, risk = WARNING, MEDIUM
            metric = "unseen_category_count"
        elif missing and train_values:
            missing_ratio = len(missing) / len(train_values)
            if missing_ratio < 0.5:
                continue
            severity, risk = INFO, LOW
            metric = "missing_category_ratio"
        else:
            continue
        issues.append(
            Issue(
                issue_id=issue_id("categorical_drift", column),
                check_id="categorical_drift",
                title="Categorical train/test drift detected",
                severity=severity,
                risk_level=risk,
                status="failed",
                scope={
                    "dataset": "train_test",
                    "column": column,
                    "column_role": "feature",
                },
                evidence=Evidence(
                    metric=metric,
                    observed_value=len(unseen) if unseen else len(missing),
                    threshold=0,
                    comparison="observed_value > threshold",
                    details={
                        "unseen_categories": unseen,
                        "missing_categories": missing,
                        "train_unique_count": len(train_values),
                        "test_unique_count": len(test_values),
                    },
                ),
                ml_impact=(
                    "Unseen or shifted categories can break encoders or reduce "
                    "model reliability."
                ),
                recommendation=(
                    "Review categorical preprocessing and ensure train/test splits "
                    "represent expected serving data."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(context, {}),
            )
        )
    return issues


def check_train_test_drift(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Run numeric and categorical train/test drift checks."""
    return [
        *check_numeric_drift(train_df, test_df, train_profile, test_profile, context),
        *check_categorical_drift(
            train_df,
            test_df,
            train_profile,
            test_profile,
            context,
        ),
    ]
