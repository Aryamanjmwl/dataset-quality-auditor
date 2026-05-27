from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_validate_creates_validation_json(tmp_path) -> None:
    contract_dir = tmp_path / "contracts"
    result = runner.invoke(
        app,
        [
            "contract",
            "examples/datasets/classification_dirty.csv",
            "--target",
            "label",
            "--output-dir",
            str(contract_dir),
        ],
    )
    assert result.exit_code == 0

    contract_path = contract_dir / "classification_dirty_contract.yaml"
    report_dir = tmp_path / "reports"
    result = runner.invoke(
        app,
        [
            "validate",
            "examples/datasets/classification_dirty.csv",
            "--contract",
            str(contract_path),
            "--output-dir",
            str(report_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Validation JSON written to:" in result.stdout
    assert (report_dir / "validation_result.json").exists()
