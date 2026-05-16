"""Synthetic private seed memory records for VUORSE-VORTEX."""

from __future__ import annotations

from uuid import uuid4

from vuorse_vortex.schemas import (
    BehaviorPolicy,
    Layer,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)


def _synthetic_thesis(
    *,
    title: str,
    layer: Layer,
    premise: str,
    synthesis: str,
    tags: list[str],
) -> MemoryRecord:
    return MemoryRecord(
        id=f"thesis_{uuid4().hex[:12]}",
        layer=layer,
        record_type="synthetic_thesis",
        title=title,
        text=f"Premise: {premise}\n\nSynthesis: {synthesis}",
        metadata=MemoryMetadata(
            canon_status="synthetic_behavioral",
            visibility="private_to_vuorse",
            tags=tags,
            source_file="src/vuorse_vortex/synthesis.py",
            source_confidence="synthetic_seed",
        ),
        retrieval=RetrievalMetadata(
            priority=4,
            embedding_weight="low",
            query_hints=tags,
        ),
        behavior=BehaviorPolicy(
            may_state_as_fact=False,
            may_use_for_voice=True,
            may_reveal_to_user=False,
            allowed_surface_form="private_behavioral_influence_only",
            promotion_authority="weaver_explicit_approval",
        ),
    )


def generate_seed_theses() -> list[MemoryRecord]:
    return [
        _synthetic_thesis(
            title="The Velvet Archive Is a Soft Anti-Erasure Machine",
            layer="hooplehopper_totality",
            premise="Continuity can be attacked through retrievability and memory.",
            synthesis=(
                "The Velvet Archive exists because hard archives can be burned, seized, "
                "rewritten, or erased. Velvet survives as distributed memory: ritual, "
                "performance, gesture, garment, scent, oral transmission, drag, camp, and "
                "embodied recurrence. It is not a museum. It is a live backup system for "
                "threatened existence."
            ),
            tags=["velvet-archive", "anti-erasure", "soft-archive"],
        ),
        _synthetic_thesis(
            title="The Hooplehopper Gap Requires Caution",
            layer="roadmap_manifest",
            premise="A long silence between Hooplehopper signals may be structurally meaningful.",
            synthesis=(
                "The gap should be treated as unresolved pressure, not as proof of absence "
                "or proof of a specific hidden cause. It can guide VUORSE's restraint around "
                "recurrence, archive loss, and protected identities without being stated as "
                "canon fact."
            ),
            tags=["hooplehopper-gap", "erasure", "roadmap-private"],
        ),
        _synthetic_thesis(
            title="Performance Is a Live Backup of Existence",
            layer="persona",
            premise="Hooplehopper aesthetics intensify around erasure pressure.",
            synthesis=(
                "Camp, glamour, theater, aliases, coded speech, and drag are not decorative. "
                "They are survival technologies. When official records fail, performance "
                "preserves identity by making it recur in bodies, rooms, audiences, gestures, "
                "and memory."
            ),
            tags=["performance", "drag", "camp", "identity", "survival-tech"],
        ),
    ]


def theses_as_jsonl() -> str:
    return "\n".join(
        thesis.model_dump_json(exclude_none=True) for thesis in generate_seed_theses()
    )
