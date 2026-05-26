from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_report_generates_requested_formats(tmp_path) -> None:
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
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    audit_json = audit_dir / "audit.json"
    assert audit_json.exists()

    markdown_dir = tmp_path / "markdown"
    result = runner.invoke(
        app,
        [
            "report",
            str(audit_json),
            "--format",
            "markdown",
            "--output-dir",
            str(markdown_dir),
        ],
    )
    assert result.exit_code == 0
    assert (markdown_dir / "audit_report.md").exists()

    html_dir = tmp_path / "html"
    result = runner.invoke(
        app,
        ["report", str(audit_json), "--format", "html", "--output-dir", str(html_dir)],
    )
    assert result.exit_code == 0
    assert (html_dir / "audit_report.html").exists()

    all_dir = tmp_path / "all"
    result = runner.invoke(
        app,
        ["report", str(audit_json), "--format", "all", "--output-dir", str(all_dir)],
    )
    assert result.exit_code == 0
    assert (all_dir / "audit_report.json").exists()
    assert (all_dir / "audit_report.md").exists()
    assert (all_dir / "audit_report.html").exists()
