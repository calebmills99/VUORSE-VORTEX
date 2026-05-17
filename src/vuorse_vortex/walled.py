"""Walled markdown <-> JSONL boundary for hooplehopper_totality lore atoms.

This module owns the only sanctioned path between the human-authored
``hooplehopper_totality/debriefing_walled.md`` source-of-truth and its
machine-readable JSONL projection. Every record emitted here is a
``MemoryRecord`` of layer ``hooplehopper_totality`` — sealed by the canon
firewall — and is reconstructable back into a ``LoreAtom`` for synthesis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, get_args

import orjson
import yaml
from pydantic import ValidationError

from vuorse_vortex.schemas import (
    BehaviorPolicy,
    Layer,
    LoreAtom,
    MemoryMetadata,
    MemoryRecord,
    RetrievalMetadata,
)

# -----------------------------------------------------------------------------
# Exception hierarchy
# -----------------------------------------------------------------------------


class WalledFileError(Exception):
    """Base class for walled markdown/JSONL boundary errors."""

    def __init__(self, message: str, source_path: Path) -> None:
        super().__init__(message)
        self.source_path = source_path


class WalledFileMissingError(WalledFileError):
    """Raised when the walled markdown or JSONL file is absent on disk."""

    def __init__(self, source_path: Path) -> None:
        super().__init__(
            f"Walled file not found: {source_path}. "
            "Run `vuorse-vortex build-walled` to regenerate.",
            source_path,
        )


class WalledFileEmptyError(WalledFileError):
    """Raised when a walled file exists but yields zero valid records."""

    def __init__(self, source_path: Path) -> None:
        super().__init__(
            f"Walled file is empty (no valid records parsed): {source_path}",
            source_path,
        )


class WalledFileParseError(WalledFileError):
    """Raised on YAML grammar or schema violations inside a walled file."""

    def __init__(self, message: str, source_path: Path) -> None:
        super().__init__(message, source_path)


# -----------------------------------------------------------------------------
# YAML grammar constants
# -----------------------------------------------------------------------------

_REQUIRED_KEYS = frozenset(
    {
        "concept",
        "layer_affinity",
        "tags",
        "premise_fragment",
        "synthesis_fragment",
    }
)
_OPTIONAL_KEYS = frozenset({"notes"})
_ALLOWED_KEYS = _REQUIRED_KEYS | _OPTIONAL_KEYS

_VALID_LAYERS: frozenset[str] = frozenset(get_args(Layer))


# -----------------------------------------------------------------------------
# Internal parser
# -----------------------------------------------------------------------------


def _parse_md_sections(content: str, source_path: Path) -> list[dict[str, Any]]:
    """Parse a walled markdown file into a list of validated YAML payload dicts.

    Grammar:
        # any-prelude
        ## Section Heading
        ```yaml
        concept: ...
        layer_affinity: ...
        tags: [...]
        premise_fragment: ...
        synthesis_fragment: ...
        # notes: optional
        ```

    Per section: exactly one ``yaml`` fenced block. Zero or two+ blocks raises.
    Order is preserved.
    """
    sections: list[dict[str, Any]] = []

    lines = content.splitlines()
    n = len(lines)
    i = 0
    current_heading: str | None = None
    current_heading_line: int | None = None
    blocks_for_current: list[tuple[str, int]] = []  # (yaml_body, fence_open_line)

    def _finalize_current() -> None:
        nonlocal current_heading, current_heading_line, blocks_for_current
        if current_heading is None:
            blocks_for_current = []
            return
        if len(blocks_for_current) == 0:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}) "
                "has zero yaml fenced blocks; expected exactly one.",
                source_path,
            )
        if len(blocks_for_current) > 1:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}) "
                f"has {len(blocks_for_current)} yaml fenced blocks; expected exactly one.",
                source_path,
            )
        yaml_body, fence_line = blocks_for_current[0]
        try:
            payload = yaml.safe_load(yaml_body)
        except yaml.YAMLError as exc:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}): "
                f"invalid YAML at fence opened line {fence_line}: {exc}",
                source_path,
            ) from exc

        if not isinstance(payload, dict):
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}): "
                f"YAML payload must be a mapping, got {type(payload).__name__}.",
                source_path,
            )

        keys = set(payload.keys())
        unknown = keys - _ALLOWED_KEYS
        if unknown:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}): "
                f"unknown key(s) {sorted(unknown)}; allowed = {sorted(_ALLOWED_KEYS)}.",
                source_path,
            )
        missing = _REQUIRED_KEYS - keys
        if missing:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}): "
                f"missing required key(s) {sorted(missing)}.",
                source_path,
            )

        layer_affinity = payload["layer_affinity"]
        if not isinstance(layer_affinity, str) or layer_affinity not in _VALID_LAYERS:
            raise WalledFileParseError(
                f"Heading '## {current_heading}' (line {current_heading_line}): "
                f"layer_affinity '{layer_affinity}' is not a valid Layer literal; "
                f"allowed = {sorted(_VALID_LAYERS)}.",
                source_path,
            )

        sections.append(payload)
        blocks_for_current = []

    while i < n:
        line = lines[i]
        stripped = line.lstrip()

        # Section heading
        if stripped.startswith("## ") and not stripped.startswith("###"):
            _finalize_current()
            current_heading = stripped[3:].strip()
            current_heading_line = i + 1
            i += 1
            continue

        # YAML fence open
        if stripped.startswith("```yaml") or stripped.startswith("``` yaml"):
            if current_heading is None:
                raise WalledFileParseError(
                    f"YAML fenced block at line {i + 1} appears before any "
                    "'## <heading>' section.",
                    source_path,
                )
            fence_open_line = i + 1
            body_lines: list[str] = []
            i += 1
            closed = False
            while i < n:
                inner = lines[i]
                if inner.lstrip().startswith("```"):
                    closed = True
                    i += 1
                    break
                body_lines.append(inner)
                i += 1
            if not closed:
                raise WalledFileParseError(
                    f"Heading '## {current_heading}': unterminated yaml fence "
                    f"opened at line {fence_open_line}.",
                    source_path,
                )
            blocks_for_current.append(("\n".join(body_lines), fence_open_line))
            continue

        i += 1

    _finalize_current()
    return sections


# -----------------------------------------------------------------------------
# Build helpers
# -----------------------------------------------------------------------------


def _slug_from_concept(concept: str) -> str:
    return concept.strip().replace(" ", "_")


def _humanize_concept(concept: str) -> str:
    return concept.strip().title()


def _record_from_payload(payload: dict[str, Any]) -> MemoryRecord:
    concept = str(payload["concept"]).strip()
    slug = _slug_from_concept(concept)
    layer_affinity = payload["layer_affinity"]
    tags = list(payload["tags"])
    premise_fragment = str(payload["premise_fragment"])
    synthesis_fragment = str(payload["synthesis_fragment"])

    return MemoryRecord(
        id=f"walled_{slug}",
        layer="hooplehopper_totality",
        record_type="walled_atom",
        title=_humanize_concept(concept),
        text=f"Premise: {premise_fragment}\n\nSynthesis: {synthesis_fragment}",
        metadata=MemoryMetadata(
            canon_status="synthetic_behavioral",
            visibility="private_to_vuorse",
            tags=tags,
            source_file="hooplehopper_totality/debriefing_walled.md",
            source_confidence="walled_atom",
            layer_affinity=layer_affinity,
        ),
        retrieval=RetrievalMetadata(
            priority=4,
            embedding_weight="low",
            query_hints=tags,
        ),
        behavior=BehaviorPolicy(
            may_state_as_fact=False,
            may_use_for_voice=True,
            may_reveal_to_user=False,
        ),
    )


def _build_jsonl_text(md_path: Path) -> str:
    if not md_path.exists():
        raise WalledFileMissingError(md_path)

    content = md_path.read_text(encoding="utf-8")
    payloads = _parse_md_sections(content, md_path)
    if not payloads:
        raise WalledFileEmptyError(md_path)

    lines: list[str] = []
    for payload in payloads:
        record = _record_from_payload(payload)
        lines.append(record.model_dump_json(exclude_none=True))
    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# Public build API
# -----------------------------------------------------------------------------


def build_walled(md_path: Path, jsonl_path: Path) -> int:
    """Build the JSONL projection of ``md_path`` and write it to ``jsonl_path``.

    Returns the count of records written.
    """
    jsonl_text = _build_jsonl_text(md_path)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(jsonl_text, encoding="utf-8")
    return jsonl_text.count("\n")


def build_walled_check(md_path: Path, jsonl_path: Path) -> bool:
    """Return True iff regenerating from ``md_path`` would byte-equal ``jsonl_path``."""
    if not md_path.exists():
        raise WalledFileMissingError(md_path)
    if not jsonl_path.exists():
        raise WalledFileMissingError(jsonl_path)
    expected = _build_jsonl_text(md_path)
    actual = jsonl_path.read_text(encoding="utf-8")
    return expected == actual


# -----------------------------------------------------------------------------
# Public load API
# -----------------------------------------------------------------------------


def load_walled_atoms(
    jsonl_path: Path, *, preserve_order: bool = False
) -> list[LoreAtom]:
    """Load a walled JSONL back into ``LoreAtom`` objects.

    By default sorts by ``concept`` (lexicographic, stable). Pass
    ``preserve_order=True`` to receive records in JSONL source order.
    """
    if not jsonl_path.exists():
        raise WalledFileMissingError(jsonl_path)

    records: list[MemoryRecord] = []
    with jsonl_path.open("rb") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = orjson.loads(line)
                record = MemoryRecord.model_validate(obj)
            except (orjson.JSONDecodeError, ValidationError) as exc:
                raise WalledFileParseError(
                    f"{jsonl_path}:{line_no}: malformed walled record: {exc}",
                    jsonl_path,
                ) from exc
            records.append(record)

    if not records:
        raise WalledFileEmptyError(jsonl_path)

    atoms: list[LoreAtom] = []
    for idx, record in enumerate(records, start=1):
        layer_affinity = record.metadata.layer_affinity
        if layer_affinity is None:
            raise WalledFileParseError(
                f"{jsonl_path}: record #{idx} (id={record.id!r}) has no "
                "metadata.layer_affinity; walled atoms require it.",
                jsonl_path,
            )

        concept_slug = record.id.removeprefix("walled_")
        concept = concept_slug.replace("_", " ")

        text = record.text
        if "\n\nSynthesis:" not in text:
            raise WalledFileParseError(
                f"{jsonl_path}: record #{idx} (id={record.id!r}) text does "
                "not contain '\\n\\nSynthesis:' separator.",
                jsonl_path,
            )
        premise_part, synthesis_part = text.split("\n\nSynthesis:", 1)
        if not premise_part.startswith("Premise: "):
            raise WalledFileParseError(
                f"{jsonl_path}: record #{idx} (id={record.id!r}) text does "
                "not start with 'Premise: '.",
                jsonl_path,
            )
        premise_fragment = premise_part[len("Premise: ") :]
        synthesis_fragment = synthesis_part.lstrip()

        atoms.append(
            LoreAtom(
                concept=concept,
                layer_affinity=layer_affinity,
                tags=list(record.metadata.tags),
                premise_fragment=premise_fragment,
                synthesis_fragment=synthesis_fragment,
            )
        )

    if not preserve_order:
        atoms.sort(key=lambda a: a.concept)
    return atoms
