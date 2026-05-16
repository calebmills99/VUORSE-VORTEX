"""VUORSE-VORTEX CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from vuorse_vortex.gpu import require_gpu
from vuorse_vortex.jsonl import validate_jsonl
from vuorse_vortex.settings import get_settings
from vuorse_vortex.synthesis import theses_as_jsonl
from vuorse_vortex.vector import get_backend

app = typer.Typer(help="VUORSE-VORTEX command line interface.")
console = Console()


@app.command()
def doctor(
    require_cuda: bool = typer.Option(
        False, "--require-cuda", help="Fail if CUDA is missing."
    ),
) -> None:
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

@app.command("synthesize")
def synthesize(output: Path = Path("synthetic_enrichment/theses.jsonl")) -> None:
    """Generate seed synthetic synthesis theses."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(theses_as_jsonl() + "\n", encoding="utf-8")
    console.print(f"[green]Wrote synthetic theses to:[/green] {output}")


@app.command("query")
def query(
    text: str = typer.Argument(..., help="Query text to search the memory store."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return."),
    backend: str | None = typer.Option(
        None, "--backend", "-b", help="Vector backend override (chromadb or faiss)."
    ),
) -> None:
    """Query the VUORSE memory vector store."""
    settings = get_settings()
    if backend:
        settings = settings.model_copy(update={"vector_backend": backend})

    require_gpu("query embedding")

    vector_backend = get_backend(settings=settings)
    results = vector_backend.query(text, top_k=top_k)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        raise typer.Exit(code=0)

    for i, result in enumerate(results, start=1):
        console.print(f"\n[bold cyan]#{i}[/bold cyan] (score: {result.score:.4f})")
        console.print(f"  [dim]id:[/dim] {result.record_id}")
        console.print(f"  [dim]layer:[/dim] {result.layer}")
        console.print(f"  {result.text[:200]}")

