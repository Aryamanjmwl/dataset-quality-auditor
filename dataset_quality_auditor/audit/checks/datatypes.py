"""Datatype risk check."""

import pandas as pd

from dataset_quality_auditor.audit.checks import issue_id, reproducibility
from dataset_quality_auditor.audit.context import AuditContext
from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.recommendations import DATATYPE_RISK
from dataset_quality_auditor.audit.severity import INFO, LOW, MEDIUM, WARNING


def check_datatype_risks(
    df: pd.DataFrame, profile: dict[str, object], context: AuditContext
) -> list[Issue]:
    issues: list[Issue] = []
    columns = profile["columns"]
    assert isinstance(columns, dict)
    for column, column_profile in columns.items():
        assert isinstance(column_profile, dict)
        if not bool(column_profile["is_categorical"]):
            continue
        non_null = df[column].dropna()
        if non_null.empty:
            continue
        parse_ratio = float(pd.to_numeric(non_null, errors="coerce").notna().mean())
        if parse_ratio < 0.80:
            continue
        severity = WARNING if parse_ratio >= 0.95 else INFO
        issues.append(
            Issue(
                issue_id=issue_id("datatype_risk", str(column)),
                check_id="datatype_risks",
                title="Object column appears numeric",
                severity=severity,
                risk_level=MEDIUM if severity == WARNING else LOW,
                status="failed",
                scope={
                    "dataset": "train",
                    "column": column,
                    "column_role": column_profile["inferred_role"],
                },
                evidence=Evidence(
                    "numeric_parse_ratio",
                    parse_ratio,
                    0.80,
                    "observed_value >= threshold",
                    {
                        "numeric_parse_ratio": parse_ratio,
                        "non_null_count": int(non_null.size),
                        "dtype": str(column_profile["dtype"]),
                    },
                ),
                ml_impact=(
                    "Numeric strings can parse inconsistently across environments."
                ),
                recommendation=DATATYPE_RISK,
                requires_human_review=False,
                reproducibility=reproducibility(
                    context, {"numeric_parse_ratio_threshold": 0.80}
                ),
            )
        )
    return issues
