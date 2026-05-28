from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.agent.nodes.risk_prioritizer import prioritize_risks
from dataset_quality_auditor.agent.state import create_initial_state


def test_prioritize_risks_orders_by_severity_and_preserves_ids() -> None:
    state = create_initial_state(sample_graph_audit_result())
    result = prioritize_risks(state)

    prioritized = result["prioritized_issues"]
    assert [issue["issue_id"] for issue in prioritized] == [
        "target_leakage_score_001",
        "missing_values_age_001",
        "id_like_customer_001",
        "datatype_risk_income_001",
    ]
    assert prioritized[0]["priority"] == "high"
    assert prioritized[1]["priority"] == "medium"
    assert prioritized[-1]["priority"] == "low"
