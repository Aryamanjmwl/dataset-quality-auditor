import pandas as pd

from dataset_quality_auditor.audit.checks.datatypes import check_datatype_risks
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_datatype_risk_detection() -> None:
    df = pd.DataFrame(
        {"income_text": ["100", "200", "unknown", "400"], "label": [0, 1, 0, 1]}
    )
    context = create_audit_context("data.csv", target_column="label")
    profile = profile_dataframe(df, target_column="label", config=context.config)

    issues = check_datatype_risks(df, profile, context)

    assert len(issues) == 0

    df = pd.DataFrame(
        {"income_text": ["100", "200", "300", "400"], "label": [0, 1, 0, 1]}
    )
    profile = profile_dataframe(df, target_column="label", config=context.config)
    issues = check_datatype_risks(df, profile, context)

    assert len(issues) == 1
    assert issues[0].scope["column"] == "income_text"
