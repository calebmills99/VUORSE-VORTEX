"""Vector database backend abstraction for VUORSE-VORTEX retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field

from vuorse_vortex.settings import Settings, get_settings


@dataclass
class QueryResult:
    """A single retrieval result from the vector store."""

    record_id: str
    text: str
    score: float
    layer: str
    metadata: dict = field(default_factory=dict)


class VectorDBBackend:
    """Abstract vector DB backend that enforces canon firewall on queries.

    SEALED_CATEGORIES are sourced from Settings.sealed_categories so that
    changes to sealed categories are centralized and consistently enforced
    across ingest and query layers.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def sealed_categories(self) -> set[str]:
        """Sealed categories sourced from centralized settings."""
        return set(self._settings.sealed_categories)

    def query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        """Query the vector store and filter out sealed-layer results.

        Subclasses should override _raw_query to implement backend-specific
        retrieval. This method applies canon firewall filtering automatically.
        """
        results = self._raw_query(text, top_k=top_k + len(self.sealed_categories) * 2)
        filtered = [r for r in results if r.layer not in self.sealed_categories]
        return filtered[:top_k]

    def _raw_query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        """Backend-specific query implementation. Override in subclasses."""
        return []

    def ingest(self, records: list[dict]) -> int:
        """Ingest records into the vector store. Returns count ingested."""
        return 0


class ChromaDBBackend(VectorDBBackend):
    """ChromaDB-backed vector retrieval (requires GPU extras)."""

    def _raw_query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        try:
            import chromadb  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is not installed. Install with: uv sync --extra gpu"
            ) from exc
        # Actual chromadb query would go here once collection is configured
        return []


class FaissBackend(VectorDBBackend):
    """FAISS-backed vector retrieval (requires GPU extras)."""

    def _raw_query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        try:
            import faiss  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "faiss-cpu is not installed. Install with: uv sync --extra gpu"
            ) from exc
        # Actual FAISS query would go here once index is loaded
        return []


def get_backend(settings: Settings | None = None) -> VectorDBBackend:
    """Return the configured vector backend based on Settings."""
    settings = settings or get_settings()
    backends = {
        "chromadb": ChromaDBBackend,
        "faiss": FaissBackend,
    }
    backend_cls = backends.get(settings.vector_backend, VectorDBBackend)
    return backend_cls(settings=settings)
