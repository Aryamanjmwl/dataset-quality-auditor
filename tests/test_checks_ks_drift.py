import pandas as pd
import pytest

pytest.importorskip("scipy")

from dataset_quality_auditor.audit.checks.ks_drift import check_ks_drift
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def _check(train: pd.DataFrame, test: pd.DataFrame):
    context = create_audit_context("train.csv", target_column="label")
    return check_ks_drift(
        train,
        test,
        profile_dataframe(train, "label"),
        profile_dataframe(test, "label"),
        context,
    )


def test_identical_distributions_produce_no_issue() -> None:
    train = pd.DataFrame({"x": list(range(20)), "label": [0, 1] * 10})
    test = pd.DataFrame({"x": list(range(20)), "label": [0, 1] * 10})

    assert _check(train, test) == []


def test_very_different_distributions_produce_warning() -> None:
    train = pd.DataFrame({"x": [0] * 20, "label": [0, 1] * 10})
    test = pd.DataFrame({"x": [100] * 20, "label": [0, 1] * 10})

    issues = _check(train, test)

    assert len(issues) == 1
    assert issues[0].check_id == "ks_drift"
    assert issues[0].severity == "warning"


def test_evidence_contains_ks_statistic_and_p_value() -> None:
    train = pd.DataFrame({"x": [0] * 20, "label": [0, 1] * 10})
    test = pd.DataFrame({"x": [100] * 20, "label": [0, 1] * 10})

    issue = _check(train, test)[0]

    assert {"ks_statistic", "p_value", "train_n", "test_n"}.issubset(
        issue.evidence.details
    )


def test_non_numeric_columns_are_skipped() -> None:
    train = pd.DataFrame({"city": ["a", "b"], "label": [0, 1]})
    test = pd.DataFrame({"city": ["a", "c"], "label": [0, 1]})

    assert _check(train, test) == []
