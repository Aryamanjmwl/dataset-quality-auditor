import json

import pytest
from tests.fixtures import sample_audit_result

from dataset_quality_auditor.ai.review_engine import generate_ai_review


def test_generate_ai_review_writes_json(tmp_path) -> None:
    audit_json = tmp_path / "audit.json"
    audit_json.write_text(json.dumps(sample_audit_result()), encoding="utf-8")

    review = generate_ai_review(audit_json, provider_name="mock", output_dir=tmp_path)

    assert (tmp_path / "ai_review.json").exists()
    assert review["provider"] == "mock"
    assert review["metadata"]["source_audit_json"] == audit_json.as_posix()


def test_generate_ai_review_rejects_unsupported_provider(tmp_path) -> None:
    audit_json = tmp_path / "audit.json"
    audit_json.write_text(json.dumps(sample_audit_result()), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported AI review provider"):
        generate_ai_review(audit_json, provider_name="openai", output_dir=tmp_path)
