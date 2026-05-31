import pytest

from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.scoring import calculate_readiness_score
from dataset_quality_auditor.audit.severity import HIGH, LOW, WARNING


def _issue(issue_id: str, severity: str, risk_level: str) -> Issue:
    return Issue(
        issue_id=issue_id,
        check_id="check",
        title="Title",
        severity=severity,
        risk_level=risk_level,
        status="failed",
        scope={},
        evidence=Evidence("metric", 1, 1, "==", {}),
        ml_impact="Impact",
        recommendation="Recommendation",
        requires_human_review=False,
        reproducibility={},
    )


def test_risk_level_high_does_not_affect_score() -> None:
    high_risk = calculate_readiness_score(
        [_issue("warning_high", WARNING, HIGH)]
    )
    low_risk = calculate_readiness_score([_issue("warning_low", WARNING, LOW)])

    assert high_risk["score"] == low_risk["score"]


def test_unknown_severity_emits_warning_and_zero_deduction() -> None:
    issue = _issue("unknown", "unknown_level", HIGH)

    with pytest.warns(UserWarning):
        score = calculate_readiness_score([issue])

    assert score["score"] == 100
    assert score["deductions"][0]["deduction"] == 0
