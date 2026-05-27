import json

from dataset_quality_auditor.audit.engine import run_audit


def test_run_audit_writes_audit_json(tmp_path) -> None:
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

    assert audit_json.exists()
    written = json.loads(audit_json.read_text(encoding="utf-8"))
    assert written["audit_id"] == result["audit_id"]
    assert written["metadata"]["deterministic"] is True
    assert written["metadata"]["ai_generated"] is False
    assert written["score"]["score"] <= 100
    assert written["issues"]
