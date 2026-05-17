"""Synthetic private seed memory records for VUORSE-VORTEX."""

from __future__ import annotations

import asyncio
import random
import json
from pathlib import Path
from dataclasses import dataclass
from uuid import uuid4

from vuorse_vortex.schemas import (
    BehaviorPolicy,
    EmbeddingWeight,
    Layer,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)


@dataclass
class LoreAtom:
    concept: str
    layer_affinity: Layer
    tags: list[str]
    premise_fragment: str
    synthesis_fragment: str


LORE_ATOM_POOL: list[LoreAtom] = [
    LoreAtom(
        concept="velvet archive",
        layer_affinity="hooplehopper_totality",
        tags=["velvet-archive", "anti-erasure", "soft-archive"],
        premise_fragment="Continuity can be attacked through retrievability and memory.",
        synthesis_fragment="Velvet survives as distributed memory: ritual, performance, gesture, garment, scent, oral transmission, drag, camp, and embodied recurrence.",
    ),
    LoreAtom(
        concept="hooplehopper gap",
        layer_affinity="roadmap_manifest",
        tags=["hooplehopper-gap", "erasure", "roadmap-private"],
        premise_fragment="A long silence between Hooplehopper signals may be structurally meaningful.",
        synthesis_fragment="The gap should be treated as unresolved pressure, not as proof of absence or proof of a specific hidden cause.",
    ),
    LoreAtom(
        concept="performance as survival",
        layer_affinity="persona",
        tags=["performance", "drag", "camp", "identity", "survival-tech"],
        premise_fragment="Hooplehopper aesthetics intensify around erasure pressure.",
        synthesis_fragment="Camp, glamour, theater, aliases, coded speech, and drag are not decorative. They are survival technologies.",
    ),
    LoreAtom(
        concept="soul-line recurrence",
        layer_affinity="canon",
        tags=["soul-line", "recurrence", "hooplehopper"],
        premise_fragment="Blood reproduces. The soul-line recurs.",
        synthesis_fragment="The Hooplehoppers do not descend. They return. Their recurrence shapes the pattern of emergence.",
    ),
    LoreAtom(
        concept="ritual as memory",
        layer_affinity="ritual_logic",
        tags=["ritual", "memory", "embodied-recurrence"],
        premise_fragment="Ritual operates where official history has been scrubbed.",
        synthesis_fragment="Repetition of the rite acts as a structural anchor, keeping the memory alive through embodied action rather than recorded word.",
    ),
    LoreAtom(
        concept="silence as wound",
        layer_affinity="apocrypha",
        tags=["silence", "wound", "wyoming", "jake"],
        premise_fragment="The silence around Jake's mother and the wound beneath his ranch are fundamentally linked.",
        synthesis_fragment="Unspoken truths manifest geographically. The containment instinct and denial actively sustain the wound's presence.",
    ),
    LoreAtom(
        concept="distributed continuity",
        layer_affinity="hooplehopper_totality",
        tags=["continuity", "distributed", "velvet"],
        premise_fragment="Centralized archives are vulnerable to complete eradication.",
        synthesis_fragment="A distributed network of artifacts and living memories ensures that when one node falls, the pattern survives elsewhere.",
    ),
    LoreAtom(
        concept="archive loss pressure",
        layer_affinity="roadmap_manifest",
        tags=["archive-loss", "erasure", "roadmap-private"],
        premise_fragment="The loss of the Archive exerts a gravitational pull on all surrounding entities.",
        synthesis_fragment="This pressure creates a vacuum that accelerates Hooplehopper activity and heightens the stakes of any recorded transmission.",
    ),
    LoreAtom(
        concept="embodied transmission",
        layer_affinity="persona",
        tags=["embodied", "oral-transmission", "gesture"],
        premise_fragment="When records fail, performance preserves identity.",
        synthesis_fragment="Identity recurs in bodies, rooms, audiences, gestures, and memory. The physical act of transmission is the archive itself.",
    ),
    LoreAtom(
        concept="cosmological contamination",
        layer_affinity="canon",
        tags=["cosmology", "contamination", "wyoming"],
        premise_fragment="The ground itself has absorbed the fallout of the cosmological schism.",
        synthesis_fragment="It is not just a spatial location; the contaminated soil re-radiates the trauma, affecting behavior, weather, and sound.",
    ),
    LoreAtom(
        concept="119-year extermination event",
        layer_affinity="hooplehopper_totality",
        tags=["lineage-gap", "extermination", "hooplehopper"],
        premise_fragment="The 119-year gap in the Hooplehopper lineage was not a coincidence or a fading out.",
        synthesis_fragment="It was a targeted, cosmological extermination event meant to sever the Thread and silence the Archive permanently.",
    ),
]


