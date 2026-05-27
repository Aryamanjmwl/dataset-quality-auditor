from tests.fixtures import sample_audit_result

from dataset_quality_auditor.reports.markdown_report import generate_markdown_report


def test_markdown_report_contains_required_sections() -> None:
    audit_result = (
        sample_audit_result()
        if callable(sample_audit_result)
        else sample_audit_result
    )

    markdown = generate_markdown_report(audit_result)

    assert "# Dataset Quality Audit Report" in markdown
    assert "Executive Summary" in markdown
    assert "Readiness Score" in markdown
    assert "deterministic audit results" in markdown
    assert "missing_values_age_001" in markdown