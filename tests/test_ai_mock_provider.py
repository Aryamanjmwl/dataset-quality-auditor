import copy

from tests.fixtures import sample_audit_result

from dataset_quality_auditor.ai.providers.mock import MockAIReviewProvider


def _audit_with_multiple_severities() -> dict[str, object]:
    audit = sample_audit_result()
    warning_issue = audit["issues"][0]
    critical_issue = copy.deepcopy(warning_issue)
    critical_issue["issue_id"] = "critical_issue_001"
    critical_issue["severity"] = "critical"
    critical_issue["requires_human_review"] = True
    info_issue = copy.deepcopy(warning_issue)
    info_issue["issue_id"] = "info_issue_001"
    info_issue["severity"] = "info"
    audit["issues"] = [warning_issue, info_issue, critical_issue]
    return audit


def test_mock_provider_returns_deterministic_output() -> None:
    audit = _audit_with_multiple_severities()
    provider = MockAIReviewProvider()

    assert provider.generate_review(audit) == provider.generate_review(audit)


def test_mock_provider_prioritizes_existing_issue_ids_by_severity() -> None:
    audit = _audit_with_multiple_severities()
    review = MockAIReviewProvider().generate_review(audit)
    audit_ids = {issue["issue_id"] for issue in audit["issues"]}
    review_ids = [issue["issue_id"] for issue in review["prioritized_issues"]]

    assert set(review_ids) == audit_ids
    assert review_ids[0] == "critical_issue_001"


def test_mock_provider_questions_only_for_human_review_issues() -> None:
    audit = _audit_with_multiple_severities()
    review = MockAIReviewProvider().generate_review(audit)

    assert len(review["human_review_questions"]) == 1
    assert review["human_review_questions"][0]["issue_id"] == "critical_issue_001"
