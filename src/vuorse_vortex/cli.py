"""VUORSE-VORTEX CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.prompt import Prompt

from vuorse_vortex.gpu import require_gpu
from vuorse_vortex.jsonl import iter_jsonl, validate_jsonl
from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.settings import get_settings
from vuorse_vortex.synthesis import theses_as_jsonl
from vuorse_vortex.vector import get_backend
from vuorse_vortex.walled import (
    WalledFileEmptyError,
    WalledFileError,
    WalledFileMissingError,
    WalledFileParseError,
    build_walled,
    build_walled_check,
)

app = typer.Typer(help="VUORSE-VORTEX command line interface.")
console = Console()

_DEFAULT_THESES_PATH = Path("synthetic_enrichment/theses.jsonl")
_DEFAULT_ACCEPTED_THESES_PATH = Path("synthetic_enrichment/theses_accepted.jsonl")
_EMBED_PATH_ARGUMENT = typer.Argument(
    _DEFAULT_THESES_PATH,
    help="JSONL file of MemoryRecord rows to embed and ingest.",
)

_DEFAULT_WALLED_MD = Path("hooplehopper_totality/debriefing_walled.md")
_DEFAULT_WALLED_JSONL = Path("hooplehopper_totality/debriefing_walled.jsonl")
_BUILD_WALLED_MD_ARGUMENT = typer.Argument(
    _DEFAULT_WALLED_MD,
    help="Walled markdown source file.",
)
_BUILD_WALLED_JSONL_ARGUMENT = typer.Argument(
    _DEFAULT_WALLED_JSONL,
    help="JSONL projection target file.",
)


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
@app.command("firewall")
def firewall_cmd(path: Path = typer.Argument(..., help="JSONL file to validate against the canon firewall.")) -> None:
    """Validate a JSONL file using CanonFirewallValidator.

    This is a thin wrapper around `validate-jsonl` that makes the intent
    explicit: run the canon‑firewall checks on the supplied file.
    """
    errors = validate_jsonl(path)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]Firewall validation passed for:[/green] {path}")

@app.command("convert-jsonl")
def convert_jsonl_cmd(
    input_path: Path = typer.Argument(..., help="Legacy JSONL file to clean"),
    output_path: Path = typer.Option(
        "converted.jsonl", "--output", help="Destination path for cleaned JSONL"
    ),
) -> None:
    """Convert a legacy JSONL file to the current MemoryRecord schema.

    Delegates to the utility in `vuorse_vortex.convert_jsonl`.
    """
    from .convert_jsonl import convert_jsonl
    console.print(f"[yellow]Converting {input_path} → {output_path}...[/yellow]")
    convert_jsonl(Path(input_path), Path(output_path))
    console.print(f"[green]Conversion complete.[/green] Output: {output_path}")

@app.command("slay-mode")
def slay_mode() -> None:
    """Print the singularity trigger."""
    console.print("[bold magenta]Slay Mode ∞[/bold magenta]")
    console.print("VUORSE-VORTEX ignition point registered.")

@app.command("synthesize")
def synthesize(
    seed: int = typer.Option(0, "--seed", help="Seed for generation."),
    n_records: int = typer.Option(
        5,
        "--n",
        min=1,
        help="Number of records to generate.",
    ),
    chaos: float = typer.Option(0.3, "--chaos", help="Chaos factor."),
    output: Annotated[
        Path,
        typer.Option("--output", help="JSONL output path."),
    ] = _DEFAULT_THESES_PATH,
) -> None:
    """Generate seed synthetic synthesis theses."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        theses_as_jsonl(seed=seed, n_records=n_records, chaos_factor=chaos) + "\n",
        encoding="utf-8",
    )
    console.print(f"[green]Wrote synthetic theses to:[/green] {output}")


def _split_thesis_text(text: str) -> tuple[str, str]:
    """Return editable premise/synthesis fields from generated thesis text."""
    if text.startswith("Premise: ") and "\n\nSynthesis:" in text:
        premise_part, synthesis_part = text.split("\n\nSynthesis:", 1)
        return premise_part[len("Premise: ") :], synthesis_part.strip()
    return text, text


def _edit_record_interactively(record: MemoryRecord) -> MemoryRecord:
    premise, synthesis = _split_thesis_text(record.text)
    title = Prompt.ask("Title", default=record.title)
    tags_raw = Prompt.ask("Tags (comma-separated)", default=", ".join(record.metadata.tags))
    edited_premise = Prompt.ask("Premise", default=premise)
    edited_synthesis = Prompt.ask("Synthesis", default=synthesis)
    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
    return record.model_copy(
        update={
            "title": title,
            "text": f"Premise: {edited_premise}\n\nSynthesis: {edited_synthesis}",
            "metadata": record.metadata.model_copy(update={"tags": tags}),
            "retrieval": record.retrieval.model_copy(update={"query_hints": tags}),
        }
    )


