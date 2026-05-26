from typer.testing import CliRunner

from dataset_quality_auditor import __version__
from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Audit tabular ML datasets before training" in result.stdout
    assert "audit" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_audit_existing_dataset() -> None:
    result = runner.invoke(
        app,
        ["audit", "examples/datasets/classification_dirty.csv", "--target", "label"],
    )

    assert result.exit_code == 0
    assert "Dataset accepted for audit planning" in result.stdout
    assert "examples/datasets/classification_dirty.csv" in result.stdout
    assert "label" in result.stdout
