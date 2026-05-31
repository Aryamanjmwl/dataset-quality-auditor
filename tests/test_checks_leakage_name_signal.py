import pandas as pd

from dataset_quality_auditor.audit.checks.leakage import (
    check_target_leakage_candidates,
)
from dataset_quality_auditor.audit.context import create_audit_context
from dataset_quality_auditor.audit.profiler import profile_dataframe


def _issues(df: pd.DataFrame):
    context = create_audit_context("data.csv", target_column="label")
    return check_target_leakage_candidates(df, profile_dataframe(df, "label"), context)


def test_numeric_column_with_signal_name_and_low_correlation_is_not_flagged() -> None:
    df = pd.DataFrame(
        {
            "outcome_score": [1, 2, 3, 4],
            "label": [1, 0, 0, 1],
        }
    )

    assert _issues(df) == []


def test_numeric_signal_name_with_medium_correlation_flagged_as_warning() -> None:
    df = pd.DataFrame(
        {
            "result": [0, 0, 1, 1, 1, 0],
            "label": [0, 0, 1, 1, 0, 0],
        }
    )

    issues = _issues(df)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert (
        issues[0].evidence.details["signal_type"]
        == "target_like_name_with_correlation"
    )


def test_nonnumeric_column_with_signal_name_is_still_flagged() -> None:
    df = pd.DataFrame(
        {
            "outcome": ["pass", "fail", "pass", "pass"],
            "label": [1, 0, 1, 1],
        }
    )

    issues = _issues(df)

    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert issues[0].evidence.details["signal_type"] == "target_like_name"


def test_no_double_reporting_when_name_and_correlation_both_high() -> None:
    df = pd.DataFrame(
        {
            "predicted_value": [0, 0, 1, 1],
            "label": [0, 0, 1, 1],
        }
    )

    issues = _issues(df)

    assert len(issues) == 1
    assert issues[0].severity == "critical"
    assert issues[0].evidence.details["signal_type"] == "target_correlation"
