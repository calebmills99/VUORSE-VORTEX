"""Centralized configuration for VUORSE-VORTEX."""

from __future__ import annotations

from pydantic import BaseModel, Field


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

    vector_backend: str = Field(
        default="chromadb",
        description="Vector DB backend to use for retrieval (chromadb or faiss).",
    )

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformer model name for embeddings.",
    )


def get_settings() -> Settings:
    """Return the current application settings."""
    return Settings()
