from typer.testing import CliRunner

from dataset_quality_auditor import __version__
from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Deterministically audit local CSV datasets" in result.stdout
    assert "audit" in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_command_help_describes_current_boundaries() -> None:
    audit_help = runner.invoke(app, ["audit", "--help"])
    contract_help = runner.invoke(app, ["contract", "--help"])
    review_help = runner.invoke(app, ["review", "--help"])

    assert audit_help.exit_code == 0
    assert "local CSV" in audit_help.stdout
    assert "train/test" in audit_help.stdout
    assert contract_help.exit_code == 0
    assert "review before relying on it" in contract_help.stdout
    assert review_help.exit_code == 0
    assert "deterministic mock" in review_help.stdout
