"""Tests for JSONL validation and schema contract alignment."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import jsonschema
import orjson
import pytest

from vuorse_vortex.jsonl import validate_jsonl
from vuorse_vortex.schemas import BehaviorPolicy, MemoryMetadata, MemoryRecord, RetrievalMetadata
from vuorse_vortex.synthesis import theses_as_jsonl

_SCHEMA_PATH = Path("schemas/vuorse_cloud_memory_record.schema.json")


def _load_schema() -> dict[str, object]:
    return orjson.loads(_SCHEMA_PATH.read_bytes())


def _load_schema_generator() -> object:
    """Import ``scripts/generate_schema.py`` without making it a package."""
    module_path = Path("scripts/generate_schema.py").resolve()
    spec = importlib.util.spec_from_file_location("generate_schema", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("generate_schema", module)
    spec.loader.exec_module(module)
    return module


def _record(record_id: str = "record-1", *, may_state_as_fact: bool = False) -> MemoryRecord:
    return MemoryRecord(
        id=record_id,
        layer="apocrypha",
        record_type="test",
        title="Private Test Record",
        text="A private test record.",
        metadata=MemoryMetadata(
            canon_status="synthetic_behavioral",
            visibility="private_to_vuorse",
            tags=["test"],
        ),
        retrieval=RetrievalMetadata(
            priority=5,
            embedding_weight="low",
            query_hints=["test"],
        ),
        behavior=BehaviorPolicy(
            may_state_as_fact=may_state_as_fact,
            may_use_for_voice=True,
            may_reveal_to_user=False,
        ),
    )


def _write_jsonl(path: Path, records: list[MemoryRecord]) -> None:
    path.write_text(
        "\n".join(record.model_dump_json(exclude_none=True) for record in records) + "\n",
        encoding="utf-8",
    )


def test_validate_jsonl_accepts_valid_record(tmp_path: Path) -> None:
    path = tmp_path / "valid.jsonl"
    _write_jsonl(path, [_record()])

    assert validate_jsonl(path) == []


def test_validate_jsonl_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.jsonl"
    _write_jsonl(path, [_record("same"), _record("same")])

    errors = validate_jsonl(path)

    assert len(errors) == 1
    assert "duplicate id" in errors[0]


def test_validate_jsonl_rejects_private_fact_violation(tmp_path: Path) -> None:
    path = tmp_path / "firewall.jsonl"
    _write_jsonl(path, [_record(may_state_as_fact=True)])

    errors = validate_jsonl(path)

    assert len(errors) == 1
    assert "may_state_as_fact" in errors[0]


def test_synthesize_output_validates_as_memory_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "synthetic.jsonl"
    path.write_text(theses_as_jsonl() + "\n", encoding="utf-8")

    assert validate_jsonl(path) == []


def test_memory_record_matches_json_schema() -> None:
    schema = _load_schema()
    record = _record().model_dump(mode="json", exclude_none=True)
    jsonschema.validate(record, schema)


# --------------------------------------------------------------------------- #
# Contract drift: the on-disk schema must match what Pydantic emits.          #
# --------------------------------------------------------------------------- #


def test_published_schema_matches_pydantic_source() -> None:
    """If ``schemas/...`` drifts from ``schemas.py``, regenerate it.

    Run ``uv run scripts/generate_schema.py`` to refresh the published file.
    """
    generator = _load_schema_generator()
    expected = generator.serialize(generator.build_schema())  # type: ignore[attr-defined]
    actual = _SCHEMA_PATH.read_text(encoding="utf-8")
    assert actual == expected, (
        "schemas/vuorse_cloud_memory_record.schema.json is out of sync with "
        "src/vuorse_vortex/schemas.py. Re-run scripts/generate_schema.py."
    )


def test_schema_generator_check_mode_passes_on_clean_tree() -> None:
    """The --check mode is the CI gate; it must return 0 on a clean tree."""
    generator = _load_schema_generator()
    assert generator.main(["--check"]) == 0  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# theses_as_jsonl() — synthesis output validates against the published schema. #
# Pre-fix this would have failed: synthesis sets source_file +                  #
# source_confidence, which the old schema rejected via additionalProperties.   #
# --------------------------------------------------------------------------- #


def test_synthesize_output_validates_against_published_schema() -> None:
    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    for line in theses_as_jsonl().splitlines():
        record = orjson.loads(line)
        # All synthesis records currently set optional metadata.source_file and
        # metadata.source_confidence. Confirm they're actually present so this
        # test continues to exercise the historical drift point if synthesis
        # changes shape.
        assert record["metadata"].get("source_file"), record
        validator.validate(record)


# --------------------------------------------------------------------------- #
# Required vs optional field behavior, locked in both directions.              #
# --------------------------------------------------------------------------- #


def _valid_record_dict() -> dict[str, object]:
    return _record().model_dump(mode="json", exclude_none=True)


@pytest.mark.parametrize(
    "field",
    ["id", "layer", "record_type", "title", "text", "metadata", "retrieval", "behavior"],
)
def test_schema_rejects_missing_required_top_level_field(field: str) -> None:
    schema = _load_schema()
    record = _valid_record_dict()
    record.pop(field)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, schema)


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("metadata", "canon_status"),
        ("metadata", "visibility"),
        ("retrieval", "priority"),
        ("retrieval", "embedding_weight"),
        ("behavior", "may_state_as_fact"),
        ("behavior", "may_use_for_voice"),
        ("behavior", "may_reveal_to_user"),
    ],
)
def test_schema_rejects_missing_required_nested_field(section: str, field: str) -> None:
    schema = _load_schema()
    record = _valid_record_dict()
    sub = record[section]
    assert isinstance(sub, dict)
    sub.pop(field)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, schema)


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("metadata", "tags"),
        ("metadata", "source_file"),
        ("metadata", "section"),
        ("metadata", "source_confidence"),
        ("retrieval", "query_hints"),
        ("behavior", "allowed_surface_form"),
        ("behavior", "promotion_authority"),
    ],
)
def test_schema_accepts_records_missing_optional_field(section: str, field: str) -> None:
    """Optional fields can be absent without tripping the schema.

    This locks in the *Pydantic* notion of optional (default_factory=list or
    ``str | None = None``). Pre-fix the schema marked ``tags`` and ``query_hints``
    as required, which contradicted the Python contract.
    """
    schema = _load_schema()
    record = _valid_record_dict()
    sub = record[section]
    assert isinstance(sub, dict)
    sub.pop(field, None)
    jsonschema.validate(record, schema)


def test_schema_rejects_unknown_top_level_property() -> None:
    """``extra=forbid`` on Pydantic → ``additionalProperties: false`` in schema."""
    schema = _load_schema()
    record = _valid_record_dict()
    record["bogus_extra"] = "nope"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, schema)


def test_schema_rejects_unknown_metadata_property() -> None:
    schema = _load_schema()
    record = _valid_record_dict()
    metadata = record["metadata"]
    assert isinstance(metadata, dict)
    metadata["unexpected"] = "value"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, schema)


def test_schema_allows_null_for_optional_string_fields() -> None:
    """Explicit ``null`` is valid for optional fields (anyOf includes null)."""
    schema = _load_schema()
    record = _valid_record_dict()
    metadata = record["metadata"]
    assert isinstance(metadata, dict)
    metadata["source_file"] = None
    metadata["section"] = None
    metadata["source_confidence"] = None
    behavior = record["behavior"]
    assert isinstance(behavior, dict)
    behavior["allowed_surface_form"] = None
    behavior["promotion_authority"] = None
    jsonschema.validate(record, schema)


# --------------------------------------------------------------------------- #
# Round-trip: anything Pydantic accepts the schema accepts, and vice versa.    #
# --------------------------------------------------------------------------- #


def test_pydantic_round_trip_through_schema() -> None:
    schema = _load_schema()
    # Walk every synthesis seed through Pydantic → JSON → JSON Schema validate
    # → Pydantic again. Catches subtle serialisation drift end-to-end.
    for line in theses_as_jsonl().splitlines():
        as_dict = orjson.loads(line)
        validated_clone = copy.deepcopy(as_dict)
        jsonschema.validate(validated_clone, schema)
        rebuilt = MemoryRecord.model_validate(as_dict)
        assert rebuilt.model_dump(mode="json", exclude_none=True) == as_dict
