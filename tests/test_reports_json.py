from tests.fixtures import sample_audit_result

from dataset_quality_auditor.reports.json_report import (
    load_audit_json,
    save_json_report,
)


def test_json_report_save_and_load_round_trip(tmp_path) -> None:
    audit_result = sample_audit_result()
    output_path = tmp_path / "nested" / "audit_report.json"

    saved_path = save_json_report(audit_result, output_path)
    loaded = load_audit_json(saved_path)

    assert saved_path.exists()
    assert loaded == audit_result
