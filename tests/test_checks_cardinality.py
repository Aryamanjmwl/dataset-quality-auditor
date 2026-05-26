import pandas as pd

from dataset_quality_auditor.audit.checks.cardinality import check_high_cardinality
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_high_cardinality_warning_and_human_review() -> None:
    df = pd.DataFrame(
        {
            "code": ["a", "b", "c", "d"],
            "numeric": [1, 2, 3, 4],
            "label": [0, 1, 0, 1],
        }
    )
    context = create_audit_context("data.csv", target_column="label")
    profile = profile_dataframe(df, target_column="label", config=context.config)

    issues = check_high_cardinality(df, profile, context)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].scope["column"] == "code"
    assert issues[0].requires_human_review is True
