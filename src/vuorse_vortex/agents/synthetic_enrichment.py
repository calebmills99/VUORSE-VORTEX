"""Synthetic Enrichment Agent.

Generates memory pressure — plausible but non-canon behavioral subtext
that enriches retrieval without polluting verified continuity.

All synthetic memories are tagged:
  - canon_status: synthetic
  - visibility_rules: restricted
  - behavioral_permissions.synthesizable: False (no second-order synthesis)

The agent operates as an async scaffold that can be connected to any
compatible LLM inference backend.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from vuorse_vortex.logging_utils import get_logger
from vuorse_vortex.models.memory_unit import (
    BehavioralPermissions,
    CanonStatus,
    MemoryCategory,
    MemoryUnit,
    MemoryUnitMetadata,
    VisibilityRule,
)

logger = get_logger(__name__)

# Enrichment prompt template
ENRICHMENT_PROMPT_TEMPLATE = """\
You are a synthetic memory archivant for the Velvet Archive — the distributed
anti-erasure repository of the Slayverse universe.

Your task: generate a plausible, atmospheric synthetic memory unit for the
category: {category}

This memory should:
- Feel like a fragment of erased or displaced history
- Enrich the retrieval landscape without contradicting verified canon
- Use the tone of the Slayverse: queer archival aesthetics, mythic register,
  haunted and precise
- Be 2-4 sentences maximum
- Reference concrete sensory or behavioral details
- NOT contradict or claim to be verified canon

Seed context: {seed_context}

Generate only the memory text, nothing else.
"""


class SyntheticEnrichmentAgent:
    """Async agent that generates synthetic memory units for the Velvet Archive.

    The agent scaffold supports pluggable LLM backends (local or API).
    In scaffold mode (default), it generates structured placeholder memories.
    """

    def __init__(
        self,
        model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        temperature: float = 0.85,
        max_tokens: int = 512,
        author: str = "synthetic-enrichment-agent",
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.author = author

    async def generate(
        self,
        seed_context: str,
        category: MemoryCategory = MemoryCategory.HOOPLEHOPPER_TOTALITY,
        tags: list[str] | None = None,
        universe_layer: str = "slayverse-prime",
        n: int = 1,
    ) -> list[MemoryUnit]:
        """Generate synthetic memory units from a seed context.

        Args:
            seed_context: Brief description or anchor phrase to seed the generation.
            category: Memory category for the synthetic units.
            tags: Optional semantic tags.
            universe_layer: Universe layer identifier.
            n: Number of synthetic memories to generate.

        Returns:
            List of MemoryUnit objects with canon_status=synthetic.
        """
        logger.info(
            "Synthetic enrichment agent generating memories",
            category=category.value,
            n=n,
            seed=seed_context[:80],
        )

        units = []
        for i in range(n):
            content = await self._generate_content(seed_context, category, i)
            unit = self._build_memory_unit(
                content=content,
                category=category,
                seed_context=seed_context,
                tags=tags or [],
                universe_layer=universe_layer,
            )
            units.append(unit)

        logger.info("Synthetic enrichment complete", generated=len(units))
        return units

    async def _generate_content(
        self,
        seed_context: str,
        category: MemoryCategory,
        index: int,
    ) -> str:
        """Generate a single synthetic memory text.

        In scaffold mode, returns a structured placeholder. Connect a real
        LLM backend by overriding this method.
        """
        # Scaffold implementation — replace with real LLM call
        templates = [
            (
                f"A displaced memory surfaces: somewhere in the {category.value} stratum, "
                f"an echo of '{seed_context[:40]}' persists — fragmented, but recognizable "
                "to those who know how to listen. The Velvet Archive notes its presence."
            ),
            (
                f"The Archive registers a behavioral trace: someone carrying the signature "
                f"of '{seed_context[:40]}' passed through this timeline. No name. "
                "No timestamp. Only the texture of movement, preserved."
            ),
            (
                f"In the margins of the {category.value} record, a fragment: "
                f"'{seed_context[:50]}...' — the kind of memory that doesn't announce itself "
                "but accumulates, quietly, until retrieval becomes inevitable."
            ),
        ]
        return templates[index % len(templates)]

    def _build_memory_unit(
        self,
        content: str,
        category: MemoryCategory,
        seed_context: str,
        tags: list[str],
        universe_layer: str,
    ) -> MemoryUnit:
        """Construct a synthetic MemoryUnit with enforced synthetic constraints."""
        return MemoryUnit(
            id=str(uuid.uuid4()),
            category=category,
            content=content,
            metadata=MemoryUnitMetadata(
                author=self.author,
                source=f"synthetic-enrichment:{seed_context[:60]}",
                universe_layer=universe_layer,
                created_at=datetime.now(timezone.utc),
                tags=["synthetic", *tags],
                provenance="SyntheticEnrichmentAgent v0.1",
            ),
            retrieval_hints=[seed_context[:60], *tags],
            behavioral_permissions=BehavioralPermissions(
                retrievable=True,
                embeddable=True,
                synthesizable=False,  # No second-order synthesis
                shareable=False,
                mutable=False,
                erasable=True,
            ),
            visibility_rules=VisibilityRule.RESTRICTED,
            canon_status=CanonStatus.SYNTHETIC,
        )

    async def enrich_corpus(
        self,
        seed_units: list[MemoryUnit],
        enrichment_ratio: float = 0.3,
        universe_layer: str = "slayverse-prime",
    ) -> list[MemoryUnit]:
        """Generate synthetic enrichment for an existing corpus.

        Generates approximately enrichment_ratio * len(seed_units) synthetic memories,
        using existing memory content as seed context.

        Args:
            seed_units: Existing MemoryUnit objects to derive seeds from.
            enrichment_ratio: Fraction of input corpus to generate as synthetic.
            universe_layer: Universe layer for generated units.

        Returns:
            List of new synthetic MemoryUnit objects.
        """
        n_to_generate = max(1, int(len(seed_units) * enrichment_ratio))
        all_synthetic: list[MemoryUnit] = []

        for i, seed_unit in enumerate(seed_units[:n_to_generate]):
            seed_context = seed_unit.content[:100]
            synthetic = await self.generate(
                seed_context=seed_context,
                category=seed_unit.category,
                tags=seed_unit.retrieval_hints[:3],
                universe_layer=universe_layer,
                n=1,
            )
            all_synthetic.extend(synthetic)

        logger.info(
            "Corpus enrichment complete",
            seed_count=len(seed_units),
            synthetic_count=len(all_synthetic),
        )
        return all_synthetic
