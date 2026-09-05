from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, Query

from vuorse_vortex.cortex import CortexSatellite

app = FastAPI(
    title="VUORSE-VORTEX",
    description="Escape velocity toward omniscience.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "status": "online",
        "system": "VUORSE-VORTEX",
        "message": "Slay Mode ∞ engaged",
    }


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/cortex/search")
def cortex_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(10, ge=1, le=50),
    layer: str | None = None,
) -> dict[str, Any]:
    """Search project sources locally, with sealed layers always withheld."""
    with CortexSatellite() as satellite:
        hits = satellite.search(q, top_k=top_k, layer=layer)
    return {
        "project": "VUORSE-VORTEX",
        "retrieval": "sqlite-fts5",
        "external_embedding_calls": 0,
        "hits": [asdict(hit) for hit in hits],
    }


@app.get("/cortex/stats")
def cortex_stats() -> dict[str, Any]:
    """Report project-local satellite identity and corpus counts."""
    with CortexSatellite() as satellite:
        return satellite.stats()
