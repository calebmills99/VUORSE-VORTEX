"""Import private debrief theses into MemoryRecord JSONL."""

from __future__ import annotations

import heapq
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from vuorse_vortex.jsonl import iter_jsonl, validate_jsonl
from vuorse_vortex.schemas import (
    BehaviorPolicy,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)
from vuorse_vortex.walled import WalledFileParseError, _parse_md_sections

_DEFAULT_SESSION = Path(".frolic-session.json")
_DEFAULT_OUTPUT_DIR = Path("synthetic_enrichment/validated")
_DEFAULT_FALLBACK_DEBRIEF = Path("hooplehopper_totality/debriefing_walled.md")

_THESIS_TAG_WEIGHTS = {
    "wound": 5,
    "silence": 5,
    "jake": 4,
    "wyoming": 4,
    "soul-line": 4,
    "recurrence": 4,
    "hooplehopper-gap": 4,
    "anti-erasure": 3,
    "survival-tech": 3,
    "ritual": 3,
    "memory": 3,
    "velvet-archive": 3,
    "distributed": 2,
    "performance": 2,
    "drag": 2,
}


@dataclass(frozen=True)
class DebriefImportResult:
    """Summary of a debrief import run."""

    source_path: Path
    output_path: Path
    record_count: int


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "debrief_thesis"


