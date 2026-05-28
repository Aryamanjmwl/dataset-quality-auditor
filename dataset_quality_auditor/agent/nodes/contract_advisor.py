"""Contract advice node for deterministic review workflows."""

from __future__ import annotations

import copy

RULE_TYPES = {
    "missing_values": "max_missing_percent_review",
    "id_like_columns": "uniqueness_or_id_role_review",
    "datatype_risks": "explicit_type_rule",
    "categorical_drift": "allowed_category_monitoring",
    "schema_mismatch": "required_column_review",
    "outlier_risk": "numeric_range_review",
}


def _column_from_issue(issue: dict[str, object]) -> str | None:
    scope = issue.get("scope", {})
    if isinstance(scope, dict) and scope.get("column") is not None:
        return str(scope["column"])
    evidence = issue.get("evidence", {})
    if isinstance(evidence, dict):
        details = evidence.get("details", {})
        if isinstance(details, dict) and details.get("column") is not None:
            return str(details["column"])
    return None


def advise_contract_rules(state: dict[str, object]) -> dict[str, object]:
    """Suggest contract rules from deterministic issues without editing files."""
    next_state = copy.deepcopy(state)
    audit_result = next_state["audit_result"]
    assert isinstance(audit_result, dict)
    issues = audit_result.get("issues", [])
    assert isinstance(issues, list)

    recommendations: list[dict[str, object]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        check_id = str(issue.get("check_id", ""))
        rule_type = RULE_TYPES.get(check_id)
        if rule_type is None:
            continue

        issue_id = str(issue["issue_id"])
        column = _column_from_issue(issue)
        recommendations.append(
            {
                "issue_id": issue_id,
                "rule_type": rule_type,
                "column": column,
                "recommendation": (
                    "Review whether the data contract should encode this "
                    "deterministic finding as an explicit validation rule."
                ),
                "reason": str(
                    issue.get(
                        "recommendation",
                        "The deterministic audit reported this issue.",
                    )
                ),
            }
        )

    next_state["contract_recommendations"] = recommendations
    return next_state
