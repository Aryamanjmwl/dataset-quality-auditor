import pandas as pd

from dataset_quality_auditor.audit.checks.drift import check_train_test_drift
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def test_similar_train_test_data_produces_no_drift_issue() -> None:
    train = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "city": ["a", "a", "b", "b"],
            "label": [0, 1, 0, 1],
        }
    )
    test = pd.DataFrame(
        {
            "x": [1.1, 2.1, 3.1, 4.1],
            "city": ["a", "a", "b", "b"],
            "label": [0, 1, 0, 1],
        }
    )
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    assert issues == []


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
    issue = next(issue for issue in issues if issue.check_id == "numeric_drift")
    assert issue.evidence.details["train_mean"] == 2.0
    assert issue.evidence.details["test_mean"] == 12.0
    assert "mean_shift" in issue.evidence.details


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


def test_dominant_categorical_category_shift_creates_warning() -> None:
    train = pd.DataFrame(
        {
            "city": ["a", "a", "a", "b", "b"],
            "label": [0, 1, 0, 1, 0],
        }
    )
    test = pd.DataFrame(
        {
            "city": ["a", "b", "b", "b", "b"],
            "label": [0, 1, 0, 1, 0],
        }
    )
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    issue = next(issue for issue in issues if issue.check_id == "categorical_drift")
    assert issue.evidence.metric == "dominant_category_shift"
    assert issue.evidence.details["train_top_category"] == "a"
    assert issue.evidence.details["test_top_category"] == "b"


def test_missing_category_ratio_uses_real_trigger_threshold() -> None:
    train = pd.DataFrame(
        {
            "city": ["a", "b", "c", "d"],
            "label": [0, 1, 0, 1],
        }
    )
    test = pd.DataFrame(
        {
            "city": ["a", "b", "a", "b"],
            "label": [0, 1, 0, 1],
        }
    )
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    issue = next(issue for issue in issues if issue.check_id == "categorical_drift")
    assert issue.evidence.metric == "missing_category_ratio"
    assert issue.evidence.threshold == 0.50
    assert issue.evidence.comparison == "observed_value >= threshold"


def test_target_distribution_shift_creates_warning_issue() -> None:
    train = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "label": [0, 0, 0, 0, 1],
        }
    )
    test = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "label": [0, 1, 1, 1, 1],
        }
    )
    context = create_audit_context("train.csv", target_column="label")

    issues = check_train_test_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )

    issue = next(
        issue for issue in issues if issue.check_id == "target_distribution_drift"
    )
    assert issue.severity == "critical"
    assert issue.evidence.metric == "max_target_distribution_shift"
    assert issue.evidence.details["train_distribution"] == {"0": 0.8, "1": 0.2}
    assert issue.evidence.details["test_distribution"] == {"0": 0.2, "1": 0.8}
