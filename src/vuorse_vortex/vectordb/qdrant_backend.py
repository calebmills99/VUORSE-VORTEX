"""Qdrant vector database backend for VUORSE-VORTEX."""

from __future__ import annotations

import asyncio
from typing import Any

from vuorse_vortex.logging_utils import get_logger
from vuorse_vortex.vectordb.base import QueryResult, VectorDBBackend

logger = get_logger(__name__)


class QdrantBackend(VectorDBBackend):
    """Qdrant backend for the Velvet Archive vector store.

    Supports both local Qdrant instances and Qdrant Cloud via API key.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "vortex_memories",
        api_key: str | None = None,
        embedding_dimension: int = 384,
    ) -> None:
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.api_key = api_key
        self.embedding_dimension = embedding_dimension
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazy-initialize the Qdrant client and ensure the collection exists."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient  # type: ignore[import]
                from qdrant_client.models import Distance, VectorParams  # type: ignore[import]

                url = f"http://{self.host}:{self.port}"
                self._client = QdrantClient(url=url, api_key=self.api_key, timeout=30)

                collections = [c.name for c in self._client.get_collections().collections]
                if self.collection_name not in collections:
                    self._client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dimension,
                            distance=Distance.COSINE,
                        ),
                    )
                    logger.info("Qdrant collection created", collection=self.collection_name)

                logger.info(
                    "Qdrant client initialized",
                    url=url,
                    collection=self.collection_name,
                )
            except ImportError as exc:
                raise ImportError(
                    "qdrant-client is required for the Qdrant backend. Install with: uv sync"
                ) from exc
        return self._client

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Upsert documents into the Qdrant collection."""
        from qdrant_client.models import PointStruct  # type: ignore[import]

        client = self._get_client()
        points = [
            PointStruct(
                id=i,
                vector=emb,
                payload={**meta, "content": doc, "_str_id": str_id},
            )
            for i, (str_id, emb, doc, meta) in enumerate(
                zip(ids, embeddings, documents, metadatas, strict=True)
            )
        ]
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.upsert(collection_name=self.collection_name, points=points),
        )
        logger.info("Qdrant upsert complete", count=len(points))

    async def query(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[QueryResult]:
        """Query Qdrant for similar documents."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue  # type: ignore[import]

        client = self._get_client()
        query_filter = None
        if where:
            must_conditions = [
                FieldCondition(key=k, match=MatchValue(value=v)) for k, v in where.items()
            ]
            query_filter = Filter(must=must_conditions)

        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(
            None,
            lambda: client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=n_results,
                query_filter=query_filter,
                with_payload=True,
            ),
        )

        results: list[QueryResult] = []
        for hit in raw:
            payload = hit.payload or {}
            results.append(
                QueryResult(
                    id=payload.get("_str_id", str(hit.id)),
                    content=payload.get("content", ""),
                    score=hit.score,
                    metadata={k: v for k, v in payload.items() if k not in ("content", "_str_id")},
                    category=payload.get("category", ""),
                    visibility=payload.get("visibility_rules", "public"),
                )
            )

        return self._filter_sealed(results)

    async def delete(self, ids: list[str]) -> None:
        """Delete documents from Qdrant by string ID."""
        from qdrant_client.models import Filter, FieldCondition, MatchAny  # type: ignore[import]

        client = self._get_client()
        delete_filter = Filter(
            must=[FieldCondition(key="_str_id", match=MatchAny(any=ids))]
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: client.delete(
                collection_name=self.collection_name,
                points_selector=delete_filter,
            ),
        )
        logger.info("Qdrant delete complete", count=len(ids))

    async def health_check(self) -> bool:
        """Return True if Qdrant is reachable."""
        try:
            client = self._get_client()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, client.get_collections)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant health check failed", error=str(exc))
            return False
