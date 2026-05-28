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


def _validate_workflow(workflow: str) -> str:
    normalized = workflow.lower()
    if normalized not in {"provider", "graph"}:
        msg = (
            f"Unsupported AI review workflow '{workflow}'. "
            "Supported: provider, graph."
        )
        raise ValueError(msg)
    return normalized


def generate_ai_review(
    audit_json_path: str | Path,
    provider_name: str = "mock",
    output_dir: str | Path = "reports",
    workflow: str = "provider",
) -> dict[str, object]:
    """Generate, validate, and save an AI review from deterministic audit JSON."""
    audit_path = Path(audit_json_path)
    audit_result = load_audit_json(audit_path)
    normalized_workflow = _validate_workflow(workflow)
    provider = _resolve_provider(provider_name)
    if normalized_workflow == "graph":
        from dataset_quality_auditor.agent.graph import run_review_graph

        review = run_review_graph(
            audit_result=audit_result,
            provider_name=provider.provider_name,
            model_name=provider.model_name,
        )
    else:
        review = provider.generate_review(audit_result)

    review["metadata"]["source_audit_json"] = audit_path.as_posix()
    assert_ai_review_valid(review, audit_result)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "ai_review.json").write_text(
        json.dumps(review, indent=2),
        encoding="utf-8",
    )
    markdown_report = review.get("markdown_report")
    if normalized_workflow == "graph" and isinstance(markdown_report, str):
        (output_path / "ai_review.md").write_text(
            markdown_report,
            encoding="utf-8",
        )
    return review
