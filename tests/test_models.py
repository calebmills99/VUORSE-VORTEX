"""Tests for core Pydantic models."""

from __future__ import annotations

import pytest

from vuorse_vortex.models.memory_unit import (
    BehavioralPermissions,
    CanonStatus,
    MemoryCategory,
    MemoryUnit,
    MemoryUnitMetadata,
    VisibilityRule,
)
from vuorse_vortex.models.hooplehopper import (
    HooplehopperIdentity,
    HooplehopperTimeline,
    TimelineStatus,
)
from vuorse_vortex.models.ritual import RitualLogic, RitualPhase, RitualStep, TransmissionMode
from vuorse_vortex.models.persona import Persona, PersonaAffiliation, PersonaState


# ---------------------------------------------------------------------------
# MemoryUnit
# ---------------------------------------------------------------------------


class TestMemoryUnit:
    def test_basic_creation(self):
        unit = MemoryUnit(
            category=MemoryCategory.CANON,
            content="The Velvet Archive endures.",
        )
        assert unit.id  # UUID4 assigned
        assert unit.category == MemoryCategory.CANON
        assert unit.content == "The Velvet Archive endures."
        assert unit.visibility_rules == VisibilityRule.PUBLIC
        assert unit.canon_status == CanonStatus.VERIFIED

    def test_roadmap_manifest_always_sealed(self):
        """roadmap_manifest must auto-seal visibility."""
        unit = MemoryUnit(
            category=MemoryCategory.ROADMAP_MANIFEST,
            content="Future plans.",
            visibility_rules=VisibilityRule.PUBLIC,  # attempt to set public
        )
        assert unit.visibility_rules == VisibilityRule.SEALED

    def test_roadmap_manifest_void_preserved(self):
        """roadmap_manifest with VOID visibility should stay VOID."""
        unit = MemoryUnit(
            category=MemoryCategory.ROADMAP_MANIFEST,
            content="Void memory.",
            visibility_rules=VisibilityRule.VOID,
        )
        assert unit.visibility_rules == VisibilityRule.VOID

    def test_synthetic_downgrade_visibility(self):
        """Synthetic memories with PUBLIC visibility downgrade to RESTRICTED."""
        unit = MemoryUnit(
            category=MemoryCategory.APOCRYPHA,
            content="A synthetic fragment.",
            canon_status=CanonStatus.SYNTHETIC,
            visibility_rules=VisibilityRule.PUBLIC,
        )
        assert unit.visibility_rules == VisibilityRule.RESTRICTED

    def test_is_publicly_queryable_true(self):
        unit = MemoryUnit(
            category=MemoryCategory.CANON,
            content="Public canon memory.",
            visibility_rules=VisibilityRule.PUBLIC,
        )
        assert unit.is_publicly_queryable() is True

    def test_is_publicly_queryable_roadmap(self):
        """roadmap_manifest is never publicly queryable."""
        unit = MemoryUnit(
            category=MemoryCategory.ROADMAP_MANIFEST,
            content="Secret roadmap.",
        )
        assert unit.is_publicly_queryable() is False

    def test_is_publicly_queryable_not_retrievable(self):
        unit = MemoryUnit(
            category=MemoryCategory.CANON,
            content="Non-retrievable.",
            behavioral_permissions=BehavioralPermissions(retrievable=False),
        )
        assert unit.is_publicly_queryable() is False

    def test_to_jsonl_record_excludes_embedding(self):
        unit = MemoryUnit(
            category=MemoryCategory.CANON,
            content="Test content.",
            embedding=[0.1, 0.2, 0.3],
        )
        record = unit.to_jsonl_record()
        assert "embedding" not in record
        assert record["content"] == "Test content."

    def test_category_string_coercion(self):
        unit = MemoryUnit(category="canon", content="String category test.")
        assert unit.category == MemoryCategory.CANON

    def test_empty_content_rejected(self):
        with pytest.raises(Exception):
            MemoryUnit(category=MemoryCategory.CANON, content="")

    def test_metadata_vorst_threat_level_bounds(self):
        with pytest.raises(Exception):
            MemoryUnitMetadata(vorst_threat_level=11)
        with pytest.raises(Exception):
            MemoryUnitMetadata(vorst_threat_level=-1)

    def test_all_categories_accepted(self):
        for category in MemoryCategory:
            unit = MemoryUnit(category=category, content="Category test.")
            assert unit.category == category


