"""JSONL validation helpers."""

from __future__ import annotations

from pathlib import Path

import orjson

from vuorse_vortex.schemas import MemoryRecord


def iter_jsonl(path: Path):
    with path.open("rb") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            yield line_no, orjson.loads(line)


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for line_no, obj in iter_jsonl(path):
        try:
            record = MemoryRecord.model_validate(obj)
        except Exception as exc:
            errors.append(f"{path}:{line_no}: schema error: {exc}")
            continue

        if record.id in seen:
            errors.append(f"{path}:{line_no}: duplicate id: {record.id}")
        seen.add(record.id)

        if record.layer in {"apocrypha", "roadmap_manifest", "hooplehopper_totality"}:
            if record.behavior.may_state_as_fact:
                errors.append(f"{path}:{line_no}: private layer may_state_as_fact must be false")
            if record.behavior.may_reveal_to_user:
                errors.append(f"{path}:{line_no}: private layer may_reveal_to_user must be false")

    return errors
