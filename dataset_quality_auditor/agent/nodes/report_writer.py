"""Markdown report node for deterministic review workflows."""

from __future__ import annotations

import copy


def _md_inline(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def _md_code(value: object) -> str:
    return _md_inline(value).replace("`", "\\`")


def _issue_summary(prioritized: list[dict[str, object]]) -> dict[str, int]:
    summary = {"high": 0, "medium": 0, "low": 0}
    for issue in prioritized:
        priority = str(issue.get("priority", "low"))
        summary[priority] = summary.get(priority, 0) + 1
    return summary


def write_review_report(state: dict[str, object]) -> dict[str, object]:
    """Write a Markdown review from deterministic audit findings."""
    next_state = copy.deepcopy(state)
    audit_result = next_state["audit_result"]
    assert isinstance(audit_result, dict)
    score = audit_result.get("score", {})
    assert isinstance(score, dict)
    prioritized = next_state.get("prioritized_issues", [])
    safe_next_steps = next_state.get("safe_next_steps", [])
    questions = next_state.get("human_review_questions", [])
    contract_advice = next_state.get("contract_recommendations", [])
    assert isinstance(prioritized, list)
    assert isinstance(safe_next_steps, list)
    assert isinstance(questions, list)
    assert isinstance(contract_advice, list)

    priority_summary = _issue_summary(
        [item for item in prioritized if isinstance(item, dict)]
    )
    lines = [
        "# AI-Assisted Dataset Review",
        "",
        "This AI-assisted review is generated from deterministic audit findings.",
        "",
        "## Readiness",
        "",
        f"- Readiness score: {_md_inline(score.get('score'))}/"
        f"{_md_inline(score.get('max_score', 100))}",
        f"- Score band: {_md_inline(score.get('score_band'))}",
        f"- Audit ID: {_md_inline(audit_result.get('audit_id'))}",
        "",
        "## Priority Summary",
        "",
        f"- High priority: {priority_summary.get('high', 0)}",
        f"- Medium priority: {priority_summary.get('medium', 0)}",
        f"- Low priority: {priority_summary.get('low', 0)}",
        "",
        "## Prioritized Issues",
        "",
    ]

    if prioritized:
        for issue in prioritized:
            if isinstance(issue, dict):
                lines.append(
                    f"- `{_md_code(issue['issue_id'])}`: "
                    f"{_md_inline(issue['priority'])} priority "
                    f"({_md_inline(issue['severity'])}, "
                    f"{_md_inline(issue['check_id'])}) - "
                    f"{_md_inline(issue['reason'])}"
                )
    else:
        lines.append("- No deterministic issues were reported.")

    lines.extend(["", "## Safe Next Steps", ""])
    if safe_next_steps:
        for step in safe_next_steps:
            if isinstance(step, dict):
                lines.append(
                    f"- `{_md_code(step['issue_id'])}`: "
                    f"{_md_inline(step['action'])} "
                    f"({_md_inline(step['automation_level'])})"
                )
    else:
        lines.append("- No issue-specific next steps are required.")

    lines.extend(["", "## Human Review Questions", ""])
    if questions:
        for question in questions:
            if isinstance(question, dict):
                lines.append(
                    f"- `{_md_code(question['issue_id'])}`: "
                    f"{_md_inline(question['question'])} "
                    f"Reason: {_md_inline(question['reason'])}"
                )
    else:
        lines.append("- No human-review-only questions were generated.")

    lines.extend(["", "## Contract Advice", ""])
    if contract_advice:
        for item in contract_advice:
            if isinstance(item, dict):
                column = item.get("column") or "dataset"
                lines.append(
                    f"- `{_md_code(item['issue_id'])}`: "
                    f"{_md_inline(item['rule_type'])} for "
                    f"`{_md_code(column)}` - "
                    f"{_md_inline(item['recommendation'])}"
                )
    else:
        lines.append("- No contract advice was generated from current issues.")

    next_state["markdown_report"] = "\n".join(lines) + "\n"
    return next_state
