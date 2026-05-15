"""VUORSE-VORTEX CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from vuorse_vortex.gpu import require_gpu
from vuorse_vortex.jsonl import validate_jsonl

app = typer.Typer(help="VUORSE-VORTEX command line interface.")
console = Console()


@app.command()
def doctor(require_cuda: bool = typer.Option(False, "--require-cuda", help="Fail if CUDA is missing.")) -> None:
    """Check runtime health."""
    console.print("[bold magenta]VUORSE-VORTEX runtime check[/bold magenta]")
    if require_cuda:
        require_gpu("doctor --require-cuda")
        console.print("[green]CUDA available. VUORSE is not on strike.[/green]")
    else:
        console.print("[yellow]CUDA not required for this diagnostic.[/yellow]")


@app.command("validate-jsonl")
def validate_jsonl_command(path: Path) -> None:
    """Validate VUORSE memory JSONL."""
    errors = validate_jsonl(path)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]Valid JSONL:[/green] {path}")


@app.command("slay-mode")
def slay_mode() -> None:
    """Print the singularity trigger."""
    console.print("[bold magenta]Slay Mode ∞[/bold magenta]")
    console.print("VUORSE-VORTEX ignition point registered.")
