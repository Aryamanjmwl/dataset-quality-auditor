"""ID-like column check."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.recommendations import ID_LIKE
from dataset_quality_auditor.audit.severity import INFO, LOW, MEDIUM, WARNING

ID_NAME_SIGNALS = (
    "id",
    "uuid",
    "identifier",
    "user_id",
    "customer_id",
    "transaction_id",
)


def check_id_like_columns(
    df: pd.DataFrame, profile: dict[str, object], context: AuditContext
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)
    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        if column == context.target_column:
            continue
        unique_percent = float(column_profile["unique_percent"])
        unique_signal = unique_percent >= context.config["id_unique_ratio_threshold"]
        name_signal = any(signal in str(column).lower() for signal in ID_NAME_SIGNALS)
        if not unique_signal and not name_signal:
            continue
        issues.append(
            Issue(
                issue_id=issue_id("id_like", str(column)),
                check_id="id_like_columns",
                title="Suspicious ID-like column detected",
                severity=WARNING if unique_signal else INFO,
                risk_level=MEDIUM if unique_signal else LOW,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_profile["inferred_role"],
                },
                evidence=Evidence(
                    "unique_percent",
                    unique_percent,
                    context.config["id_unique_ratio_threshold"],
                    "observed_value >= threshold or name contains ID signal",
                    {
                        "unique_count": int(column_profile["unique_count"]),
                        "total_rows": int(profile["row_count"]),
                        "name_signal": name_signal,
                        "unique_signal": unique_signal,
                    },
                ),
                ml_impact="ID-like columns may create leakage or brittle memorization.",
                recommendation=ID_LIKE,
                requires_human_review=True,
                reproducibility=reproducibility(
                    context,
                    {
                        "id_unique_ratio_threshold": context.config[
                            "id_unique_ratio_threshold"
                        ],
                        "name_signals": list(ID_NAME_SIGNALS),
                    },
                ),
            )
        )
    return issues
