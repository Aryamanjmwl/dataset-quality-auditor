import json

from dataset_quality_auditor.audit.engine import run_audit


def test_run_audit_writes_json_and_returns_core_sections(tmp_path) -> None:
    dataset = tmp_path / "data.csv"
    dataset.write_text(
        "customer_id,age,income_text,constant_feature,label\n"
        "a,1,100,on,1\n"
        "b,,200,on,1\n"
        "b,,200,on,1\n"
        "c,3,300,on,0\n",
        encoding="utf-8",
    )

    result = run_audit(str(dataset), target_column="label", output_dir=str(tmp_path))
    audit_json = tmp_path / "audit.json"
    written = json.loads(audit_json.read_text(encoding="utf-8"))

    assert audit_json.exists()
    assert written["audit_id"] == result["audit_id"]
    assert "profile" in result
    assert "issues" in result
    assert "score" in result
    assert "metadata" in result
    assert result["metadata"]["deterministic"] is True
    assert result["metadata"]["ai_generated"] is False