def _load_session(session_path: Path) -> dict[str, Any]:
    try:
        session = json.loads(session_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid Frolic session JSON: {session_path}: {exc}") from exc
    if not isinstance(session, dict):
        raise ValueError(
            f"Invalid Frolic session JSON: {session_path}: top-level value must be an object"
        )
    return cast(dict[str, Any], session)


def _event_paths(session: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for event in session.get("events", []):
        if not isinstance(event, dict):
            continue
        raw = event.get("relativePath") or event.get("file")
        if isinstance(raw, str) and raw.strip():
            paths.append(Path(raw))
    return paths


def resolve_debrief_source(
    session_path: Path = _DEFAULT_SESSION,
    source_path: Path | None = None,
    fallback_path: Path = _DEFAULT_FALLBACK_DEBRIEF,
) -> Path:
    """Resolve the debrief markdown source for a Frolic session."""

    if source_path is not None:
        return source_path

    session = _load_session(session_path)
    session_dir = session_path.parent
    candidates: list[Path] = []
    for path in _event_paths(session):
        resolved = path if path.is_absolute() else session_dir / path
        name = resolved.name.lower()
        if "debrief" in name and resolved.suffix.lower() in {".md", ".markdown"}:
            candidates.append(resolved)

    existing = [path for path in candidates if path.exists()]
    if existing:
        return existing[0]

    fallback = fallback_path if fallback_path.is_absolute() else session_dir / fallback_path
    if fallback.exists():
        return fallback

    described = ", ".join(str(path) for path in candidates) or "none"
    raise FileNotFoundError(
        "No debrief markdown file was referenced by the Frolic session and "
        f"fallback was missing. Referenced candidates: {described}; fallback: {fallback}"
    )


def _score_payload(payload: dict[str, Any]) -> int:
    tags = [str(tag).lower() for tag in payload.get("tags", [])]
    text = " ".join(
        [
            str(payload.get("concept", "")),
            str(payload.get("premise_fragment", "")),
            str(payload.get("synthesis_fragment", "")),
            " ".join(tags),
        ]
    ).lower()

    score = sum(_THESIS_TAG_WEIGHTS.get(tag, 0) for tag in tags)
    score += sum(weight for marker, weight in _THESIS_TAG_WEIGHTS.items() if marker in text)
    score += min(len(set(tags)), 10)
    if len(str(payload.get("synthesis_fragment", "")).strip()) >= 80:
        score += 2
    return score


def _strongest_payloads(payloads: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    best_by_text: dict[tuple[str, str], dict[str, Any]] = {}
    for payload in payloads:
        key = (
            str(payload["premise_fragment"]).strip().lower(),
            str(payload["synthesis_fragment"]).strip().lower(),
        )
        current = best_by_text.get(key)
        if current is None or _score_payload(payload) > _score_payload(current):
            best_by_text[key] = payload

    ranked = sorted(
        best_by_text.values(),
        key=lambda payload: (
            _score_payload(payload),
            len(set(str(tag).lower() for tag in payload.get("tags", []))),
            str(payload.get("concept", "")),
        ),
        reverse=True,
    )
    return ranked[:limit]


def _record_from_payload(
    payload: dict[str, Any], *, source_file: str, date_stamp: str
) -> MemoryRecord:
    concept = str(payload["concept"]).strip()
    tags = list(dict.fromkeys(str(tag) for tag in payload["tags"]))
    slug = _slug(concept)

    return MemoryRecord(
        id=f"debrief_private_{date_stamp}_{slug}",
        layer="hooplehopper_totality",
        record_type="debrief_private_thesis",
        title=concept.replace("_", " ").title(),
        text=(
            f"Premise: {str(payload['premise_fragment']).strip()}\n\n"
            f"Synthesis: {str(payload['synthesis_fragment']).strip()}"
        ),
        metadata=MemoryMetadata(
            canon_status="synthetic_behavioral",
            visibility="private_to_vuorse",
            tags=tags,
            source_file=source_file,
            source_confidence="debrief_import",
            layer_affinity=payload["layer_affinity"],
        ),
        retrieval=RetrievalMetadata(
            priority=7,
            embedding_weight="high",
            query_hints=tags,
        ),
        behavior=BehaviorPolicy(
            may_state_as_fact=False,
            may_use_for_voice=True,
            may_reveal_to_user=False,
            allowed_surface_form="private synthesis only; never state as public canon",
            promotion_authority="the Weaver",
        ),
    )


def import_debrief_theses(
    session_path: Path = _DEFAULT_SESSION,
    source_path: Path | None = None,
    output_path: Path | None = None,
    limit: int = 8,
) -> DebriefImportResult:
    """Extract high-signal debrief theses into validated private MemoryRecord JSONL."""

    session_path = session_path.resolve()
    repo_root = session_path.parent
    source = resolve_debrief_source(session_path, source_path)
    if not source.is_absolute():
        source = repo_root / source

    content = source.read_text(encoding="utf-8")
    payloads = _parse_md_sections(content, source)
    if not payloads:
        raise WalledFileParseError(f"No debrief theses found in {source}", source)

    session = _load_session(session_path)
    date_stamp = str(session.get("timestamp", "unknown"))[:10].replace("-", "")
    try:
        source_file = str(source.relative_to(repo_root))
    except ValueError:
        source_file = str(source)
    records = [
        _record_from_payload(payload, source_file=source_file, date_stamp=date_stamp)
        for payload in _strongest_payloads(payloads, limit)
    ]

    target = output_path
    if target is None:
        target = _DEFAULT_OUTPUT_DIR / f"debrief_private_theses_{date_stamp}.jsonl"
    if not target.is_absolute():
        target = repo_root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(record.model_dump_json(exclude_none=True) for record in records) + "\n",
        encoding="utf-8",
    )

    errors = validate_jsonl(target)
    if errors:
        raise ValueError("Imported debrief JSONL failed validation:\n" + "\n".join(errors))

    return DebriefImportResult(source_path=source, output_path=target, record_count=len(records))


# ---------------------------------------------------------------------------
# JSONL-based extractor: distil strongest theses from an existing JSONL artifact
# ---------------------------------------------------------------------------


def _thesis_key(record: MemoryRecord) -> tuple[str, str]:
    return record.title.strip().lower(), record.text.strip().lower()


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
        raise ValueError("limit must be >= 1")

    deduped: dict[tuple[str, str], MemoryRecord] = {}
    for _, obj in iter_jsonl(source_path):
        rec = MemoryRecord.model_validate(obj)
        key = _thesis_key(rec)
        existing = deduped.get(key)
        if existing is None or _score(rec) > _score(existing):
            deduped[key] = rec

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
    if imported:
        output_path.write_text(
            "\n".join(r.model_dump_json(exclude_none=True) for r in imported) + "\n",
            encoding="utf-8",
        )
    else:
        output_path.write_text("", encoding="utf-8")
    return imported
