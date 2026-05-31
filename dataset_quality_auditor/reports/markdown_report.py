"""Markdown report generation."""

from pathlib import Path


def _fmt(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _md_inline(value: object) -> str:
    return _fmt(value).replace("\r", " ").replace("\n", " ").strip()


def _md_code(value: object) -> str:
    return _md_inline(value).replace("`", "\\`")


def _md_cell(value: object) -> str:
    return (
        _md_inline(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("`", "\\`")
    )


def _issue_counts(issues: list[dict[str, object]]) -> dict[str, int]:
    return {
        severity: sum(1 for issue in issues if issue.get("severity") == severity)
        for severity in ("critical", "warning", "info")
    }


def _recommendations(issues: list[dict[str, object]]) -> list[str]:
    seen: set[str] = set()
    recommendations: list[str] = []
    for issue in issues:
        recommendation = str(issue.get("recommendation", "")).strip()
        if recommendation and recommendation not in seen:
            seen.add(recommendation)
            recommendations.append(recommendation)
    return recommendations


def _display_profile(audit_result: dict) -> dict[str, object]:
    profile = audit_result["profile"]
    if audit_result.get("mode") == "train_test":
        return profile["train"]
    return profile


def generate_markdown_report(audit_result: dict) -> str:
    profile = _display_profile(audit_result)
    score = audit_result["score"]
    metadata = audit_result["metadata"]
    issues = list(audit_result.get("issues", []))
    counts = _issue_counts(issues)
    columns = profile["columns"]

    lines = [
        "# Dataset Quality Audit Report",
        "",
        "This report is generated from deterministic audit results.",
        "",
        "## Executive Summary",
        "",
        f"- Dataset path: `{_md_code(audit_result['dataset_path'])}`",
        f"- Test dataset path: `{_md_code(audit_result.get('test_dataset_path'))}`",
        f"- Target column: `{_md_code(audit_result.get('target_column'))}`",
        f"- Row count: {_md_inline(profile['row_count'])}",
        f"- Column count: {_md_inline(profile['column_count'])}",
        f"- Readiness score: {_md_inline(score['score'])}/"
        f"{_md_inline(score['max_score'])}",
        f"- Score band: `{_md_code(score['score_band'])}`",
        f"- Total issues: {len(issues)}",
        f"- Critical: {counts['critical']}",
        f"- Warning: {counts['warning']}",
        f"- Info: {counts['info']}",
        "",
        "## Dataset Overview",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Rows | {_md_cell(profile['row_count'])} |",
        f"| Columns | {_md_cell(profile['column_count'])} |",
        f"| Duplicate rows | {_md_cell(profile['duplicate_row_count'])} |",
        f"| Duplicate percent | {_md_cell(profile['duplicate_row_percent'])} |",
        f"| Target column | {_md_cell(audit_result.get('target_column'))} |",
        f"| Mode | {_md_cell(audit_result.get('mode', 'single_dataset'))} |",
        f"| Audit ID | {_md_cell(audit_result['audit_id'])} |",
        f"| Created at | {_md_cell(audit_result['created_at'])} |",
        "",
        "## Readiness Score",
        "",
        f"Score: **{_md_inline(score['score'])}/{_md_inline(score['max_score'])}**",
        "",
        f"Band: **{_md_inline(score['score_band'])}**",
        "",
        "This score is deterministic. AI cannot modify it.",
        "",
        "| Issue ID | Severity | Deduction | Reason |",
        "|---|---|---:|---|",
    ]
    for deduction in score.get("deductions", []):
        lines.append(
            "| {issue_id} | {severity} | {deduction} | {reason} |".format(
                issue_id=_md_cell(deduction.get("issue_id")),
                severity=_md_cell(deduction.get("severity")),
                deduction=_md_cell(deduction.get("deduction")),
                reason=_md_cell(deduction.get("reason")),
            )
        )
    lines.extend(["", "## Issue Summary", ""])
    for label, severity in (
        ("Critical", "critical"),
        ("Warning", "warning"),
        ("Info", "info"),
    ):
        lines.extend([f"### {label}", ""])
        group = [issue for issue in issues if issue.get("severity") == severity]
        if not group:
            lines.extend(["No issues.", ""])
            continue
        for issue in group:
            evidence = issue["evidence"]
            scope = issue["scope"]
            lines.extend(
                [
                    f"- `{_md_code(issue['issue_id'])}`: "
                    f"{_md_inline(issue['title'])}",
                    f"  - Affected column: `{_md_code(scope.get('column'))}`",
                    f"  - Evidence metric: `{_md_code(evidence['metric'])}`",
                    f"  - Observed value: "
                    f"{_md_inline(evidence['observed_value'])}",
                    f"  - Threshold: {_md_inline(evidence['threshold'])}",
                    f"  - Recommendation: {_md_inline(issue['recommendation'])}",
                    "  - Human review required: "
                    f"{_md_inline(issue['requires_human_review'])}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Column Overview",
            "",
            "| Column | Role | Type | Missing % | Unique % | Numeric | Categorical |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for column in columns.values():
        lines.append(
            (
                "| {name} | {role} | {dtype} | {missing} | {unique} | "
                "{num} | {cat} |"
            ).format(
                name=_md_cell(column["name"]),
                role=_md_cell(column["inferred_role"]),
                dtype=_md_cell(column["dtype"]),
                missing=_md_cell(column["missing_percent"]),
                unique=_md_cell(column["unique_percent"]),
                num=_md_cell(column["is_numeric"]),
                cat=_md_cell(column["is_categorical"]),
            )
    )
    lines.extend(["", "## Recommended Next Steps", ""])
    recommendations = _recommendations(issues)
    lines.extend(
        [f"- {_md_inline(item)}" for item in recommendations]
        or ["No issue recommendations."]
    )
    lines.extend(
        [
            "",
            "## Reproducibility Metadata",
            "",
            f"- Package version: `{_md_code(metadata['package_version'])}`",
            f"- Engine version: `{_md_code(metadata['engine_version'])}`",
            f"- Deterministic: `{_md_code(metadata['deterministic'])}`",
            f"- AI generated: `{_md_code(metadata['ai_generated'])}`",
            "",
        ]
    )
    return "\n".join(lines)


def save_markdown_report(audit_result: dict, output_path: str | Path) -> Path:
    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(generate_markdown_report(audit_result), encoding="utf-8")
    return report_path
