"""Embedding pipeline for VUORSE-VORTEX.

GPU-first sentence embedding pipeline using sentence-transformers.
Supports batch processing of MemoryUnit objects into vector representations
for storage in ChromaDB or Qdrant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from vuorse_vortex.gpu import get_device
from vuorse_vortex.logging_utils import get_logger

if TYPE_CHECKING:
    from vuorse_vortex.models.memory_unit import MemoryUnit

logger = get_logger(__name__)


class EmbeddingPipeline:
    """Sentence embedding pipeline backed by a HuggingFace model.

    Lazy-loads the model on first use to avoid CUDA/import overhead at
    import time.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device_id: int = 0,
        require_cuda: bool = True,
        batch_size: int = 64,
    ) -> None:
        self.model_name = model_name
        self.batch_size = batch_size
        self._device = get_device(device_id=device_id, require_cuda=require_cuda)
        self._model: object | None = None

    def _load_model(self) -> None:
        """Lazy-load the sentence-transformers model onto the target device."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import]

            logger.info("Loading embedding model", model=self.model_name, device=self._device)
            self._model = SentenceTransformer(self.model_name, device=self._device)
            logger.info("Embedding model loaded", model=self.model_name)
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for the embedding pipeline. "
                "Install it with: uv sync"
            ) from exc

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text strings.

        Args:
            texts: Input texts to embed.

        Returns:
            List of embedding vectors (one per input text).
        """
        self._load_model()
        logger.info("Embedding texts", count=len(texts), batch_size=self.batch_size)

        results: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            vectors = self._model.encode(  # type: ignore[union-attr]
                batch,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            results.extend(v.tolist() for v in vectors)

        logger.info("Embedding complete", total=len(results))
        return results

    def embed_memory_units(self, units: list["MemoryUnit"]) -> list["MemoryUnit"]:
        """Embed a list of MemoryUnit objects, storing vectors in-place.

        Args:
            units: MemoryUnit objects to embed.

        Returns:
            The same units with .embedding populated.
        """
        texts = [u.content for u in units]
        vectors = self.embed_texts(texts)
        for unit, vector in zip(units, vectors, strict=True):
            unit.embedding = vector
        return units

    @property
    def device(self) -> str:
        """Return the resolved device string."""
        return self._device
