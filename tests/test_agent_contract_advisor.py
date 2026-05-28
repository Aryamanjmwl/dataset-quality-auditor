from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.agent.nodes.contract_advisor import advise_contract_rules
from dataset_quality_auditor.agent.state import create_initial_state


def test_contract_advice_references_existing_issue_ids() -> None:
    state = create_initial_state(sample_graph_audit_result())
    result = advise_contract_rules(state)

    advice = result["contract_recommendations"]
    assert {item["issue_id"] for item in advice} == {
        "datatype_risk_income_001",
        "missing_values_age_001",
        "id_like_customer_001",
    }
    assert {item["rule_type"] for item in advice} == {
        "explicit_type_rule",
        "max_missing_percent_review",
        "uniqueness_or_id_role_review",
    }
