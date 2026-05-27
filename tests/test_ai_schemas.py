from dataset_quality_auditor.ai.schemas import AIReview, PrioritizedIssue


def test_ai_review_schema_contains_required_top_level_fields() -> None:
    review = AIReview(
        provider="mock",
        model="deterministic-mock",
        audit_id="audit-1",
        readiness_score=72,
        score_band="needs_attention",
        summary="Summary",
        prioritized_issues=[
            PrioritizedIssue(
                issue_id="issue-1",
                priority="high",
                reason="Reason",
                severity="critical",
                check_id="check",
            )
        ],
        metadata={
            "deterministic_source": True,
            "ai_generated": True,
            "source_audit_json": "reports/audit.json",
        },
    ).to_dict()

    assert review["review_version"] == "0.1.0"
    assert review["provider"] == "mock"
    assert review["readiness_score"] == 72
    assert review["prioritized_issues"][0]["issue_id"] == "issue-1"
    assert review["metadata"]["ai_generated"] is True
