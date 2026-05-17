"""End-to-end embed → query smoke run for VUORSE-VORTEX against an approved manifest.

Drives the embed + sample-query stages of the pipeline against the configured
vector backend. Synthesis and validation no longer happen here — those are CPU
work that runs locally via the ``synthesize-interactive`` HIL on the dev box.
The on-Vast script consumes the reviewed JSONL pointed at by the
``VUORSE_APPROVED_MANIFEST`` environment variable and refuses to start without
it.

Honors CORTEX_REQUIRE_GPU strict mode the same way the CLI does; if GPU is
required and missing, this exits non-zero with the standard "GPU tantrum"
message.

This is NOT a PEP 723 standalone script — it imports from vuorse_vortex and is
intended to run inside the project environment (where torch + sentence-transformers
+ chromadb are installed). On Vast.ai that env is /venv/main; ``uv run`` picks
it up automatically when UV_PROJECT_ENVIRONMENT points there.

Usage:
  export VUORSE_APPROVED_MANIFEST=synthetic_enrichment/theses_accepted.jsonl
  CORTEX_REQUIRE_GPU=1 uv run scripts/run_synthetic_pipeline.py
  uv run scripts/run_synthetic_pipeline.py --top-k 5
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console

from vuorse_vortex.gpu import gpu_required, require_gpu
from vuorse_vortex.jsonl import iter_jsonl, validate_jsonl
from vuorse_vortex.settings import get_settings
from vuorse_vortex.vector import get_backend

console = Console()
err_console = Console(stderr=True)

MANIFEST_ENV_VAR = "VUORSE_APPROVED_MANIFEST"
_REFUSAL_BANNER = "[bold red]GPU pipeline refused:[/bold red]"
_PRODUCER_HINT = (
    "Run `uv run vuorse-vortex synthesize-interactive` locally to produce a "
    "reviewed JSONL, then set "
    f"`{MANIFEST_ENV_VAR}=<path>` before invoking this script."
)


def _heading(text: str) -> None:
    console.print(f"\n[bold magenta]{text}[/bold magenta]")


def _refuse(reason: str) -> None:
    err_console.print(f"\n{_REFUSAL_BANNER} {reason}")
    err_console.print(_PRODUCER_HINT)


def _resolve_manifest() -> Path | None:
    raw = os.environ.get(MANIFEST_ENV_VAR)
    if raw is None or not raw.strip():
        _refuse(
            f"{MANIFEST_ENV_VAR} is not set. No manifest, no embed."
        )
        return None

    manifest = Path(raw).expanduser()
    if not manifest.is_file():
        _refuse(
            f"{MANIFEST_ENV_VAR}={raw!s} does not point at an existing file."
        )
        return None

    try:
        errors = validate_jsonl(manifest)
    except Exception as exc:
        err_console.print(
            f"\n{_REFUSAL_BANNER} {MANIFEST_ENV_VAR}={raw!s} could not be parsed "
            f"as JSONL: {exc}"
        )
        err_console.print(_PRODUCER_HINT)
        return None

    if errors:
        err_console.print(
            f"\n{_REFUSAL_BANNER} {MANIFEST_ENV_VAR}={raw!s} failed validate_jsonl:"
        )
        for error in errors:
            err_console.print(f"  [red]{error}[/red]")
        err_console.print(_PRODUCER_HINT)
        return None

    record_count = sum(1 for _ in iter_jsonl(manifest))
    if record_count == 0:
        _refuse(
            f"{MANIFEST_ENV_VAR}={raw!s} contains zero JSONL records. "
            "No manifest, no embed."
        )
        return None

    return manifest


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


def _embed(manifest: Path) -> int:
    _heading(f"Embedding approved manifest → {manifest}")
    settings = get_settings()
    records = [obj for _, obj in iter_jsonl(manifest)]
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
        "--top-k",
        type=int,
        default=3,
        help="Number of results per sample query.",
    )
    args = parser.parse_args(argv)

    manifest = _resolve_manifest()
    if manifest is None:
        return 1

    samples = ["velvet archive", "performance as survival"]

    try:
        _doctor()
        _embed(manifest)
        _query_samples(samples, top_k=args.top_k)
    except Exception as exc:
        err_console.print(f"\n[bold red]Pipeline failed:[/bold red] {exc}")
        return 1

    _heading("Pipeline complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
