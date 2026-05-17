"""Tests for the real ChromaDBBackend ingest/query path.

Skipped when ``chromadb`` or ``sentence-transformers`` are unavailable, and
when CUDA is unavailable — the backend enforces GPU strict mode internally.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from vuorse_vortex.gpu import cuda_available
from vuorse_vortex.settings import Settings
from vuorse_vortex.vector import ChromaDBBackend, QueryResult


@pytest.fixture
def chroma_backend(tmp_path: Path) -> ChromaDBBackend:
    pytest.importorskip("chromadb")
    pytest.importorskip("sentence_transformers")
    if not cuda_available():
        pytest.skip("CUDA unavailable; ChromaDBBackend requires GPU.")
    settings = Settings(
        vector_backend="chromadb",
        chromadb_path=str(tmp_path / "chromadb"),
        chromadb_collection="test_collection",
    )
    return ChromaDBBackend(settings=settings)


def _record(
    record_id: str,
    *,
    layer: str,
    text: str,
    canon_status: str = "synthetic_behavioral",
    visibility: str = "private_to_vuorse",
    tags: list[str] | None = None,
    priority: int = 5,
) -> dict[str, Any]:
    return {
        "id": record_id,
        "layer": layer,
        "record_type": "test",
        "title": f"title-{record_id}",
        "text": text,
        "metadata": {
            "canon_status": canon_status,
            "visibility": visibility,
            "tags": tags or [],
        },
        "retrieval": {
            "priority": priority,
            "embedding_weight": "low",
            "query_hints": [],
        },
        "behavior": {
            "may_state_as_fact": False,
            "may_use_for_voice": True,
            "may_reveal_to_user": False,
        },
    }


def test_ingest_then_query_returns_ranked_results(chroma_backend: ChromaDBBackend) -> None:
    records = [
        _record("rec-velvet", layer="persona", text="The velvet archive shelters performers."),
        _record("rec-cowboy", layer="canon", text="Jake walks the Wyoming ridge alone."),
        _record("rec-survive", layer="persona", text="Performance is a live backup of identity."),
    ]
    count = chroma_backend.ingest(records)
    assert count == 3

    results = chroma_backend.query("velvet archive memory", top_k=2)
    assert results, "expected at least one result for velvet archive query"
    assert all(isinstance(r, QueryResult) for r in results)
    assert results[0].record_id == "rec-velvet"


def test_query_filters_sealed_layers(chroma_backend: ChromaDBBackend) -> None:
    records = [
        _record("rec-sealed", layer="apocrypha", text="velvet archive private apocrypha entry"),
        _record("rec-open", layer="persona", text="velvet archive public-facing persona note"),
    ]
    chroma_backend.ingest(records)

    results = chroma_backend.query("velvet archive", top_k=5)
    layers = {r.layer for r in results}
    assert "apocrypha" not in layers
    assert any(r.record_id == "rec-open" for r in results)
