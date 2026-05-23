"""Chaos engine tests, wired through the walled-JSONL fixture."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vuorse_vortex.schemas import MemoryRecord
from vuorse_vortex.synthesis import (
    ChaosEngine,
    SynthesisConfig,
    generate_seed_theses,
    theses_as_jsonl,
)


@pytest.mark.parametrize("seed", [1, 42, 99, 777])
@pytest.mark.parametrize("preserve_atom_order", [False, True])
def test_seed_reproducibility(
    seed: int, preserve_atom_order: bool, patch_walled_pool: Path
) -> None:
    """Same (seed, preserve_atom_order, walled pool) -> identical records."""
    cfg1 = SynthesisConfig(
        seed=seed, n_records=5, preserve_atom_order=preserve_atom_order
    )
    cfg2 = SynthesisConfig(
        seed=seed, n_records=5, preserve_atom_order=preserve_atom_order
    )
    records1 = list(ChaosEngine(cfg1).generate_records(n=cfg1.n_records))
    records2 = list(ChaosEngine(cfg2).generate_records(n=cfg2.n_records))

    assert len(records1) == 5
    assert [r.model_dump() for r in records1] == [r.model_dump() for r in records2]


@pytest.mark.parametrize("seed1, seed2", [(42, 99), (1, 2), (777, 888)])
@pytest.mark.parametrize("preserve_atom_order", [False, True])
def test_seed_variation(
    seed1: int, seed2: int, preserve_atom_order: bool, patch_walled_pool: Path
) -> None:
    """Different seeds produce different output."""
    cfg1 = SynthesisConfig(
        seed=seed1, n_records=5, preserve_atom_order=preserve_atom_order
    )
    cfg2 = SynthesisConfig(
        seed=seed2, n_records=5, preserve_atom_order=preserve_atom_order
    )
    records1 = list(ChaosEngine(cfg1).generate_records(n=cfg1.n_records))
    records2 = list(ChaosEngine(cfg2).generate_records(n=cfg2.n_records))

    assert [r.model_dump() for r in records1] != [r.model_dump() for r in records2]


def test_schema_validity(patch_walled_pool: Path) -> None:
    """All records pass MemoryRecord.model_validate(r.model_dump())."""
    records = generate_seed_theses(seed=42, n_records=10)
    for r in records:
        validated = MemoryRecord.model_validate(r.model_dump())
        assert validated.id == r.id


def test_behavioral_policy(patch_walled_pool: Path) -> None:
    """All records have the canon-firewall-safe behavioral policy."""
    records = generate_seed_theses(seed=42, n_records=10)
    for r in records:
        assert r.behavior.may_state_as_fact is False
        assert r.behavior.may_reveal_to_user is False
        assert r.behavior.may_use_for_voice is True
        assert r.metadata.visibility == "private_to_vuorse"
        assert r.metadata.canon_status == "synthetic_behavioral"


def test_default_n_records_is_five(patch_walled_pool: Path) -> None:
    """generate_seed_theses() with no args yields exactly 5 records from walled pool."""
    records = generate_seed_theses()
    assert len(records) == 5
    for r in records:
        assert r.id.startswith("chaos_")


def test_theses_as_jsonl_valid(patch_walled_pool: Path) -> None:
    """theses_as_jsonl() produces valid JSONL (one parseable JSON object per line)."""
    jsonl_str = theses_as_jsonl(seed=42, n_records=5)
    lines = jsonl_str.strip().split("\n")

    assert len(lines) == 5
    for line in lines:
        obj = json.loads(line)
        assert "id" in obj
        assert obj["id"].startswith("chaos_")
        MemoryRecord.model_validate(obj)


def test_concept_cleaning_and_filtering() -> None:
    """Verify that concept sifting functions sanitise and filter metadata/nonsense."""
    from vuorse_vortex.sifting import clean_concept_name, is_valid_concept_name

    # 1. Test clean_concept_name
    assert clean_concept_name("2. Series Overview") == "Series Overview"
    assert clean_concept_name("[LOCKED] The Thread") == "The Thread"
    assert clean_concept_name("canon_artifacts_md_artifact_note_the_thread_full_224_0116d6a8ed") == "the thread full"
    assert clean_concept_name("concept_with_underscores") == "concept with underscores"

    # 2. Test is_valid_concept_name
    assert not is_valid_concept_name("0116d6a8ed")
    assert not is_valid_concept_name("12345")
    assert not is_valid_concept_name("document preamble")
    assert is_valid_concept_name("The Thread")
    assert is_valid_concept_name("Eli")

    # 3. Test that crystallize cleans titles
    from vuorse_vortex.schemas import LoreAtom
    from vuorse_vortex.synthesis import RecordCrystallizer, SynthesisConfig
    import random

    crystallizer = RecordCrystallizer()
    atoms = [
        LoreAtom(
            concept="canon_artifacts_md_artifact_note_the_thread_full_224_0116d6a8ed",
            layer_affinity="canon",
            tags=["thread"],
            premise_fragment="Premise fragment",
            synthesis_fragment="Synthesis fragment",
        ),
        LoreAtom(
            concept="[LOCKED] Jake_McCullen",
            layer_affinity="canon",
            tags=["jake"],
            premise_fragment="Premise",
            synthesis_fragment="Synthesis",
        )
    ]
    config = SynthesisConfig(seed=42)
    rng = random.Random(42)
    record = crystallizer.crystallize(atoms, seed=42, record_index=0, config=config, rng=rng)

    assert "0116d6a8ed" not in record.title
    assert "canon_artifacts" not in record.title
    assert "[LOCKED]" not in record.title
    assert "_" not in record.title
    assert record.title == "The Thread Full / Jake Mccullen"

