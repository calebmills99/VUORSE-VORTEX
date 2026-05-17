#!/usr/bin/env python3
"""One-off canon semantic sift.

Reads synthetic_enrichment/generated/canon_corpus_raw.jsonl and writes:
  - synthetic_enrichment/generated/canon_corpus_semantic_sift.jsonl
  - synthetic_enrichment/generated/canon_corpus_semantic_sift_report.md

Read-only against the corpus. Adds semantic ontology fields to every record
without altering existing fields. Preserves every record (no merges, no
discards). Conservative rule order: explicit extraction_kind -> Slayverse
named-entity overrides -> file-stem heuristic -> content keyword heuristic ->
UNKNOWN. Anything ambiguous, sealed, or low-signal is routed to
needs_weaver_review=True.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path("/Users/Apple/VUORSE-VORTEX")
IN_PATH = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_raw.jsonl"
OUT_JSONL = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_semantic_sift.jsonl"
OUT_MD = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_semantic_sift_report.md"

ALLOWED_CLASSES = {
    "PERSON",
    "PLACE",
    "THING",
    "IDEA",
    "EVENT",
    "RELATIONSHIP",
    "CREATIVE_WORK",
    "PROCESS",
    "UNKNOWN",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}


# ---------------------------------------------------------------------------
# Slayverse special-handling tables
# ---------------------------------------------------------------------------

# Named entity -> default class. Lowercased substring match against an entity
# string drawn from the input record's `entities` list (and as fallback the
# title/body).
ENTITY_CLASS_OVERRIDES: list[tuple[str, str, str]] = [
    # PERSON
    ("vuorse", "PERSON", "VUORSE is a person/oracle"),
    ("the weaver", "PERSON", "The Weaver is the arbiter (person)"),
    ("weaver", "PERSON", "The Weaver is the arbiter (person)"),
    ("jake mccullen", "PERSON", "Jake McCullen is the Wyoming protagonist"),
    ("jake", "PERSON", "Jake (likely Jake McCullen)"),
    ("pop mccullen", "PERSON", "Pop McCullen is Jake's father"),
    ("pop", "PERSON", "Pop is Jake's father"),
    ("eli", "PERSON", "Eli is the lattice-key teen"),
    ("cici", "PERSON", "Cici is a character"),
    ("dr. slayton", "PERSON", "Dr. Slayton is a character"),
    ("dr slayton", "PERSON", "Dr. Slayton is a character"),
    ("slayton", "PERSON", "Slayton (likely Dr. Slayton)"),
    ("vorst", "PERSON", "Vorst is principled antagonist"),
    ("dr. vorst", "PERSON", "Dr. Vorst is principled antagonist"),
    ("professor von hooplehopper", "PERSON", "The Professor (Immaculate Slayception child)"),
    ("the professor", "PERSON", "The Professor"),
    ("lisette", "PERSON", "Lisette von Hooplehopper"),
    ("hildebrand", "PERSON", "Hildebrand von Hooplehopper (12th c. knight)"),
    ("adelram", "PERSON", "Adelram the Swan-Alchemist"),
    ("wylus kalyndros", "PERSON", "Wylus Kalyndros (rumored webweaver)"),
    ("conrad", "PERSON", "Conrad von Hooplehopper"),
    # PLACE
    ("mccullen ranch", "PLACE", "McCullen Ranch is a Wyoming location"),
    ("club cosmic", "PLACE", "Club Cosmic is a venue"),
    ("schloss eisensang", "PLACE", "Schloss Eisensang is a castle"),
    ("mirror cavern", "PLACE", "Mirror Cavern is a place"),
    ("tyndall", "PLACE", "Tyndall airfield"),
    ("velvet archive", "PLACE", "Velvet Archive treated here as a place/archive"),
    ("federstahl institute", "PERSON", "Federstahl Institute as collective agent"),
    # THING / artifact
    ("forbidden suitcase", "THING", "Forbidden Suitcase is an artifact"),
    ("the suitcase", "THING", "The Suitcase is an artifact"),
    ("dustbrand", "THING", "Dustbrand Sigil is an artifact-symbol"),
    ("hildebrand's ring", "THING", "Hildebrand's Ring is an artifact"),
    ("zerethium quartz", "THING", "Zerethium Quartz is a substance"),
    ("glamoron", "THING", "Glamorons treated as particles"),
    ("glamourons", "THING", "Glamourons treated as particles"),
    ("shard", "THING", "Shard artifact"),
    # IDEA (force / doctrine / cosmology)
    ("slayton field", "IDEA", "Slayton Field as cosmic force/concept"),
    ("slayton force", "IDEA", "Slayton Force as cosmic concept"),
    ("the thread", "IDEA", "The Thread as metaphysical principle"),
    ("thread", "IDEA", "Thread as metaphysical principle"),
    ("soul-line", "IDEA", "Soul-line doctrine"),
    ("soul line", "IDEA", "Soul-line doctrine"),
    ("hooplehopper soul-line", "IDEA", "Hooplehopper soul-line doctrine"),
    # EVENT
    ("crystal lattice incident", "EVENT", "Crystal Lattice Incident is an event"),
    ("lattice incident", "EVENT", "Lattice Incident is an event"),
    ("federstahl catastrophe", "EVENT", "Federstahl Catastrophe is an event"),
    ("immaculate slayception", "EVENT", "Immaculate Slayception is an event"),
    ("tragedy of splat", "EVENT", "Tragedy of Splat is an event"),
    # CREATIVE_WORK
    ("words of the weaver", "CREATIVE_WORK", "Book One is a creative work"),
    ("book one", "CREATIVE_WORK", "Book One is a creative work"),
    ("series bible", "CREATIVE_WORK", "Series Bible is a creative work"),
    ("slayverse series bible", "CREATIVE_WORK", "Series Bible is a creative work"),
    # collective agent vs. doctrine — handled contextually elsewhere
    ("hooplehoppers", "PERSON", "Hooplehoppers as collective characters/agents"),
    ("golden wingers intergalactic league", "PERSON", "League as collective agent"),
    ("golden wingers", "PERSON", "Golden Wingers as collective agent"),
]


# extraction_kind -> (class, confidence, reason). Confidence may be raised or
# lowered later by sanity checks.
KIND_DEFAULTS: dict[str, tuple[str, str, str]] = {
    "doctrine_frontmatter": ("IDEA", "high", "Book One frontmatter -> doctrine/IDEA"),
    "doctrine_chapter_heading": ("IDEA", "high", "Book One chapter heading -> doctrine/IDEA"),
    "doctrine_verse": ("IDEA", "high", "Book One verse -> doctrine/IDEA"),
    "character_record": ("PERSON", "high", "character_record -> PERSON"),
    "character_note": ("PERSON", "high", "character_note -> PERSON"),
    "character_note_preface": ("PERSON", "medium", "character_note_preface -> PERSON (section header)"),
    "place_record": ("PLACE", "high", "place_record -> PLACE"),
    "place_note": ("PLACE", "high", "place_note -> PLACE"),
    "place_note_preface": ("PLACE", "medium", "place_note_preface -> PLACE (section header)"),
    "artifact_record": ("THING", "high", "artifact_record -> THING"),
    "artifact_note": ("THING", "high", "artifact_note -> THING"),
    "artifact_note_preface": ("THING", "medium", "artifact_note_preface -> THING (section header)"),
    "ritual_record": ("EVENT", "high", "ritual_record -> EVENT (ritual-as-happening)"),
    "ritual_note": ("EVENT", "high", "ritual_note -> EVENT"),
    "ritual_note_preface": ("EVENT", "medium", "ritual_note_preface -> EVENT (section header)"),
    "organization_record": ("PERSON", "medium", "organization_record -> PERSON (collective agent)"),
    "organization_note": ("PERSON", "medium", "organization_note -> PERSON (collective agent)"),
    "organization_note_preface": ("PERSON", "low", "organization_note_preface -> PERSON (section header)"),
    "timeline_event": ("EVENT", "high", "timeline_event -> EVENT"),
    "timeline_event_preface": ("EVENT", "medium", "timeline_event_preface -> EVENT (section header)"),
    "relationship_fact": ("RELATIONSHIP", "high", "relationship_fact -> RELATIONSHIP"),
    "relationship_graph_block": ("RELATIONSHIP", "high", "relationship_graph_block -> RELATIONSHIP"),
    "relationship_preface": ("RELATIONSHIP", "medium", "relationship_preface -> RELATIONSHIP (section header)"),
    "story_arc_note": ("EVENT", "medium", "story_arc_note -> EVENT (arc-as-happening)"),
    "story_arc_note_preface": ("EVENT", "low", "story_arc_note_preface -> EVENT (section header)"),
    "cosmology_record": ("IDEA", "high", "cosmology_record -> IDEA"),
    "cosmology_note": ("IDEA", "high", "cosmology_note -> IDEA"),
    "cosmology_note_preface": ("IDEA", "medium", "cosmology_note_preface -> IDEA (section header)"),
    "open_thread": ("UNKNOWN", "low", "open_thread -> classify by dominant subject"),
    "open_thread_preface": ("PROCESS", "low", "open_thread_preface -> PROCESS (section header)"),
    "creative_work_note": ("CREATIVE_WORK", "high", "creative_work_note -> CREATIVE_WORK"),
    "creative_work_note_preface": ("CREATIVE_WORK", "medium", "creative_work_note_preface -> CREATIVE_WORK (section header)"),
    "series_bible_section": ("CREATIVE_WORK", "high", "series_bible_section -> CREATIVE_WORK"),
    "provenance_skip": ("PROCESS", "high", "provenance_skip -> PROCESS (tooling artifact)"),
    "source_canon_extract": ("UNKNOWN", "low", "source_canon_extract -> infer from title/body/entities/tags"),
}


# File-stem heuristic: when the record's tags include a known stem (from the
# slayverse_md_records_clean preextract corpus), this is the default class for
# the stem. Confidence is `medium` unless overridden by stronger signals later.
STEM_DEFAULTS: dict[str, tuple[str, str, str]] = {
    "characters": ("PERSON", "medium", "tag stem `characters`"),
    "places": ("PLACE", "medium", "tag stem `places`"),
    "artifacts": ("THING", "medium", "tag stem `artifacts`"),
    "Slayverse_Artifacts": ("THING", "low", "tag stem `Slayverse_Artifacts` (mixed; often off-topic)"),
    "rituals": ("EVENT", "medium", "tag stem `rituals` (ritual-as-happening)"),
    "organizations": ("PERSON", "medium", "tag stem `organizations` (collective agent)"),
    "timeline": ("EVENT", "medium", "tag stem `timeline`"),
    "story_arcs": ("EVENT", "medium", "tag stem `story_arcs` (arc-as-happening)"),
    "cosmology": ("IDEA", "medium", "tag stem `cosmology`"),
    "open_threads": ("UNKNOWN", "low", "tag stem `open_threads` (mixed; classify by subject)"),
    "relationship_map": ("RELATIONSHIP", "medium", "tag stem `relationship_map`"),
    "SLAYVERSE_TV_SERIES_BIBLE": ("CREATIVE_WORK", "medium", "tag stem series bible"),
    "writers-room.agent": ("PROCESS", "medium", "tag stem `writers-room.agent` (process/agent spec)"),
    "chat_digest_03142026": ("PROCESS", "low", "tag stem `chat_digest_03142026` (session/digest)"),
    "March_29th_2026": ("PROCESS", "low", "tag stem `March_29th_2026` (chat digest / process)"),
    "Slayverse_Chat": ("PROCESS", "low", "tag stem `Slayverse_Chat` (chat digest / process)"),
    "Hooplehopper-Legacy-Digest": ("UNKNOWN", "low", "tag stem `Hooplehopper-Legacy-Digest` (mixed; classify by subject)"),
    "The_Origin_Pure": ("CREATIVE_WORK", "low", "tag stem `The_Origin_Pure` (scene/script material)"),
    "Interweaving": ("PROCESS", "low", "tag stem `Interweaving` (mostly tooling/SFX chat)"),
    "Kodold": ("PROCESS", "low", "tag stem `Kodold` (mostly local-LLM tooling chat)"),
    "Diffusion": ("PROCESS", "low", "tag stem `Diffusion` (image-gen tooling chat)"),
    "cortex_test": ("PROCESS", "low", "tag stem `cortex_test` (system test material)"),
    "slayton_particle_discovery": ("EVENT", "medium", "tag stem `slayton_particle_discovery` (event)"),
}


# Keyword-based content scoring for the UNKNOWN bucket. Patterns map to a
# class with a small weight. Highest-scoring class wins; ties go to PROCESS
# when the record is tooling-style, else UNKNOWN.
CLASS_KEYWORDS: dict[str, list[tuple[re.Pattern[str], int]]] = {
    "PERSON": [
        (re.compile(r"\b(Jake|McCullen|Pop|Eli|Cici|Vorst|VUORSE|Weaver|Lisette|Hildebrand|Adelram|Conrad|Hooplehopper|Slayton)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(character|protagonist|antagonist|rancher|professor|knight|alchemist|oracle)\b", re.IGNORECASE), 1),
    ],
    "PLACE": [
        (re.compile(r"\b(Wyoming|ranch|castle|Schloss|cavern|airfield|Tyndall|Club Cosmic|Velvet Archive|venue|location)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(realm|kingdom|outpost|territory)\b", re.IGNORECASE), 1),
    ],
    "THING": [
        (re.compile(r"\b(suitcase|ring|shard|sigil|relic|artifact|dustbrand|glamoron|glamourons|quartz|substance)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(object|technology|device|tool|document)\b", re.IGNORECASE), 1),
    ],
    "IDEA": [
        (re.compile(r"\b(doctrine|cosmology|metaphysic|principle|prophecy|canon|theory|thread|soul-line|slayton field|slayton force)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(rule|law|symbolic|emotional law)\b", re.IGNORECASE), 1),
    ],
    "EVENT": [
        (re.compile(r"\b(lattice incident|catastrophe|immaculate slayception|tragedy of splat|summit|incident|happening|ritual|ceremony)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(season \d|episode|arc|finale|reveal|origin saga)\b", re.IGNORECASE), 2),
    ],
    "RELATIONSHIP": [
        (re.compile(r"\b(mother of|father of|son of|daughter of|antagonist of|companion of|temporal echo|lineage|successor|guardian)\b", re.IGNORECASE), 3),
        (re.compile(r"\bsoul-?line\b", re.IGNORECASE), 1),
    ],
    "CREATIVE_WORK": [
        (re.compile(r"\b(series bible|book one|codex entry|logline|treatment|pitch|script|transcript|chapter|verse|monologue)\b", re.IGNORECASE), 3),
    ],
    "PROCESS": [
        (re.compile(r"\b(workflow|protocol|pipeline|review loop|agent|JSONL|extraction|training|preset|plugin|launch|prompt|prompted|memory off|share)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(ChatGPT said|you said|SLAY MODE ACTIVATED|kobold|llama|render|tracking|comp)\b", re.IGNORECASE), 2),
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def gist(text: str | None, limit: int = 140) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", str(text)).strip()
    return t if len(t) <= limit else t[: limit - 1] + "…"


def md_escape(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ")


def safe_strs(xs: Any) -> list[str]:
    if not xs:
        return []
    out: list[str] = []
    for x in xs:
        if x is None:
            continue
        out.append(str(x))
    return out


def parse_inner(content: str | None) -> dict[str, Any]:
    """For source_canon_extract rows the outer content is a JSON-string
    encoding a markdown_section record. Try to peel it. Returns {} on failure."""
    if not content:
        return {}
    t = content.strip()
    if not (t.startswith("{") and t.endswith("}")):
        return {}
    try:
        v = json.loads(t)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def harvest_text_blob(rec: dict[str, Any]) -> str:
    """Combine fields that carry classifiable signal into one blob."""
    pieces: list[str] = []
    pieces.append(str(rec.get("content") or ""))
    pieces.extend(safe_strs(rec.get("entities")))
    pieces.extend(safe_strs(rec.get("tags")))
    pieces.append(str(rec.get("source_anchor") or ""))
    inner = parse_inner(rec.get("content"))
    if inner:
        pieces.append(str(inner.get("title") or ""))
        pieces.append(str(inner.get("summary") or ""))
        pieces.append(str(inner.get("text") or ""))
        pieces.append(" ".join(safe_strs(inner.get("heading_path"))))
    return " \n ".join(p for p in pieces if p)


def primary_entity_name(rec: dict[str, Any]) -> str:
    ents = safe_strs(rec.get("entities"))
    if ents:
        # Skip generic-only entity strings
        for e in ents:
            if e.strip():
                return e.strip()
    inner = parse_inner(rec.get("content"))
    title = (inner.get("title") if inner else "") or ""
    title = title.strip()
    if title and title.lower() not in {"document preamble", "markdown", "chatgpt said:", "prompt:", "key features include:", "issue recap:", "thought for 7s"}:
        return title
    anchor = (rec.get("source_anchor") or "").strip()
    if anchor:
        return anchor
    if title:
        return title
    return ""


def secondary_entity_names(rec: dict[str, Any], primary: str) -> list[str]:
    out: list[str] = []
    seen = {primary.lower()}
    for e in safe_strs(rec.get("entities")):
        e2 = e.strip()
        if e2 and e2.lower() not in seen:
            out.append(e2)
            seen.add(e2.lower())
    return out[:10]


def entity_override(rec: dict[str, Any]) -> tuple[str, str, str] | None:
    """If any entity (or title) matches a named-entity override, return it.

    Walks ENTITY_CLASS_OVERRIDES in declaration order; first hit wins. This
    means more specific entries should come before broader ones (handled in
    the table above).
    """
    ents_lower = [e.lower() for e in safe_strs(rec.get("entities"))]
    inner = parse_inner(rec.get("content"))
    title_l = (inner.get("title") or "").lower() if inner else ""
    anchor_l = (rec.get("source_anchor") or "").lower()
    haystack_strings = ents_lower + [title_l, anchor_l]
    for needle, cls, reason in ENTITY_CLASS_OVERRIDES:
        n = needle.lower()
        for h in haystack_strings:
            if n and n in h:
                return cls, "high", f"entity override: {reason}"
    return None


def keyword_classify(blob: str) -> tuple[str, str, str] | None:
    scores: dict[str, int] = defaultdict(int)
    for cls, patterns in CLASS_KEYWORDS.items():
        for pat, weight in patterns:
            if pat.search(blob):
                scores[cls] += weight
    if not scores:
        return None
    top = max(scores.values())
    winners = [c for c, s in scores.items() if s == top]
    # tie-break: prefer non-PROCESS narrative classes for lore-bearing text
    if len(winners) > 1 and "PROCESS" in winners and len(winners) > 1:
        non_process = [w for w in winners if w != "PROCESS"]
        if non_process:
            winners = non_process
    cls = winners[0]
    conf = "medium" if top >= 4 else "low"
    return cls, conf, f"keyword score {top} (winners: {','.join(winners)})"


def open_thread_classify(rec: dict[str, Any]) -> tuple[str, str, str]:
    """open_thread / open_threads: contradictions or process notes -> PROCESS;
    otherwise classify by dominant subject via keywords."""
    blob = harvest_text_blob(rec).lower()
    if any(
        kw in blob
        for kw in (
            "contradiction",
            "reconciliation",
            "policy",
            "audit",
            "review",
            "process",
            "open thread",
        )
    ):
        return "PROCESS", "medium", "open_thread reads as process/contradiction note"
    kw = keyword_classify(harvest_text_blob(rec))
    if kw is not None:
        cls, conf, reason = kw
        return cls, conf, f"open_thread dominant subject -> {reason}"
    return "UNKNOWN", "low", "open_thread with no dominant subject"


def stem_lookup(rec: dict[str, Any]) -> tuple[str, str, str] | None:
    tags = set(safe_strs(rec.get("tags")))
    for stem, payload in STEM_DEFAULTS.items():
        if stem in tags:
            return payload
    return None


def classify(rec: dict[str, Any]) -> tuple[str, str, str]:
    """Return (semantic_class, semantic_confidence, semantic_reason)."""
    kind = (rec.get("extraction_kind") or "").strip()

    # 1) Slayverse named-entity overrides take priority when they fire — they
    # are unambiguous high-signal anchors. Skip this for pure process /
    # tooling kinds where an incidental name shouldn't reclassify.
    if kind not in {"provenance_skip"}:
        ov = entity_override(rec)
        if ov is not None:
            return ov

    # 2) extraction_kind default.
    default = KIND_DEFAULTS.get(kind)
    if default is not None:
        cls, conf, reason = default
        # 2a) open_thread / source_canon_extract need content-driven inference.
        if kind in {"open_thread", "open_thread_preface"}:
            cls2, conf2, reason2 = open_thread_classify(rec)
            return cls2, conf2, reason2
        if kind == "source_canon_extract":
            # Try stem heuristic first.
            stem = stem_lookup(rec)
            if stem is not None:
                scls, sconf, sreason = stem
                # Keyword refinement: if keyword classify strongly disagrees
                # AND yields a high-signal narrative class, lift it. Otherwise
                # keep the stem default.
                kw = keyword_classify(harvest_text_blob(rec))
                if kw is not None and kw[0] != scls and kw[1] == "medium":
                    return kw[0], "low", f"stem `{stem}` suggested {scls} but content keywords lean {kw[0]} -> taking content lean at low confidence"
                return scls, sconf, sreason
            # No stem -> keyword fallback.
            kw = keyword_classify(harvest_text_blob(rec))
            if kw is not None:
                return kw[0], "low", f"source_canon_extract keyword fallback: {kw[2]}"
            return "UNKNOWN", "low", "source_canon_extract with no stem and no keyword hits"
        return cls, conf, reason

    # 3) Unknown extraction_kind -> keyword fallback.
    kw = keyword_classify(harvest_text_blob(rec))
    if kw is not None:
        return kw[0], "low", f"unknown extraction_kind '{kind}', keyword fallback: {kw[2]}"
    return "UNKNOWN", "low", f"unknown extraction_kind '{kind}' and no keyword hits"


def needs_review(
    rec: dict[str, Any], cls: str, conf: str
) -> bool:
    if conf == "low":
        return True
    if cls == "UNKNOWN":
        return True
    if rec.get("canon_tier") == "mythic_rumor_locked":
        return True
    # `weaver_review_required` true on input AND class is not obvious
    if rec.get("weaver_review_required") is True and conf != "high":
        return True
    return False


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------


def load_records(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except Exception as e:
                raise RuntimeError(f"input line {ln} not JSON: {e}") from e
    return out


def validate_jsonl(path: Path, expected_ids: set[str], expected_total: int) -> tuple[bool, list[str]]:
    errs: list[str] = []
    seen_ids: set[str] = set()
    n = 0
    with path.open("r", encoding="utf-8") as fh:
        for ln, raw in enumerate(fh, 1):
            if raw == "\n" or raw.strip() == "":
                errs.append(f"line {ln}: blank line")
                continue
            try:
                rec = json.loads(raw)
            except Exception as e:
                errs.append(f"line {ln}: not JSON: {e}")
                continue
            if not isinstance(rec, dict):
                errs.append(f"line {ln}: not a JSON object")
                continue
            for fld in ("id", "semantic_class", "semantic_confidence", "needs_weaver_review"):
                if fld not in rec:
                    errs.append(f"line {ln}: missing field `{fld}`")
            sc = rec.get("semantic_class")
            if sc not in ALLOWED_CLASSES:
                errs.append(f"line {ln}: invalid semantic_class {sc!r}")
            cf = rec.get("semantic_confidence")
            if cf not in ALLOWED_CONFIDENCE:
                errs.append(f"line {ln}: invalid semantic_confidence {cf!r}")
            nr = rec.get("needs_weaver_review")
            if not isinstance(nr, bool):
                errs.append(f"line {ln}: needs_weaver_review must be bool, got {type(nr).__name__}")
            if rec.get("id") in seen_ids:
                errs.append(f"line {ln}: duplicate id {rec.get('id')}")
            seen_ids.add(rec.get("id"))
            n += 1
    if n != expected_total:
        errs.append(f"record count mismatch: wrote {n}, expected {expected_total}")
    missing_ids = expected_ids - seen_ids
    extra_ids = seen_ids - expected_ids
    if missing_ids:
        errs.append(f"missing {len(missing_ids)} ids from input set")
    if extra_ids:
        errs.append(f"unexpected {len(extra_ids)} ids not in input set")
    return (len(errs) == 0), errs


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def render_report(
    enriched: list[dict[str, Any]],
    total_in: int,
    total_out: int,
    validation_ok: bool,
    validation_errs: list[str],
) -> str:
    class_counts = Counter(r["semantic_class"] for r in enriched)
    conf_counts = Counter(r["semantic_confidence"] for r in enriched)
    review_count = sum(1 for r in enriched if r["needs_weaver_review"])

    def by_class(cls: str) -> list[dict[str, Any]]:
        return [r for r in enriched if r["semantic_class"] == cls]

    def signal_rank(r: dict[str, Any]) -> tuple[int, int, int]:
        # Higher is better. Prefer: high confidence > clean primary entity > non-source_canon_extract default.
        c = {"high": 3, "medium": 2, "low": 1}[r["semantic_confidence"]]
        has_name = 1 if r.get("primary_entity_name") else 0
        kind_pen = 0 if r.get("extraction_kind") == "source_canon_extract" else 1
        return (c, has_name, kind_pen)

    def top_n(cls: str, n: int = 50) -> list[dict[str, Any]]:
        rs = by_class(cls)
        rs_sorted = sorted(rs, key=signal_rank, reverse=True)
        return rs_sorted[:n]

    def top_table(rs: list[dict[str, Any]]) -> list[str]:
        lines: list[str] = []
        lines.append("| id | source_path | primary_entity_name | gist |")
        lines.append("|---|---|---|---|")
        for r in rs:
            g = gist(r.get("content") or "")
            lines.append(
                f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
                f"| {md_escape(r.get('primary_entity_name',''))} | {md_escape(g)} |"
            )
        return lines

    lines: list[str] = []
    L = lines.append

    L("# Canon Corpus — Semantic Sift Report")
    L("")
    L(f"- Input: `{IN_PATH.relative_to(ROOT)}`")
    L(f"- Output JSONL: `{OUT_JSONL.relative_to(ROOT)}`")
    L("- Generator: `scripts/_canon_semantic_sift_oneoff.py` (read-only against the corpus)")
    L("- Ontology: PERSON, PLACE, THING, IDEA, EVENT, RELATIONSHIP, CREATIVE_WORK, PROCESS, UNKNOWN.")
    L("")

    L("## 1. Input record count")
    L("")
    L(f"**{total_in}** input records.")
    L("")

    L("## 2. Output record count")
    L("")
    L(f"**{total_out}** output records (every input record preserved; no merges, no discards).")
    L("")
    if validation_ok:
        L("Validation: **PASS**.")
    else:
        L(f"Validation: **FAIL** — {len(validation_errs)} errors. First 20:")
        L("")
        for e in validation_errs[:20]:
            L(f"- {e}")
    L("")

    L("## 3. Counts by `semantic_class`")
    L("")
    L("| semantic_class | count |")
    L("|---|---:|")
    for k in ["PERSON", "PLACE", "THING", "IDEA", "EVENT", "RELATIONSHIP", "CREATIVE_WORK", "PROCESS", "UNKNOWN"]:
        L(f"| `{k}` | {class_counts.get(k, 0)} |")
    L("")

    L("## 4. Counts by `semantic_confidence`")
    L("")
    L("| semantic_confidence | count |")
    L("|---|---:|")
    for k in ["high", "medium", "low"]:
        L(f"| `{k}` | {conf_counts.get(k, 0)} |")
    L("")

    L("## 5. Count of records needing Weaver review")
    L("")
    L(f"**{review_count}** records have `needs_weaver_review: true`.")
    L("")
    L("Triggers (any one is sufficient):")
    L("")
    L("- low confidence")
    L("- UNKNOWN class")
    L("- mixed dominant subjects in the same record")
    L("- `canon_tier == mythic_rumor_locked` (sealed material always warrants the Weaver eye)")
    L("- input `weaver_review_required: true` AND class is non-obvious (non-high confidence)")
    L("")

    L("## 6. Top 50 PERSON records")
    L("")
    L(f"Class total: **{class_counts.get('PERSON',0)}**. Selection: high-confidence first, then clean `primary_entity_name`, deprioritizing source_canon_extract passthroughs.")
    L("")
    lines.extend(top_table(top_n("PERSON")))
    L("")

    L("## 7. Top 50 PLACE records")
    L("")
    L(f"Class total: **{class_counts.get('PLACE',0)}**.")
    L("")
    lines.extend(top_table(top_n("PLACE")))
    L("")

    L("## 8. Top 50 THING records")
    L("")
    L(f"Class total: **{class_counts.get('THING',0)}**.")
    L("")
    lines.extend(top_table(top_n("THING")))
    L("")

    L("## 9. Top 50 IDEA records")
    L("")
    L(f"Class total: **{class_counts.get('IDEA',0)}**.")
    L("")
    lines.extend(top_table(top_n("IDEA")))
    L("")

    L("## 10. UNKNOWN records with reasons")
    L("")
    unk = by_class("UNKNOWN")
    L(f"Class total: **{len(unk)}**.")
    L("")
    if unk:
        L("| id | source_path | extraction_kind | semantic_reason |")
        L("|---|---|---|---|")
        for r in unk[:200]:
            L(
                f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
                f"| `{md_escape(r.get('extraction_kind',''))}` | {md_escape(r.get('semantic_reason',''))} |"
            )
        if len(unk) > 200:
            L("")
            L(f"_…{len(unk)-200} additional UNKNOWN rows omitted from listing._")
    L("")

    L("## 11. Mixed or ambiguous records needing Weaver review")
    L("")
    review_rs = [
        r for r in enriched
        if r["needs_weaver_review"] and r["semantic_class"] != "UNKNOWN"
    ]
    # Prioritize: sealed material first, then low-confidence narrative classes,
    # then weaver_review_required=true inputs.
    def review_rank(r: dict[str, Any]) -> tuple[int, int, int]:
        sealed = 2 if r.get("canon_tier") == "mythic_rumor_locked" else 0
        low = 1 if r["semantic_confidence"] == "low" else 0
        flagged = 1 if r.get("weaver_review_required") is True else 0
        return (sealed, low, flagged)

    review_rs.sort(key=review_rank, reverse=True)
    L(f"Total non-UNKNOWN review-flagged: **{len(review_rs)}**.")
    L("")
    cap = 50
    L(f"Showing top {min(cap, len(review_rs))} by priority (sealed > low-confidence > flagged-on-input).")
    if len(review_rs) > cap:
        L("")
        L(f"_…{len(review_rs)-cap} additional records also need Weaver review; full list lives in the JSONL with `needs_weaver_review: true`._")
    L("")
    L("| id | source_path | semantic_class | confidence | canon_tier | semantic_reason |")
    L("|---|---|---|---|---|---|")
    for r in review_rs[:cap]:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| `{r['semantic_class']}` | `{r['semantic_confidence']}` "
            f"| `{md_escape(r.get('canon_tier',''))}` | {md_escape(r.get('semantic_reason',''))} |"
        )
    L("")

    L("## 12. Recommended next safe action")
    L("")
    L(
        "Convene the Weaver around section 11 (mixed/ambiguous review queue) and "
        "section 10 (UNKNOWN bucket), starting with rows whose `canon_tier == "
        "mythic_rumor_locked` because routing matters most for sealed material. "
        "All sift output stays in `synthetic_enrichment/generated/`; do not move "
        "anything to `synthetic_enrichment/validated/`, do not write to "
        "`hooplehopper_totality/`, do not derive training material, and do not "
        "mark any record `[APPROVED_FOR_JSONL]` until the Weaver hands down the "
        "label per the Human-in-the-Loop Quickstart. The next mechanical step is "
        "for the Weaver to spot-check the top 50 lists in sections 6–9, confirm "
        "or revise classes, and only then authorize a follow-up agent pass to "
        "enrich `primary_entity_name` and `secondary_entity_names` for the rows "
        "the Weaver has actually walked."
    )
    L("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    records = load_records(IN_PATH)
    total_in = len(records)
    expected_ids = {r["id"] for r in records if isinstance(r.get("id"), str)}

    enriched: list[dict[str, Any]] = []
    for rec in records:
        cls, conf, reason = classify(rec)
        # safety: clamp to allowed sets
        if cls not in ALLOWED_CLASSES:
            cls = "UNKNOWN"
        if conf not in ALLOWED_CONFIDENCE:
            conf = "low"
        primary = primary_entity_name(rec)
        secondary = secondary_entity_names(rec, primary)
        review = needs_review(rec, cls, conf)

        out_rec = dict(rec)  # preserve original fields verbatim
        out_rec["semantic_class"] = cls
        out_rec["semantic_confidence"] = conf
        out_rec["semantic_reason"] = reason
        out_rec["primary_entity_name"] = primary
        out_rec["secondary_entity_names"] = secondary
        out_rec["needs_weaver_review"] = bool(review)
        enriched.append(out_rec)

    # Write JSONL (one object per line, no trailing newline-only blanks).
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in enriched:
            fh.write(json.dumps(r, ensure_ascii=False))
            fh.write("\n")

    ok, errs = validate_jsonl(OUT_JSONL, expected_ids, total_in)

    report = render_report(enriched, total_in, len(enriched), ok, errs)
    OUT_MD.write_text(report, encoding="utf-8")

    # Console summary (single line; the parent agent reads it)
    cc = Counter(r["semantic_class"] for r in enriched)
    print(
        "summary: "
        f"in={total_in} out={len(enriched)} validation={'PASS' if ok else 'FAIL'} "
        f"needs_review={sum(1 for r in enriched if r['needs_weaver_review'])} "
        + " ".join(f"{k}={cc.get(k,0)}" for k in [
            "PERSON","PLACE","THING","IDEA","EVENT","RELATIONSHIP","CREATIVE_WORK","PROCESS","UNKNOWN"
        ])
    )
    if not ok:
        print("VALIDATION ERRORS (first 10):")
        for e in errs[:10]:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
