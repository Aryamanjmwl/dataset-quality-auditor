from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_audit_prints_score_and_writes_audit_json(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "examples/datasets/classification_dirty.csv",
            "--target",
            "label",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Readiness Score:" in result.stdout
    assert "Audit JSON written to:" in result.stdout
    assert (tmp_path / "audit.json").exists()
