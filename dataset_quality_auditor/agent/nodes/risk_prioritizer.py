"""Risk prioritization node for deterministic review workflows."""

from __future__ import annotations

import copy

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}
PRIORITY_BY_SEVERITY = {
    "critical": "high",
    "warning": "medium",
    "info": "low",
}


def prioritize_risks(state: dict[str, object]) -> dict[str, object]:
    """Prioritize existing audit issues without changing their meaning."""
    next_state = copy.deepcopy(state)
    audit_result = next_state["audit_result"]
    assert isinstance(audit_result, dict)
    issues = audit_result.get("issues", [])
    assert isinstance(issues, list)

    indexed_issues = [
        (index, issue)
        for index, issue in enumerate(issues)
        if isinstance(issue, dict)
    ]
    sorted_issues = sorted(
        indexed_issues,
        key=lambda item: (
            SEVERITY_ORDER.get(str(item[1].get("severity")), 99),
            item[0],
        ),
    )

    prioritized: list[dict[str, object]] = []
    for _, issue in sorted_issues:
        severity = str(issue.get("severity", "info"))
        issue_id = str(issue["issue_id"])
        title = str(issue.get("title", "Deterministic audit issue"))
        prioritized.append(
            {
                "issue_id": issue_id,
                "priority": PRIORITY_BY_SEVERITY.get(severity, "low"),
                "severity": severity,
                "check_id": str(issue.get("check_id", "")),
                "reason": (
                    f"{title} was reported by the deterministic audit "
                    f"with {severity} severity."
                ),
            }
        )

    next_state["prioritized_issues"] = prioritized
    return next_state
