from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from vuorse_vortex import cortex_mcp
from vuorse_vortex.cortex import CortexSatellite


def test_mcp_catalog_names_project_tools() -> None:
    tools = asyncio.run(cortex_mcp.list_tools())
    assert [tool.name for tool in tools] == ["search_vuorse", "vuorse_cortex_stats"]


def test_mcp_search_returns_provenance(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = tmp_path / "project"
    source = root / "canon" / "characters" / "oracle.md"
    source.parent.mkdir(parents=True)
    source.write_text("Miss Slaytonia VUORSE guards the velvet gate.", encoding="utf-8")
    db_path = tmp_path / "satellite.sqlite3"
    with CortexSatellite(db_path) as satellite:
        satellite.build(base=root, roots=("canon",), chunk_chars=240)

    monkeypatch.setattr(cortex_mcp, "CortexSatellite", lambda: CortexSatellite(db_path))
    content = asyncio.run(
        cortex_mcp.call_tool("search_vuorse", {"query": "Slaytonia VUORSE", "num_results": 3})
    )
    payload = json.loads(content[0].text)

    assert payload["project"] == "VUORSE-VORTEX"
    assert payload["external_embedding_calls"] == 0
    assert payload["hits"][0]["source_path"] == "canon/characters/oracle.md"
