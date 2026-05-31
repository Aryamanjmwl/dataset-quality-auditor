"""Deterministic readiness scoring."""

import warnings

from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, INFO, WARNING

# risk_level values (HIGH/MEDIUM/LOW) are metadata only and do not appear in
# BASE_DEDUCTIONS. Only severity drives deductions.
BASE_DEDUCTIONS = {
    CRITICAL: 20,
    WARNING: 8,
    INFO: 2,
}
HUMAN_REVIEW_DEDUCTION = 2
SEVERITY_CAPS = {
    CRITICAL: 40,
    WARNING: 32,
    INFO: 10,
}


def _score_band(score: int) -> str:
    if score >= 85:
        return "ready"
    if score >= 60:
        return "needs_attention"
    return "high_risk"


def calculate_readiness_score(issues: list[Issue]) -> dict[str, object]:
    """Calculate a deterministic readiness score from issue severities."""
    deductions: list[dict[str, object]] = []
    severity_totals = {
        severity: {"raw": 0, "capped": 0, "issues": 0}
        for severity in (CRITICAL, WARNING, INFO)
    }
    human_review_total = 0

    for issue in issues:
        base_deduction = BASE_DEDUCTIONS.get(issue.severity)
        if base_deduction is None:
            warnings.warn(
                (
                    f"Unknown severity '{issue.severity}' for issue "
                    f"'{issue.issue_id}'; no deduction applied."
                ),
                UserWarning,
                stacklevel=2,
            )
            base_deduction = 0

        severity_deduction = base_deduction
        reason = f"{issue.severity} issue"
        if issue.severity in severity_totals:
            totals = severity_totals[issue.severity]
            totals["issues"] += 1
            totals["raw"] += base_deduction
            remaining_cap = SEVERITY_CAPS[issue.severity] - totals["capped"]
            severity_deduction = max(0, min(base_deduction, remaining_cap))
            totals["capped"] += severity_deduction
            if severity_deduction < base_deduction:
                reason = f"{issue.severity} issue; cap applied"

        review_deduction = 0
        if issue.requires_human_review:
            review_deduction = HUMAN_REVIEW_DEDUCTION
            human_review_total += review_deduction
            reason = f"{reason}; requires human review"

        deductions.append(
            {
                "issue_id": issue.issue_id,
                "severity": issue.severity,
                "deduction": severity_deduction + review_deduction,
                "reason": reason,
            }
        )

    total_deduction = (
        sum(totals["capped"] for totals in severity_totals.values())
        + human_review_total
    )
    score = max(0, min(100, 100 - total_deduction))
    return {
        "score": score,
        "max_score": 100,
        "score_band": _score_band(score),
        "deductions": deductions,
        "severity_totals": severity_totals,
    }
