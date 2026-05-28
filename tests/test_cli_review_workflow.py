from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_review_graph_workflow_writes_json_and_markdown(tmp_path) -> None:
    audit_dir = tmp_path / "reports"
    audit_result = runner.invoke(
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
    assert audit_result.exit_code == 0

    review_result = runner.invoke(
        app,
        [
            "review",
            str(audit_dir / "audit.json"),
            "--provider",
            "mock",
            "--workflow",
            "graph",
            "--output-dir",
            str(audit_dir),
        ],
    )

    assert review_result.exit_code == 0
    assert "graph" in review_result.output
    assert "mock" in review_result.output
    assert (audit_dir / "ai_review.json").exists()
    assert (audit_dir / "ai_review.md").exists()
