"""Deterministic readiness scoring."""

from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import CRITICAL, INFO, WARNING

BASE_DEDUCTIONS = {CRITICAL: 20, WARNING: 8, INFO: 2}
HUMAN_REVIEW_DEDUCTION = 2


def _score_band(score: int) -> str:
    if score >= 85:
        return "ready"
    if score >= 60:
        return "needs_attention"
    return "high_risk"


def calculate_readiness_score(issues: list[Issue]) -> dict[str, object]:
    deductions: list[dict[str, object]] = []
    total = 0
    for issue in issues:
        deduction = BASE_DEDUCTIONS.get(issue.severity, 0)
        reason = f"{issue.severity} issue"
        if issue.requires_human_review:
            deduction += HUMAN_REVIEW_DEDUCTION
            reason = f"{reason}; requires human review"
        total += deduction
        deductions.append(
            {
                "issue_id": issue.issue_id,
                "severity": issue.severity,
                "deduction": deduction,
                "reason": reason,
            }
        )
    score = max(0, min(100, 100 - total))
    return {
        "score": score,
        "max_score": 100,
        "score_band": _score_band(score),
        "deductions": deductions,
    }
