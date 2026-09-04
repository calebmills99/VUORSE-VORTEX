"""VUORSE-VORTEX CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.prompt import Prompt

from vuorse_vortex.debrief_import import extract_strongest_private_theses
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
vast_app = typer.Typer(help="Vast.ai billing insurance: status, cost, teardown.")
app.add_typer(vast_app, name="vast")
console = Console()

_DEFAULT_THESES_PATH = Path("synthetic_enrichment/theses.jsonl")
_DEFAULT_ACCEPTED_THESES_PATH = Path("synthetic_enrichment/theses_accepted.jsonl")
_EMBED_PATH_ARGUMENT = typer.Argument(
    _DEFAULT_THESES_PATH,
    help="JSONL file of MemoryRecord rows to embed and ingest.",
)

_DEFAULT_WALLED_MD = Path("hooplehopper_totality/debriefing_walled.md")
_DEFAULT_WALLED_JSONL = Path("hooplehopper_totality/debriefing_walled.jsonl")
_DEFAULT_DEBRIEF_IMPORT_SOURCE = Path("hooplehopper_totality/debriefing_walled.jsonl")
_DEFAULT_DEBRIEF_IMPORT_OUTPUT = Path("synthetic_enrichment/private_debrief_theses.jsonl")
_DEFAULT_CONVERT_JSONL_OUTPUT = Path("converted.jsonl")
_BUILD_WALLED_MD_ARGUMENT = typer.Argument(
    _DEFAULT_WALLED_MD,
    help="Walled markdown source file.",
)
_BUILD_WALLED_JSONL_ARGUMENT = typer.Argument(
    _DEFAULT_WALLED_JSONL,
    help="JSONL projection target file.",
)
_FIREWALL_PATH_ARGUMENT = typer.Argument(
    ...,
    help="JSONL file to validate against the canon firewall.",
)
_CONVERT_INPUT_PATH_ARGUMENT = typer.Argument(
    ...,
    help="Legacy JSONL file to clean.",
)
_CONVERT_OUTPUT_PATH_OPTION = typer.Option(
    _DEFAULT_CONVERT_JSONL_OUTPUT,
    "--output",
    help="Destination path for cleaned JSONL.",
)
_INDEX_REFRESH_OPTION = typer.Option(
    False,
    "--refresh",
    help="Re-build the full semantic graph.",
)
_IMPORT_DEBRIEF_SOURCE_ARGUMENT = typer.Argument(
    _DEFAULT_DEBRIEF_IMPORT_SOURCE,
    help="Debrief JSONL source to distill into strongest private theses.",
)
_IMPORT_DEBRIEF_OUTPUT_OPTION = typer.Option(
    _DEFAULT_DEBRIEF_IMPORT_OUTPUT,
    "--output",
    help="Target MemoryRecord JSONL path.",
)
_IMPORT_DEBRIEF_LIMIT_OPTION = typer.Option(
    12,
    "--limit",
    min=1,
    help="Number of strongest theses to keep.",
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


@app.command("import-debrief")
def import_debrief_cmd(
    session_path: Annotated[
        Path,
        typer.Option(
            "--session",
            help="Frolic session JSON used to resolve the debrief source.",
        ),
    ] = Path(".frolic-session.json"),
    source_path: Annotated[
        Path | None,
        typer.Option(
            "--source",
            help="Explicit debrief markdown source. Overrides session resolution.",
        ),
    ] = None,
    output_path: Annotated[
        Path | None,
        typer.Option("--output", help="Destination MemoryRecord JSONL path."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            min=1,
            help="Maximum strongest debrief theses to import.",
        ),
    ] = 8,
) -> None:
    """Import private debrief theses into validated MemoryRecord JSONL."""
    from vuorse_vortex.debrief_import import import_debrief_theses

    try:
        result = import_debrief_theses(
            session_path=session_path,
            source_path=source_path,
            output_path=output_path,
            limit=limit,
        )
    except Exception as exc:
        console.print(f"[red]Debrief import failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Imported {result.record_count} private theses[/green]")
    console.print(f"[cyan]Source:[/cyan] {result.source_path}")
    console.print(f"[cyan]Output:[/cyan] {result.output_path}")


@app.command("firewall")
def firewall_cmd(path: Path = _FIREWALL_PATH_ARGUMENT) -> None:
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
    input_path: Path = _CONVERT_INPUT_PATH_ARGUMENT,
    output_path: Path = _CONVERT_OUTPUT_PATH_OPTION,
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



@app.command("import-debrief-theses")
def import_debrief_theses(
    source: Path = _IMPORT_DEBRIEF_SOURCE_ARGUMENT,
    output: Path = _IMPORT_DEBRIEF_OUTPUT_OPTION,
    limit: int = _IMPORT_DEBRIEF_LIMIT_OPTION,
) -> None:
    """Create repo-native private thesis imports from a debrief JSONL artifact."""
    try:
        records = extract_strongest_private_theses(source, output, limit=limit)
    except (OSError, ValueError) as exc:
        console.print(f"[red]Import failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    errors = validate_jsonl(output)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Imported {len(records)} private theses:[/green] {output} "
        f"from [cyan]{source}[/cyan]"
    )


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

@app.command("index")
def index(refresh: bool = _INDEX_REFRESH_OPTION) -> None:
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


_BUILD_INDEX_WHAT_OPTION = typer.Option(
    "all",
    "--what",
    help="Which index to build: sources, entities, relationships, or all.",
)
_BUILD_INDEX_CHECK_OPTION = typer.Option(
    False,
    "--check",
    help="Verify indexes are current; exit non-zero if drifted. Writes nothing.",
)
_BUILD_INDEX_PDF_OPTION = typer.Option(
    False,
    "--include-pdf",
    help="Index derived PDF renders alongside their markdown sources.",
)
_BUILD_INDEX_FINALE_OPTION = typer.Option(
    False,
    "--include-finale",
    help="Walk roadmap/finale/. Private roadmap scope; withheld by default.",
)


@app.command("build-index")
def build_index_cmd(
    what: str = _BUILD_INDEX_WHAT_OPTION,
    check: bool = _BUILD_INDEX_CHECK_OPTION,
    include_pdf: bool = _BUILD_INDEX_PDF_OPTION,
    include_finale: bool = _BUILD_INDEX_FINALE_OPTION,
) -> None:
    """Build corpus source manifest, entity index, and relationship index."""
    from vuorse_vortex.indexing import (
        ENTITY_INDEX_OUT,
        RELATIONSHIP_INDEX_OUT,
        SOURCE_MANIFEST_OUT,
        IndexingError,
        build_entity_index,
        build_relationship_index,
        build_source_manifest,
        is_current,
    )

    choices = {"sources", "entities", "relationships", "all"}
    if what not in choices:
        console.print(f"[red]Unknown --what value:[/red] {what}. Choose from {sorted(choices)}.")
        raise typer.Exit(code=1)

    targets = {"sources", "entities", "relationships"} if what == "all" else {what}
    out = None if check else "write"
    drifted: list[Path] = []

    try:
        if "sources" in targets:
            manifest, report = build_source_manifest(
                out_path=None if out is None else SOURCE_MANIFEST_OUT,
                include_pdf=include_pdf,
                include_finale=include_finale,
            )
            console.print(
                f"[bold magenta]Sources[/bold magenta] scanned {report.scanned}, "
                f"indexed {report.entries} "
                f"([yellow]{report.sealed_entries} sealed[/yellow])"
            )
            for path in report.unrouted:
                console.print(f"  [yellow]unrouted:[/yellow] {path}")
            for path in report.mixed_files:
                console.print(f"  [red]mixed privacy posture:[/red] {path}")
            for note in report.stale_paths:
                console.print(f"  [yellow]stale:[/yellow] {note}")
            if check and not is_current(SOURCE_MANIFEST_OUT, manifest):
                drifted.append(SOURCE_MANIFEST_OUT)

        if "entities" in targets:
            entity_index = build_entity_index(
                out_path=None if out is None else ENTITY_INDEX_OUT
            )
            console.print(
                f"[bold magenta]Entities[/bold magenta] {entity_index['entity_count']}, "
                f"surface forms {entity_index['surface_form_count']}, "
                f"distinctive tokens {entity_index['distinctive_token_count']}"
            )
            for line in entity_index["repairs_applied"]:
                console.print(f"  [cyan]repaired:[/cyan] {line}")
            for token in entity_index["ambiguous_tokens"]:
                console.print(f"  [yellow]ambiguous token:[/yellow] {token}")
            if check and not is_current(ENTITY_INDEX_OUT, entity_index):
                drifted.append(ENTITY_INDEX_OUT)

        if "relationships" in targets:
            rel_index = build_relationship_index(
                out_path=None if out is None else RELATIONSHIP_INDEX_OUT
            )
            console.print(
                f"[bold magenta]Relationships[/bold magenta] {rel_index['edge_count']} edges, "
                f"{rel_index['dangling_count']} dangling"
            )
            for edge in rel_index["dangling_edges"]:
                console.print(
                    f"  [red]dangling:[/red] {edge['from']} -> {edge['to']} "
                    f"(missing {', '.join(edge['missing'])})"
                )
            if rel_index["dangling_related_count"]:
                console.print(
                    f"  [yellow]{rel_index['dangling_related_count']} 'related' refs "
                    "point at entities that do not exist:[/yellow]"
                )
                for eid, missing in rel_index["dangling_related"].items():
                    console.print(f"    [yellow]{eid}[/yellow] -> {', '.join(missing)}")
            if check and not is_current(RELATIONSHIP_INDEX_OUT, rel_index):
                drifted.append(RELATIONSHIP_INDEX_OUT)
    except IndexingError as exc:
        console.print(f"[red]Index build failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if check:
        if drifted:
            for path in drifted:
                console.print(f"[red]Drifted:[/red] {path} is not current with its sources.")
            raise typer.Exit(code=1)
        console.print("[green]All requested indexes are up to date.[/green]")
        return

    console.print("[green]Indexes written to manifests/corpus/.[/green]")


# --------------------------------------------------------------------------- #
# Vast.ai billing insurance                                                    #
# --------------------------------------------------------------------------- #

_VAST_ANY_ACCOUNT_OPTION = typer.Option(
    False,
    "--any-account",
    help="Skip the VUORSE_VAST_ACCOUNT guard and act on whatever account is authenticated.",
)
_VAST_STRICT_OPTION = typer.Option(
    False,
    "--strict",
    help="Exit non-zero when anything is still rented, not just when it is dead.",
)
_VAST_YES_OPTION = typer.Option(
    False,
    "--yes",
    help="Actually destroy. Without this the command only reports what it would destroy.",
)
_VAST_IDS_ARGUMENT = typer.Argument(
    None,
    help="Instance ids to destroy. Omit to target every dead-but-billing instance.",
)


def _vast_account_banner(any_account: bool) -> None:
    """Print auth provenance and account identity. Never prints the key."""
    from vuorse_vortex.vast import api_key_source, assert_expected_account, fetch_vast_user

    console.print(f"[dim]auth source:[/dim] {api_key_source()}")
    user = fetch_vast_user() if any_account else assert_expected_account()
    console.print(
        f"[dim]account:[/dim] {user.get('email') or '<unknown>'} "
        f"id={user.get('id')} credit={user.get('credit')}"
    )


@vast_app.command("status")
def vast_status(
    any_account: bool = _VAST_ANY_ACCOUNT_OPTION,
    strict: bool = _VAST_STRICT_OPTION,
) -> None:
    """List rented instances with burn rate and accrued cost.

    Exits 2 when an instance is dead but still billing, or, with --strict,
    when anything at all is still rented.
    """
    from vuorse_vortex.vast import (
        VastError,
        dead_instances,
        list_instances,
        total_burn_rate,
    )

    try:
        _vast_account_banner(any_account)
        instances = list_instances()
    except VastError as exc:
        console.print(f"[red]Vast check failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if not instances:
        console.print("[green]No Vast instances. Nothing is billing.[/green]")
        return

    burn = total_burn_rate(instances)
    console.print(
        f"[bold magenta]{len(instances)} instance(s)[/bold magenta] "
        f"burning [yellow]${burn:.4f}/hr[/yellow]"
    )
    for inst in instances:
        style = "red" if inst.is_dead else "cyan"
        console.print(f"[{style}]{inst.describe()}[/{style}]")

    dead = dead_instances(instances)
    if dead:
        console.print(
            f"\n[red]{len(dead)} instance(s) exited but still rented.[/red] "
            "The container died; the meter did not. Run: "
            "[bold]vuorse-vortex vast destroy[/bold]"
        )
        raise typer.Exit(code=2)
    if strict:
        console.print("\n[yellow]--strict: instances are still rented.[/yellow]")
        raise typer.Exit(code=2)


@vast_app.command("destroy")
def vast_destroy(
    ids: list[str] = _VAST_IDS_ARGUMENT,
    yes: bool = _VAST_YES_OPTION,
    any_account: bool = _VAST_ANY_ACCOUNT_OPTION,
) -> None:
    """Destroy instances. Dry-run by default; --yes commits.

    With no ids, targets every instance that has exited while still rented.
    """
    from vuorse_vortex.vast import (
        VastError,
        dead_instances,
        destroy_ids,
        list_instances,
    )

    try:
        _vast_account_banner(any_account)
        instances = list_instances()
    except VastError as exc:
        console.print(f"[red]Vast lookup failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    by_id = {inst.id: inst for inst in instances}
    if ids:
        unknown = [i for i in ids if i not in by_id]
        if unknown:
            console.print(f"[red]No such instance on this account:[/red] {', '.join(unknown)}")
            raise typer.Exit(code=1)
        targets = [by_id[i] for i in ids]
    else:
        targets = dead_instances(instances)

    if not targets:
        console.print("[green]Nothing to destroy.[/green]")
        return

    console.print(f"[bold]Would destroy {len(targets)} instance(s):[/bold]")
    for inst in targets:
        console.print(f"[yellow]{inst.describe()}[/yellow]")

    if not yes:
        console.print(
            "\n[yellow]Dry run. Nothing was destroyed.[/yellow] "
            "Re-run with [bold]--yes[/bold] to commit."
        )
        return

    try:
        destroyed = destroy_ids([inst.id for inst in targets], dry_run=False)
    except VastError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Destroyed {len(destroyed)} instance(s):[/green] {', '.join(destroyed)}")
