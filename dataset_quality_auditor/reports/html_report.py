"""HTML report generation."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _template_environment() -> Environment:
    template_dir = Path(__file__).parent / "templates"
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
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


def generate_html_report(audit_result: dict) -> str:
    issues = list(audit_result.get("issues", []))
    template = _template_environment().get_template("report.html.j2")
    return template.render(
        audit=audit_result,
        profile=audit_result["profile"],
        score=audit_result["score"],
        issues=issues,
        issue_counts=_issue_counts(issues),
        recommendations=_recommendations(issues),
        metadata=audit_result["metadata"],
    )


def save_html_report(audit_result: dict, output_path: str | Path) -> Path:
    report_path = Path(output_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(generate_html_report(audit_result), encoding="utf-8")
    return report_path
