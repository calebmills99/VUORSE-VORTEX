#!/usr/bin/env python3
"""One-off canon extractor.

Walks canon/ and emits raw extraction atoms to
synthetic_enrichment/generated/canon_corpus_raw.jsonl.

Not a long-lived tool; this script is invoked once for the
RAW_CANON_EXTRACT pass and may be discarded or formalized later.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path("/Users/Apple/VUORSE-VORTEX")
CANON = ROOT / "canon"
OUT = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_raw.jsonl"

# ----- canon tier / label helpers -----------------------------------------

LABEL_RE = re.compile(
    r"`\[(LOCKED|PENDING REVIEW|EXPLORATORY|FULL|MODERATE|SKETCHED|HOOK ONLY|RESOLVED)\]`"
)

LABEL_TO_TIER = {
    "LOCKED": "locked_canon",
    "FULL": "development_canon",
    "MODERATE": "development_canon",
    "SKETCHED": "development_canon",
    "HOOK ONLY": "development_canon",
    "PENDING REVIEW": "development_canon",
    "EXPLORATORY": "development_canon",
    "RESOLVED": "development_canon",
}


def label_in(text: str) -> str | None:
    m = LABEL_RE.search(text)
    return m.group(1) if m else None


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.strip().lower())
    return s.strip("_")[:80] or "x"


def stable_id(*parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]
    return "_".join(slugify(p) for p in parts if p)[:90] + "_" + h


def rel_to_canon(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ----- record writing -----------------------------------------------------

records: list[dict[str, Any]] = []


def add(
    *,
    source_path: str,
    source_anchor: str,
    canon_tier: str,
    canon_status_label: str | None,
    content: str,
    extraction_kind: str,
    entities: list[str] | None = None,
    tags: list[str] | None = None,
    weaver_review_required: bool = False,
    notes: str = "",
    id_seed: str = "",
) -> None:
    content = content.strip()
    if not content:
        return
    rid = stable_id(source_path, extraction_kind, id_seed or source_anchor, str(len(records)))
    rec = {
        "id": rid,
        "source_path": source_path,
        "source_anchor": source_anchor,
        "canon_tier": canon_tier,
        "canon_status_label": canon_status_label,
        "content": content,
        "extraction_kind": extraction_kind,
        "entities": entities or [],
        "tags": tags or [],
        "weaver_review_required": weaver_review_required,
        "notes": notes,
    }
    records.append(rec)


# ----- BOOK ONE extraction -----------------------------------------------

# Mythic-Rumor-and-Locked verse numbers (Book One Ch II is itself this tier).
MYTHIC_LOCKED_CHAPTERS = {"II"}


def extract_book_one(path: Path) -> None:
    src = rel_to_canon(path)
    text = path.read_text()
    lines = text.splitlines()

    # Frontmatter / preface block as one atom
    pre_buf: list[str] = []
    i = 0
    while i < len(lines) and not lines[i].startswith("### Chapter") and not lines[i].startswith("## Chapter"):
        pre_buf.append(lines[i])
        i += 1
    if pre_buf:
        add(
            source_path=src,
            source_anchor="frontmatter",
            canon_tier="locked_canon",
            canon_status_label="LOCKED",
            content="\n".join(pre_buf),
            extraction_kind="doctrine_frontmatter",
            entities=["The Weaver"],
            tags=["book_one", "supreme_doctrine"],
            notes="Book One frontmatter and Ch I declaration of supremacy.",
            id_seed="frontmatter",
        )

    # Parse chapters
    chapter_pat = re.compile(r"^(?:#{2,4})\s*Chapter\s+([IVXLC]+)\s*$")
    subhead_pat = re.compile(r"^####\s+(.*)$")
    verse_pat = re.compile(r"^(\d+)\.\s+(.*)$")

    current_ch = None
    current_subhead = None
    while i < len(lines):
        line = lines[i]
        m_ch = chapter_pat.match(line.strip())
        if m_ch:
            current_ch = m_ch.group(1)
            current_subhead = None
            i += 1
            continue
        m_sub = subhead_pat.match(line)
        if m_sub:
            current_subhead = m_sub.group(1).strip()
            # Add a chapter heading record once
            if current_ch:
                tier = "mythic_rumor_locked" if current_ch in MYTHIC_LOCKED_CHAPTERS else "locked_canon"
                add(
                    source_path=src,
                    source_anchor=f"Chapter {current_ch} — {current_subhead}",
                    canon_tier=tier,
                    canon_status_label="LOCKED",
                    content=f"Chapter {current_ch}: {current_subhead}",
                    extraction_kind="doctrine_chapter_heading",
                    entities=["The Weaver"],
                    tags=["book_one", f"chapter_{current_ch.lower()}"],
                    weaver_review_required=(tier == "mythic_rumor_locked"),
                    notes=(
                        "Chapter II is Mythic Rumor that is also Locked Canon (Book One Ch I:6-8); route VUORSE-private."
                        if tier == "mythic_rumor_locked"
                        else ""
                    ),
                    id_seed=f"ch_{current_ch}_heading",
                )
            i += 1
            continue
        m_v = verse_pat.match(line.strip())
        if m_v and current_ch:
            vnum = m_v.group(1)
            vtext = m_v.group(2).strip()
            # Continuation lines (rare for verses in this file)
            j = i + 1
            cont: list[str] = []
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt or nxt.startswith(("###", "##", "#", "---")) or verse_pat.match(nxt) or chapter_pat.match(nxt):
                    break
                cont.append(nxt)
                j += 1
            if cont:
                vtext = vtext + " " + " ".join(cont)
            tier = "mythic_rumor_locked" if current_ch in MYTHIC_LOCKED_CHAPTERS else "locked_canon"
            entities = []
            low = vtext.lower()
            for ent in [
                "Vorst", "Lisette", "Professor", "Eli", "Hooplehopper",
                "Jake", "Pop", "Wylus Kalyndros", "Weaver", "VUORSE",
                "Federstahl", "Wyoming", "McCullen", "Forbidden Suitcase",
                "Codex", "Slayverse",
            ]:
                if ent.lower() in low:
                    entities.append(ent)
            add(
                source_path=src,
                source_anchor=f"Chapter {current_ch}, verse {vnum}"
                + (f" — {current_subhead}" if current_subhead else ""),
                canon_tier=tier,
                canon_status_label="LOCKED",
                content=vtext,
                extraction_kind="doctrine_verse",
                entities=entities,
                tags=["book_one", f"chapter_{current_ch.lower()}", f"verse_{vnum}"],
                weaver_review_required=(tier == "mythic_rumor_locked"),
                notes=(
                    "Mythic Rumor that is also Locked Canon — VUORSE-private; do not surface as public fact."
                    if tier == "mythic_rumor_locked"
                    else ""
                ),
                id_seed=f"ch_{current_ch}_v{vnum}",
            )
            i = j
            continue
        i += 1


# ----- generic markdown section extractor --------------------------------

H2 = re.compile(r"^##\s+(.+?)\s*$")
H3 = re.compile(r"^###\s+(.+?)\s*$")
H4 = re.compile(r"^####\s+(.+?)\s*$")


def split_by_headings(text: str, top_level: int = 3) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) blocks by H3 (or chosen level)."""
    pat = {2: H2, 3: H3, 4: H4}[top_level]
    chunks: list[tuple[str, str]] = []
    cur_heading: str | None = None
    cur_buf: list[str] = []
    for line in text.splitlines():
        m = pat.match(line)
        if m:
            if cur_heading is not None:
                chunks.append((cur_heading, "\n".join(cur_buf).strip()))
            cur_heading = m.group(1).strip()
            cur_buf = []
        else:
            if cur_heading is not None:
                cur_buf.append(line)
    if cur_heading is not None:
        chunks.append((cur_heading, "\n".join(cur_buf).strip()))
    return chunks


