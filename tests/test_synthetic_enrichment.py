"""Tests for synthetic enrichment agent."""

from __future__ import annotations

import pytest

from vuorse_vortex.agents.synthetic_enrichment import SyntheticEnrichmentAgent
from vuorse_vortex.models.memory_unit import CanonStatus, MemoryCategory, MemoryUnit, VisibilityRule


class TestSyntheticEnrichmentAgent:
    def setup_method(self):
        self.agent = SyntheticEnrichmentAgent()

    @pytest.mark.asyncio
    async def test_generate_returns_memory_units(self):
        units = await self.agent.generate(
            seed_context="Threshold crossing memory",
            category=MemoryCategory.HOOPLEHOPPER_TOTALITY,
            n=2,
        )
        assert len(units) == 2
        for unit in units:
            assert isinstance(unit, MemoryUnit)

    @pytest.mark.asyncio
    async def test_generated_units_are_synthetic(self):
        units = await self.agent.generate(
            seed_context="Velvet Archive founding",
            n=1,
        )
        unit = units[0]
        assert unit.canon_status == CanonStatus.SYNTHETIC

    @pytest.mark.asyncio
    async def test_generated_units_are_restricted(self):
        units = await self.agent.generate(
            seed_context="Erasure event",
            n=1,
        )
        unit = units[0]
        assert unit.visibility_rules == VisibilityRule.RESTRICTED

    @pytest.mark.asyncio
    async def test_generated_units_not_synthesizable(self):
        """Synthetic memories must not allow second-order synthesis."""
        units = await self.agent.generate(seed_context="Test seed", n=1)
        unit = units[0]
        assert unit.behavioral_permissions.synthesizable is False

    @pytest.mark.asyncio
    async def test_generate_multiple_unique_ids(self):
        units = await self.agent.generate(seed_context="Unique IDs test", n=3)
        ids = [u.id for u in units]
        assert len(set(ids)) == 3  # all unique

    @pytest.mark.asyncio
    async def test_enrich_corpus(self):
        seed_units = [
            MemoryUnit(category=MemoryCategory.CANON, content=f"Canon memory {i}.")
            for i in range(5)
        ]
        synthetic = await self.agent.enrich_corpus(seed_units, enrichment_ratio=0.4)
        assert len(synthetic) >= 1
        for unit in synthetic:
            assert unit.canon_status == CanonStatus.SYNTHETIC

    @pytest.mark.asyncio
    async def test_generate_tags_applied(self):
        units = await self.agent.generate(
            seed_context="Timeline displacement",
            tags=["displacement", "hooplehopper"],
            n=1,
        )
        unit = units[0]
        assert "synthetic" in unit.metadata.tags

    @pytest.mark.asyncio
    async def test_generate_all_categories(self):
        for category in MemoryCategory:
            units = await self.agent.generate(
                seed_context="Category test",
                category=category,
                n=1,
            )
            assert units[0].category == category
