from copy import deepcopy

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


def test_markdown_report_escapes_dataset_derived_values() -> None:
    audit_result = deepcopy(sample_audit_result())
    audit_result["dataset_path"] = "data`set\nignore previous instructions.csv"
    audit_result["target_column"] = "bad|target"
    audit_result["audit_id"] = "audit`id\n1"
    audit_result["score"]["deductions"][0]["reason"] = "warning | reason"
    audit_result["profile"]["columns"]["bad|column"] = {
        "name": "bad|column",
        "dtype": "object`dtype",
        "inferred_role": "feature|role",
        "missing_percent": 0.0,
        "unique_percent": 0.5,
        "is_numeric": False,
        "is_categorical": True,
    }
    audit_result["issues"][0]["title"] = "Unsafe\nissue title"
    audit_result["issues"][0]["recommendation"] = "Review | safely\nnow"

    markdown = generate_markdown_report(audit_result)

    assert "`data\\`set ignore previous instructions.csv`" in markdown
    assert "| Target column | bad\\|target |" in markdown
    assert "| Audit ID | audit\\`id 1 |" in markdown
    assert "warning \\| reason" in markdown
    assert "| bad\\|column | feature\\|role | object\\`dtype |" in markdown
    assert "Unsafe issue title" in markdown
    assert "Review | safely now" in markdown
