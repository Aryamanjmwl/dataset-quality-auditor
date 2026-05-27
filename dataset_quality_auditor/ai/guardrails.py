"""Guardrails for validating AI review output."""


def get_audit_issue_ids(audit_result: dict) -> set[str]:
    """Return issue IDs present in deterministic audit output."""
    return {str(issue["issue_id"]) for issue in audit_result.get("issues", [])}


def _audit_score(audit_result: dict) -> dict[str, object]:
    score = audit_result["score"]
    assert isinstance(score, dict)
    return score


def _validate_issue_references(
    ai_review: dict,
    audit_issue_ids: set[str],
    field: str,
    errors: list[dict[str, object]],
) -> None:
    for index, item in enumerate(ai_review.get(field, [])):
        issue_id = str(item.get("issue_id"))
        if issue_id not in audit_issue_ids:
            errors.append(
                {
                    "field": field,
                    "index": index,
                    "error": f"Unknown issue_id '{issue_id}'.",
                }
            )


def validate_ai_review(ai_review: dict, audit_result: dict) -> list[dict[str, object]]:
    """Return guardrail validation errors for an AI review."""
    errors: list[dict[str, object]] = []
    audit_issue_ids = get_audit_issue_ids(audit_result)
    for field in (
        "prioritized_issues",
        "safe_next_steps",
        "human_review_questions",
    ):
        _validate_issue_references(ai_review, audit_issue_ids, field, errors)

    score = _audit_score(audit_result)
    if ai_review.get("readiness_score") != score.get("score"):
        errors.append(
            {
                "field": "readiness_score",
                "error": "AI review readiness_score must match audit score.",
            }
        )
    if ai_review.get("score_band") != score.get("score_band"):
        errors.append(
            {
                "field": "score_band",
                "error": "AI review score_band must match audit score band.",
            }
        )
    metadata = ai_review.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append({"field": "metadata", "error": "metadata must be an object."})
        return errors
    if metadata.get("ai_generated") is not True:
        errors.append(
            {"field": "metadata.ai_generated", "error": "Must be true."}
        )
    if metadata.get("deterministic_source") is not True:
        errors.append(
            {"field": "metadata.deterministic_source", "error": "Must be true."}
        )
    return errors


def assert_ai_review_valid(ai_review: dict, audit_result: dict) -> None:
    """Raise ValueError if an AI review violates guardrails."""
    errors = validate_ai_review(ai_review, audit_result)
    if errors:
        msg = f"AI review failed guardrail validation: {errors}"
        raise ValueError(msg)
