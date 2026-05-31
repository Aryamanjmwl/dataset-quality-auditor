import json

from tests.fixtures import sample_graph_audit_result
from typer.testing import CliRunner

from dataset_quality_auditor.cli import app
from dataset_quality_auditor.reports import save_json_report

runner = CliRunner()


def test_cli_gate_passes_when_limits_are_satisfied(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(
        app,
        [
            "gate",
            str(audit_path),
            "--min-score",
            "40",
            "--max-critical",
            "1",
            "--max-high",
            "1",
            "--max-medium",
            "2",
            "--max-human-review",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert "Dataset Quality Auditor Gate" in result.output
    assert "PASS" in result.output
    assert "50/100" in result.output


def test_cli_gate_fails_when_score_is_below_minimum(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["gate", str(audit_path), "--min-score", "80"])

    assert result.exit_code == 1
    assert "Dataset Quality Auditor Gate" in result.output
    assert "FAIL" in result.output
    assert "score 50 is below minimum 80" in result.output


def test_cli_gate_fails_when_critical_count_exceeds_limit(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["gate", str(audit_path), "--max-critical", "0"])

    assert result.exit_code == 1
    assert "Dataset Quality Auditor Gate" in result.output
    assert "FAIL" in result.output
    assert "critical issue count 1 exceeds maximum 0" in result.output


def test_cli_gate_json_outputs_machine_readable_result(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(
        app,
        [
            "gate",
            str(audit_path),
            "--min-score",
            "80",
            "--max-critical",
            "0",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["passed"] is False
    assert payload["reasons"] == [
        "score 50 is below minimum 80",
        "critical issue count 1 exceeds maximum 0",
    ]
    assert payload["summary"]["score"] == 50
    assert payload["summary"]["issue_count"] == 4
    assert payload["gate"] == {
        "max_critical": 0,
        "min_score": 80.0,
    }


def test_cli_gate_rejects_invalid_format(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["gate", str(audit_path), "--format", "yaml"])

    assert result.exit_code != 0
    assert "Unsupported summary format" in result.output


def test_cli_gate_missing_audit_json_fails_clearly(tmp_path) -> None:
    result = runner.invoke(app, ["gate", str(tmp_path / "missing.json")])

    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_cli_gate_rejects_invalid_min_score(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["gate", str(audit_path), "--min-score", "101"])

    assert result.exit_code != 0
    assert result.exception is not None
    assert (
        "Usage:" in result.output
        or "Error" in result.output
        or "Invalid value" in result.output
    )


def test_cli_gate_rejects_negative_issue_limit(tmp_path) -> None:
    audit_path = save_json_report(sample_graph_audit_result(), tmp_path / "audit.json")

    result = runner.invoke(app, ["gate", str(audit_path), "--max-critical", "-1"])

    assert result.exit_code != 0
    assert result.exception is not None
    assert (
        "Usage:" in result.output
        or "Error" in result.output
        or "Invalid value" in result.output
    )