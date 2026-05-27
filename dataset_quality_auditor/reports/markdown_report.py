"""Markdown report generation."""

from pathlib import Path


def _fmt(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


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


def generate_markdown_report(audit_result: dict) -> str:
    profile = audit_result["profile"]
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
        f"- Dataset path: `{audit_result['dataset_path']}`",
        f"- Target column: `{audit_result.get('target_column')}`",
        f"- Row count: {profile['row_count']}",
        f"- Column count: {profile['column_count']}",
        f"- Readiness score: {score['score']}/{score['max_score']}",
        f"- Score band: `{score['score_band']}`",
        f"- Total issues: {len(issues)}",
        f"- Critical: {counts['critical']}",
        f"- Warning: {counts['warning']}",
        f"- Info: {counts['info']}",
        "",
        "## Dataset Overview",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Rows | {profile['row_count']} |",
        f"| Columns | {profile['column_count']} |",
        f"| Duplicate rows | {profile['duplicate_row_count']} |",
        f"| Duplicate percent | {_fmt(profile['duplicate_row_percent'])} |",
        f"| Target column | {_fmt(audit_result.get('target_column'))} |",
        f"| Audit ID | {audit_result['audit_id']} |",
        f"| Created at | {audit_result['created_at']} |",
        "",
        "## Readiness Score",
        "",
        f"Score: **{score['score']}/{score['max_score']}**",
        "",
        f"Band: **{score['score_band']}**",
        "",
        "This score is deterministic. AI cannot modify it.",
        "",
        "| Issue ID | Severity | Deduction | Reason |",
        "|---|---|---:|---|",
    ]
    for deduction in score.get("deductions", []):
        lines.append(
            "| {issue_id} | {severity} | {deduction} | {reason} |".format(
                **deduction
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
                    f"- `{issue['issue_id']}`: {issue['title']}",
                    f"  - Affected column: `{_fmt(scope.get('column'))}`",
                    f"  - Evidence metric: `{evidence['metric']}`",
                    f"  - Observed value: {_fmt(evidence['observed_value'])}",
                    f"  - Threshold: {_fmt(evidence['threshold'])}",
                    f"  - Recommendation: {issue['recommendation']}",
                    "  - Human review required: "
                    f"{issue['requires_human_review']}",
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
                name=column["name"],
                role=column["inferred_role"],
                dtype=column["dtype"],
                missing=_fmt(column["missing_percent"]),
                unique=_fmt(column["unique_percent"]),
                num=column["is_numeric"],
                cat=column["is_categorical"],
            )
    )
    lines.extend(["", "## Recommended Next Steps", ""])
    recommendations = _recommendations(issues)
    lines.extend(
        [f"- {item}" for item in recommendations] or ["No issue recommendations."]
    )
    lines.extend(
        [
            "",
            "## Reproducibility Metadata",
            "",
            f"- Package version: `{metadata['package_version']}`",
            f"- Engine version: `{metadata['engine_version']}`",
            f"- Deterministic: `{metadata['deterministic']}`",
            f"- AI generated: `{metadata['ai_generated']}`",
            "",
        ]
    )
    return "\n".join(lines)


def save_markdown_report(audit_result: dict, output_path: str | Path) -> Path:
    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(generate_markdown_report(audit_result), encoding="utf-8")
    return report_path