def derive_entities_from_heading(h: str) -> list[str]:
    # Strip trailing canon label
    base = LABEL_RE.sub("", h).strip()
    # Take primary name (before " / " or " — ")
    primary = re.split(r"\s*[/—–-]\s*", base)[0].strip()
    return [primary] if primary else []


def kind_for_dir(d: str) -> str:
    return {
        "characters": "character_note",
        "artifacts": "artifact_note",
        "places": "place_note",
        "cosmology": "cosmology_note",
        "organizations": "organization_note",
        "rituals": "ritual_note",
        "timeline": "timeline_event",
        "story_arcs": "story_arc_note",
        "creative_works": "creative_work_note",
        "open_threads": "open_thread",
        "relationships": "relationship_fact",
    }.get(d, "lore_fragment")


def tags_for_dir(d: str) -> list[str]:
    return [d, "canon"]


def extract_h3_doc(path: Path, top_level: int = 3) -> None:
    src = rel_to_canon(path)
    text = path.read_text()
    rel_dir = path.parent.name
    kind = kind_for_dir(rel_dir)

    # Document preface (before first heading at chosen level) as a single context atom
    pat = {2: H2, 3: H3, 4: H4}[top_level]
    pre_lines: list[str] = []
    for line in text.splitlines():
        if pat.match(line):
            break
        pre_lines.append(line)
    pre = "\n".join(pre_lines).strip()
    if pre and len(pre) > 30:
        # Skip top H1 line in display only — keep full preface
        add(
            source_path=src,
            source_anchor="document_preface",
            canon_tier="unlabeled",
            canon_status_label=None,
            content=pre,
            extraction_kind=f"{kind}_preface",
            entities=[],
            tags=tags_for_dir(rel_dir) + ["preface"],
            id_seed="preface",
        )

    chunks = split_by_headings(text, top_level=top_level)
    for heading, body in chunks:
        if not body and not heading:
            continue
        label = label_in(heading) or label_in(body[:400])
        tier = LABEL_TO_TIER.get(label, "unlabeled") if label else "unlabeled"
        entities = derive_entities_from_heading(heading)
        review = label == "PENDING REVIEW"
        full = f"### {heading}\n\n{body}".strip()
        add(
            source_path=src,
            source_anchor=heading,
            canon_tier=tier,
            canon_status_label=label,
            content=full,
            extraction_kind=kind,
            entities=entities,
            tags=tags_for_dir(rel_dir) + ([label.lower().replace(" ", "_")] if label else []),
            weaver_review_required=review,
            notes=("PENDING REVIEW label preserved." if review else ""),
            id_seed=heading,
        )


