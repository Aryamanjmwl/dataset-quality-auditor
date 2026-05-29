import pandas as pd

from dataset_quality_auditor.audit.checks.schema_mismatch import check_schema_mismatch
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_missing_test_feature_column_produces_critical_issue() -> None:
    train = pd.DataFrame({"age": [1, 2], "city": ["a", "b"], "label": [0, 1]})
    test = pd.DataFrame({"city": ["a", "b"], "label": [0, 1]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_schema_mismatch(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert any(
        issue.scope["column"] == "age" and issue.severity == "critical"
        for issue in issues
    )


def test_extra_test_column_produces_info_issue() -> None:
    train = pd.DataFrame({"age": [1, 2], "label": [0, 1]})
    test = pd.DataFrame({"age": [1, 2], "extra": [3, 4], "label": [0, 1]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_schema_mismatch(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert any(issue.severity == "info" for issue in issues)
    assert any("extra" in issue.evidence.details["extra_in_test"] for issue in issues)


def test_type_kind_mismatch_produces_warning_issue() -> None:
    train = pd.DataFrame({"feature": [1, 2, 3], "label": [0, 1, 0]})
    test = pd.DataFrame({"feature": ["low", "medium", "high"], "label": [0, 1, 0]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_schema_mismatch(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    issue = next(
        issue
        for issue in issues
        if issue.issue_id.startswith("schema_type_kind_mismatch_feature")
    )
    assert issue.severity == "warning"
    assert issue.evidence.details["type_kind_mismatches"]["feature"] == {
        "train_kind": "numeric",
        "test_kind": "categorical",
    }
