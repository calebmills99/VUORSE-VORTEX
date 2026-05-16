"""Tests for centralized settings and canon firewall."""

from vuorse_vortex.firewall import CanonFirewallValidator
from vuorse_vortex.schemas import BehaviorPolicy, MemoryMetadata, MemoryRecord, RetrievalMetadata
from vuorse_vortex.settings import Settings, get_settings
from vuorse_vortex.vector import VectorDBBackend, get_backend


def _make_record(layer: str, may_state_as_fact: bool = False, may_reveal: bool = False):
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


def test_settings_default_sealed_categories():
    settings = get_settings()
    assert "apocrypha" in settings.sealed_categories
    assert "roadmap_manifest" in settings.sealed_categories
    assert "hooplehopper_totality" in settings.sealed_categories


def test_settings_custom_sealed_categories():
    settings = Settings(sealed_categories=["apocrypha"])
    assert settings.sealed_categories == ["apocrypha"]


def test_firewall_validator_uses_settings():
    settings = Settings(sealed_categories=["apocrypha"])
    validator = CanonFirewallValidator(settings=settings)
    assert validator.sealed_categories == ["apocrypha"]


def test_firewall_validator_passes_valid_record():
    validator = CanonFirewallValidator()
    record = _make_record("apocrypha", may_state_as_fact=False, may_reveal=False)
    assert validator.validate_record(record) == []


def test_firewall_validator_catches_violations():
    validator = CanonFirewallValidator()
    record = _make_record("roadmap_manifest", may_state_as_fact=True, may_reveal=True)
    errors = validator.validate_record(record)
    assert len(errors) == 2
    assert "may_state_as_fact" in errors[0]
    assert "may_reveal_to_user" in errors[1]


def test_firewall_validator_ignores_non_sealed_layers():
    validator = CanonFirewallValidator()
    record = _make_record("canon", may_state_as_fact=True, may_reveal=True)
    assert validator.validate_record(record) == []


def test_firewall_custom_sealed_does_not_flag_removed_layer():
    settings = Settings(sealed_categories=["apocrypha"])
    validator = CanonFirewallValidator(settings=settings)
    record = _make_record("roadmap_manifest", may_state_as_fact=True, may_reveal=True)
    # roadmap_manifest is not sealed in this custom config
    assert validator.validate_record(record) == []


def test_vector_backend_sealed_from_settings():
    settings = Settings(sealed_categories=["apocrypha", "roadmap_manifest"])
    backend = VectorDBBackend(settings=settings)
    assert backend.sealed_categories == {"apocrypha", "roadmap_manifest"}


def test_get_backend_respects_settings():
    settings = Settings(vector_backend="chromadb")
    backend = get_backend(settings=settings)
    assert backend._settings.vector_backend == "chromadb"


def test_get_backend_default():
    backend = get_backend()
    assert backend._settings.vector_backend == "chromadb"
