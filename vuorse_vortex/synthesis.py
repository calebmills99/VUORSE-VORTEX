"""Synthetic private seed memory records for VUORSE-VORTEX."""

from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from vuorse_vortex.schemas import (
    BehaviorPolicy,
    EmbeddingWeight,
    LoreAtom,
    MemoryMetadata,
    MemoryRecord,
    Provenance,
    RetrievalMetadata,
)
from vuorse_vortex.sifting import clean_concept_name, is_valid_concept_name
from vuorse_vortex.walled import load_walled_atoms

_DEFAULT_WALLED_JSONL = Path("hooplehopper_totality/debriefing_walled.jsonl")


@dataclass
class SynthesisConfig:
    seed: int
    n_records: int = 5
    chaos_factor: float = 0.3
    layer_weights: dict[str, float] | None = None
    embedding_weight_bias: EmbeddingWeight = "low"
    preserve_atom_order: bool = False


class ChaosField:
    def __init__(self, rng: random.Random, chaos_factor: float, pool: list[LoreAtom]):
        self.displacement: dict[str, float] = {}
        for atom in pool:
            self.add_atom(atom, rng, chaos_factor)

    def add_atom(self, atom: LoreAtom, rng: random.Random, chaos_factor: float) -> None:
        self.displacement[atom.concept] = rng.uniform(-chaos_factor, chaos_factor)


class AtomSampler:
    def __init__(
        self,
        config: SynthesisConfig,
        chaos_field: ChaosField,
        rng: random.Random,
        pool: list[LoreAtom],
    ):
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
            if not is_valid_concept_name(atom.concept):
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
        self,
        atoms: list[LoreAtom],
        seed: int,
        record_index: int,
        config: SynthesisConfig,
        rng: random.Random,
    ) -> MemoryRecord:
        premise_anchor = atoms[0]
        synthesis_driver = atoms[1]

        base_weight = (config.layer_weights or {}).get(premise_anchor.layer_affinity, 1.0)
        effective_layer_weight = max(0.01, base_weight)
        priority = min(6, round(effective_layer_weight * 2))

        tags: set[str] = set()
        for atom in atoms:
            tags.update(atom.tags)

        record_id = f"chaos_{seed}_{record_index}_{rng.getrandbits(32):08x}"
        clean_anchor = clean_concept_name(premise_anchor.concept).title()
        clean_driver = clean_concept_name(synthesis_driver.concept).title()
        title = f"{clean_anchor} / {clean_driver}"
        text = (
            f"Premise: {premise_anchor.premise_fragment}\n\n"
            f"Synthesis: {synthesis_driver.synthesis_fragment}"
        )

        # Provenance: record exactly which atoms (by concept) crystallized this
        # record, and how deep into the chaos recursion we are. Generation is
        # the deepest parent + 1 so an accepted record fed back as an atom and
        # then recombined doesn't claim it's still gen 1.
        parent_atom_ids = [atom.concept for atom in atoms]
        generation = max((atom.generation for atom in atoms), default=0) + 1

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
                provenance=Provenance(
                    parent_atom_ids=parent_atom_ids,
                    generation=generation,
                    engine="ChaosEngine",
                ),
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
        self.pool = load_walled_atoms(
            _DEFAULT_WALLED_JSONL,
            preserve_order=config.preserve_atom_order,
        )
        for atom in self.pool:
            atom.concept = clean_concept_name(atom.concept)
        self.chaos_field = ChaosField(self.rng, config.chaos_factor, self.pool)
        self.sampler = AtomSampler(self.config, self.chaos_field, self.rng, self.pool)
        self.crystallizer = RecordCrystallizer()
        # Dedup over the FULL picked-atom set, not just the first two atoms,
        # and permutation-invariant: ("a", "b", "c") and ("c", "a", "b") are
        # the same combination. A reshuffle-and-retry attack against the old
        # 2-tuple key used to slip through; this closes it.
        self.used_concept_sets: set[frozenset[str]] = set()
        self.record_index = 0

    def add_record_as_atom(self, record: MemoryRecord) -> None:
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

        concept = clean_concept_name(record.title)
        if not concept:
            concept = clean_concept_name(record.id)

        provenance = record.metadata.provenance
        parent_atom_ids = tuple(provenance.parent_atom_ids) if provenance else ()
        generation = provenance.generation if provenance else 0

        atom = LoreAtom(
            concept=concept,
            layer_affinity=record.layer,
            tags=record.metadata.tags,
            premise_fragment=premise,
            synthesis_fragment=synthesis,
            parent_atom_ids=parent_atom_ids,
            generation=generation,
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

            concept_set = frozenset(atom.concept for atom in atoms)
            if concept_set in self.used_concept_sets:
                attempts += 1
                if attempts > 1000:
                    raise RuntimeError("Exhausted combination space")
                continue

            record = self.crystallizer.crystallize(
                atoms, self.config.seed, self.record_index, self.config, self.rng
            )
            try:
                MemoryRecord.model_validate(record.model_dump())
            except Exception:
                attempts += 1
                continue

            self.used_concept_sets.add(concept_set)
            self.record_index += 1
            return record

    def generate_records(self, n: int | None = None) -> Iterator[MemoryRecord]:
        """Yield generated records until ``n`` is reached or combinations exhaust."""
        count = 0
        while n is None or count < n:
            try:
                yield self.generate_next()
            except RuntimeError:
                break
            count += 1


def _generate_chaos_records(config: SynthesisConfig) -> list[MemoryRecord]:
    engine = ChaosEngine(config)
    return list(engine.generate_records(n=config.n_records))


def generate_seed_theses(
    seed: int = 0,
    n_records: int = 5,
    chaos_factor: float = 0.3,
    layer_weights: dict[str, float] | None = None,
) -> list[MemoryRecord]:
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
    n_records: int = 5,
    chaos_factor: float = 0.3,
    layer_weights: dict[str, float] | None = None,
) -> str:
    return "\n".join(
        r.model_dump_json(exclude_none=True)
        for r in generate_seed_theses(
            seed=seed,
            n_records=n_records,
            chaos_factor=chaos_factor,
            layer_weights=layer_weights,
        )
    )
