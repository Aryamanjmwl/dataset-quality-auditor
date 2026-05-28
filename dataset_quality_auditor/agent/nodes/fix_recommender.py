"""Safe fix recommendation node for deterministic review workflows."""

from __future__ import annotations

import copy


def _issue_map(audit_result: dict[str, object]) -> dict[str, dict[str, object]]:
    issues = audit_result.get("issues", [])
    assert isinstance(issues, list)
    return {
        str(issue["issue_id"]): issue
        for issue in issues
        if isinstance(issue, dict) and "issue_id" in issue
    }


def recommend_fixes(state: dict[str, object]) -> dict[str, object]:
    """Create safe next steps from existing deterministic recommendations."""
    next_state = copy.deepcopy(state)
    audit_result = next_state["audit_result"]
    assert isinstance(audit_result, dict)
    issues_by_id = _issue_map(audit_result)
    prioritized = next_state.get("prioritized_issues", [])
    assert isinstance(prioritized, list)

    next_steps: list[dict[str, object]] = []
    human_questions: list[dict[str, object]] = []
    for prioritized_issue in prioritized:
        if not isinstance(prioritized_issue, dict):
            continue
        issue_id = str(prioritized_issue["issue_id"])
        issue = issues_by_id[issue_id]
        requires_review = bool(issue.get("requires_human_review", False))
        recommendation = str(issue.get("recommendation", "Review this issue."))
        impact = str(issue.get("ml_impact", "This may affect model readiness."))

        next_steps.append(
            {
                "issue_id": issue_id,
                "action": recommendation,
                "why": impact,
                "automation_level": (
                    "manual_review"
                    if requires_review
                    else "safe_suggestion_only"
                ),
            }
        )
        if requires_review:
            next_steps[-1]["action"] = (
                f"Manually review this finding before changing training data "
                f"or pipeline behavior. {recommendation}"
            )
            human_questions.append(
                {
                    "issue_id": issue_id,
                    "question": (
                        "Is this column or condition valid, available at "
                        "prediction time, and appropriate for model training?"
                    ),
                    "reason": impact,
                }
            )

    next_state["safe_next_steps"] = next_steps
    next_state["human_review_questions"] = human_questions
    return next_state
