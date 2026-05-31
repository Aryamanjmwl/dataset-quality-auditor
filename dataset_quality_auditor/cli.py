"""Command-line interface for Dataset Quality Auditor."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dataset_quality_auditor import __version__
from dataset_quality_auditor.ai import generate_ai_review
from dataset_quality_auditor.audit.engine import run_audit
from dataset_quality_auditor.audit.summary import (
    evaluate_audit_gate,
    summarize_audit_result,
)
from dataset_quality_auditor.contracts import (
    generate_contract,
    save_contract,
    save_validation_result,
    validate_dataset,
)
from dataset_quality_auditor.reports import (
    load_audit_json,
    save_html_report,
    save_json_report,
    save_markdown_report,
)

app = typer.Typer(
    add_completion=False,
    help=(
        "Deterministically audit local CSV datasets before ML training. "
        "Supports single-dataset and train/test workflows."
    ),
    no_args_is_help=True,
)
console = Console()
REPORT_FORMATS = {"json", "markdown", "html", "all"}
SUMMARY_FORMATS = {"json", "text"}


def _planned_message(feature: str) -> None:
    console.print(
        Panel.fit(
            f"[bold]{feature}[/bold] is planned for a future phase.\n"
            "The deterministic audit engine will remain the source of truth.",
            border_style="cyan",
        )
    )


def _display_path(path: Path) -> str:
    return path.as_posix()


def _validate_report_format(report_format: str) -> str:
    normalized = report_format.lower()
    if normalized not in REPORT_FORMATS:
        allowed = ", ".join(sorted(REPORT_FORMATS))
        msg = (
            f"Unsupported report format '{report_format}'. "
            f"Supported formats: {allowed}."
        )
        raise typer.BadParameter(msg)
    return normalized


def _validate_summary_format(summary_format: str) -> str:
    normalized = summary_format.lower()
    if normalized not in SUMMARY_FORMATS:
        allowed = ", ".join(sorted(SUMMARY_FORMATS))
        msg = (
            f"Unsupported summary format '{summary_format}'. "
            f"Supported formats: {allowed}."
        )
        raise typer.BadParameter(msg)
    return normalized


def _validate_gate_options(
    min_score: float,
    max_critical: int | None,
    max_high: int | None,
    max_medium: int | None,
    max_human_review: int | None,
) -> None:
    if min_score < 0 or min_score > 100:
        raise typer.BadParameter("--min-score must be between 0 and 100.")

    limits = {
        "--max-critical": max_critical,
        "--max-high": max_high,
        "--max-medium": max_medium,
        "--max-human-review": max_human_review,
    }
    for option, value in limits.items():
        if value is not None and value < 0:
            raise typer.BadParameter(f"{option} must be greater than or equal to 0.")


def _write_report_artifacts(
    audit_result: dict,
    report_format: str,
    output_dir: str,
    include_json_report: bool,
) -> list[Path]:
    normalized = _validate_report_format(report_format)
    output_path = Path(output_dir)
    generated: list[Path] = []
    if include_json_report and normalized in {"json", "all"}:
        generated.append(
            save_json_report(audit_result, output_path / "audit_report.json")
        )
    if normalized in {"markdown", "all"}:
        generated.append(
            save_markdown_report(audit_result, output_path / "audit_report.md")
        )
    if normalized in {"html", "all"}:
        generated.append(
            save_html_report(audit_result, output_path / "audit_report.html")
        )
    return generated


def _print_audit_summary(audit_result: dict, generated_paths: list[Path]) -> None:
    raw_profile = audit_result["profile"]
    assert isinstance(raw_profile, dict)
    profile = (
        raw_profile["train"]
        if audit_result.get("mode") == "train_test"
        else raw_profile
    )
    score = audit_result["score"]
    issues = audit_result["issues"]
    assert isinstance(profile, dict)
    assert isinstance(score, dict)
    assert isinstance(issues, list)

    issue_counts = {"critical": 0, "warning": 0, "info": 0}
    for issue in issues:
        assert isinstance(issue, dict)
        severity = str(issue["severity"])
        issue_counts[severity] = issue_counts.get(severity, 0) + 1

    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Mode:", str(audit_result.get("mode", "single_dataset")))
    table.add_row("Dataset:", str(audit_result["dataset_path"]))
    if audit_result.get("test_dataset_path"):
        table.add_row("Test dataset:", str(audit_result["test_dataset_path"]))
    table.add_row("Target:", str(audit_result.get("target_column") or "not provided"))
    table.add_row("Rows:", str(profile["row_count"]))
    table.add_row("Columns:", str(profile["column_count"]))
    table.add_row("", "")
    table.add_row("Readiness Score:", f"{score['score']}/{score['max_score']}")
    table.add_row("Band:", str(score["score_band"]))
    table.add_row("", "")
    table.add_row("Issues:", "")
    table.add_row("Critical:", str(issue_counts["critical"]))
    table.add_row("Warnings:", str(issue_counts["warning"]))
    table.add_row("Info:", str(issue_counts["info"]))
    table.add_row("", "")
    for index, path in enumerate(generated_paths):
        label = "Generated:" if index else "Audit JSON written to:"
        table.add_row(label, path.as_posix())

    console.print("[bold]Dataset Quality Auditor[/bold]\n")
    console.print(table)


@app.command()
def version() -> None:
    """Show the installed package version."""
    console.print(f"Dataset Quality Auditor [bold]v{__version__}[/bold]")


@app.command()
def audit(
    dataset: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a local CSV dataset.",
        ),
    ],
    target: Annotated[
        str | None,
        typer.Option("--target", "-t", help="Target column name, if available."),
    ] = None,
    test_dataset: Annotated[
        Path | None,
        typer.Option(
            "--test",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Optional local CSV test dataset for train/test checks.",
        ),
    ] = None,
    output_dir: Annotated[
        str,
        typer.Option(
            "--output-dir",
            help="Directory where audit.json and optional reports are written.",
        ),
    ] = "reports",
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Optional YAML file with supported audit threshold overrides.",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Optional report format to generate: json, markdown, html, all.",
        ),
    ] = "json",
) -> None:
    """Audit a local CSV dataset, optionally with a train/test CSV pair."""
    _validate_report_format(format)
    try:
        audit_result = run_audit(
            dataset_path=_display_path(dataset),
            target_column=target,
            test_dataset_path=_display_path(test_dataset) if test_dataset else None,
            output_dir=output_dir,
            config_path=_display_path(config) if config else None,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    generated = [Path(output_dir) / "audit.json"]
    generated.extend(
        _write_report_artifacts(
            audit_result,
            report_format=format,
            output_dir=output_dir,
            include_json_report=False,
        )
    )
    _print_audit_summary(audit_result, generated)


@app.command()
def report(
    audit_json: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to audit.json from a deterministic audit run.",
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help=(
                "Report format to generate from audit JSON: "
                "json, markdown, html, all."
            ),
        ),
    ] = "markdown",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directory where report files are written."),
    ] = "reports",
) -> None:
    """Generate JSON, Markdown, or HTML reports from audit JSON."""
    _validate_report_format(format)
    try:
        audit_result = load_audit_json(audit_json)
    except FileNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    generated = _write_report_artifacts(
        audit_result,
        report_format=format,
        output_dir=output_dir,
        include_json_report=True,
    )
    console.print("[bold]Dataset Quality Auditor Report[/bold]\n")
    for path in generated:
        console.print(f"Generated: [cyan]{path.as_posix()}[/cyan]")


@app.command()
def summary(
    audit_json: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to audit.json from a deterministic audit run.",
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Summary output format: text or json.",
        ),
    ] = "text",
) -> None:
    """Print a compact summary from existing audit JSON without rerunning checks."""
    normalized = _validate_summary_format(format)
    try:
        audit_result = load_audit_json(audit_json)
        audit_summary = summarize_audit_result(audit_result)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if normalized == "json":
        console.print(json.dumps(audit_summary, indent=2, sort_keys=True))
        return

    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Dataset:", str(audit_summary["dataset_path"]))
    table.add_row("Mode:", str(audit_summary["mode"]))
    if "test_dataset_path" in audit_summary:
        table.add_row("Test dataset:", str(audit_summary["test_dataset_path"]))
    if "target_column" in audit_summary:
        table.add_row("Target:", str(audit_summary["target_column"]))
    table.add_row(
        "Readiness Score:",
        f"{audit_summary['score']}/{audit_summary['max_score']}",
    )
    table.add_row("Band:", str(audit_summary["score_band"]))
    table.add_row("Issues:", str(audit_summary["issue_count"]))
    table.add_row("Failed issues:", str(audit_summary["failed_count"]))
    table.add_row(
        "Human review:",
        str(audit_summary["requires_human_review_count"]),
    )
    table.add_row(
        "Top issue IDs:",
        ", ".join(audit_summary["top_issue_ids"]) or "none",
    )
    console.print("[bold]Dataset Quality Auditor Summary[/bold]\n")
    console.print(table)


@app.command()
def gate(
    audit_json: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to audit.json from a deterministic audit run.",
        ),
    ],
    min_score: Annotated[
        float,
        typer.Option(
            "--min-score",
            help="Minimum readiness score required to pass.",
        ),
    ] = 0,
    max_critical: Annotated[
        int | None,
        typer.Option(
            "--max-critical",
            help="Maximum allowed critical issues. Omit for no limit.",
        ),
    ] = None,
    max_high: Annotated[
        int | None,
        typer.Option(
            "--max-high",
            help="Maximum allowed high-risk issues. Omit for no limit.",
        ),
    ] = None,
    max_medium: Annotated[
        int | None,
        typer.Option(
            "--max-medium",
            help="Maximum allowed medium-risk issues. Omit for no limit.",
        ),
    ] = None,
    max_human_review: Annotated[
        int | None,
        typer.Option(
            "--max-human-review",
            help="Maximum allowed issues requiring human review. Omit for no limit.",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Gate output format: text or json.",
        ),
    ] = "text",
) -> None:
    """Evaluate deterministic CI/CD gate rules from existing audit JSON."""
    normalized = _validate_summary_format(format)
    _validate_gate_options(
        min_score,
        max_critical,
        max_high,
        max_medium,
        max_human_review,
    )
    try:
        audit_result = load_audit_json(audit_json)
        result = evaluate_audit_gate(
            audit_result,
            min_score=min_score,
            max_critical=max_critical,
            max_high=max_high,
            max_medium=max_medium,
            max_human_review=max_human_review,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    if normalized == "json":
        console.print(json.dumps(result, indent=2, sort_keys=True))
    else:
        summary_result = result["summary"]
        assert isinstance(summary_result, dict)
        risk_level_counts = summary_result["risk_level_counts"]
        severity_counts = summary_result["severity_counts"]
        assert isinstance(risk_level_counts, dict)
        assert isinstance(severity_counts, dict)

        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold")
        table.add_column()
        table.add_row("Status:", "PASS" if result["passed"] else "FAIL")
        table.add_row(
            "Readiness Score:",
            f"{summary_result['score']}/{summary_result['max_score']}",
        )
        table.add_row("Critical issues:", str(severity_counts.get("critical", 0)))
        table.add_row("High-risk issues:", str(risk_level_counts.get("high", 0)))
        table.add_row("Medium-risk issues:", str(risk_level_counts.get("medium", 0)))
        table.add_row(
            "Human review issues:",
            str(summary_result["requires_human_review_count"]),
        )
        reasons = result["reasons"]
        assert isinstance(reasons, list)
        reason_text = "; ".join(str(reason) for reason in reasons) or "none"
        table.add_row("Reasons:", reason_text)
        console.print("[bold]Dataset Quality Auditor Gate[/bold]\n")
        console.print(table)

    if not result["passed"]:
        raise typer.Exit(code=1)


@app.command()
def contract(
    dataset: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a local CSV dataset.",
        ),
    ],
    target: Annotated[
        str | None,
        typer.Option("--target", "-t", help="Target column name, if available."),
    ] = None,
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directory where contract YAML is written."),
    ] = "contracts",
    filename: Annotated[
        str | None,
        typer.Option("--filename", help="Optional contract filename."),
    ] = None,
) -> None:
    """Infer a YAML data contract from local CSV data; review before relying on it."""
    try:
        generated_contract = generate_contract(_display_path(dataset), target)
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output_name = filename or f"{dataset.stem}_contract.yaml"
    output_path = save_contract(generated_contract, Path(output_dir) / output_name)
    columns = generated_contract["columns"]
    assert isinstance(columns, dict)
    review_count = sum(
        1
        for column_contract in columns.values()
        if isinstance(column_contract, dict)
        and bool(column_contract.get("requires_human_review", False))
    )

    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Dataset:", _display_path(dataset))
    table.add_row("Target:", target or "not provided")
    table.add_row("Columns included:", str(len(columns)))
    table.add_row("Human review hints:", str(review_count))
    table.add_row("Contract written to:", output_path.as_posix())
    console.print("[bold]Dataset Quality Auditor Contract[/bold]\n")
    console.print(table)


@app.command()
def validate(
    dataset: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a local CSV dataset to validate.",
        ),
    ],
    contract: Annotated[
        Path,
        typer.Option(
            "--contract",
            "-c",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a YAML contract generated by dqa contract.",
        ),
    ],
    output_dir: Annotated[
        str,
        typer.Option(
            "--output-dir",
            help="Directory where validation JSON is written.",
        ),
    ] = "reports",
) -> None:
    """Validate a local CSV dataset against a deterministic YAML contract."""
    try:
        result = validate_dataset(_display_path(dataset), _display_path(contract))
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    output_path = save_validation_result(
        result,
        Path(output_dir) / "validation_result.json",
    )
    summary = result["summary"]
    assert isinstance(summary, dict)

    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Status:", "passed" if result["passed"] else "failed")
    table.add_row("Total checks:", str(summary["total_checks"]))
    table.add_row("Failed checks:", str(summary["failed_checks"]))
    table.add_row("Validation JSON written to:", output_path.as_posix())
    console.print("[bold]Dataset Quality Auditor Validation[/bold]\n")
    console.print(table)


@app.command()
def review(
    audit_json: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to audit.json from a deterministic audit run.",
        ),
    ],
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            help="Review provider. Currently only the local deterministic mock.",
        ),
    ] = "mock",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directory where ai_review.json is written."),
    ] = "reports",
    workflow: Annotated[
        str,
        typer.Option(
            "--workflow",
            help=(
                "Review workflow: provider or graph. "
                "Both use existing audit findings."
            ),
        ),
    ] = "provider",
) -> None:
    """Review existing audit findings with the mock/local guarded workflow."""
    try:
        ai_review = generate_ai_review(
            audit_json_path=audit_json,
            provider_name=provider,
            output_dir=output_dir,
            workflow=workflow,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output_path = Path(output_dir) / "ai_review.json"
    markdown_path = Path(output_dir) / "ai_review.md"
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Provider:", str(ai_review["provider"]))
    table.add_row("Workflow:", workflow)
    table.add_row("Model:", str(ai_review["model"]))
    table.add_row("Audit ID:", str(ai_review["audit_id"]))
    table.add_row("Readiness score:", str(ai_review["readiness_score"]))
    table.add_row(
        "Prioritized issues:",
        str(len(ai_review["prioritized_issues"])),
    )
    table.add_row(
        "Human review questions:",
        str(len(ai_review["human_review_questions"])),
    )
    table.add_row("AI review written to:", output_path.as_posix())
    if workflow.lower() == "graph" and markdown_path.exists():
        table.add_row("Markdown review written to:", markdown_path.as_posix())
    console.print("[bold]Dataset Quality Auditor AI Review[/bold]\n")
    console.print(table)


if __name__ == "__main__":
    app()
