"""Tests for centralized settings and canon firewall."""

from vuorse_vortex.firewall import CanonFirewallValidator
from vuorse_vortex.gpu import _reset_cuda_cache
from vuorse_vortex.schemas import (
    BehaviorPolicy,
    Layer,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)
from vuorse_vortex.settings import Settings, get_settings
from vuorse_vortex.vector import ChromaDBBackend, FaissBackend, VectorDBBackend, get_backend


def _make_record(
    layer: Layer, may_state_as_fact: bool = False, may_reveal: bool = False
) -> MemoryRecord:
    return MemoryRecord(
        id="test-1",
        layer=layer,
        record_type="test",
        title="Test Record",
        text="Test text",
        metadata=MemoryMetadata(
            canon_status="locked",
            visibility="public",
        ),
        retrieval=RetrievalMetadata(priority=5, embedding_weight="medium"),
        behavior=BehaviorPolicy(
            may_state_as_fact=may_state_as_fact,
            may_use_for_voice=True,
            may_reveal_to_user=may_reveal,
        ),
    )


def test_settings_default_sealed_categories() -> None:
    settings = get_settings()
    assert "apocrypha" in settings.sealed_categories
    assert "roadmap_manifest" in settings.sealed_categories
    assert "hooplehopper_totality" in settings.sealed_categories


def test_settings_custom_sealed_categories() -> None:
    settings = Settings(sealed_categories=["apocrypha"])
    assert settings.sealed_categories == ["apocrypha"]


def test_firewall_validator_uses_settings() -> None:
    settings = Settings(sealed_categories=["apocrypha"])
    validator = CanonFirewallValidator(settings=settings)
    assert validator.sealed_categories == ["apocrypha"]


def test_firewall_validator_passes_valid_record() -> None:
    validator = CanonFirewallValidator()
    record = _make_record("apocrypha", may_state_as_fact=False, may_reveal=False)
    assert validator.validate_record(record) == []


def test_firewall_validator_catches_violations() -> None:
    validator = CanonFirewallValidator()
    record = _make_record("roadmap_manifest", may_state_as_fact=True, may_reveal=True)
    errors = validator.validate_record(record)
    assert len(errors) == 2
    assert "may_state_as_fact" in errors[0]
    assert "may_reveal_to_user" in errors[1]


def test_firewall_validator_ignores_non_sealed_layers() -> None:
    validator = CanonFirewallValidator()
    record = _make_record("canon", may_state_as_fact=True, may_reveal=True)
    assert validator.validate_record(record) == []


def test_firewall_custom_sealed_does_not_flag_removed_layer() -> None:
    settings = Settings(sealed_categories=["apocrypha"])
    validator = CanonFirewallValidator(settings=settings)
    record = _make_record("roadmap_manifest", may_state_as_fact=True, may_reveal=True)
    # roadmap_manifest is not sealed in this custom config
    assert validator.validate_record(record) == []


def test_vector_backend_sealed_from_settings() -> None:
    settings = Settings(sealed_categories=["apocrypha", "roadmap_manifest"])
    backend = VectorDBBackend(settings=settings)
    assert backend.sealed_categories == {"apocrypha", "roadmap_manifest"}


def test_get_backend_respects_settings() -> None:
    settings = Settings(vector_backend="chromadb")
    backend = get_backend(settings=settings)
    assert backend._settings.vector_backend == "chromadb"


def test_get_backend_default() -> None:
    backend = get_backend()
    assert backend._settings.vector_backend == "chromadb"


def test_get_backend_rejects_unknown_backend() -> None:
    settings = Settings.model_construct(vector_backend="unknown", sealed_categories=[])
    try:
        get_backend(settings=settings)
    except ValueError as exc:
        assert "Unknown vector backend" in str(exc)
    else:
        raise AssertionError("Expected unknown vector backend to raise ValueError")


def test_chromadb_backend_query_enforces_gpu_before_import(monkeypatch) -> None:
    monkeypatch.setenv("CORTEX_REQUIRE_GPU", "1")
    monkeypatch.delenv("CORTEX_ALLOW_CPU_DIAGNOSTIC", raising=False)
    _reset_cuda_cache()

    backend = ChromaDBBackend()
    try:
        backend.query("private memory", top_k=1)
    except RuntimeError as exc:
        assert "chromadb vector query" in str(exc)
    else:
        raise AssertionError("Expected ChromaDB backend query to enforce GPU strict mode")


def test_faiss_backend_query_enforces_gpu_before_import(monkeypatch) -> None:
    monkeypatch.setenv("CORTEX_REQUIRE_GPU", "1")
    monkeypatch.delenv("CORTEX_ALLOW_CPU_DIAGNOSTIC", raising=False)
    _reset_cuda_cache()

    backend = FaissBackend()
    try:
        backend.query("private memory", top_k=1)
    except RuntimeError as exc:
        assert "faiss vector query" in str(exc)
    else:
        raise AssertionError("Expected FAISS backend query to enforce GPU strict mode")
