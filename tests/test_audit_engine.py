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


def test_run_audit_train_test_json_includes_drift_findings(tmp_path) -> None:
    train = tmp_path / "train.csv"
    test = tmp_path / "test.csv"
    train.write_text(
        "feature,segment,label\n"
        "1,a,0\n"
        "2,a,0\n"
        "3,a,0\n"
        "4,b,0\n"
        "5,b,1\n",
        encoding="utf-8",
    )
    test.write_text(
        "feature,segment,label\n"
        "20,a,0\n"
        "21,c,1\n"
        "22,c,1\n"
        "23,c,1\n"
        "24,c,1\n",
        encoding="utf-8",
    )

    run_audit(
        str(train),
        target_column="label",
        test_dataset_path=str(test),
        output_dir=str(tmp_path),
    )
    audit_json = tmp_path / "audit.json"
    written = json.loads(audit_json.read_text(encoding="utf-8"))
    check_ids = {issue["check_id"] for issue in written["issues"]}

    assert written["mode"] == "train_test"
    assert written["test_dataset_path"] == test.as_posix()
    assert "numeric_drift" in check_ids
    assert "categorical_drift" in check_ids
    assert "target_distribution_drift" in check_ids
