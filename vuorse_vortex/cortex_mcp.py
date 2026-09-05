"""MCP stdio adapter for the VUORSE-VORTEX Cortex Satellite."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ToolAnnotations

from vuorse_vortex.cortex import CortexSatellite

server = Server("vuorse-cortex")
READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


@server.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_vuorse",
            description=(
                "Search the local VUORSE-VORTEX canon-aware corpus satellite. "
                "Every hit includes a source path and canon metadata; sealed layers are withheld."
            ),
            annotations=READ_ONLY_ANNOTATIONS,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "num_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10,
                    },
                    "layer": {"type": ["string", "null"], "default": None},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="vuorse_cortex_stats",
            description=(
                "Return the VUORSE-VORTEX satellite fingerprint, source and chunk counts, "
                "retrieval mode, and external embedding call count."
            ),
            annotations=READ_ONLY_ANNOTATIONS,
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    with CortexSatellite() as satellite:
        if name == "search_vuorse":
            query = str(arguments.get("query", "")).strip()
            if not query:
                raise ValueError("query must not be empty")
            num_results = max(1, min(int(arguments.get("num_results", 10)), 50))
            layer_value = arguments.get("layer")
            layer = str(layer_value) if layer_value is not None else None
            hits = satellite.search(query, top_k=num_results, layer=layer)
            payload = {
                "project": "VUORSE-VORTEX",
                "retrieval": "sqlite-fts5",
                "external_embedding_calls": 0,
                "hits": [asdict(hit) for hit in hits],
            }
        elif name == "vuorse_cortex_stats":
            payload = satellite.stats()
        else:
            raise ValueError(f"unknown tool: {name}")
    return [TextContent(type="text", text=json.dumps(payload, indent=2, sort_keys=True))]


async def _run_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()
