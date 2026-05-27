from tests.fixtures import sample_audit_result

from dataset_quality_auditor.reports.html_report import generate_html_report


def test_html_report_contains_core_content() -> None:
    html = generate_html_report(sample_audit_result())

    assert "<html" in html
    assert "Dataset Quality Audit Report" in html
    assert "92/100" in html
    assert "warning" in html
    assert "missing_values_age_001" in html
