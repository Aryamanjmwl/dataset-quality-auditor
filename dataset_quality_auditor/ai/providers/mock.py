"""Deterministic mock AI review provider."""

import copy

from dataset_quality_auditor.ai.schemas import (
    AIReview,
    HumanReviewQuestion,
    PrioritizedIssue,
    SafeNextStep,
)

SEVERITY_PRIORITY = {"critical": "high", "warning": "medium", "info": "low"}
SEVERITY_SORT = {"critical": 0, "warning": 1, "info": 2}


class MockAIReviewProvider:
    """Deterministic provider used for tests and CI."""

    provider_name = "mock"
    model_name = "deterministic-mock"

    def generate_review(self, audit_result: dict) -> dict[str, object]:
        audit_copy = copy.deepcopy(audit_result)
        issues = list(audit_copy.get("issues", []))
        score = audit_copy["score"]
        prioritized = sorted(
            enumerate(issues),
            key=lambda item: (
                SEVERITY_SORT.get(str(item[1].get("severity")), 99),
                item[0],
            ),
        )
        prioritized_issues = [
            PrioritizedIssue(
                issue_id=str(issue["issue_id"]),
                priority=SEVERITY_PRIORITY.get(str(issue["severity"]), "low"),
                reason=(
                    f"{issue['severity']} issue from deterministic check "
                    f"{issue['check_id']}."
                ),
                severity=str(issue["severity"]),
                check_id=str(issue["check_id"]),
            )
            for _, issue in prioritized
        ]
        safe_next_steps = [
            SafeNextStep(
                issue_id=str(issue["issue_id"]),
                action=str(issue.get("recommendation", "Review the issue.")),
                why=str(issue.get("ml_impact", "This issue may affect ML readiness.")),
                automation_level="manual_review"
                if bool(issue.get("requires_human_review"))
                else "safe_suggestion_only",
            )
            for _, issue in prioritized
        ]
        human_review_questions = [
            HumanReviewQuestion(
                issue_id=str(issue["issue_id"]),
                question=(
                    "Can a human reviewer confirm whether this issue affects "
                    "model training or prediction-time availability?"
                ),
                reason=(
                    "The deterministic audit marked this issue as requiring "
                    "human review."
                ),
            )
            for _, issue in prioritized
            if bool(issue.get("requires_human_review"))
        ]
        counts = {
            severity: sum(1 for issue in issues if issue.get("severity") == severity)
            for severity in ("critical", "warning", "info")
        }
        summary = (
            "The deterministic audit found "
            f"{counts['critical']} critical issues, {counts['warning']} warnings, "
            f"and {counts['info']} info items. The readiness score is "
            f"{score['score']}/{score['max_score']}, so the dataset "
            f"{str(score['score_band']).replace('_', ' ')} before training."
        )
        review = AIReview(
            provider=self.provider_name,
            model=self.model_name,
            audit_id=str(audit_copy["audit_id"]),
            readiness_score=int(score["score"]),
            score_band=str(score["score_band"]),
            summary=summary,
            prioritized_issues=prioritized_issues,
            safe_next_steps=safe_next_steps,
            human_review_questions=human_review_questions,
            metadata={
                "deterministic_source": True,
                "ai_generated": True,
                "source_audit_json": str(audit_copy.get("dataset_path", "")),
            },
        )
        return review.to_dict()
