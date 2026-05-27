"""Target leakage candidate checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING

TARGET_NAME_SIGNALS = (
    "label",
    "target",
    "outcome",
    "result",
    "prediction",
    "predicted",
    "score_after",
    "post",
    "final",
)
TARGET_CORRELATION_THRESHOLD = 0.95
DOMINANT_TARGET_RATIO_THRESHOLD = 0.98
MAX_CATEGORY_COUNT = 50


def _numeric_target_correlation(
    feature: pd.Series,
    target: pd.Series,
) -> float | None:
    feature_is_numeric = pd.api.types.is_numeric_dtype(feature)
    target_is_numeric = pd.api.types.is_numeric_dtype(target)
    if not (feature_is_numeric and target_is_numeric):
        return None
    value = feature.corr(target)
    if pd.isna(value):
        return None
    return float(abs(value))


def _categorical_target_ratio(feature: pd.Series, target: pd.Series) -> float | None:
    non_null = pd.DataFrame({"feature": feature, "target": target}).dropna()
    if non_null.empty or non_null["feature"].nunique() > MAX_CATEGORY_COUNT:
        return None
    ratios = []
    for _, group in non_null.groupby("feature"):
        ratios.append(float(group["target"].value_counts(normalize=True).max()))
    if not ratios:
        return None
    return min(ratios)


def _leakage_issue(
    context: AuditContext,
    column: str,
    signal_type: str,
    observed_metric: float | str | bool,
    threshold: float | str | bool,
    severity: str,
    risk_level: str,
) -> Issue:
    return Issue(
        issue_id=issue_id("target_leakage_candidate", f"{column}_{signal_type}"),
        check_id="target_leakage_candidate",
        title="Target leakage candidate detected",
        severity=severity,
        risk_level=risk_level,
        status="failed",
        scope={"dataset": "train", "column": column, "column_role": "feature"},
        evidence=Evidence(
            metric="leakage_candidate_signal",
            observed_value=observed_metric,
            threshold=threshold,
            comparison="observed_value indicates possible leakage",
            details={
                "signal_type": signal_type,
                "observed_metric": observed_metric,
                "threshold": threshold,
                "column": column,
                "target_column": context.target_column,
            },
        ),
        ml_impact=(
            "A target leakage candidate can inflate training and validation "
            "metrics if the feature is derived from the target event."
        ),
        recommendation=(
            "Confirm whether this feature is available at prediction time; "
            "remove it from training if it is derived from or created after the "
            "target event."
        ),
        requires_human_review=True,
        reproducibility=reproducibility(
            context,
            {
                "target_correlation_threshold": TARGET_CORRELATION_THRESHOLD,
                "dominant_target_ratio_threshold": DOMINANT_TARGET_RATIO_THRESHOLD,
            },
        ),
    )


def check_target_leakage_candidates(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    if context.target_column is None or context.target_column not in df.columns:
        return []
    target = df[context.target_column]
    issues: list[Issue] = []
    for column in df.columns:
        if column == context.target_column:
            continue
        lower_name = str(column).lower()
        if any(signal in lower_name for signal in TARGET_NAME_SIGNALS):
            issues.append(
                _leakage_issue(
                    context,
                    str(column),
                    "target_like_name",
                    True,
                    True,
                    WARNING,
                    MEDIUM,
                )
            )
            continue
        correlation = _numeric_target_correlation(df[column], target)
        if correlation is not None and correlation >= TARGET_CORRELATION_THRESHOLD:
            issues.append(
                _leakage_issue(
                    context,
                    str(column),
                    "target_correlation",
                    correlation,
                    TARGET_CORRELATION_THRESHOLD,
                    CRITICAL,
                    HIGH,
                )
            )
            continue
        if not pd.api.types.is_numeric_dtype(df[column]):
            dominant_ratio = _categorical_target_ratio(df[column], target)
            if (
                dominant_ratio is not None
                and dominant_ratio >= DOMINANT_TARGET_RATIO_THRESHOLD
            ):
                issues.append(
                    _leakage_issue(
                        context,
                        str(column),
                        "category_target_mapping",
                        dominant_ratio,
                        DOMINANT_TARGET_RATIO_THRESHOLD,
                        CRITICAL,
                        HIGH,
                    )
                )
    return issues