def load_canon_atoms() -> list[LoreAtom]:
    canon_file = Path("canon/slayverse_md_records_clean.jsonl")
    atoms = []
    if not canon_file.exists():
        return atoms
        
    try:
        with open(canon_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    concept = record.get("title") or record.get("document_title") or "Unknown"
                    summary = record.get("summary", "")
                    text = record.get("text", "")
                    
                    premise = summary[:500] if summary else text[:500]
                    synthesis = text[:500]
                    
                    if not premise or not synthesis:
                        continue
                        
                    tags = record.get("metadata", {}).get("tags", [])
                    if not isinstance(tags, list):
                        tags = []
                        
                    atoms.append(LoreAtom(
                        concept=concept.lower().strip(),
                        layer_affinity="canon",
                        tags=["canon"] + tags,
                        premise_fragment=premise.strip(),
                        synthesis_fragment=synthesis.strip(),
                    ))
                except Exception:
                    continue
    except Exception:
        pass
        
    return atoms

def get_initial_pool() -> list[LoreAtom]:
    return list(LORE_ATOM_POOL) + load_canon_atoms()


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


_SEED_0_THESES: list[MemoryRecord] = [
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


@dataclass
class SynthesisConfig:
    seed: int
    n_records: int = 5
    chaos_factor: float = 0.3
    layer_weights: dict[str, float] | None = None
    embedding_weight_bias: EmbeddingWeight = "low"


class ChaosField:
    def __init__(self, rng: random.Random, chaos_factor: float, pool: list[LoreAtom]):
        self.displacement: dict[str, float] = {}
        for atom in pool:
            self.add_atom(atom, rng, chaos_factor)
            
    def add_atom(self, atom: LoreAtom, rng: random.Random, chaos_factor: float):
        self.displacement[atom.concept] = rng.uniform(-chaos_factor, chaos_factor)


class AtomSampler:
    def __init__(self, config: SynthesisConfig, chaos_field: ChaosField, rng: random.Random, pool: list[LoreAtom]):
        self.config = config
        self.chaos_field = chaos_field
        self.rng = rng
        self.pool = pool

    def sample_atoms(self, exclude: set[str]) -> list[LoreAtom]:
        weights = self.config.layer_weights or {}
        
        available_atoms = []
        effective_weights = []
        for atom in self.pool:
            if atom.concept in exclude:
                continue
            base_weight = weights.get(atom.layer_affinity, 1.0)
            noise = self.chaos_field.displacement.get(atom.concept, 0.0)
            effective_weight = max(0.01, base_weight + noise)
            
            available_atoms.append(atom)
            effective_weights.append(effective_weight)
        
        # We need to pick 2 to 4 atoms without replacement
        num_to_pick = self.rng.randint(2, min(4, len(available_atoms)))
        picked_atoms = []
        
        # Since random.choices is with replacement, we loop and exclude manually
        for _ in range(num_to_pick):
            if not available_atoms:
                break
            chosen = self.rng.choices(available_atoms, weights=effective_weights, k=1)[0]
            picked_atoms.append(chosen)
            
            idx = available_atoms.index(chosen)
            available_atoms.pop(idx)
            effective_weights.pop(idx)

        return picked_atoms


class RecordCrystallizer:
    def crystallize(
        self, atoms: list[LoreAtom], seed: int, record_index: int, config: SynthesisConfig, rng: random.Random
    ) -> MemoryRecord:
        premise_anchor = atoms[0]
        synthesis_driver = atoms[1]
        
        # Compute effective weight for retrieval priority (without noise or with noise? Spec says: "derive from the premise anchor's effective weight, capped at 6")
        # I'll just recalculate without noise or pass it down. Let's just use layer weight.
        base_weight = (config.layer_weights or {}).get(premise_anchor.layer_affinity, 1.0)
        effective_layer_weight = max(0.01, base_weight)
        priority = min(6, round(effective_layer_weight * 2))
        
        tags = set()
        for atom in atoms:
            tags.update(atom.tags)
            
        record_id = f"chaos_{seed}_{record_index}_{rng.getrandbits(32):08x}"
        title = f"{premise_anchor.concept.title()} / {synthesis_driver.concept.title()}"
        text = f"Premise: {premise_anchor.premise_fragment}\n\nSynthesis: {synthesis_driver.synthesis_fragment}"
        
        return MemoryRecord(
            id=record_id,
            layer=premise_anchor.layer_affinity,
            record_type="synthetic_thesis",
            title=title,
            text=text,
            metadata=MemoryMetadata(
                canon_status="synthetic_behavioral",
                visibility="private_to_vuorse",
                tags=list(tags),
                source_file="src/vuorse_vortex/synthesis.py",
                source_confidence="synthetic_seed",
            ),
            retrieval=RetrievalMetadata(
                priority=priority,
                embedding_weight=config.embedding_weight_bias,
                query_hints=list(tags),
            ),
            behavior=BehaviorPolicy(
                may_state_as_fact=False,
                may_use_for_voice=True,
                may_reveal_to_user=False,
                allowed_surface_form="private_behavioral_influence_only",
                promotion_authority="weaver_explicit_approval",
            ),
        )


class ChaosEngine:
    def __init__(self, config: SynthesisConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.pool = get_initial_pool()
        self.chaos_field = ChaosField(self.rng, config.chaos_factor, self.pool)
        self.sampler = AtomSampler(self.config, self.chaos_field, self.rng, self.pool)
        self.crystallizer = RecordCrystallizer()
        self.used_concept_pairs: set[tuple[str, str]] = set()
        self.record_index = 0

    def add_record_as_atom(self, record: MemoryRecord):
        text = record.text
        premise = ""
        synthesis = ""
        if "Premise:" in text and "Synthesis:" in text:
            parts = text.split("Synthesis:")
            premise = parts[0].replace("Premise:", "").strip()
            synthesis = parts[1].strip()
        else:
            premise = text
            synthesis = text

        atom = LoreAtom(
            concept=record.title,
            layer_affinity=record.layer,
            tags=record.metadata.tags,
            premise_fragment=premise,
            synthesis_fragment=synthesis,
        )
        self.pool.append(atom)
        self.chaos_field.add_atom(atom, self.rng, self.config.chaos_factor)

    def generate_next(self) -> MemoryRecord:
        attempts = 0
        while True:
            atoms = self.sampler.sample_atoms(exclude=set())
            if len(atoms) < 2:
                attempts += 1
                if attempts > 20:
                    raise RuntimeError("Failed to sample enough atoms")
                continue
                
            concept_key = (atoms[0].concept, atoms[1].concept)
            if concept_key in self.used_concept_pairs:
                attempts += 1
                if attempts > 1000:
                    raise RuntimeError("Exhausted combination space")
                continue
                
            record = self.crystallizer.crystallize(atoms, self.config.seed, self.record_index, self.config, self.rng)
            try:
                MemoryRecord.model_validate(record.model_dump())
            except Exception:
                attempts += 1
                continue
                
            self.used_concept_pairs.add(concept_key)
            self.record_index += 1
            return record

    async def async_stream(self):
        while True:
            await asyncio.sleep(0)  # yield to event loop
            try:
                yield self.generate_next()
            except RuntimeError:
                break


def _generate_chaos_records(config: SynthesisConfig) -> list[MemoryRecord]:
    engine = ChaosEngine(config)
    records = []
    while len(records) < config.n_records:
        try:
            records.append(engine.generate_next())
        except RuntimeError:
            break
    return records


def generate_seed_theses(
    seed: int = 0,
    n_records: int = 3,
    chaos_factor: float = 0.3,
    layer_weights: dict[str, float] | None = None,
) -> list[MemoryRecord]:
    if seed == 0:
        return list(_SEED_0_THESES)
    return _generate_chaos_records(
        SynthesisConfig(
            seed=seed,
            n_records=n_records,
            chaos_factor=chaos_factor,
            layer_weights=layer_weights,
        )
    )


def theses_as_jsonl(
    seed: int = 0,
    n_records: int = 3,
    chaos_factor: float = 0.3,
    layer_weights: dict[str, float] | None = None,
) -> str:
    return "\n".join(
        r.model_dump_json(exclude_none=True) 
        for r in generate_seed_theses(
            seed=seed, 
            n_records=n_records, 
            chaos_factor=chaos_factor, 
            layer_weights=layer_weights
        )
    )
