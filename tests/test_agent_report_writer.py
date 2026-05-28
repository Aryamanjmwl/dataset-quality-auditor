from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.agent.nodes.contract_advisor import advise_contract_rules
from dataset_quality_auditor.agent.nodes.fix_recommender import recommend_fixes
from dataset_quality_auditor.agent.nodes.report_writer import write_review_report
from dataset_quality_auditor.agent.nodes.risk_prioritizer import prioritize_risks
from dataset_quality_auditor.agent.state import create_initial_state


def test_write_review_report_contains_deterministic_wording_and_ids() -> None:
    state = create_initial_state(sample_graph_audit_result())
    state = prioritize_risks(state)
    state = recommend_fixes(state)
    state = advise_contract_rules(state)
    result = write_review_report(state)

    markdown = result["markdown_report"]
    assert (
        "This AI-assisted review is generated from deterministic audit findings."
        in markdown
    )
    assert "Readiness score: 50/100" in markdown
    assert "target_leakage_score_001" in markdown
    assert "missing_values_age_001" in markdown
