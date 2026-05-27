"""Feature correlation risk checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import MEDIUM, WARNING

CORRELATION_THRESHOLD = 0.95
MAX_CORRELATION_ISSUES = 20


def check_correlation_risk(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    numeric_features = [
        column
        for column in df.columns
        if column != context.target_column and pd.api.types.is_numeric_dtype(df[column])
    ]
    if len(numeric_features) < 2:
        return []
    corr = df[numeric_features].corr(numeric_only=True).abs()
    pairs: list[tuple[str, str, float]] = []
    for index, column_a in enumerate(numeric_features):
        for column_b in numeric_features[index + 1 :]:
            value = corr.loc[column_a, column_b]
            if pd.isna(value):
                continue
            if float(value) >= CORRELATION_THRESHOLD:
                pairs.append((column_a, column_b, float(value)))
    pairs.sort(key=lambda item: item[2], reverse=True)
    issues: list[Issue] = []
    for column_a, column_b, value in pairs[:MAX_CORRELATION_ISSUES]:
        issues.append(
            Issue(
                issue_id=issue_id("correlation_risk", f"{column_a}_{column_b}"),
                check_id="correlation_risk",
                title="Highly correlated feature pair detected",
                severity=WARNING,
                risk_level=MEDIUM,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": f"{column_a},{column_b}",
                    "column_role": "feature",
                },
                evidence=Evidence(
                    metric="absolute_pearson_correlation",
                    observed_value=value,
                    threshold=CORRELATION_THRESHOLD,
                    comparison="observed_value >= threshold",
                    details={
                        "column_a": column_a,
                        "column_b": column_b,
                        "correlation": value,
                    },
                ),
                ml_impact=(
                    "Highly correlated features may be redundant and can make "
                    "model interpretation or regularization harder."
                ),
                recommendation=(
                    "Review redundant features and consider feature selection or "
                    "regularisation."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(
                    context,
                    {"correlation_threshold": CORRELATION_THRESHOLD},
                ),
            )
        )
    return issues
