from pathlib import Path

from dataset_quality_auditor.audit.engine import run_audit


def test_public_sample_audit_smoke(tmp_path) -> None:
    result = run_audit(
        "examples/sample.csv",
        target_column="target",
        output_dir=str(tmp_path),
    )

    assert Path(tmp_path / "audit.json").exists()
    assert result["mode"] == "single_dataset"
    assert result["dataset_path"] == "examples/sample.csv"
    assert result["target_column"] == "target"
    assert result["metadata"]["deterministic"] is True
    assert result["metadata"]["ai_generated"] is False
    assert result["profile"]["row_count"] == 4
    assert result["score"]["max_score"] == 100
    assert result["issues"]
