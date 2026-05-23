"""Provenance + dedup tests for the chaos synthesis engine.

These tests pin two related invariants that the AI-engineering review flagged
as P0 gaps:

1. Every chaos-engine record carries ``metadata.provenance`` with the
   concepts of the parent atoms and a non-zero generation depth. Without
   this, accepting a record back into the atom pool and recompounding it
   produces traceable-by-nobody lineage drift.

2. The dedup key is the FULL set of picked atoms, not just the first two.
   With three or more atoms sampled, a permuted reshuffle previously slipped
   past the old ``(atoms[0], atoms[1])`` 2-tuple key.
"""

from __future__ import annotations

from pathlib import Path

from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.synthesis import ChaosEngine, SynthesisConfig, generate_seed_theses


def test_records_carry_provenance(patch_walled_pool: Path) -> None:
    records = generate_seed_theses(seed=42, n_records=5)
    for r in records:
        assert r.metadata.provenance is not None, (
            f"record {r.id} missing provenance — accepted-into-pool feedback "
            "loops would be untraceable"
        )
        prov = r.metadata.provenance
        assert prov.engine == "ChaosEngine"
        assert prov.generation >= 1, "walled atoms are gen 0; crystallized output is gen 1+"
        assert len(prov.parent_atom_ids) >= 2
        # All parent ids should be non-empty cleaned concept strings, not
        # raw record ids or empty strings.
        for pid in prov.parent_atom_ids:
            assert isinstance(pid, str) and pid.strip()


def test_dedup_uses_full_atom_set_not_just_first_pair(patch_walled_pool: Path) -> None:
    """No two emitted records may share the same set of parent atoms.

    The old dedup key was ``(atoms[0].concept, atoms[1].concept)``. If two
    samples picked the same atoms in a different order, or picked an
    overlapping pair plus a different third atom, dedup didn't fire. The
    permutation-invariant frozenset check closes both holes.
    """
    records = generate_seed_theses(seed=99, n_records=15)
    seen: set[frozenset[str]] = set()
    for r in records:
        assert r.metadata.provenance is not None
        key = frozenset(r.metadata.provenance.parent_atom_ids)
        assert key not in seen, (
            f"record {r.id} reuses parent-atom set {sorted(key)} — "
            "permutation-invariant dedup is broken"
        )
        seen.add(key)


def test_accept_and_recompound_increments_generation(patch_walled_pool: Path) -> None:
    """Feeding an accepted record back into the pool, then sampling again,
    should produce a record whose generation is strictly greater than the
    fed-back record. This is the lineage-depth signal the Weaver can gate on.
    """
    engine = ChaosEngine(SynthesisConfig(seed=7, n_records=5))
    first = engine.generate_next()
    assert first.metadata.provenance is not None
    first_gen = first.metadata.provenance.generation

    # Feed the accepted record back as an atom.
    engine.add_record_as_atom(first)

    # The next record may or may not USE the fed-back atom — chaos sampling
    # is stochastic. Generate enough records that we very likely hit one
    # that does, and check that when we do, the generation grows.
    saw_deeper = False
    for _ in range(20):
        r = engine.generate_next()
        assert r.metadata.provenance is not None
        if r.metadata.provenance.generation > first_gen:
            saw_deeper = True
            break
    assert saw_deeper, (
        "after accepting a record back into the pool, at least one "
        "subsequent crystallization should have produced a deeper-generation "
        "record — chaos lineage depth is not being propagated"
    )


def test_provenance_survives_json_round_trip(patch_walled_pool: Path) -> None:
    """Provenance must serialize through ``model_dump_json`` and back."""
    record = generate_seed_theses(seed=1, n_records=1)[0]
    payload = record.model_dump_json(exclude_none=True)
    rebuilt = MemoryRecord.model_validate_json(payload)
    assert rebuilt.metadata.provenance == record.metadata.provenance


def test_reproducibility_unchanged_by_provenance_addition(
    patch_walled_pool: Path,
) -> None:
    """Adding the provenance field must not break seed reproducibility."""
    a = generate_seed_theses(seed=42, n_records=5)
    b = generate_seed_theses(seed=42, n_records=5)
    assert [r.model_dump() for r in a] == [r.model_dump() for r in b]
