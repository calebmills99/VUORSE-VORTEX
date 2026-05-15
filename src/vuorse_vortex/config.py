"""Configuration management for VUORSE-VORTEX."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorBackend(str, Enum):
    CHROMADB = "chromadb"
    QDRANT = "qdrant"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VORTEX_",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    archive_name: str = Field(default="velvet-archive", description="Name of the active archive instance")
    universe_layer: str = Field(default="slayverse-prime", description="Active universe layer identifier")

    # --- Vector DB ---
    vector_backend: VectorBackend = Field(default=VectorBackend.CHROMADB, description="Vector database backend")
    chromadb_host: str = Field(default="localhost", description="ChromaDB host")
    chromadb_port: int = Field(default=8000, description="ChromaDB port")
    chromadb_collection: str = Field(default="vortex_memories", description="ChromaDB collection name")
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection: str = Field(default="vortex_memories", description="Qdrant collection name")
    qdrant_api_key: str | None = Field(default=None, description="Qdrant API key (cloud)")

    # --- Embedding ---
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model identifier",
    )
    embedding_batch_size: int = Field(default=64, description="Batch size for embedding inference")
    embedding_device: str = Field(default="cuda", description="Torch device (cuda / cpu)")
    embedding_dimension: int = Field(default=384, description="Output embedding dimension")

    # --- GPU ---
    require_cuda: bool = Field(default=True, description="Enforce CUDA availability; fail if absent")
    cuda_device_id: int = Field(default=0, description="CUDA device index")

    # --- Synthetic Enrichment ---
    enrichment_temperature: float = Field(default=0.85, description="Sampling temperature for synthetic generation")
    enrichment_max_tokens: int = Field(default=512, description="Max tokens for synthetic memory generation")
    enrichment_model: str = Field(default="mistralai/Mistral-7B-Instruct-v0.2", description="LLM for enrichment")

    # --- Canon Firewall ---
    sealed_categories: list[str] = Field(
        default=["roadmap_manifest"],
        description="Memory categories that must never be exposed via public query interfaces",
    )
    firewall_strict_mode: bool = Field(default=True, description="Reject rather than warn on firewall violations")

    # --- Paths ---
    manifests_dir: Path = Field(default=Path("manifests"), description="Directory for JSONL manifests")
    output_dir: Path = Field(default=Path("output"), description="Output directory for generated files")

    # --- Logging ---
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(default="json", description="Log format: json or console")


def get_settings() -> Settings:
    """Return the global settings singleton."""
    return Settings()