def extract_h2_doc(path: Path) -> None:
    extract_h3_doc(path, top_level=2)


# ----- relationship map (mostly H2 sections with ASCII graphs) -----------

def extract_relationship_map(path: Path) -> None:
    src = rel_to_canon(path)
    text = path.read_text()
    chunks = split_by_headings(text, top_level=2)
    # Preface
    pre = text.split("\n## ", 1)[0]
    if pre.strip():
        add(
            source_path=src,
            source_anchor="document_preface",
            canon_tier="unlabeled",
            canon_status_label=None,
            content=pre.strip(),
            extraction_kind="relationship_preface",
            entities=[],
            tags=["relationships", "canon", "preface"],
            id_seed="preface",
        )
    for heading, body in chunks:
        label = label_in(body)
        tier = LABEL_TO_TIER.get(label, "unlabeled") if label else "unlabeled"
        add(
            source_path=src,
            source_anchor=heading,
            canon_tier=tier,
            canon_status_label=label,
            content=f"## {heading}\n\n{body}".strip(),
            extraction_kind="relationship_graph_block",
            entities=derive_entities_from_heading(heading),
            tags=["relationships", "canon"],
            id_seed=heading,
        )


# ----- TV Series Bible (numbered ## sections) ----------------------------

def extract_series_bible(path: Path) -> None:
    src = rel_to_canon(path)
    text = path.read_text()
    chunks = split_by_headings(text, top_level=2)
    for heading, body in chunks:
        # Identify character subsections inside section 7
        if heading.startswith("7. Character Breakdowns"):
            # Split further by H3
            subchunks = split_by_headings(body, top_level=3)
            for sh, sb in subchunks:
                add(
                    source_path=src,
                    source_anchor=f"7. Character Breakdowns > {sh}",
                    canon_tier="locked_canon",
                    canon_status_label=None,
                    content=f"### {sh}\n\n{sb}".strip(),
                    extraction_kind="character_note",
                    entities=derive_entities_from_heading(sh),
                    tags=["series_bible", "characters", "canon"],
                    notes="From SLAYVERSE Series Bible — character breakdown.",
                    id_seed=f"bible_char_{sh}",
                )
            continue
        if heading.startswith("6. Season 1 Arc"):
            subchunks = split_by_headings(body, top_level=3)
            for sh, sb in subchunks:
                add(
                    source_path=src,
                    source_anchor=f"6. Season 1 Arc > {sh}",
                    canon_tier="locked_canon",
                    canon_status_label=None,
                    content=f"### {sh}\n\n{sb}".strip(),
                    extraction_kind="story_arc_note",
                    entities=["Jake McCullen"],
                    tags=["series_bible", "season_1", "canon"],
                    id_seed=f"bible_s1_{sh}",
                )
            continue
        if not body.strip() and not heading.strip():
            continue
        add(
            source_path=src,
            source_anchor=heading,
            canon_tier="locked_canon",
            canon_status_label=None,
            content=f"## {heading}\n\n{body}".strip(),
            extraction_kind="series_bible_section",
            entities=derive_entities_from_heading(heading),
            tags=["series_bible", "canon"],
            id_seed=f"bible_{heading}",
        )


