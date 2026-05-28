from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.agent.nodes.fix_recommender import recommend_fixes
from dataset_quality_auditor.agent.nodes.risk_prioritizer import prioritize_risks
from dataset_quality_auditor.agent.state import create_initial_state


def test_recommend_fixes_reference_existing_issue_ids() -> None:
    state = prioritize_risks(create_initial_state(sample_graph_audit_result()))
    result = recommend_fixes(state)

    issue_ids = {
        issue["issue_id"]
        for issue in result["audit_result"]["issues"]
    }
    assert {
        step["issue_id"]
        for step in result["safe_next_steps"]
    }.issubset(issue_ids)


def test_human_review_issues_get_manual_review_level() -> None:
    state = prioritize_risks(create_initial_state(sample_graph_audit_result()))
    result = recommend_fixes(state)

    steps = {
        step["issue_id"]: step["automation_level"]
        for step in result["safe_next_steps"]
    }
    assert steps["target_leakage_score_001"] == "manual_review"
    assert steps["id_like_customer_001"] == "manual_review"
    assert steps["missing_values_age_001"] == "safe_suggestion_only"
