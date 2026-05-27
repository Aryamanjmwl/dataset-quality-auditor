"""JSON-serializable schemas for AI review output."""

from dataclasses import asdict, dataclass, field

REVIEW_VERSION = "0.1.0"


@dataclass(frozen=True)
class PrioritizedIssue:
    issue_id: str
    priority: str
    reason: str
    severity: str
    check_id: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SafeNextStep:
    issue_id: str
    action: str
    why: str
    automation_level: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class HumanReviewQuestion:
    issue_id: str
    question: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AIReview:
    provider: str
    model: str
    audit_id: str
    readiness_score: int
    score_band: str
    summary: str
    prioritized_issues: list[PrioritizedIssue] = field(default_factory=list)
    safe_next_steps: list[SafeNextStep] = field(default_factory=list)
    human_review_questions: list[HumanReviewQuestion] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    review_version: str = REVIEW_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "review_version": self.review_version,
            "provider": self.provider,
            "model": self.model,
            "audit_id": self.audit_id,
            "readiness_score": self.readiness_score,
            "score_band": self.score_band,
            "summary": self.summary,
            "prioritized_issues": [
                issue.to_dict() for issue in self.prioritized_issues
            ],
            "safe_next_steps": [step.to_dict() for step in self.safe_next_steps],
            "human_review_questions": [
                question.to_dict() for question in self.human_review_questions
            ],
            "metadata": self.metadata,
        }
