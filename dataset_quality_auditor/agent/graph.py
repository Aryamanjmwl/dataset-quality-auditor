"""Deterministic graph runner for AI-assisted audit review."""

from __future__ import annotations

from dataset_quality_auditor.agent.nodes import (
    advise_contract_rules,
    prioritize_risks,
    recommend_fixes,
    validate_workflow_output,
    write_review_report,
)
from dataset_quality_auditor.agent.state import create_initial_state


def run_review_graph(
    audit_result: dict[str, object],
    provider_name: str = "mock",
    model_name: str = "deterministic-mock",
) -> dict[str, object]:
    """Run the local graph-style review workflow."""
    if provider_name.lower() != "mock":
        msg = "Graph workflow currently supports only the mock provider."
        raise ValueError(msg)

    state = create_initial_state(
        audit_result=audit_result,
        provider_name=provider_name,
        model_name=model_name,
    )
    for node in (
        prioritize_risks,
        recommend_fixes,
        advise_contract_rules,
        write_review_report,
        validate_workflow_output,
    ):
        state = node(state)

    ai_review = state["ai_review"]
    assert isinstance(ai_review, dict)
    return ai_review
