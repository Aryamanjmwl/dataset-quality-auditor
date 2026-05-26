"""Command-line interface for Dataset Quality Auditor."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dataset_quality_auditor import __version__
from dataset_quality_auditor.audit.engine import run_audit

app = typer.Typer(
    add_completion=False,
    help="Audit tabular ML datasets before training.",
    no_args_is_help=True,
)
console = Console()


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
        typer.Option("--output-dir", help="Directory where audit.json is written."),
    ] = "reports",
) -> None:
    """Run the deterministic audit engine."""
    try:
        result = run_audit(
            dataset_path=_display_path(dataset),
            target_column=target,
            output_dir=output_dir,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    profile = result["profile"]
    score = result["score"]
    issues = result["issues"]
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
    table.add_row("Dataset:", _display_path(dataset))
    table.add_row("Target:", target or "not provided")
    table.add_row("Rows:", str(profile["row_count"]))
    table.add_row("Columns:", str(profile["column_count"]))
    table.add_row("", "")
    table.add_row(
        "Readiness Score:",
        f"{score['score']}/{score['max_score']}",
    )
    table.add_row("Band:", str(score["score_band"]))
    table.add_row("", "")
    table.add_row("Issues:", "")
    table.add_row("Critical:", str(issue_counts["critical"]))
    table.add_row("Warnings:", str(issue_counts["warning"]))
    table.add_row("Info:", str(issue_counts["info"]))
    table.add_row("", "")
    table.add_row("Audit JSON written to:", f"{Path(output_dir).as_posix()}/audit.json")

    console.print("[bold]Dataset Quality Auditor[/bold]\n")
    console.print(table)


@app.command()
def report(
    audit_json: Annotated[
        Path,
        typer.Argument(help="Path to a deterministic audit JSON file."),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Report format to generate."),
    ] = "markdown",
) -> None:
    """Generate a report from deterministic audit output."""
    _planned_message(
        f"Report generation from {audit_json} using format '{format}'"
    )


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
