import pandas as pd

from dataset_quality_auditor.audit.checks.leakage import (
    check_target_leakage_candidates,
)
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_target_like_name_creates_human_review_issue() -> None:
    df = pd.DataFrame(
        {"outcome_score": [1, 2, 3, 4], "feature": [9, 8, 7, 6], "label": [0, 0, 1, 1]}
    )
    context = create_audit_context("data.csv", target_column="label")

    issues = check_target_leakage_candidates(
        df,
        profile_dataframe(df, "label"),
        context,
    )

    assert any(issue.requires_human_review for issue in issues)
    assert any(issue.scope["column"] == "outcome_score" for issue in issues)


def test_high_target_correlation_creates_leakage_candidate() -> None:
    df = pd.DataFrame({"feature": [0, 0, 1, 1], "label": [0, 0, 1, 1]})
    context = create_audit_context("data.csv", target_column="label")

    issues = check_target_leakage_candidates(
        df,
        profile_dataframe(df, "label"),
        context,
    )

    assert len(issues) == 1
    assert issues[0].severity == "critical"
    assert issues[0].requires_human_review is True
