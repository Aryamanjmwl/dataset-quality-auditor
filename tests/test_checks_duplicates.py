import pandas as pd

from dataset_quality_auditor.audit.checks.duplicates import check_duplicate_rows
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_duplicate_rows_create_issue() -> None:
    df = pd.DataFrame(
        {
            "x": [1, 1, *range(2, 20)],
            "y": ["a", "a", *[f"value_{index}" for index in range(2, 20)]],
        }
    )
    context = create_audit_context("data.csv")
    profile = profile_dataframe(df, config=context.config)

    issues = check_duplicate_rows(df, profile, context)

    assert len(issues) == 1
    assert issues[0].check_id == "duplicate_rows"
    assert issues[0].evidence.details["duplicate_row_count"] == 1