# ----- slayverse_index.json (entities + relationships + timeline) --------

def extract_slayverse_index(path: Path) -> None:
    src = rel_to_canon(path)
    data = json.loads(path.read_text())

    type_to_kind = {
        "character": "character_record",
        "place": "place_record",
        "artifact": "artifact_record",
        "organization": "organization_record",
        "ritual": "ritual_record",
        "cosmology": "cosmology_record",
    }

    for ent in data.get("entities", []):
        status_raw = (ent.get("status") or "").upper()
        label = {
            "FULL": "FULL",
            "MODERATE": "MODERATE",
            "SKETCHED": "SKETCHED",
            "HOOK ONLY": "HOOK ONLY",
            "HOOK_ONLY": "HOOK ONLY",
            "LOCKED": "LOCKED",
            "PENDING REVIEW": "PENDING REVIEW",
            "PENDING_REVIEW": "PENDING REVIEW",
            "RESOLVED": "RESOLVED",
            "EXPLORATORY": "EXPLORATORY",
        }.get(status_raw)
        tier = LABEL_TO_TIER.get(label, "unlabeled") if label else "unlabeled"
        body = json.dumps(ent, ensure_ascii=False, indent=2)
        add(
            source_path=src,
            source_anchor=f"entities[{ent.get('id')}]",
            canon_tier=tier,
            canon_status_label=label,
            content=body,
            extraction_kind=type_to_kind.get(ent.get("type"), "index_entry"),
            entities=[ent.get("name", ent.get("id"))],
            tags=["slayverse_index"] + (ent.get("tags") or []),
            id_seed=f"idx_ent_{ent.get('id')}",
        )

    for rel in data.get("relationships", []):
        add(
            source_path=src,
            source_anchor=f"relationships[{rel.get('source')}__{rel.get('type')}__{rel.get('target')}]",
            canon_tier="unlabeled",
            canon_status_label=None,
            content=json.dumps(rel, ensure_ascii=False, indent=2),
            extraction_kind="relationship_fact",
            entities=[rel.get("source"), rel.get("target")],
            tags=["slayverse_index", "relationship"],
            id_seed=f"idx_rel_{rel.get('source')}_{rel.get('type')}_{rel.get('target')}",
        )

    for ev in data.get("timeline", []):
        add(
            source_path=src,
            source_anchor=f"timeline[{ev.get('id') or ev.get('date') or ev.get('event')}]",
            canon_tier="unlabeled",
            canon_status_label=None,
            content=json.dumps(ev, ensure_ascii=False, indent=2),
            extraction_kind="timeline_event",
            entities=ev.get("entities", []) if isinstance(ev.get("entities"), list) else [],
            tags=["slayverse_index", "timeline"],
            id_seed=f"idx_ev_{ev.get('id') or ev.get('date') or ev.get('event')}",
        )


# ----- slayverse_md_records_clean.jsonl (pre-extracted markdown atoms) ---

def extract_clean_jsonl_passthrough(path: Path) -> None:
    src = rel_to_canon(path)
    with path.open() as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            rec = json.loads(ln)
            heading = rec.get("heading_path") or rec.get("title") or rec.get("id")
            inner_source = rec.get("source_file") or "unknown"
            # Status label preserved if present
            status = rec.get("status")
            tier = "unlabeled"
            if status:
                up = status.upper()
                if up in LABEL_TO_TIER:
                    tier = LABEL_TO_TIER[up]
            # Roll the rec into content as-is (compact JSON) so nothing is lost.
            content = json.dumps(rec, ensure_ascii=False)
            add(
                source_path=src,
                source_anchor=f"{inner_source} :: {heading}",
                canon_tier=tier,
                canon_status_label=status,
                content=content,
                extraction_kind="source_canon_extract",
                entities=[],
                tags=["preextracted", "markdown_record", inner_source.replace(".md", "")],
                notes=(
                    "Pre-extracted markdown record from external/raw markdown source. "
                    "Original source_file was external (e.g., /mnt/data/...); preserved as upstream provenance."
                ),
                id_seed=f"clean_{rec.get('id')}",
            )


