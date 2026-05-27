import copy

import pytest
from tests.fixtures import sample_audit_result

from dataset_quality_auditor.ai.guardrails import (
    assert_ai_review_valid,
    validate_ai_review,
)
from dataset_quality_auditor.ai.providers.mock import MockAIReviewProvider


def test_valid_mock_review_passes_guardrails() -> None:
    audit_result = sample_audit_result()
    review = MockAIReviewProvider().generate_review(audit_result)

    assert validate_ai_review(review, audit_result) == []
    assert_ai_review_valid(review, audit_result)


def test_unknown_issue_id_fails_guardrails() -> None:
    audit_result = sample_audit_result()
    review = MockAIReviewProvider().generate_review(audit_result)
    review["prioritized_issues"][0]["issue_id"] = "unknown"

    with pytest.raises(ValueError, match="Unknown issue_id"):
        assert_ai_review_valid(review, audit_result)


def test_changed_readiness_score_fails_guardrails() -> None:
    audit_result = sample_audit_result()
    review = MockAIReviewProvider().generate_review(audit_result)
    changed = copy.deepcopy(review)
    changed["readiness_score"] = 1

    with pytest.raises(ValueError, match="readiness_score"):
        assert_ai_review_valid(changed, audit_result)


def test_changed_score_band_fails_guardrails() -> None:
    audit_result = sample_audit_result()
    review = MockAIReviewProvider().generate_review(audit_result)
    review["score_band"] = "high_risk"

    with pytest.raises(ValueError, match="score_band"):
        assert_ai_review_valid(review, audit_result)
