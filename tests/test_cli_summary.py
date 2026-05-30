import json

from tests.fixtures import sample_graph_audit_result
from typer.testing import CliRunner

from dataset_quality_auditor.cli import app
from dataset_quality_auditor.reports import save_json_report

runner = CliRunner()


def test_cli_summary_json_outputs_machine_readable_summary(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["summary", str(audit_path), "--format", "json"])

    assert result.exit_code == 0
    summary = json.loads(result.output)
    assert summary["score"] == 50
    assert summary["issue_count"] == 4
    assert summary["requires_human_review_count"] == 2
    assert summary["top_issue_ids"][0] == "datatype_risk_income_001"


def test_cli_summary_text_outputs_human_summary(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["summary", str(audit_path), "--format", "text"])

    assert result.exit_code == 0
    assert "Dataset Quality Auditor Summary" in result.output
    assert "Readiness Score:" in result.output
    assert "50/100" in result.output
    assert "target_leakage_score_001" in result.output


def test_cli_summary_rejects_invalid_format(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["summary", str(audit_path), "--format", "yaml"])

    assert result.exit_code != 0
    assert "Unsupported summary format" in result.output


def test_cli_summary_missing_audit_json_fails_clearly(tmp_path) -> None:
    result = runner.invoke(app, ["summary", str(tmp_path / "missing.json")])

    assert result.exit_code != 0
    assert "does not exist" in result.output
