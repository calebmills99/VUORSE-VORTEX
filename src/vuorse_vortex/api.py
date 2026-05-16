from __future__ import annotations

from typing import Any

from fastapi import FastAPI

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
