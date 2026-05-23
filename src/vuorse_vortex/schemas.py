"""Pydantic schemas for VUORSE memory records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Layer = Literal[
    "canon",
    "persona",
    "apocrypha",
    "ritual_logic",
    "roadmap_manifest",
    "hooplehopper_totality",
    "dialogue",
    "relationship_graph",
    "rule",
]

CanonStatus = Literal[
    "locked",
    "draft",
    "roadmap_private",
    "synthetic_behavioral",
    "non_canon_private",
    "poetic_private",
    "system_rule",
    "unknown",
]

Visibility = Literal[
    "public",
    "behavioral",
    "private_to_vuorse",
    "internal",
    "weaver_only",
]

EmbeddingWeight = Literal["low", "medium", "high", "critical"]


class Provenance(BaseModel):
    """Where a synthesized record came from, so the chaos lineage stays traceable.

    Root records (walled atoms, hand-authored canon) leave this absent. Chaos
    Engine outputs must populate it. ``generation`` is the recursion depth:
    walled atoms = 0, first crystallization = 1, an accept-and-recompound = 2,
    etc. The Weaver review loop can then refuse to accept records past a
    chosen depth without explicit acknowledgement.
    """

    model_config = ConfigDict(extra="forbid")

    parent_atom_ids: list[str] = Field(default_factory=list)
    generation: int = Field(default=0, ge=0)
    engine: str | None = None  # e.g. "ChaosEngine" — leaves room for future producers


class MemoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canon_status: CanonStatus
    visibility: Visibility
    tags: list[str] = Field(default_factory=list)
    source_file: str | None = None
    section: str | None = None
    source_confidence: str | None = None
    layer_affinity: Layer | None = None
    provenance: Provenance | None = None


class RetrievalMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: int = Field(ge=0, le=10)
    embedding_weight: EmbeddingWeight
    query_hints: list[str] = Field(default_factory=list)


class BehaviorPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    may_state_as_fact: bool
    may_use_for_voice: bool
    may_reveal_to_user: bool
    allowed_surface_form: str | None = None
    promotion_authority: str | None = None


class MemoryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    layer: Layer
    record_type: str
    title: str
    text: str
    metadata: MemoryMetadata
    retrieval: RetrievalMetadata
    behavior: BehaviorPolicy


@dataclass
class LoreAtom:
    concept: str
    layer_affinity: Layer
    tags: list[str]
    premise_fragment: str
    synthesis_fragment: str
    # Lineage. Walled atoms and other root sources leave parent_atom_ids empty
    # and generation=0. Chaos-engine-recompounded atoms carry the concepts of
    # their parents and one generation deeper than the deepest parent.
    parent_atom_ids: tuple[str, ...] = ()
    generation: int = 0
