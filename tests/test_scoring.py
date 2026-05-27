from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.scoring import calculate_readiness_score
from dataset_quality_auditor.audit.severity import (
    CRITICAL,
    HIGH,
    INFO,
    LOW,
    MEDIUM,
    WARNING,
)


def _issue(issue_id: str, severity: str, review: bool = False) -> Issue:
    return Issue(
        issue_id=issue_id,
        check_id="check",
        title="Title",
        severity=severity,
        risk_level={CRITICAL: HIGH, WARNING: MEDIUM, INFO: LOW}[severity],
        status="failed",
        scope={},
        evidence=Evidence("metric", 1, 1, "==", {}),
        ml_impact="Impact",
        recommendation="Recommendation",
        requires_human_review=review,
        reproducibility={},
    )


def test_scoring_deterministic_deductions() -> None:
    score = calculate_readiness_score(
        [
            _issue("critical", CRITICAL),
            _issue("warning", WARNING, review=True),
            _issue("info", INFO),
        ]
    )

    assert score["score"] == 68
    assert score["score_band"] == "needs_attention"
    assert [item["deduction"] for item in score["deductions"]] == [20, 10, 2]
