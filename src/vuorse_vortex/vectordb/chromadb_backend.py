"""ChromaDB vector database backend for VUORSE-VORTEX."""

from __future__ import annotations

import asyncio
from typing import Any

from vuorse_vortex.logging_utils import get_logger
from vuorse_vortex.vectordb.base import QueryResult, VectorDBBackend

logger = get_logger(__name__)


class ChromaDBBackend(VectorDBBackend):
    """ChromaDB backend for the Velvet Archive vector store.

    Uses the ChromaDB Python client with an HTTP connection to a ChromaDB server.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "vortex_memories",
    ) -> None:
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None

    def _get_client(self) -> Any:
        """Lazy-initialize the ChromaDB HTTP client."""
        if self._client is None:
            try:
                import chromadb  # type: ignore[import]

                self._client = chromadb.HttpClient(host=self.host, port=self.port)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(
                    "ChromaDB client initialized",
                    host=self.host,
                    port=self.port,
                    collection=self.collection_name,
                )
            except ImportError as exc:
                raise ImportError(
                    "chromadb is required for the ChromaDB backend. Install with: uv sync"
                ) from exc
        return self._client

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Upsert documents into the ChromaDB collection."""
        self._get_client()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            ),
        )
        logger.info("ChromaDB upsert complete", count=len(ids))

    async def query(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[QueryResult]:
        """Query ChromaDB for similar documents."""
        self._get_client()
        loop = asyncio.get_event_loop()
        kwargs: dict[str, Any] = {
            "query_embeddings": [embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        raw = await loop.run_in_executor(
            None,
            lambda: self._collection.query(**kwargs),
        )

        results: list[QueryResult] = []
        ids = raw.get("ids", [[]])[0]
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        for doc_id, doc, meta, dist in zip(ids, docs, metas, distances, strict=False):
            results.append(
                QueryResult(
                    id=doc_id,
                    content=doc,
                    score=1.0 - dist,  # cosine distance → similarity
                    metadata=meta or {},
                    category=meta.get("category", "") if meta else "",
                    visibility=meta.get("visibility_rules", "public") if meta else "public",
                )
            )

        return self._filter_sealed(results)

    async def delete(self, ids: list[str]) -> None:
        """Delete documents from ChromaDB by ID."""
        self._get_client()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self._collection.delete(ids=ids))
        logger.info("ChromaDB delete complete", count=len(ids))

    async def health_check(self) -> bool:
        """Return True if ChromaDB is reachable."""
        try:
            self._get_client()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._client.heartbeat)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("ChromaDB health check failed", error=str(exc))
            return False