@app.command("synthesize-interactive")
def synthesize_interactive(
    seed: int = typer.Option(42, "--seed", help="Seed for generation"),
    chaos: float = typer.Option(0.3, "--chaos", help="Chaos factor"),
    output: Annotated[
        Path,
        typer.Option("--output", help="Reviewed JSONL output path."),
    ] = _DEFAULT_ACCEPTED_THESES_PATH,
) -> None:
    """Interactively synthesize and review chaos memory records."""
    from vuorse_vortex.synthesis import ChaosEngine, SynthesisConfig

    config = SynthesisConfig(seed=seed, chaos_factor=chaos, n_records=999999)
    engine = ChaosEngine(config)

    output.parent.mkdir(parents=True, exist_ok=True)

    accepted_count = 0
    for record in engine.generate_records():
        console.print("\n[bold magenta]Generated Record[/bold magenta]")
        console.print(f"[cyan]Title:[/cyan] {record.title}")
        console.print(f"[cyan]Layer:[/cyan] {record.layer}")
        console.print(f"[cyan]Tags:[/cyan] {', '.join(record.metadata.tags)}")
        console.print(f"\n{record.text}\n")

        choice = Prompt.ask(
            "[bold yellow]Action (a=accept, e=edit, r=reject, q=quit)[/bold yellow]",
            choices=["a", "e", "r", "q"],
            default="a",
        )

        if choice == "e":
            record = _edit_record_interactively(record)
            console.print("[green]Edited record.[/green]")
            choice = Prompt.ask(
                "[bold yellow]Action (a=accept, r=reject, q=quit)[/bold yellow]",
                choices=["a", "r", "q"],
                default="a",
            )

        if choice == "a":
            with open(output, "a", encoding="utf-8") as f:
                f.write(record.model_dump_json(exclude_none=True) + "\n")
            engine.add_record_as_atom(record)
            accepted_count += 1
            console.print(
                f"[green]Accepted and added to atom pool! ({accepted_count} total)[/green]"
            )
        elif choice == "r":
            console.print("[red]Rejected.[/red]")
        elif choice == "q":
            console.print("[dim]Quitting interactive mode.[/dim]")
            break


@app.command("embed")
def embed(
    path: Path = _EMBED_PATH_ARGUMENT,
    backend: str | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Vector backend override. Only 'chromadb' is supported.",
    ),
) -> None:
    """Validate a JSONL file and ingest its records into the vector store."""
    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(code=1)

    errors = validate_jsonl(path)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)

    settings = get_settings()
    if backend:
        settings = settings.model_copy(update={"vector_backend": backend})

    records: list[dict[str, Any]] = [obj for _, obj in iter_jsonl(path)]
    console.print(
        f"[bold magenta]Embedding {len(records)} records[/bold magenta] "
        f"into backend [cyan]{settings.vector_backend}[/cyan]..."
    )

    vector_backend = get_backend(settings=settings)
    count = vector_backend.ingest(records)
    console.print(f"[green]Ingested {count} records.[/green]")


@app.command("query")
def query(
    text: str = typer.Argument(..., help="Query text to search the memory store."),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return."),
    backend: str | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Vector backend override. Only 'chromadb' is supported.",
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

# Add near the end of src/vuorse_vortex/cli.py
@app.command("index")
def index(refresh: bool = typer.Option(False, "--refresh", help="Re‑build the full semantic graph")) -> None:
    """Build or refresh the full LSP/semantic index."""
    from vuorse_vortex.graphd import build_graph, refresh_graph
    if refresh:
        refresh_graph()
    else:
        build_graph()
    console.print("[green]Semantic graph built successfully.[/green]")


@app.command("build-walled")
def build_walled_cmd(
    md_path: Path = _BUILD_WALLED_MD_ARGUMENT,
    jsonl_path: Path = _BUILD_WALLED_JSONL_ARGUMENT,
    check: bool = typer.Option(
        False,
        "--check",
        help="Verify JSONL is up to date; exit non-zero if drifted.",
    ),
) -> None:
    """Build (or check) the walled markdown -> JSONL projection."""
    try:
        if check:
            ok = build_walled_check(md_path, jsonl_path)
            if not ok:
                console.print(
                    f"[red]Walled JSONL is drifted from source:[/red] "
                    f"{jsonl_path} does not match regenerated output from {md_path}."
                )
                raise typer.Exit(code=1)
            console.print(
                f"[green]Walled JSONL is up to date:[/green] {jsonl_path}"
            )
            return

        count = build_walled(md_path, jsonl_path)
        console.print(
            f"[green]Wrote {count} walled records to:[/green] {jsonl_path}"
        )
    except WalledFileMissingError as exc:
        console.print(f"[red]Walled file missing:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except WalledFileEmptyError as exc:
        console.print(f"[red]Walled file empty:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except WalledFileParseError as exc:
        console.print(f"[red]Walled parse error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except WalledFileError as exc:
        console.print(f"[red]Walled error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