# ---------------------------------------------------------------------------
# HooplehopperIdentity
# ---------------------------------------------------------------------------


class TestHooplehopperIdentity:
    def test_basic_creation(self):
        identity = HooplehopperIdentity(
            hooplehopper_id="hop-001",
            name="Cerulean-7",
        )
        assert identity.hooplehopper_id == "hop-001"
        assert identity.name == "Cerulean-7"
        assert identity.timelines == []

    def test_active_timeline_count(self):
        identity = HooplehopperIdentity(
            hooplehopper_id="hop-002",
            timelines=[
                HooplehopperTimeline(timeline_id="t1", status=TimelineStatus.PRESENT),
                HooplehopperTimeline(timeline_id="t2", status=TimelineStatus.ERASED),
                HooplehopperTimeline(timeline_id="t3", status=TimelineStatus.ECHOING),
                HooplehopperTimeline(timeline_id="t4", status=TimelineStatus.DISPLACED),
            ],
        )
        assert identity.active_timeline_count() == 2  # PRESENT + ECHOING

    def test_erased_timeline_count(self):
        identity = HooplehopperIdentity(
            hooplehopper_id="hop-003",
            timelines=[
                HooplehopperTimeline(timeline_id="t1", status=TimelineStatus.ERASED),
                HooplehopperTimeline(timeline_id="t2", status=TimelineStatus.ERASED),
                HooplehopperTimeline(timeline_id="t3", status=TimelineStatus.PRESENT),
            ],
        )
        assert identity.erased_timeline_count() == 2

    def test_totality_confidence_bounds(self):
        with pytest.raises(Exception):
            HooplehopperIdentity(hooplehopper_id="x", totality_confidence=1.5)


# ---------------------------------------------------------------------------
# RitualLogic
# ---------------------------------------------------------------------------


class TestRitualLogic:
    def test_basic_ritual(self):
        ritual = RitualLogic(
            ritual_id="rite-001",
            name="Threshold Rite",
            purpose="Preserve crossing memory",
        )
        assert ritual.ritual_id == "rite-001"
        assert ritual.hardened_step_count() == 0  # no steps yet

    def test_hardened_step_count(self):
        ritual = RitualLogic(
            ritual_id="rite-002",
            name="Embodied Rite",
            purpose="Test",
            steps=[
                RitualStep(
                    order=0,
                    phase=RitualPhase.INVOCATION,
                    description="Invoke",
                    transmission_mode=TransmissionMode.EMBODIED,
                    anti_erasure_weight=0.9,
                ),
                RitualStep(
                    order=1,
                    phase=RitualPhase.ENACTMENT,
                    description="Enact",
                    transmission_mode=TransmissionMode.ORAL,
                    anti_erasure_weight=0.3,
                ),
            ],
        )
        assert ritual.hardened_step_count() == 1


# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------


class TestPersona:
    def test_basic_persona(self):
        persona = Persona(
            persona_id="persona-001",
            name="The Archivist",
            affiliation=PersonaAffiliation.VELVET_ARCHIVE,
        )
        assert persona.persona_id == "persona-001"
        assert persona.is_erased() is False

    def test_erased_persona(self):
        persona = Persona(
            persona_id="persona-002",
            name="Lost One",
            state=PersonaState.ERASED,
        )
        assert persona.is_erased() is True
        assert persona.recovery_possible() is False  # no continuity anchors

    def test_recovery_possible_with_anchors(self):
        persona = Persona(
            persona_id="persona-003",
            name="Recoverable",
            state=PersonaState.ERASED,
            continuity_anchors=["event-001", "ritual-rite-001"],
        )
        assert persona.recovery_possible() is True

    def test_displaced_recovery_with_anchors(self):
        persona = Persona(
            persona_id="persona-004",
            name="Displaced",
            state=PersonaState.DISPLACED,
            continuity_anchors=["anchor-001"],
        )
        assert persona.recovery_possible() is True

    def test_vorst_threat_bounds(self):
        with pytest.raises(Exception):
            Persona(persona_id="p", name="X", vorst_threat_assessment=1.5)
