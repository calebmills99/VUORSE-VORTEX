#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vuorse-vortex",
# ]
# [tool.uv.sources]
# vuorse-vortex = { path = "..", editable = true }
# ///
"""End-to-end synthesize → validate → embed → query smoke run for VUORSE-VORTEX.

Drives the canonical pipeline against the configured vector backend. Honors
CORTEX_REQUIRE_GPU strict mode the same way the CLI does; if GPU is required
and missing, this exits non-zero with the standard "GPU tantrum" message.

Usage:
  CORTEX_REQUIRE_GPU=1 uv run scripts/run_synthetic_pipeline.py
  uv run scripts/run_synthetic_pipeline.py --output path/to/theses.jsonl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from vuorse_vortex.gpu import gpu_required, require_gpu
from vuorse_vortex.jsonl import iter_jsonl, validate_jsonl
from vuorse_vortex.settings import get_settings
from vuorse_vortex.synthesis import theses_as_jsonl
from vuorse_vortex.vector import get_backend

console = Console()
err_console = Console(stderr=True)


def _heading(text: str) -> None:
    console.print(f"\n[bold magenta]{text}[/bold magenta]")


def _doctor() -> None:
    _heading("VUORSE-VORTEX runtime check")
    if gpu_required():
        require_gpu("synthetic pipeline doctor")
        console.print("[green]CUDA available. VUORSE is not on strike.[/green]")
    else:
        console.print(
            "[yellow]CORTEX_REQUIRE_GPU is not set; running without GPU strict-mode "
            "enforcement.[/yellow]"
        )


def _synthesize(output: Path) -> None:
    _heading(f"Synthesizing seed theses → {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(theses_as_jsonl() + "\n", encoding="utf-8")
    console.print(f"[green]Wrote synthetic theses to:[/green] {output}")


def _validate(output: Path) -> None:
    _heading(f"Validating {output}")
    errors = validate_jsonl(output)
    if errors:
        for error in errors:
            err_console.print(f"[red]{error}[/red]")
        raise RuntimeError(f"validate_jsonl failed for {output}")
    console.print(f"[green]Valid JSONL:[/green] {output}")


def _embed(output: Path) -> int:
    _heading("Embedding theses into vector store")
    settings = get_settings()
    records = [obj for _, obj in iter_jsonl(output)]
    backend = get_backend(settings=settings)
    count = backend.ingest(records)
    console.print(
        f"[green]Ingested {count} records[/green] into backend "
        f"[cyan]{settings.vector_backend}[/cyan]."
    )
    return count


def _query_samples(samples: list[str], top_k: int) -> None:
    _heading("Sample queries")
    backend = get_backend()
    for sample in samples:
        console.print(f"\n[bold]query:[/bold] {sample}")
        results = backend.query(sample, top_k=top_k)
        if not results:
            console.print("  [yellow](no results)[/yellow]")
            continue
        for i, result in enumerate(results, start=1):
            console.print(
                f"  [cyan]#{i}[/cyan] (score {result.score:.4f}) "
                f"[dim]layer:[/dim] {result.layer} "
                f"[dim]id:[/dim] {result.record_id}"
            )
            console.print(f"    {result.text[:160]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("synthetic_enrichment/theses.jsonl"),
        help="JSONL output path for synthesized theses.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of results per sample query.",
    )
    args = parser.parse_args(argv)

    samples = ["velvet archive", "performance as survival"]

    try:
        _doctor()
        _synthesize(args.output)
        _validate(args.output)
        _embed(args.output)
        _query_samples(samples, top_k=args.top_k)
    except Exception as exc:
        err_console.print(f"\n[bold red]Pipeline failed:[/bold red] {exc}")
        return 1

    _heading("Pipeline complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
