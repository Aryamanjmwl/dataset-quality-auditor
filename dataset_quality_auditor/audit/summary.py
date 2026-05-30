"""Compact summaries for deterministic audit results."""

from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_audit_result(audit_result: dict[str, Any]) -> dict[str, Any]:
    """Build a compact, JSON-serializable summary from audit JSON fields."""
    score = audit_result.get("score")
    issues = audit_result.get("issues")
    if not isinstance(score, dict):
        msg = "Audit JSON is missing a valid 'score' object."
        raise ValueError(msg)
    if not isinstance(issues, list):
        msg = "Audit JSON is missing a valid 'issues' list."
        raise ValueError(msg)

    severity_counts: Counter[str] = Counter()
    risk_level_counts: Counter[str] = Counter()
    check_counts: Counter[str] = Counter()
    failed_count = 0
    requires_human_review_count = 0
    top_issue_ids: list[str] = []

    for issue in issues:
        if not isinstance(issue, dict):
            msg = "Audit JSON contains a non-object issue entry."
            raise ValueError(msg)

        issue_id = str(issue.get("issue_id", ""))
        if issue_id and len(top_issue_ids) < 10:
            top_issue_ids.append(issue_id)

        severity = issue.get("severity")
        if severity is not None:
            severity_counts[str(severity)] += 1

        risk_level = issue.get("risk_level")
        if risk_level is not None:
            risk_level_counts[str(risk_level)] += 1

        check_id = issue.get("check_id")
        if check_id is not None:
            check_counts[str(check_id)] += 1

        if issue.get("status") == "failed":
            failed_count += 1
        if bool(issue.get("requires_human_review", False)):
            requires_human_review_count += 1

    summary: dict[str, Any] = {
        "dataset_path": audit_result.get("dataset_path"),
        "mode": audit_result.get("mode", "single_dataset"),
        "score": score.get("score"),
        "max_score": score.get("max_score"),
        "score_band": score.get("score_band"),
        "issue_count": len(issues),
        "severity_counts": _sorted_counts(severity_counts),
        "risk_level_counts": _sorted_counts(risk_level_counts),
        "failed_count": failed_count,
        "requires_human_review_count": requires_human_review_count,
        "check_counts": _sorted_counts(check_counts),
        "top_issue_ids": top_issue_ids,
    }

    if audit_result.get("test_dataset_path") is not None:
        summary["test_dataset_path"] = audit_result.get("test_dataset_path")
    if audit_result.get("target_column") is not None:
        summary["target_column"] = audit_result.get("target_column")

    return summary


def _sorted_counts(counts: Counter[str]) -> dict[str, int]:
    return {key: counts[key] for key in sorted(counts)}
