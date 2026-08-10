# Stub implementation of the VUORSE-VORTEX semantic graph utilities.

"""graphd – placeholder for full LSP/semantic index builder.

The real implementation lives in the upstream repository and provides
functions to construct a symbol graph from the LSP index.  For now we
expose minimal stubs so that the CLI `vuorse-vortex index` command can
run without raising `ModuleNotFoundError`.

Both functions simply log their action; the heavy‑lifting will be added
later when the full graph builder is merged.
"""

from rich.console import Console

console = Console()


def build_graph() -> None:
    """Build the semantic graph from scratch.

    In the full implementation this would invoke the LSP indexer,
    parse symbols, apply the canon firewall, and persist a SQLite cache.
    Here we only emit a log message so downstream commands succeed.
    """
    console.print("[yellow]Stub build_graph called – no real index built.[/yellow]")


def refresh_graph() -> None:
    """Refresh an existing graph.

    The real version would diff the current source tree against the
    cached graph and incrementally update nodes/edges.  The stub simply
    logs its invocation.
    """
    console.print("[yellow]Stub refresh_graph called – cache not updated.[/yellow]")
