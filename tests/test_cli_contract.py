from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_contract_creates_yaml_file(tmp_path) -> None:
    result = runner.invoke(
        app,
        [
            "contract",
            "examples/datasets/classification_dirty.csv",
            "--target",
            "label",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Contract written to:" in result.stdout
    assert (tmp_path / "classification_dirty_contract.yaml").exists()
