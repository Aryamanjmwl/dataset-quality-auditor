"""State container for deterministic review workflows."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field


@dataclass
class ReviewState:
    """JSON-serializable state passed between review graph nodes."""

    audit_result: dict[str, object]
    provider_name: str = "mock"
    model_name: str = "deterministic-mock"
    prioritized_issues: list[dict[str, object]] = field(default_factory=list)
    safe_next_steps: list[dict[str, object]] = field(default_factory=list)
    contract_recommendations: list[dict[str, object]] = field(default_factory=list)
    human_review_questions: list[dict[str, object]] = field(default_factory=list)
    markdown_report: str = ""
    ai_review: dict[str, object] = field(default_factory=dict)
    validation_errors: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Return a detached dictionary suitable for node execution."""
        return {
            "audit_result": copy.deepcopy(self.audit_result),
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "prioritized_issues": copy.deepcopy(self.prioritized_issues),
            "safe_next_steps": copy.deepcopy(self.safe_next_steps),
            "contract_recommendations": copy.deepcopy(
                self.contract_recommendations
            ),
            "human_review_questions": copy.deepcopy(
                self.human_review_questions
            ),
            "markdown_report": self.markdown_report,
            "ai_review": copy.deepcopy(self.ai_review),
            "validation_errors": copy.deepcopy(self.validation_errors),
        }


def create_initial_state(
    audit_result: dict[str, object],
    provider_name: str = "mock",
    model_name: str = "deterministic-mock",
) -> dict[str, object]:
    """Create the initial graph state from deterministic audit output."""
    return ReviewState(
        audit_result=copy.deepcopy(audit_result),
        provider_name=provider_name,
        model_name=model_name,
    ).to_dict()
