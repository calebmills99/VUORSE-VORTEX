"""Vector database backend abstraction for VUORSE-VORTEX retrieval."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from vuorse_vortex.gpu import require_gpu
from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.settings import Settings, get_settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


@dataclass
class QueryResult:
    """A single retrieval result from the vector store."""

    record_id: str
    text: str
    score: float
    layer: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _normalize_record(record: dict[str, Any] | MemoryRecord) -> dict[str, Any]:
    """Accept either a ``MemoryRecord`` or a raw dict; return a dict."""
    if isinstance(record, MemoryRecord):
        return record.model_dump(mode="json", exclude_none=True)
    return record


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
        Results are best-effort: if filtering removes sealed records, fewer
        than top_k records may be returned.
        """
        results = self._raw_query(text, top_k=top_k + len(self.sealed_categories) * 2)
        filtered = [r for r in results if r.layer not in self.sealed_categories]
        return filtered[:top_k]

    def _raw_query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        """Backend-specific query implementation. Override in subclasses."""
        return []

    def ingest(self, records: Sequence[dict[str, Any] | MemoryRecord]) -> int:
        """Ingest records into the vector store. Returns count ingested."""
        return 0


class ChromaDBBackend(VectorDBBackend):
    """ChromaDB-backed vector retrieval (requires GPU extras)."""

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__(settings=settings)
        self._client: Any | None = None
        self._collection: Any | None = None
        self._encoder: SentenceTransformer | None = None

    def _get_collection(self) -> Any:
        if self._collection is not None:
            return self._collection
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is not installed. Install with: uv sync --extra gpu"
            ) from exc
        self._client = chromadb.PersistentClient(path=self._settings.chromadb_path)
        self._collection = self._client.get_or_create_collection(
            name=self._settings.chromadb_collection,
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    def _get_encoder(self) -> SentenceTransformer:
        if self._encoder is not None:
            return self._encoder
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install with: uv sync --extra gpu"
            ) from exc
        self._encoder = SentenceTransformer(self._settings.embedding_model, device="cuda")
        return self._encoder

    def _encode(self, texts: list[str]) -> list[list[float]]:
        encoder = self._get_encoder()
        vectors = encoder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [vec.tolist() for vec in vectors]

    def ingest(self, records: Sequence[dict[str, Any] | MemoryRecord]) -> int:
        require_gpu("chromadb ingest")
        if not records:
            return 0

        normalized = [_normalize_record(r) for r in records]
        ids = [str(r["id"]) for r in normalized]
        documents = [str(r["text"]) for r in normalized]
        metadatas: list[dict[str, Any]] = []
        for r in normalized:
            meta = r.get("metadata") or {}
            retrieval = r.get("retrieval") or {}
            metadatas.append(
                {
                    "layer": r.get("layer", "unknown"),
                    "canon_status": meta.get("canon_status", "unknown"),
                    "visibility": meta.get("visibility", "internal"),
                    "tags": json.dumps(meta.get("tags", [])),
                    "priority": int(retrieval.get("priority", 0)),
                }
            )

        embeddings = self._encode(documents)
        collection = self._get_collection()
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    def _raw_query(self, text: str, top_k: int = 5) -> list[QueryResult]:
        require_gpu("chromadb vector query")
        collection = self._get_collection()
        query_embedding = self._encode([text])[0]
        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        ids = (raw.get("ids") or [[]])[0]
        docs = (raw.get("documents") or [[]])[0]
        dists = (raw.get("distances") or [[]])[0]
        metas = (raw.get("metadatas") or [[]])[0]

        results: list[QueryResult] = []
        for record_id, doc, dist, meta in zip(ids, docs, dists, metas, strict=False):
            meta_dict: dict[str, Any] = dict(meta or {})
            layer = str(meta_dict.get("layer", "unknown"))
            score = 1.0 - float(dist)
            results.append(
                QueryResult(
                    record_id=str(record_id),
                    text=str(doc or ""),
                    score=score,
                    layer=layer,
                    metadata=meta_dict,
                )
            )
        return results


class FaissBackend(VectorDBBackend):
    """FAISS-backed vector retrieval — NOT IMPLEMENTED.

    Previously this class accepted ``ingest()`` calls and silently returned 0,
    while ``_raw_query()`` returned ``[]`` — meaning users who selected the
    FAISS backend saw "Ingested N records" messages but nothing was ever
    persisted or retrievable. That was a silent data-loss bug.

    The class is preserved as a tombstone so the import surface stays stable
    and the slot for a real FAISS implementation is reserved. Constructing it
    raises immediately; ``get_backend()`` will never produce one because
    ``Settings.vector_backend`` is now narrowed to ``Literal["chromadb"]``.
    """

    _UNSUPPORTED_MESSAGE = (
        "FaissBackend is not implemented. Use vector_backend='chromadb'. "
        "If you need FAISS, implement real ingest() and _raw_query() against a "
        "persisted faiss index before re-enabling it in Settings.VectorBackendName."
    )

    def __init__(self, settings: Settings | None = None) -> None:
        raise NotImplementedError(self._UNSUPPORTED_MESSAGE)


def get_backend(settings: Settings | None = None) -> VectorDBBackend:
    """Return the configured vector backend based on Settings.

    Only ``chromadb`` is supported. ``Settings.vector_backend`` is typed as
    ``Literal["chromadb"]``, so Pydantic validation rejects anything else
    before reaching this function — but we defend in depth in case a caller
    bypasses Settings validation (e.g. by constructing a backend dict directly
    or by setting an attribute on an already-constructed Settings instance).
    """
    settings = settings or get_settings()
    backend_name = settings.vector_backend
    if backend_name == "chromadb":
        return ChromaDBBackend(settings=settings)
    raise ValueError(
        f"Unsupported vector backend: {backend_name!r}. "
        "Only 'chromadb' is implemented; see FaissBackend tombstone for details."
    )
