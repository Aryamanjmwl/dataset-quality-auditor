import pandas as pd

from dataset_quality_auditor.audit.checks.missing import check_missing_values
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_missing_warning_and_critical_thresholds_create_issues() -> None:
    df = pd.DataFrame(
        {
            "warning_col": [1, None, 3, 4, 5],
            "critical_col": [None, None, None, 4, 5],
            "ok_col": [1, 2, 3, 4, 5],
        }
    )
    context = create_audit_context("data.csv")
    profile = profile_dataframe(df, config=context.config)

    issues = check_missing_values(df, profile, context)
    severities = {issue.scope["column"]: issue.severity for issue in issues}

    assert severities["warning_col"] == "warning"
    assert severities["critical_col"] == "critical"
    assert "ok_col" not in severities
