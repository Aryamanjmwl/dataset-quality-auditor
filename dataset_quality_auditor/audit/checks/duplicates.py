"""Duplicate row checks."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING


def check_duplicate_rows(
    df: pd.DataFrame,
    profile: dict[str, object],
    context: AuditContext,
) -> list[Issue]:
    duplicate_row_count = int(profile["duplicate_row_count"])
    duplicate_row_percent = float(profile["duplicate_row_percent"])

    if duplicate_row_percent >= context.config["duplicate_critical_threshold"]:
        severity = CRITICAL
        risk_level = HIGH
        threshold = context.config["duplicate_critical_threshold"]
    elif duplicate_row_count > 0:
        severity = WARNING
        risk_level = MEDIUM
        threshold = context.config["duplicate_warning_threshold"]
    else:
        return []

    return [
        Issue(
            issue_id=issue_id("duplicate_rows", "dataset"),
            check_id="duplicate_rows",
            title="Duplicate rows detected",
            severity=severity,
            risk_level=risk_level,
            status="failed",
            scope={"dataset": "train", "column": None, "column_role": None},
            evidence=Evidence(
                metric="duplicate_row_percent",
                observed_value=duplicate_row_percent,
                threshold=threshold,
                comparison="observed_value >= threshold",
                details={
                    "duplicate_row_count": duplicate_row_count,
                    "duplicate_row_percent": duplicate_row_percent,
                    "total_rows": int(profile["row_count"]),
                },
            ),
            ml_impact=(
                "Duplicate rows can distort validation estimates and make "
                "models overfit repeated records."
            ),
            recommendation=(
                "Investigate duplicate records and decide whether they represent "
                "valid repeated observations before training."
            ),
            requires_human_review=False,
            reproducibility=reproducibility(
                context,
                {"duplicate_warning_threshold": threshold},
            ),
        )
    ]
