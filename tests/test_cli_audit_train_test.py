from typer.testing import CliRunner

from dataset_quality_auditor.cli import app

runner = CliRunner()


def test_cli_audit_train_test_mode_writes_audit_json(tmp_path) -> None:
    train = tmp_path / "train.csv"
    test = tmp_path / "test.csv"
    train.write_text("age,city,label\n1,a,0\n2,b,1\n", encoding="utf-8")
    test.write_text("age,city,label\n2,b,1\n10,c,0\n", encoding="utf-8")
    output_dir = tmp_path / "reports"

    result = runner.invoke(
        app,
        [
            "audit",
            str(train),
            "--test",
            str(test),
            "--target",
            "label",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "train_test" in result.stdout
    assert "Test dataset:" in result.stdout
    assert (output_dir / "audit.json").exists()
