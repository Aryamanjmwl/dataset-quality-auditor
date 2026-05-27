"""Provider interface for AI review generation."""

from typing import Protocol


class AIReviewProvider(Protocol):
    provider_name: str
    model_name: str

    def generate_review(self, audit_result: dict) -> dict[str, object]:
        """Generate a review from deterministic audit output."""
        ...
