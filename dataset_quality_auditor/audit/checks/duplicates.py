"""Duplicate row check."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, HIGH, MEDIUM, WARNING


def check_duplicate_rows(
    df: pd.DataFrame, profile: dict[str, object], context: AuditContext
) -> list[Issue]:
    duplicate_count = int(profile["duplicate_row_count"])
    duplicate_percent = float(profile["duplicate_row_percent"])
    if duplicate_percent >= context.config["duplicate_critical_threshold"]:
        severity, risk, threshold = (
            CRITICAL,
            HIGH,
            context.config["duplicate_critical_threshold"],
        )
    elif duplicate_count > 0:
        severity, risk, threshold = (
            WARNING,
            MEDIUM,
            context.config["duplicate_warning_threshold"],
        )
    else:
        return []
    return [
        Issue(
            issue_id=issue_id("duplicate_rows", "dataset"),
            check_id="duplicate_rows",
            title="Duplicate rows detected",
            severity=severity,
            risk_level=risk,
            status="failed",
            scope={"dataset": "train", "column": None, "column_role": None},
            evidence=Evidence(
                "duplicate_row_percent",
                duplicate_percent,
                threshold,
                "observed_value >= threshold",
                {
                    "duplicate_row_count": duplicate_count,
                    "duplicate_row_percent": duplicate_percent,
                    "total_rows": int(profile["row_count"]),
                },
            ),
            ml_impact="Duplicate rows can distort validation estimates.",
            recommendation=(
                "Investigate duplicate records and decide whether they represent "
                "valid repeated observations before training."
            ),
            requires_human_review=False,
            reproducibility=reproducibility(
                context, {"duplicate_warning_threshold": threshold}
            ),
        )
    ]
