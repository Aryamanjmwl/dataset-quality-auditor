import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()
DATASET = "examples/datasets/classification_dirty.csv"


def run_cli(args: list[str]) -> None:
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output


def test_audit_json_artifact_has_stable_public_structure(tmp_path: Path) -> None:
    run_cli(
        [
            "audit",
            DATASET,
            "--target",
            "label",
            "--output-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
    )

    audit = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))

    assert {
        "audit_id",
        "created_at",
        "dataset_path",
        "target_column",
        "profile",
        "issues",
        "score",
        "metadata",
    }.issubset(audit)
    assert audit["dataset_path"] == DATASET
    assert audit["target_column"] == "label"
    assert audit["profile"]["row_count"] > 0
    assert audit["profile"]["column_count"] > 0
    assert {"score", "max_score", "score_band", "deductions"}.issubset(
        audit["score"]
    )
    assert audit["metadata"]["deterministic"] is True
    assert audit["metadata"]["ai_generated"] is False
    assert audit["issues"]
    assert all("issue_id" in issue for issue in audit["issues"])


def test_report_artifacts_have_expected_headings_and_sections(tmp_path: Path) -> None:
    run_cli(
        [
            "audit",
            DATASET,
            "--target",
            "label",
            "--output-dir",
            str(tmp_path),
            "--format",
            "all",
        ],
    )

    markdown = (tmp_path / "audit_report.md").read_text(encoding="utf-8")
    html = (tmp_path / "audit_report.html").read_text(encoding="utf-8")

    assert "# Dataset Quality Audit Report" in markdown
    assert "## Executive Summary" in markdown
    assert "## Readiness Score" in markdown
    assert "This report is generated from deterministic audit results." in markdown
    assert "<html" in html
    assert "Dataset Quality Audit Report" in html
    assert "Readiness Score" in html
    assert "Issues" in html


def test_contract_and_validation_artifacts_have_stable_structure(
    tmp_path: Path,
) -> None:
    contract_dir = tmp_path / "contracts"
    report_dir = tmp_path / "reports"
    run_cli(
        [
            "contract",
            DATASET,
            "--target",
            "label",
            "--output-dir",
            str(contract_dir),
        ],
    )
    contract_path = contract_dir / "classification_dirty_contract.yaml"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    assert contract["contract_version"] == "0.1.0"
    assert contract["created_by"] == "dataset-quality-auditor"
    assert contract["dataset"]["source"] == DATASET
    assert contract["dataset"]["target_column"] == "label"
    assert "columns" in contract
    assert "label" in contract["columns"]
    assert contract["metadata"]["deterministic"] is True
    assert contract["metadata"]["ai_generated"] is False

    run_cli(
        [
            "validate",
            DATASET,
            "--contract",
            str(contract_path),
            "--output-dir",
            str(report_dir),
        ],
    )
    validation = json.loads(
        (report_dir / "validation_result.json").read_text(encoding="utf-8")
    )

    assert {"passed", "contract_path", "dataset_path", "summary", "checks"}.issubset(
        validation
    )
    assert validation["dataset_path"] == DATASET
    assert validation["summary"]["total_checks"] == len(validation["checks"])
    assert validation["checks"]
    assert all(
        {"rule_id", "status", "severity"}.issubset(check)
        for check in validation["checks"]
    )


def test_mock_review_artifacts_reference_audit_issue_ids(tmp_path: Path) -> None:
    run_cli(
        [
            "audit",
            DATASET,
            "--target",
            "label",
            "--output-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
    )
    run_cli(
        [
            "review",
            str(tmp_path / "audit.json"),
            "--provider",
            "mock",
            "--workflow",
            "graph",
            "--output-dir",
            str(tmp_path),
        ],
    )

    audit = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))
    review = json.loads((tmp_path / "ai_review.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "ai_review.md").read_text(encoding="utf-8")
    audit_issue_ids = {issue["issue_id"] for issue in audit["issues"]}

    assert review["provider"] == "mock"
    assert review["readiness_score"] == audit["score"]["score"]
    assert review["score_band"] == audit["score"]["score_band"]
    assert review["metadata"]["deterministic_source"] is True
    assert review["metadata"]["ai_generated"] is True
    assert review["prioritized_issues"]
    assert {
        item["issue_id"] for item in review["prioritized_issues"]
    }.issubset(audit_issue_ids)
    assert (
        "This AI-assisted review is generated from deterministic audit findings."
        in markdown
    )
    assert review["prioritized_issues"][0]["issue_id"] in markdown