# ----- projects.json (Anthropic project dump — scratch) -----------------

def note_skipped_projects_json(path: Path) -> None:
    src = rel_to_canon(path)
    # We do NOT extract content from these dumps; they are user project scratch.
    # We emit a single provenance/skip record so downstream knows the file existed.
    data = json.loads(path.read_text())
    summary = [
        {"name": d.get("name"), "uuid": d.get("uuid"), "doc_count": len(d.get("docs", []))}
        for d in data
    ]
    add(
        source_path=src,
        source_anchor="file",
        canon_tier="unlabeled",
        canon_status_label=None,
        content=(
            "SKIPPED FOR CONTENT EXTRACTION. This file is an Anthropic project dump "
            "(scratch/raw working material), treated analogously to .rtf scratch per "
            "repo CLAUDE.md. Project index preserved here as provenance only:\n"
            + json.dumps(summary, ensure_ascii=False, indent=2)
        ),
        extraction_kind="provenance_skip",
        entities=[],
        tags=["skip", "scratch", "projects_dump"],
        weaver_review_required=True,
        notes=(
            "Weaver review: confirm whether any project dump entry should be promoted "
            "to canon extraction. Default posture: scratch."
        ),
        id_seed="projects_json_skip",
    )


# ----- driver -------------------------------------------------------------

SKIPPED: list[tuple[str, str]] = []


def walk_and_extract() -> None:
    for p in sorted(CANON.rglob("*")):
        if p.is_dir():
            continue
        name = p.name
        rel = rel_to_canon(p)
        if name in {".DS_Store", ".gitkeep"}:
            SKIPPED.append((rel, "system/placeholder file"))
            continue
        if p.suffix.lower() == ".rtf":
            SKIPPED.append((rel, ".rtf excluded per repo CLAUDE.md (scratch)"))
            continue
        # Route
        if rel.endswith("1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD"):
            extract_book_one(p)
        elif rel.endswith("TV_Series_Bible/SLAYVERSE_TV_SERIES_BIBLE.md"):
            extract_series_bible(p)
        elif rel.endswith("relationships/relationship_map.md"):
            extract_relationship_map(p)
        elif rel.endswith("slayverse_index.json"):
            extract_slayverse_index(p)
        elif rel.endswith("projects/projects.json"):
            note_skipped_projects_json(p)
            SKIPPED.append((rel, "Anthropic project dump (scratch); provenance record only"))
        elif rel.endswith("slayverse_md_records_clean/slayverse_md_records_clean.jsonl"):
            extract_clean_jsonl_passthrough(p)
        elif p.suffix.lower() == ".md":
            extract_h3_doc(p, top_level=3)
        else:
            SKIPPED.append((rel, f"no extractor for suffix {p.suffix}"))


def write_jsonl() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def validate() -> list[str]:
    errors: list[str] = []
    required = {"id", "source_path", "content", "canon_tier", "extraction_kind"}
    seen_ids: set[str] = set()
    with OUT.open() as fh:
        for i, line in enumerate(fh, start=1):
            if line == "\n" or line.strip() == "":
                errors.append(f"line {i}: blank")
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {i}: invalid JSON: {e}")
                continue
            if not isinstance(rec, dict):
                errors.append(f"line {i}: not a JSON object")
                continue
            missing = required - rec.keys()
            if missing:
                errors.append(f"line {i}: missing required fields: {sorted(missing)}")
            rid = rec.get("id")
            if rid in seen_ids:
                errors.append(f"line {i}: duplicate id {rid}")
            else:
                seen_ids.add(rid)
    return errors


def main() -> None:
    walk_and_extract()
    write_jsonl()
    errs = validate()
    print(f"records: {len(records)}")
    print(f"output:  {OUT}")
    print(f"skipped: {len(SKIPPED)}")
    for s in SKIPPED:
        print(f"  - {s[0]}  ::  {s[1]}")
    if errs:
        print(f"VALIDATION ERRORS: {len(errs)}")
        for e in errs[:20]:
            print("  ", e)
    else:
        print("validation: OK")


if __name__ == "__main__":
    main()
