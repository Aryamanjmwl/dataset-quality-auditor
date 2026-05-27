"""Provider-agnostic AI review engine."""

import json
from pathlib import Path

from dataset_quality_auditor.ai.guardrails import assert_ai_review_valid
from dataset_quality_auditor.ai.providers.base import AIReviewProvider
from dataset_quality_auditor.ai.providers.mock import MockAIReviewProvider
from dataset_quality_auditor.reports.json_report import load_audit_json


def _resolve_provider(provider_name: str) -> AIReviewProvider:
    normalized = provider_name.lower()
    if normalized == "mock":
        return MockAIReviewProvider()
    msg = f"Unsupported AI review provider '{provider_name}'. Supported: mock."
    raise ValueError(msg)


def generate_ai_review(
    audit_json_path: str | Path,
    provider_name: str = "mock",
    output_dir: str | Path = "reports",
) -> dict[str, object]:
    """Generate, validate, and save an AI review from deterministic audit JSON."""
    audit_path = Path(audit_json_path)
    audit_result = load_audit_json(audit_path)
    provider = _resolve_provider(provider_name)
    review = provider.generate_review(audit_result)
    review["metadata"]["source_audit_json"] = audit_path.as_posix()
    assert_ai_review_valid(review, audit_result)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "ai_review.json").write_text(
        json.dumps(review, indent=2),
        encoding="utf-8",
    )
    return review
