from tests.fixtures import sample_graph_audit_result

from dataset_quality_auditor.audit.summary import summarize_audit_result


def test_summarize_audit_result_returns_compact_counts() -> None:
    summary = summarize_audit_result(sample_graph_audit_result())

    assert summary["dataset_path"] == "examples/datasets/classification_dirty.csv"
    assert summary["mode"] == "single_dataset"
    assert summary["score"] == 50
    assert summary["max_score"] == 100
    assert summary["score_band"] == "high_risk"
    assert summary["issue_count"] == 4
    assert summary["severity_counts"] == {
        "critical": 1,
        "info": 1,
        "warning": 2,
    }
    assert summary["risk_level_counts"] == {
        "high": 1,
        "low": 1,
        "medium": 2,
    }
    assert summary["failed_count"] == 4
    assert summary["requires_human_review_count"] == 2
    assert summary["check_counts"]["missing_values"] == 1
    assert summary["top_issue_ids"] == [
        "datatype_risk_income_001",
        "target_leakage_score_001",
        "missing_values_age_001",
        "id_like_customer_001",
    ]
