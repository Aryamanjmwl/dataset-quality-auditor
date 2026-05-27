"""Outlier risk checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING


def check_outlier_risk(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)
    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        if column == context.target_column or not bool(column_profile["is_numeric"]):
            continue
        series = df[column].dropna()
        if series.empty:
            continue
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_mask = (series < lower) | (series > upper)
        outlier_count = int(outlier_mask.sum())
        outlier_percent = float(outlier_count / len(df)) if len(df) else 0.0
        if outlier_percent >= 0.15:
            severity, risk, threshold = CRITICAL, HIGH, 0.15
        elif outlier_percent >= 0.05:
            severity, risk, threshold = WARNING, MEDIUM, 0.05
        else:
            continue
        issues.append(
            Issue(
                issue_id=issue_id("outlier_risk", str(column)),
                check_id="outlier_risk",
                title="Numeric outlier risk detected",
                severity=severity,
                risk_level=risk,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_profile["inferred_role"],
                },
                evidence=Evidence(
                    metric="outlier_percent",
                    observed_value=outlier_percent,
                    threshold=threshold,
                    comparison="observed_value >= threshold",
                    details={
                        "lower_bound": lower,
                        "upper_bound": upper,
                        "outlier_count": outlier_count,
                        "outlier_percent": outlier_percent,
                    },
                ),
                ml_impact=(
                    "Outliers can dominate model training or distort scaling if "
                    "not handled consistently."
                ),
                recommendation=(
                    "Inspect outliers before training and consider robust "
                    "preprocessing where appropriate; do not blindly remove them."
                ),
                requires_human_review=False,
                reproducibility=reproducibility(
                    context,
                    {"iqr_multiplier": 1.5, "warning_threshold": 0.05},
                ),
            )
        )
    return issues
