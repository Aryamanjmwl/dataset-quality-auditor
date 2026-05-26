from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.scoring import calculate_readiness_score


def _issue(issue_id: str, severity: str, review: bool = False) -> Issue:
    risk_level = {
        "critical": "high",
        "warning": "medium",
        "info": "low",
    }[severity]
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
        requires_human_review=review,
        reproducibility={},
    )


def test_scoring_deterministic_deductions_and_human_review_extra() -> None:
    score = calculate_readiness_score(
        [
            _issue("critical", "critical"),
            _issue("warning", "warning", review=True),
            _issue("info", "info"),
        ]
    )

    assert score["score"] == 68
    assert score["score_band"] == "needs_attention"
    assert [item["deduction"] for item in score["deductions"]] == [20, 10, 2]


def test_scoring_high_risk_band() -> None:
    score = calculate_readiness_score(
        [_issue(f"critical_{index}", "critical") for index in range(3)]
    )

    assert score["score"] == 40
    assert score["score_band"] == "high_risk"
