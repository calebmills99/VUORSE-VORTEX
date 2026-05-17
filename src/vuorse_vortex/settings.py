"""Centralized configuration for VUORSE-VORTEX."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

VectorBackendName = Literal["chromadb", "faiss"]


class Settings(BaseModel):
    """Application-wide settings with centralized sealed category definitions.

    The sealed_categories list defines which layers are subject to canon firewall
    rules. Records in these layers must have may_state_as_fact=False and
    may_reveal_to_user=False.
    """

    sealed_categories: list[str] = Field(
        default=["apocrypha", "roadmap_manifest", "hooplehopper_totality"],
        description="Layers subject to canon firewall enforcement.",
    )

    vector_backend: VectorBackendName = Field(
        default="chromadb",
        description="Vector DB backend to use for retrieval (chromadb or faiss).",
    )

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformer model name for embeddings.",
    )

    chromadb_path: str = Field(
        default="embeddings/indexes/chromadb",
        description="On-disk path for the persistent ChromaDB client.",
    )

    chromadb_collection: str = Field(
        default="vuorse_memory",
        description="Collection name used inside the ChromaDB store.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the current application settings."""
    return Settings()


def clear_settings() -> None:
    """Clear cached settings, primarily for tests."""
    get_settings.cache_clear()
