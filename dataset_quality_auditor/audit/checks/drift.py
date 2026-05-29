"""Train/test drift checks."""

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

CATEGORY_SHIFT_THRESHOLD = 0.30
MISSING_CATEGORY_RATIO_THRESHOLD = 0.50
TARGET_SHIFT_WARNING_THRESHOLD = 0.25
TARGET_SHIFT_CRITICAL_THRESHOLD = 0.50


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
        train_distribution = _value_distribution(train_df[column])
        test_distribution = _value_distribution(test_df[column])
        train_top = _dominant_category(train_distribution)
        test_top = _dominant_category(test_distribution)
        dominant_shift = 0.0
        dominant_changed = False
        if train_top is not None and test_top is not None:
            train_value, train_ratio = train_top
            test_value, test_ratio = test_top
            dominant_changed = train_value != test_value
            dominant_shift = abs(test_ratio - train_distribution.get(test_value, 0.0))
        if unseen:
            severity, risk = WARNING, MEDIUM
            metric = "unseen_category_count"
            observed_value = len(unseen)
        elif missing and train_values:
            missing_ratio = len(missing) / len(train_values)
            if missing_ratio < MISSING_CATEGORY_RATIO_THRESHOLD:
                continue
            severity, risk = INFO, LOW
            metric = "missing_category_ratio"
            observed_value = float(missing_ratio)
        elif dominant_changed and dominant_shift >= CATEGORY_SHIFT_THRESHOLD:
            severity, risk = WARNING, MEDIUM
            metric = "dominant_category_shift"
            observed_value = float(dominant_shift)
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
                    observed_value=observed_value,
                    threshold=_categorical_drift_threshold(metric),
                    comparison=_categorical_drift_comparison(metric),
                    details={
                        "unseen_categories": unseen[:10],
                        "missing_categories": missing[:10],
                        "train_unique_count": len(train_values),
                        "test_unique_count": len(test_values),
                        "train_top_category": train_top[0] if train_top else None,
                        "test_top_category": test_top[0] if test_top else None,
                        "train_top_frequency": train_top[1] if train_top else None,
                        "test_top_frequency": test_top[1] if test_top else None,
                        "dominant_category_changed": dominant_changed,
                        "dominant_category_shift": float(dominant_shift),
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


def check_target_distribution_drift(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_profile: dict[str, object],
    test_profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    """Detect deterministic target distribution changes in train/test mode."""
    if (
        context.target_column is None
        or context.target_column not in train_df.columns
        or context.target_column not in test_df.columns
    ):
        return []

    train_distribution = _value_distribution(train_df[context.target_column])
    test_distribution = _value_distribution(test_df[context.target_column])
    if not train_distribution or not test_distribution:
        return []

    labels = sorted(set(train_distribution) | set(test_distribution))
    shifts = {
        label: abs(
            test_distribution.get(label, 0.0) - train_distribution.get(label, 0.0)
        )
        for label in labels
    }
    max_shift = max(shifts.values(), default=0.0)
    if max_shift >= TARGET_SHIFT_CRITICAL_THRESHOLD:
        severity, risk, threshold = CRITICAL, HIGH, TARGET_SHIFT_CRITICAL_THRESHOLD
    elif max_shift >= TARGET_SHIFT_WARNING_THRESHOLD:
        severity, risk, threshold = WARNING, MEDIUM, TARGET_SHIFT_WARNING_THRESHOLD
    else:
        return []

    return [
        Issue(
            issue_id=issue_id("target_distribution_drift", context.target_column),
            check_id="target_distribution_drift",
            title="Target distribution drift detected",
            severity=severity,
            risk_level=risk,
            status="failed",
            scope={
                "dataset": "train_test",
                "column": context.target_column,
                "column_role": "target",
            },
            evidence=Evidence(
                metric="max_target_distribution_shift",
                observed_value=float(max_shift),
                threshold=threshold,
                comparison="observed_value >= threshold",
                details={
                    "train_distribution": train_distribution,
                    "test_distribution": test_distribution,
                    "class_distribution_shift": shifts,
                    "train_row_count": int(
                        train_df[context.target_column].notna().sum()
                    ),
                    "test_row_count": int(
                        test_df[context.target_column].notna().sum()
                    ),
                },
            ),
            ml_impact=(
                "Target distribution changes can make test metrics less comparable "
                "to training conditions."
            ),
            recommendation=(
                "Review split strategy and class balance before interpreting model "
                "evaluation metrics."
            ),
            requires_human_review=False,
            reproducibility=reproducibility(
                context,
                {"target_distribution_shift_threshold": threshold},
            ),
        )
    ]


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
        *check_target_distribution_drift(
            train_df,
            test_df,
            train_profile,
            test_profile,
            context,
        ),
    ]


def _value_distribution(series: pd.Series) -> dict[str, float]:
    non_null = series.dropna()
    total = int(len(non_null))
    if total == 0:
        return {}
    counts = non_null.astype(str).value_counts(normalize=True)
    return {str(key): float(value) for key, value in counts.sort_index().items()}


def _categorical_drift_threshold(metric: str) -> float | int:
    if metric == "dominant_category_shift":
        return CATEGORY_SHIFT_THRESHOLD
    if metric == "missing_category_ratio":
        return MISSING_CATEGORY_RATIO_THRESHOLD
    return 0


def _categorical_drift_comparison(metric: str) -> str:
    if metric in {"dominant_category_shift", "missing_category_ratio"}:
        return "observed_value >= threshold"
    return "observed_value > threshold"


def _dominant_category(distribution: dict[str, float]) -> tuple[str, float] | None:
    if not distribution:
        return None
    value, frequency = max(distribution.items(), key=lambda item: (item[1], item[0]))
    return value, float(frequency)
