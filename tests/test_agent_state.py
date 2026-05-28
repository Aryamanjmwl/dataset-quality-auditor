from tests.fixtures import sample_audit_result

from dataset_quality_auditor.agent.state import ReviewState, create_initial_state


def test_review_state_initializes_empty_lists() -> None:
    state = ReviewState(audit_result=sample_audit_result()).to_dict()

    assert state["provider_name"] == "mock"
    assert state["model_name"] == "deterministic-mock"
    assert state["prioritized_issues"] == []
    assert state["safe_next_steps"] == []
    assert state["contract_recommendations"] == []
    assert state["human_review_questions"] == []


def test_create_initial_state_copies_audit_result() -> None:
    audit_result = sample_audit_result()
    state = create_initial_state(audit_result)
    audit_result["audit_id"] = "changed"

    assert state["audit_result"]["audit_id"] == "audit-001"
