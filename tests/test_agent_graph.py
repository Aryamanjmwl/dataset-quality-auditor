import copy

from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.agent.graph import run_review_graph
from dataset_quality_auditor.ai.guardrails import assert_ai_review_valid


def test_run_review_graph_returns_valid_ai_review() -> None:
    audit_result = sample_graph_audit_result()
    review = run_review_graph(audit_result)

    assert review["provider"] == "mock"
    assert review["model"] == "deterministic-mock"
    assert review["readiness_score"] == audit_result["score"]["score"]
    assert "markdown_report" in review
    assert_ai_review_valid(review, audit_result)


def test_run_review_graph_does_not_mutate_audit_result() -> None:
    audit_result = sample_graph_audit_result()
    original = copy.deepcopy(audit_result)

    run_review_graph(audit_result)

    assert audit_result == original
