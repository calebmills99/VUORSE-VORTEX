"""Abstract base class for VUORSE-VORTEX vector database backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryResult:
    """A single result returned from a vector database query."""

    id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    category: str = ""
    visibility: str = "public"


class VectorDBBackend(ABC):
    """Abstract interface for vector database backends.

    All backends must support upsert, query, delete, and health-check operations.
    The canon firewall is enforced at this layer — sealed categories are never
    returned via query().
    """

    SEALED_CATEGORIES: frozenset[str] = frozenset({"roadmap_manifest"})

    @abstractmethod
    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Upsert memory units into the vector store.

        Args:
            ids: Unique IDs for each document.
            embeddings: Pre-computed embedding vectors.
            documents: Raw text content for each document.
            metadatas: Metadata dicts for each document.
        """

    @abstractmethod
    async def query(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[QueryResult]:
        """Query the vector store for similar documents.

        Sealed categories are automatically excluded from results.

        Args:
            embedding: Query embedding vector.
            n_results: Maximum number of results to return.
            where: Optional metadata filter.

        Returns:
            List of QueryResult objects, sorted by similarity score (desc).
        """

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        """Delete memory units by ID.

        Args:
            ids: IDs of documents to delete.
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the backend is healthy and reachable."""

    def _filter_sealed(self, results: list[QueryResult]) -> list[QueryResult]:
        """Remove sealed categories from query results (canon firewall enforcement)."""
        return [r for r in results if r.category not in self.SEALED_CATEGORIES]
