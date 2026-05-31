"""Anthropic Claude provider for AI-assisted audit review."""

import json
import os


class AnthropicAIReviewProvider:
    provider_name: str = "anthropic"

    def __init__(self, model_name: str = "claude-sonnet-4-20250514") -> None:
        self.model_name = model_name

    def generate_review(self, audit_result: dict) -> dict[str, object]:
        try:
            import anthropic
        except ImportError as exc:
            msg = (
                "anthropic package is not installed. "
                "Install with: pip install anthropic"
            )
            raise ImportError(msg) from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            msg = "ANTHROPIC_API_KEY environment variable is not set."
            raise ValueError(msg)

        prompt = _build_review_prompt(audit_result)
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=self.model_name,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
        parsed = json.loads(text)
        assert isinstance(parsed, dict)
        return parsed


def _build_review_prompt(audit_result: dict) -> str:
    score = audit_result["score"]
    issues = audit_result.get("issues", [])
    issue_lines = [
        (
            f"- issue_id={issue.get('issue_id')}; "
            f"severity={issue.get('severity')}; "
            f"title={issue.get('title')}; "
            f"recommendation={issue.get('recommendation')}"
        )
        for issue in issues
    ]
    return "\n".join(
        [
            "You are reviewing deterministic dataset audit output.",
            "The deterministic audit JSON is the source of truth.",
            "Respond only with a JSON object matching the AI review schema.",
            "Do not invent issue IDs or findings.",
            "Preserve the exact readiness_score and score_band from the audit.",
            "Set metadata.ai_generated=true.",
            "Set metadata.deterministic_source=true.",
            f"Dataset path: {audit_result.get('dataset_path')}",
            f"Audit mode: {audit_result.get('mode', 'single_dataset')}",
            f"Readiness score: {score.get('score')}/{score.get('max_score')}",
            f"Score band: {score.get('score_band')}",
            "Issues:",
            *issue_lines,
        ]
    )
