from tests.test_scoring import _issue

from dataset_quality_auditor.audit.scoring import calculate_readiness_score
from dataset_quality_auditor.audit.severity import CRITICAL, INFO, WARNING


def test_single_critical_beats_six_warnings() -> None:
    score_with_one_critical = calculate_readiness_score(
        [_issue("critical", CRITICAL)]
    )
    score_with_six_warnings = calculate_readiness_score(
        [_issue(f"warning_{index}", WARNING) for index in range(6)]
    )

    assert score_with_one_critical["score"] > score_with_six_warnings["score"]


def test_cap_stops_at_severity_limit() -> None:
    score_with_four_warnings = calculate_readiness_score(
        [_issue(f"warning_{index}", WARNING) for index in range(4)]
    )
    score_with_ten_warnings = calculate_readiness_score(
        [_issue(f"warning_{index}", WARNING) for index in range(10)]
    )

    assert score_with_ten_warnings["score"] == score_with_four_warnings["score"]
    assert score_with_ten_warnings["severity_totals"]["warning"] == {
        "raw": 80,
        "capped": 32,
        "issues": 10,
    }


def test_human_review_deduction_is_uncapped() -> None:
    score = calculate_readiness_score(
        [_issue(f"info_{index}", INFO, review=True) for index in range(5)]
    )

    assert score["score"] == 80
    assert score["severity_totals"]["info"] == {
        "raw": 10,
        "capped": 10,
        "issues": 5,
    }


def test_severity_totals_key_present() -> None:
    score = calculate_readiness_score([_issue("critical", CRITICAL)])

    assert set(score["severity_totals"]) == {"critical", "warning", "info"}
    assert set(score["severity_totals"]["critical"]) == {
        "raw",
        "capped",
        "issues",
    }


def test_existing_no_issues_returns_100() -> None:
    score = calculate_readiness_score([])

    assert score["score"] == 100
