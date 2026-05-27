"""Missing value checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.recommendations import MISSING_VALUES
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING


def check_missing_values(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)

    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        missing_percent = float(column_profile["missing_percent"])
        if missing_percent >= context.config["missing_critical_threshold"]:
            severity = CRITICAL
            risk_level = HIGH
            threshold = context.config["missing_critical_threshold"]
        elif missing_percent >= context.config["missing_warning_threshold"]:
            severity = WARNING
            risk_level = MEDIUM
            threshold = context.config["missing_warning_threshold"]
        else:
            continue

        column_role = str(column_profile["inferred_role"])
        issues.append(
            Issue(
                issue_id=issue_id("missing_values", str(column)),
                check_id="missing_values",
                title="Missing values detected in feature column",
                severity=severity,
                risk_level=risk_level,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_role,
                },
                evidence=Evidence(
                    metric="missing_percent",
                    observed_value=missing_percent,
                    threshold=threshold,
                    comparison="observed_value >= threshold",
                    details={
                        "missing_count": int(column_profile["missing_count"]),
                        "total_rows": int(profile["row_count"]),
                        "missing_percent": missing_percent,
                    },
                ),
                ml_impact=(
                    "Missing values can make model training unstable if not "
                    "handled consistently."
                ),
                recommendation=MISSING_VALUES,
                requires_human_review=False,
                reproducibility=reproducibility(
                    context,
                    {"missing_warning_threshold": threshold},
                ),
            )
        )

    return issues
