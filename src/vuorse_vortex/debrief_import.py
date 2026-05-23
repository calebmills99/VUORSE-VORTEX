"""Import strongest private theses from debrief JSONL artifacts."""

from __future__ import annotations

import heapq
from pathlib import Path

from vuorse_vortex.jsonl import iter_jsonl
from vuorse_vortex.schemas import MemoryRecord


def _thesis_key(record: MemoryRecord) -> tuple[str, str]:
    text = record.text.strip().lower()
    return record.title.strip().lower(), text


def _score(record: MemoryRecord) -> tuple[int, int, int]:
    return (
        record.retrieval.priority,
        len(record.metadata.tags),
        len(record.text),
    )


def extract_strongest_private_theses(
    source_path: Path,
    output_path: Path,
    *,
    limit: int = 12,
    id_prefix: str = "se_private_debrief",
) -> list[MemoryRecord]:
    """Extract a top-N, de-duplicated thesis set and write MemoryRecord JSONL.

    Private behavior flags are enforced on every emitted record.

    Uses streaming deduplication and heapq.nlargest to keep memory bounded
    even for large source files.
    """
    if limit < 1:
        msg = "limit must be >= 1"
        raise ValueError(msg)

    # Streaming deduplication: keep best-scored record per key
    deduped: dict[tuple[str, str], MemoryRecord] = {}
    for _, obj in iter_jsonl(source_path):
        rec = MemoryRecord.model_validate(obj)
        key = _thesis_key(rec)
        existing = deduped.get(key)
        if existing is None or _score(rec) > _score(existing):
            deduped[key] = rec

    # Use heapq.nlargest for memory-bounded top-N selection
    strongest = heapq.nlargest(limit, deduped.values(), key=_score)

    imported: list[MemoryRecord] = []
    for idx, rec in enumerate(strongest, start=1):
        imported.append(
            rec.model_copy(
                update={
                    "id": f"{id_prefix}_{idx:03d}",
                    "record_type": "debrief_import_thesis",
                    "metadata": rec.metadata.model_copy(
                        update={"source_file": str(source_path)}
                    ),
                    "behavior": rec.behavior.model_copy(
                        update={
                            "may_state_as_fact": False,
                            "may_reveal_to_user": False,
                        }
                    ),
                }
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Avoid writing a single blank line when imported is empty
    if imported:
        output_path.write_text(
            "\n".join(r.model_dump_json(exclude_none=True) for r in imported) + "\n",
            encoding="utf-8",
        )
    else:
        output_path.write_text("", encoding="utf-8")
    return imported
