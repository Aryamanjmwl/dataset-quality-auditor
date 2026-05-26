"""Command-line interface for Dataset Quality Auditor."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from dataset_quality_auditor import __version__

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
        str,
        typer.Option("--target", "-t", help="Name of the target column."),
    ],
) -> None:
    """Prepare to audit a dataset."""
    console.print(
        Panel.fit(
            "[bold green]Dataset accepted for audit planning[/bold green]\n"
            f"Dataset: [cyan]{_display_path(dataset)}[/cyan]\n"
            f"Target column: [cyan]{target}[/cyan]\n\n"
            "Full deterministic checks and scoring are planned for Phase 3.",
            border_style="green",
        )
    )


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
