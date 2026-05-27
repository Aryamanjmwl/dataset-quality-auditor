import pandas as pd

from dataset_quality_auditor.audit.checks.drift import check_train_test_drift
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_numeric_mean_shift_creates_drift_issue() -> None:
    train = pd.DataFrame({"x": [0, 1, 2, 3, 4], "label": [0, 0, 1, 1, 1]})
    test = pd.DataFrame({"x": [10, 11, 12, 13, 14], "label": [0, 0, 1, 1, 1]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert any(issue.check_id == "numeric_drift" for issue in issues)


def test_unseen_categorical_category_creates_warning() -> None:
    train = pd.DataFrame({"city": ["a", "b", "a"], "label": [0, 1, 0]})
    test = pd.DataFrame({"city": ["a", "c"], "label": [0, 1]})
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert any(issue.check_id == "categorical_drift" for issue in issues)
    assert any("c" in issue.evidence.details["unseen_categories"] for issue in issues)
