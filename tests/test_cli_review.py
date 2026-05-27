from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_review_generates_ai_review_json(tmp_path) -> None:
    audit_dir = tmp_path / "audit"
    result = runner.invoke(
        app,
        [
            "audit",
            "examples/datasets/classification_dirty.csv",
            "--target",
            "label",
            "--output-dir",
            str(audit_dir),
        ],
    )
    assert result.exit_code == 0

    review_dir = tmp_path / "review"
    result = runner.invoke(
        app,
        [
            "review",
            str(audit_dir / "audit.json"),
            "--provider",
            "mock",
            "--output-dir",
            str(review_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Provider:" in result.stdout
    assert "mock" in result.stdout
    assert (review_dir / "ai_review.json").exists()
