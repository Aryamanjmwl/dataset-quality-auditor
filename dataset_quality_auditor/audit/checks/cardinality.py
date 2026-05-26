"""High-cardinality check."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.recommendations import HIGH_CARDINALITY
from dataset_quality_auditor.audit.severity import MEDIUM, WARNING


def check_high_cardinality(
    df: pd.DataFrame, profile: dict[str, object], context: AuditContext
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)
    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        if column == context.target_column or bool(column_profile["is_numeric"]):
            continue
        unique_percent = float(column_profile["unique_percent"])
        if unique_percent < context.config["high_cardinality_threshold"]:
            continue
        issues.append(
            Issue(
                issue_id=issue_id("high_cardinality", str(column)),
                check_id="high_cardinality",
                title="High-cardinality categorical column detected",
                severity=WARNING,
                risk_level=MEDIUM,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_profile["inferred_role"],
                },
                evidence=Evidence(
                    "unique_percent",
                    unique_percent,
                    context.config["high_cardinality_threshold"],
                    "observed_value >= threshold",
                    {
                        "unique_count": int(column_profile["unique_count"]),
                        "total_rows": int(profile["row_count"]),
                        "unique_percent": unique_percent,
                    },
                ),
                ml_impact="High-cardinality categories can create unstable encodings.",
                recommendation=HIGH_CARDINALITY,
                requires_human_review=(
                    unique_percent >= context.config["id_unique_ratio_threshold"]
                ),
                reproducibility=reproducibility(
                    context,
                    {
                        "high_cardinality_threshold": context.config[
                            "high_cardinality_threshold"
                        ],
                        "id_unique_ratio_threshold": context.config[
                            "id_unique_ratio_threshold"
                        ],
                    },
                ),
            )
        )
    return issues
