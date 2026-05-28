"""Final output validation node for deterministic review workflows."""

from __future__ import annotations

import copy

from dataset_quality_auditor.ai.schemas import REVIEW_VERSION


def _summary(audit_result: dict[str, object], issue_count: int) -> str:
    score = audit_result.get("score", {})
    assert isinstance(score, dict)
    return (
        f"The graph review prioritized {issue_count} deterministic issues. "
        f"The readiness score is {score.get('score')}/"
        f"{score.get('max_score', 100)} with score band "
        f"{score.get('score_band')}."
    )


def validate_workflow_output(state: dict[str, object]) -> dict[str, object]:
    """Build and guardrail-check the final graph review object."""
    next_state = copy.deepcopy(state)
    audit_result = next_state["audit_result"]
    assert isinstance(audit_result, dict)
    score = audit_result.get("score", {})
    assert isinstance(score, dict)
    prioritized = next_state.get("prioritized_issues", [])
    assert isinstance(prioritized, list)

    ai_review: dict[str, object] = {
        "review_version": REVIEW_VERSION,
        "provider": next_state.get("provider_name", "mock"),
        "model": next_state.get("model_name", "deterministic-mock"),
        "audit_id": audit_result.get("audit_id"),
        "readiness_score": score.get("score"),
        "score_band": score.get("score_band"),
        "summary": _summary(audit_result, len(prioritized)),
        "prioritized_issues": prioritized,
        "safe_next_steps": next_state.get("safe_next_steps", []),
        "human_review_questions": next_state.get("human_review_questions", []),
        "contract_recommendations": next_state.get(
            "contract_recommendations",
            [],
        ),
        "markdown_report": next_state.get("markdown_report", ""),
        "metadata": {
            "deterministic_source": True,
            "ai_generated": True,
            "source_audit_json": "",
            "workflow": "graph",
        },
    }

    try:
        from dataset_quality_auditor.ai.guardrails import assert_ai_review_valid

        assert_ai_review_valid(ai_review, audit_result)
    except ValueError as exc:
        next_state["validation_errors"] = [
            {"error": str(exc), "stage": "output_validator"}
        ]
        raise

    next_state["ai_review"] = ai_review
    next_state["validation_errors"] = []
    return next_state
