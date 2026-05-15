"""VUORSE-VORTEX Typer CLI entrypoint.

  vortex --help
  vortex ingest <file.jsonl>
  vortex validate <file.jsonl>
  vortex enrich --category hooplehopper_totality
  vortex query "Hooplehopper displacement event"
  vortex gpu-status
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vuorse_vortex import __version__
from vuorse_vortex.config import Settings, VectorBackend, get_settings
from vuorse_vortex.logging_utils import configure_logging, get_logger

app = typer.Typer(
    name="vortex",
    help="VUORSE-VORTEX: Anti-erasure cognition architecture for the Slayverse.",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()
err_console = Console(stderr=True)


def _setup(settings: Settings) -> None:
    configure_logging(
        log_level=settings.log_level.value,
        log_format=settings.log_format,
    )


# ---------------------------------------------------------------------------
# Version callback
# ---------------------------------------------------------------------------


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]VUORSE-VORTEX[/] [dim]v{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(  # noqa: UP007
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """
    [bold cyan]VUORSE-VORTEX[/] — A haunted cathedral with a search index.

    Anti-erasure cognition architecture for the Slayverse universe.
    """


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------


@app.command()
def ingest(
    path: Path = typer.Argument(..., help="Path to a JSONL file of MemoryUnit records."),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Run canon firewall before ingest."),
    embed: bool = typer.Option(False, "--embed/--no-embed", help="Compute embeddings during ingest."),
) -> None:
    """Ingest a JSONL memory file into the Velvet Archive."""
    settings = get_settings()
    _setup(settings)
    logger = get_logger("cli.ingest")

    if not path.exists():
        err_console.print(f"[red]File not found:[/] {path}")
        raise typer.Exit(code=1)

    records = []
    with path.open() as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                err_console.print(f"[red]JSON parse error on line {lineno}:[/] {exc}")
                raise typer.Exit(code=1) from exc

    console.print(
        Panel(
            f"[cyan]Ingesting[/] [bold]{len(records)}[/] memory units from [dim]{path}[/]",
            title="Velvet Archive — Ingest",
        )
    )

    if validate:
        from vuorse_vortex.agents.canon_firewall import CanonFirewallValidator

        validator = CanonFirewallValidator(strict_mode=settings.firewall_strict_mode)
        try:
            report = validator.validate_jsonl_records(records)
            if report.is_clean:
                console.print(f"[green]✓ Canon firewall passed[/] ({report.total_units} units)")
            else:
                console.print(
                    f"[yellow]⚠ Canon firewall:[/] {report.critical_count} critical, "
                    f"{report.warning_count} warnings"
                )
                for v in report.violations:
                    severity_color = "red" if v.is_critical() else "yellow"
                    console.print(
                        f"  [{severity_color}][{v.rule}][/] {v.detail}"
                    )
        except ValueError as exc:
            err_console.print(f"[red]Canon firewall rejected ingest:[/] {exc}")
            raise typer.Exit(code=1) from exc

    if embed:
        from vuorse_vortex.embedding.pipeline import EmbeddingPipeline
        from vuorse_vortex.models.memory_unit import MemoryUnit

        pipeline = EmbeddingPipeline(
            model_name=settings.embedding_model,
            device_id=settings.cuda_device_id,
            require_cuda=settings.require_cuda,
            batch_size=settings.embedding_batch_size,
        )
        units = [MemoryUnit.model_validate(r) for r in records]
        units = pipeline.embed_memory_units(units)
        console.print(f"[green]✓ Embeddings computed[/] ({len(units)} units)")

    logger.info("Ingest complete", count=len(records), path=str(path))
    console.print(f"[green]✓ Ingested {len(records)} memory units[/]")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


@app.command()
def validate(
    path: Path = typer.Argument(..., help="Path to a JSONL file to validate."),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Fail on critical violations."),
) -> None:
    """Run the canon firewall validator on a JSONL memory file."""
    settings = get_settings()
    _setup(settings)

    if not path.exists():
        err_console.print(f"[red]File not found:[/] {path}")
        raise typer.Exit(code=1)

    records = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    from vuorse_vortex.agents.canon_firewall import CanonFirewallValidator

    validator = CanonFirewallValidator(strict_mode=False)
    report = validator.validate_jsonl_records(records)

    table = Table(title="Canon Firewall Report", show_header=True)
    table.add_column("Unit ID", style="dim", max_width=38)
    table.add_column("Rule")
    table.add_column("Severity")
    table.add_column("Detail")

    for v in report.violations:
        severity_style = "red" if v.is_critical() else "yellow"
        table.add_row(
            v.unit_id[:36],
            v.rule,
            f"[{severity_style}]{v.severity}[/]",
            v.detail[:80],
        )

    console.print(table)
    console.print(
        f"\n[bold]Total:[/] {report.total_units}  "
        f"[green]Passed:[/] {len(report.passed)}  "
        f"[red]Critical:[/] {report.critical_count}  "
        f"[yellow]Warnings:[/] {report.warning_count}"
    )

    if strict and not report.is_clean:
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# enrich
# ---------------------------------------------------------------------------


@app.command()
def enrich(
    seed: str = typer.Argument(..., help="Seed context phrase for synthetic generation."),
    category: str = typer.Option("hooplehopper_totality", "--category", "-c", help="Memory category."),
    n: int = typer.Option(3, "--count", "-n", help="Number of synthetic memories to generate."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSONL file path."),  # noqa: UP007
) -> None:
    """Run the synthetic enrichment agent to generate memory pressure."""
    settings = get_settings()
    _setup(settings)

    from vuorse_vortex.agents.synthetic_enrichment import SyntheticEnrichmentAgent
    from vuorse_vortex.models.memory_unit import MemoryCategory

    try:
        mem_category = MemoryCategory(category)
    except ValueError:
        err_console.print(
            f"[red]Invalid category:[/] {category!r}. "
            f"Valid values: {[c.value for c in MemoryCategory]}"
        )
        raise typer.Exit(code=1) from None

    agent = SyntheticEnrichmentAgent(
        model=settings.enrichment_model,
        temperature=settings.enrichment_temperature,
        max_tokens=settings.enrichment_max_tokens,
    )

    console.print(
        Panel(
            f"Generating [bold]{n}[/] synthetic memories\n"
            f"Category: [cyan]{category}[/]\n"
            f"Seed: [dim]{seed}[/]",
            title="Synthetic Enrichment Agent",
        )
    )

    units = asyncio.run(agent.generate(seed_context=seed, category=mem_category, n=n))

    for i, unit in enumerate(units, 1):
        console.print(f"\n[bold cyan][{i}][/] {unit.content}")

    if output:
        with output.open("w") as f:
            for unit in units:
                f.write(json.dumps(unit.to_jsonl_record()) + "\n")
        console.print(f"\n[green]✓ Written to {output}[/]")


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------


@app.command()
def query(
    text: str = typer.Argument(..., help="Query text to search the Velvet Archive."),
    n: int = typer.Option(5, "--results", "-n", help="Number of results to return."),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Vector backend: chromadb or qdrant."),  # noqa: UP007
) -> None:
    """Query the Velvet Archive vector store."""
    settings = get_settings()
    _setup(settings)

    backend_choice = VectorBackend(backend) if backend else settings.vector_backend

    console.print(
        Panel(
            f"[cyan]Query:[/] {text}\n[dim]Backend: {backend_choice.value}[/]",
            title="Velvet Archive — Query",
        )
    )

    # Scaffold: real query requires a running vector DB and embedding pipeline
    console.print(
        "[yellow]⚠ Query requires a running vector database and embedding pipeline.[/]\n"
        "Start ChromaDB or Qdrant, then run:\n"
        "  [dim]vortex ingest --embed manifests/sample_synthetic_memory.jsonl[/]\n"
        "before querying."
    )


# ---------------------------------------------------------------------------
# gpu-status
# ---------------------------------------------------------------------------


@app.command(name="gpu-status")
def gpu_status() -> None:
    """Check CUDA/GPU availability and device info."""
    settings = get_settings()
    _setup(settings)

    from vuorse_vortex.gpu import gpu_status_report

    report = gpu_status_report()

    table = Table(title="GPU Status", show_header=True)
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("CUDA Available", "[green]Yes[/]" if report["cuda_available"] else "[red]No[/]")
    table.add_row("Device Count", str(report["device_count"]))

    devices = report.get("devices", [])
    if isinstance(devices, list):
        for device in devices:
            if isinstance(device, dict):
                table.add_row(
                    f"GPU {device.get('index', '?')}",
                    f"{device.get('name', '?')} "
                    f"({device.get('total_memory_gb', '?')} GB, "
                    f"CUDA {device.get('compute_capability', '?')})",
                )

    console.print(table)

    if not report["cuda_available"]:
        console.print(
            "\n[yellow]⚠ No CUDA GPU detected.[/] "
            "VUORSE-VORTEX is designed for GPU-first operation.\n"
            "Embedding and inference will fall back to CPU with degraded performance."
        )


if __name__ == "__main__":
    app()
