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


def evaluate_audit_gate(
    audit_result: dict[str, Any],
    *,
    min_score: float = 0,
    max_critical: int | None = None,
    max_high: int | None = None,
    max_medium: int | None = None,
    max_human_review: int | None = None,
) -> dict[str, Any]:
    """Evaluate deterministic CI/CD gate rules against existing audit JSON."""
    summary = summarize_audit_result(audit_result)
    score = summary.get("score")
    if not isinstance(score, int | float):
        msg = "Audit summary is missing a numeric readiness score."
        raise ValueError(msg)

    gate: dict[str, int | float] = {"min_score": min_score}
    reasons: list[str] = []

    if score < min_score:
        reasons.append(
            f"score {_format_number(score)} is below minimum "
            f"{_format_number(min_score)}"
        )

    severity_counts = summary["severity_counts"]
    risk_level_counts = summary["risk_level_counts"]
    if not isinstance(severity_counts, dict) or not isinstance(risk_level_counts, dict):
        msg = "Audit summary contains invalid count objects."
        raise ValueError(msg)

    _evaluate_count_limit(
        reasons,
        gate,
        key="max_critical",
        label="critical issue count",
        observed=int(severity_counts.get("critical", 0)),
        limit=max_critical,
    )
    _evaluate_count_limit(
        reasons,
        gate,
        key="max_high",
        label="high risk issue count",
        observed=int(risk_level_counts.get("high", 0)),
        limit=max_high,
    )
    _evaluate_count_limit(
        reasons,
        gate,
        key="max_medium",
        label="medium risk issue count",
        observed=int(risk_level_counts.get("medium", 0)),
        limit=max_medium,
    )
    _evaluate_count_limit(
        reasons,
        gate,
        key="max_human_review",
        label="human review issue count",
        observed=int(summary["requires_human_review_count"]),
        limit=max_human_review,
    )

    return {
        "passed": not reasons,
        "reasons": reasons,
        "summary": summary,
        "gate": gate,
    }


def _sorted_counts(counts: Counter[str]) -> dict[str, int]:
    return {key: counts[key] for key in sorted(counts)}


def _evaluate_count_limit(
    reasons: list[str],
    gate: dict[str, int | float],
    *,
    key: str,
    label: str,
    observed: int,
    limit: int | None,
) -> None:
    if limit is None:
        return
    gate[key] = limit
    if observed > limit:
        reasons.append(f"{label} {observed} exceeds maximum {limit}")


def _format_number(value: int | float) -> str:
    return f"{value:g}"
