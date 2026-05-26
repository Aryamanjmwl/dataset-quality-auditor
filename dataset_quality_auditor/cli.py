"""Command-line interface for Dataset Quality Auditor."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dataset_quality_auditor import __version__
from dataset_quality_auditor.audit.engine import run_audit
from dataset_quality_auditor.reports import (
    load_audit_json,
    save_html_report,
    save_json_report,
    save_markdown_report,
)

app = typer.Typer(
    add_completion=False,
    help="Audit tabular ML datasets before training.",
    no_args_is_help=True,
)
console = Console()
REPORT_FORMATS = {"json", "markdown", "html", "all"}


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
        msg = f"Unsupported report format '{report_format}'. Use one of: {allowed}."
        raise typer.BadParameter(msg)
    return normalized


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
    profile = audit_result["profile"]
    score = audit_result["score"]
    issues = list(audit_result["issues"])
    counts = {
        severity: sum(1 for issue in issues if issue["severity"] == severity)
        for severity in ("critical", "warning", "info")
    }
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Dataset:", str(audit_result["dataset_path"]))
    table.add_row("Target:", str(audit_result.get("target_column")))
    table.add_row("Rows:", str(profile["row_count"]))
    table.add_row("Columns:", str(profile["column_count"]))
    table.add_row("", "")
    table.add_row("Readiness Score:", f"{score['score']}/{score['max_score']}")
    table.add_row("Band:", str(score["score_band"]))
    table.add_row("", "")
    table.add_row("Issues:", "")
    table.add_row("Critical:", str(counts["critical"]))
    table.add_row("Warnings:", str(counts["warning"]))
    table.add_row("Info:", str(counts["info"]))
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
            help="Path to a tabular dataset file.",
        ),
    ],
    target: Annotated[
        str | None,
        typer.Option("--target", "-t", help="Name of the target column."),
    ] = None,
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directory where reports are written."),
    ] = "reports",
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Report format: json, markdown, html, all.",
        ),
    ] = "json",
) -> None:
    """Run the deterministic audit engine."""
    _validate_report_format(format)
    try:
        audit_result = run_audit(
            dataset_path=_display_path(dataset),
            target_column=target,
            output_dir=output_dir,
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
            help="Path to a deterministic audit JSON file.",
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Report format: json, markdown, html, all.",
        ),
    ] = "markdown",
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directory where report files are written."),
    ] = "reports",
) -> None:
    """Generate reports from deterministic audit output."""
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
def contract(
    dataset: Annotated[Path, typer.Argument(help="Path to a dataset file.")],
    target: Annotated[
        str,
        typer.Option("--target", "-t", help="Name of the target column."),
    ],
) -> None:
    """Generate a dataset contract."""
    _planned_message(
        f"Contract generation for {dataset} with target column '{target}'"
    )


@app.command()
def validate(
    dataset: Annotated[Path, typer.Argument(help="Path to a dataset file.")],
    contract: Annotated[
        Path,
        typer.Option("--contract", "-c", help="Path to a dataset contract."),
    ],
) -> None:
    """Validate a dataset against a contract."""
    _planned_message(f"Validation of {dataset} against contract {contract}")


if __name__ == "__main__":
    app()
