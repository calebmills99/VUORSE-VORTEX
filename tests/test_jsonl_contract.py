"""Tests for JSONL validation and schema contract alignment."""

from __future__ import annotations

from pathlib import Path

import jsonschema
import orjson

from vuorse_vortex.jsonl import validate_jsonl
from vuorse_vortex.schemas import BehaviorPolicy, MemoryMetadata, MemoryRecord, RetrievalMetadata
from vuorse_vortex.synthesis import theses_as_jsonl


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
    schema = orjson.loads(Path("schemas/vuorse_cloud_memory_record.schema.json").read_bytes())
    record = _record().model_dump(mode="json", exclude_none=True)

    jsonschema.validate(record, schema)
