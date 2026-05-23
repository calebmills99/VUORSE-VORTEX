"""Defense-in-depth tests for the canon firewall on the vector-ingest path.

These tests deliberately do NOT require CUDA: the firewall must catch sealed-
layer leak attempts before any GPU work happens, so a CPU-only CI environment
should still raise on a violating ingest. If a future change moves the GPU
gate above the firewall check, these tests will start failing in CI (which is
the point — that ordering would mean any GPU-less environment silently swaps
firewall enforcement for an unrelated GPU error).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from vuorse_vortex.firewall import CanonFirewallViolation
from vuorse_vortex.schemas import (
    BehaviorPolicy,
    Layer,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)
from vuorse_vortex.settings import Settings
from vuorse_vortex.vector import ChromaDBBackend, VectorDBBackend


def _record(
    record_id: str,
    *,
    layer: Layer = "apocrypha",
    may_state_as_fact: bool = False,
    may_reveal_to_user: bool = False,
) -> dict[str, Any]:
    return {
        "id": record_id,
        "layer": layer,
        "record_type": "test",
        "title": f"title-{record_id}",
        "text": "private apocryphal text",
        "metadata": {
            "canon_status": "synthetic_behavioral",
            "visibility": "private_to_vuorse",
            "tags": [],
        },
        "retrieval": {
            "priority": 5,
            "embedding_weight": "low",
            "query_hints": [],
        },
        "behavior": {
            "may_state_as_fact": may_state_as_fact,
            "may_use_for_voice": True,
            "may_reveal_to_user": may_reveal_to_user,
        },
    }


def _chroma_backend(tmp_path: Path) -> ChromaDBBackend:
    """Build a ChromaDBBackend pointed at a tmp dir. No GPU/chromadb required —
    the firewall check fires before any of that is touched."""
    settings = Settings(
        vector_backend="chromadb",
        chromadb_path=str(tmp_path / "chromadb"),
        chromadb_collection="firewall_test",
    )
    return ChromaDBBackend(settings=settings)


def test_ingest_rejects_sealed_layer_with_may_state_as_fact_true(tmp_path: Path) -> None:
    backend = _chroma_backend(tmp_path)
    bad = _record("leak-1", layer="apocrypha", may_state_as_fact=True)
    with pytest.raises(CanonFirewallViolation, match="may_state_as_fact"):
        backend.ingest([bad])


def test_ingest_rejects_sealed_layer_with_may_reveal_to_user_true(tmp_path: Path) -> None:
    backend = _chroma_backend(tmp_path)
    bad = _record("leak-2", layer="roadmap_manifest", may_reveal_to_user=True)
    with pytest.raises(CanonFirewallViolation, match="may_reveal_to_user"):
        backend.ingest([bad])


def test_ingest_rejects_hooplehopper_totality_with_both_flags_true(tmp_path: Path) -> None:
    backend = _chroma_backend(tmp_path)
    bad = _record(
        "leak-3",
        layer="hooplehopper_totality",
        may_state_as_fact=True,
        may_reveal_to_user=True,
    )
    with pytest.raises(CanonFirewallViolation):
        backend.ingest([bad])


def test_ingest_violation_names_record_and_backend(tmp_path: Path) -> None:
    """The exception message should identify the offending record id and the
    backend that refused it, so a stray ingest call from anywhere in the
    process is traceable without a full traceback."""
    backend = _chroma_backend(tmp_path)
    bad = _record("identified-leak", layer="apocrypha", may_state_as_fact=True)
    with pytest.raises(CanonFirewallViolation) as exc_info:
        backend.ingest([bad])
    msg = str(exc_info.value)
    assert "identified-leak" in msg
    assert "apocrypha" in msg
    assert "ChromaDBBackend" in msg


def test_ingest_rejects_schema_violation_with_value_error(tmp_path: Path) -> None:
    """Schema-broken dicts are caught by the firewall preflight too, not just
    pydantic deep inside the ingest path."""
    backend = _chroma_backend(tmp_path)
    broken = {"id": "no-layer-field", "text": "incomplete"}
    with pytest.raises(ValueError, match="schema error"):
        backend.ingest([broken])


def test_validate_for_ingest_accepts_pydantic_instances(tmp_path: Path) -> None:
    backend = _chroma_backend(tmp_path)
    rec = MemoryRecord(
        id="valid-1",
        layer="canon",
        record_type="test",
        title="canon ok",
        text="canon text",
        metadata=MemoryMetadata(canon_status="locked", visibility="public"),
        retrieval=RetrievalMetadata(priority=3, embedding_weight="low"),
        behavior=BehaviorPolicy(
            may_state_as_fact=True,
            may_use_for_voice=True,
            may_reveal_to_user=True,
        ),
    )
    validated = backend._validate_for_ingest([rec])
    assert validated == [rec]


def test_validate_for_ingest_empty_input_returns_empty(tmp_path: Path) -> None:
    backend = _chroma_backend(tmp_path)
    assert backend._validate_for_ingest([]) == []


def test_base_class_ingest_returns_zero_without_persisting() -> None:
    """The abstract base ``VectorDBBackend.ingest`` is the default for any
    subclass that forgets to override — it must not silently appear to succeed
    on real data. Returning 0 + persisting nothing is the safe behavior."""
    backend = VectorDBBackend()
    assert backend.ingest([_record("anything", layer="canon")]) == 0


def test_custom_sealed_categories_flow_into_backend_firewall(tmp_path: Path) -> None:
    """If sealed_categories is reconfigured, ingest enforcement follows."""
    settings = Settings(
        sealed_categories=["persona"],
        vector_backend="chromadb",
        chromadb_path=str(tmp_path / "chromadb"),
    )
    backend = ChromaDBBackend(settings=settings)
    bad = _record("persona-leak", layer="persona", may_state_as_fact=True)
    with pytest.raises(CanonFirewallViolation, match="may_state_as_fact"):
        backend.ingest([bad])

    # And the previously-sealed default layer is no longer sealed under this config.
    now_ok = _record(
        "apocrypha-allowed",
        layer="apocrypha",
        may_state_as_fact=True,
        may_reveal_to_user=True,
    )
    # We can't actually persist (no CUDA in CI), but we CAN confirm the
    # firewall preflight does not raise.
    assert backend._validate_for_ingest([now_ok])[0].id == "apocrypha-allowed"
