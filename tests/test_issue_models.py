from dataset_quality_auditor.audit.evidence import Evidence
from dataset_quality_auditor.audit.issues import Issue
from dataset_quality_auditor.audit.severity import MEDIUM, WARNING


def test_evidence_to_dict() -> None:
    evidence = Evidence(
        metric="missing_percent",
        observed_value=0.2,
        threshold=0.1,
        comparison="observed_value >= threshold",
        details={"missing_count": 2},
    )

    assert evidence.to_dict()["metric"] == "missing_percent"
    assert evidence.to_dict()["details"]["missing_count"] == 2


def test_issue_to_dict() -> None:
    evidence = Evidence("missing_percent", 0.2, 0.1, ">=", {})
    issue = Issue(
        issue_id="missing_age_001",
        check_id="missing_values",
        title="Missing values detected",
        severity=WARNING,
        risk_level=MEDIUM,
        status="failed",
        scope={"dataset": "train", "column": "age"},
        evidence=evidence,
        ml_impact="Impact",
        recommendation="Recommendation",
        requires_human_review=False,
        reproducibility={"check_version": "0.1.0", "parameters": {}},
    )

    result = issue.to_dict()

    assert result["issue_id"] == "missing_age_001"
    assert result["evidence"]["observed_value"] == 0.2
