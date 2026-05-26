import pandas as pd

from dataset_quality_auditor.audit.checks.id_like import check_id_like_columns
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_id_like_column_requires_human_review() -> None:
    df = pd.DataFrame({"customer_id": ["a", "b", "c", "d"], "label": [0, 1, 0, 1]})
    context = create_audit_context("data.csv", target_column="label")
    profile = profile_dataframe(df, target_column="label", config=context.config)

    issues = check_id_like_columns(df, profile, context)

    assert len(issues) == 1
    assert issues[0].scope["column"] == "customer_id"
    assert issues[0].requires_human_review is True
