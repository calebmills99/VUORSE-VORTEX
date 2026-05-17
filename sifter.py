#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ALLOWED_CLASSES = {
    "PERSON",
    "PLACE",
    "THING",
    "IDEA",
    "EVENT",
    "RELATIONSHIP",
    "CREATIVE_WORK",
    "PROCESS",
    "METADATA",
}

ALLOWED_CONFIDENCE = {"high", "medium", "low"}

STOP_WORDS = {
    "the", "a", "an", "and", "but", "or", "nor", "by", "over", "under",
    "through", "with", "from", "into", "beneath", "above", "below", "within",
    "without", "between", "among", "is", "was", "were", "be", "been", "being",
    "have", "has", "had", "of", "in", "on", "for", "to", "as", "at", "that",
    "this", "these", "those", "it", "its", "their", "his", "her", "them",
    "they", "he", "she", "we", "you", "i", "not", "no", "yes", "do", "does",
    "did", "will", "would", "shall", "should", "may", "might", "can", "could",
    "must", "then", "than", "so", "if", "when", "where", "what", "which",
    "who", "whom", "whose", "how", "why",
}

# Order matters: more specific / longer phrases should win.
SLAYVERSE_TERMS: dict[str, list[str]] = {
    "PERSON": [
        "Miss Slaytonia VUORSE",
        "Miss Slaytonia Verse",
        "Professor Von Hooplehopper",
        "Professor von Hooplehopper",
        "Dr. Mariah Elena Slayton Rios del Campo",
        "Mariah Elena Slayton Rios del Campo",
        "Dr. Elena Slayton",
        "Dr. Mariah Slayton",
        "Hildebrand von Hooplehopper",
        "Conrad von Hooplehopper",
        "Adelram von Hooplehopper",
        "Margarethe von Hooplehopper",
        "Benedict the Ash-Faced",
        "Velma the Snake in Silk",
        "Lysander von Hooplehopper",
        "Theresia von Hooplehopper",
        "Yssenda von Hooplehopper",
        "Sigismund von Hooplehopper",
        "Isolde von Hooplehopper",
        "Ludolf von Hooplehopper",
        "Jake McCullen",
        "Jacob Elijah McCullen",
        "Eli McCullen",
        "Doctor Vorst",
        "Dr. Vorst",
        "Professor A.",
        "The Shrouded Patriarch",
        "The Weaver",
        "Wylus Kalyndros",
        "DJ Parallax",
        "Cici the Cat",
        "VUORSE",
        "Slaytonia",
        "Lisette",
        "Vorst",
        "Pop",
        "Jake",
        "Eli",
        "Cici",
    ],
    "PLACE": [
        "McCullen Ranch",
        "Powder River Basin",
        "Wyoming Rift",
        "Wyoming rift",
        "North Pasture",
        "north pasture",
        "Schloss Eisensang",
        "Mirror Cavern",
        "Schloss Federstahl",
        "Berlin Cathedral",
        "bombed-out Berlin cathedral",
        "Club Cosmic",
        "Federstahl Nebula Outpost V",
        "Slayton Plane",
        "Velvet Archive",
        "Balmoral",
        "Black Forest",
        "Venice",
        "Berlin",
        "Weimar",
        "Konigsberg",
        "Königsberg",
        "Wyoming",
    ],
    "THING": [
        "Forbidden Suitcase",
        "Dustbrand Sigil",
        "Crystal Shard",
        "Federstahl Crystal",
        "Crystal Node",
        "Zerethium Quartz",
        "Hildebrand's Ring",
        "Slayton Codex",
        "The Slayton Codex",
        "Glamorons",
        "Glamourons",
        "Slayton Particles",
        "Federkreis Devices",
        "Brass Kaleidoscopes",
        "VUORSE's Mic",
        "Seal VI",
        "Slayton Loop",
        "The Codex",
        "Codex",
        "Dustbrand",
        "Suitcase",
        "Shard",
        "Ring",
    ],
    "IDEA": [
        "Mythic Rumor That Is Also Locked Canon",
        "Mythic-Rumor-and-Locked",
        "Narrative Collapse",
        "Post-Truth Cosmology",
        "Mandela Effect",
        "Corrective Chronogenesis",
        "Blood Resonance",
        "Lattice Proximity Contamination",
        "Slayton Force",
        "Slayton Field",
        "Slayton Energy",
        "Quantum Eleganza",
        "Slayton Layer",
        "The Thread",
        "Thread",
        "soul-line",
        "bloodline",
        "temporal diaspora",
        "Temporal Diaspora",
        "Guardian Lineage",
        "ontological deletion",
        "locked canon",
        "development canon",
        "mythic rumor",
        "canon hierarchy",
        "Codex prophecy",
        "prophecy",
        "Eden",
    ],
    "EVENT": [
        "Crystal Lattice Incident",
        "Federstahl Catastrophe",
        "Lattice Fracture",
        "Federstahl Lattice Incident",
        "Immaculate Slayception",
        "Tragedy of Splat",
        "Slay Mode Activation Rite",
        "Ritual of Reflection",
        "Velvet Rite",
        "Three Snap Protocol",
        "Sixth Summit",
        "Fifth Galactic Summit",
        "Second Galactic Summit",
        "20-Year Sleep",
        "20-Year Sleep Cycle",
        "The Wound Under the Prairie",
        "Season 1",
        "Season One",
    ],
    "RELATIONSHIP": [
        "mother",
        "father",
        "companion",
        "temporal echo",
        "antagonist",
        "guardian",
        "successor",
        "lineage",
        "mentor",
        "descendant",
        "ancestor",
        "soul-line succession",
        "counter-lineage",
        "blood descendant",
        "spiritual successor",
        "creator",
        "confrontation",
    ],
    "CREATIVE_WORK": [
        "Words of Weaver Book One",
        "Words of the Weaver",
        "Book One",
        "SLAYVERSE_TV_SERIES_BIBLE",
        "Series Bible",
        "Golden Wingers Charter",
        "Golden Wingers Intergalactic League Charter",
        "Canon Ledger",
        "Human-in-the-Loop Quickstart",
        "Narrative Philosophy Protocol",
        "Synthesis Process",
        "Mock Room Protocol",
        "Secret Sauce",
        "Hooplehopper Biography Inventory",
        "Codex prophecy",
    ],
    "PROCESS": [
        "Human-in-the-Loop Quickstart",
        "synthesis process",
        "mock-room protocol",
        "room pressure model",
        "narrative philosophy protocol",
        "JSONL extraction",
        "JSONL validation",
        "canon firewall",
        "training pipeline",
        "review loop",
        "semantic sift",
        "weaver review",
        "workflow",
        "protocol",
        "process",
        "pipeline",
        "validator",
        "firewall",
        "embedding",
    ],
}

# Priority prevents broad PROCESS terms like "protocol" from defeating named artifacts / characters.
CLASS_PRIORITY = [
    "PERSON",
    "PLACE",
    "THING",
    "EVENT",
    "RELATIONSHIP",
    "CREATIVE_WORK",
    "IDEA",
    "PROCESS",
]

RECORD_TYPE_DEFAULTS = {
    "character_record": "PERSON",
    "place_record": "PLACE",
    "artifact_record": "THING",
    "ritual_record": "EVENT",
    "organization_record": "IDEA",
    "timeline_record": "EVENT",
    "relationship_record": "RELATIONSHIP",
    "prophecy_record": "IDEA",
    "symbolic_system_record": "IDEA",
    "doctrine_record": "IDEA",
    "source_canon_extract": None,
}

SOURCE_PATH_HINTS = [
    ("characters", "PERSON"),
    ("places", "PLACE"),
    ("artifacts", "THING"),
    ("rituals", "EVENT"),
    ("organizations", "IDEA"),
    ("timeline", "EVENT"),
    ("relationships", "RELATIONSHIP"),
    ("relationship_map", "RELATIONSHIP"),
    ("TV_Series_Bible", "CREATIVE_WORK"),
    ("1_words_of_weaver_book_one", "CREATIVE_WORK"),
    (".jsonl", "METADATA"),
]

PROCESS_PATH_HINTS = [
    "writers-room",
    "agents/",
    ".claude/agents",
    "synthesis-process",
    "mock-room-protocol",
    "secret-sauce",
    "HUMAN_IN_THE_LOOP",
    "narrative-philosophy-protocol",
]


@dataclass
class Classification:
    semantic_class: str
    confidence: str
    reason: str
    focus: str
    dominant: str
    secondary: list[str]
    needs_review: bool


def normalize(s: Any) -> str:
    if s is None:
        return ""
    if isinstance(s, str):
        return s
    if isinstance(s, (list, tuple, set)):
        return " ".join(normalize(x) for x in s)
    if isinstance(s, dict):
        return " ".join(f"{k} {normalize(v)}" for k, v in s.items())
    return str(s)


def clean_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def record_text(record: dict[str, Any]) -> str:
    parts = [
        normalize(record.get("title")),
        normalize(record.get("name")),
        normalize(record.get("source_section")),
        normalize(record.get("source_anchor")),
        normalize(record.get("record_type")),
        normalize(record.get("extraction_kind")),
        normalize(record.get("entities")),
        normalize(record.get("tags")),
        normalize(record.get("summary")),
        normalize(record.get("body")),
        normalize(record.get("content")),
    ]
    return clean_space(" ".join(p for p in parts if p))


def title_text(record: dict[str, Any]) -> str:
    return clean_space(
        normalize(record.get("title"))
        or normalize(record.get("name"))
        or normalize(record.get("source_section"))
        or normalize(record.get("id"))
    )


def source_path(record: dict[str, Any]) -> str:
    return normalize(record.get("source_path")) or normalize(record.get("source_file"))


def contains_term(haystack: str, term: str) -> bool:
    # Phrase-aware, case-insensitive. Allows possessive punctuation.
    if not term:
        return False
    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None


def dictionary_matches(text: str) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for cls in CLASS_PRIORITY:
        for term in sorted(SLAYVERSE_TERMS[cls], key=len, reverse=True):
            if contains_term(text, term):
                matches.append((cls, term))
    return matches


def first_dictionary_class(text: str) -> tuple[str | None, str | None, list[str]]:
    matches = dictionary_matches(text)
    if not matches:
        return None, None, []
    for cls in CLASS_PRIORITY:
        for m_cls, term in matches:
            if m_cls == cls:
                secondary = []
                seen = {term.lower()}
                for _, other in matches:
                    if other.lower() not in seen:
                        secondary.append(other)
                        seen.add(other.lower())
                    if len(secondary) >= 10:
                        break
                return cls, term, secondary
    return matches[0][0], matches[0][1], [m[1] for m in matches[1:11]]


def likely_process_text(record: dict[str, Any], text: str) -> bool:
    lower = text.lower()
    path = source_path(record).lower()
    process_words = [
        "workflow", "protocol", "process", "pipeline", "validator", "validation",
        "jsonl", "human-in-the-loop", "quickstart", "agent", "subagent",
        "ticket", "epic", "review loop", "synthesis ladder", "room pressure",
        "canon firewall", "training corpus", "metadata", "schema",
    ]
    hit_words = sum(1 for w in process_words if w in lower)
    path_process = any(h.lower() in path for h in PROCESS_PATH_HINTS)
    # Require strong evidence. Do not let a single "protocol" in body dominate lore.
    return hit_words >= 3 or (path_process and hit_words >= 1)


def class_from_record_type(record: dict[str, Any]) -> str | None:
    rt = normalize(record.get("record_type")) or normalize(record.get("extraction_kind"))
    rt = rt.strip()
    if rt in RECORD_TYPE_DEFAULTS:
        return RECORD_TYPE_DEFAULTS[rt]
    # Some earlier extracts used broader labels.
    rt_lower = rt.lower()
    if "character" in rt_lower:
        return "PERSON"
    if "place" in rt_lower or "location" in rt_lower:
        return "PLACE"
    if "artifact" in rt_lower or "technology" in rt_lower:
        return "THING"
    if "timeline" in rt_lower or "event" in rt_lower:
        return "EVENT"
    if "relationship" in rt_lower:
        return "RELATIONSHIP"
    if "doctrine" in rt_lower or "cosmology" in rt_lower or "prophecy" in rt_lower:
        return "IDEA"
    if "creative" in rt_lower or "work" in rt_lower or "document" in rt_lower:
        return "CREATIVE_WORK"
    if "process" in rt_lower or "protocol" in rt_lower or "workflow" in rt_lower:
        return "PROCESS"
    return None


def class_from_source_path(record: dict[str, Any]) -> str | None:
    path = source_path(record).lower()
    for hint, cls in SOURCE_PATH_HINTS:
        if hint.lower() in path:
            return cls
    if any(h.lower() in path for h in PROCESS_PATH_HINTS):
        return "PROCESS"
    return None


def extract_candidate_phrases_regex(text: str, limit: int = 10) -> list[str]:
    # Proper-noun-ish phrases and title-cased runs.
    candidates: list[str] = []

    # Terms in quotes or markdown headings can be strong candidates.
    for match in re.finditer(r"[*_`\"“”']{0,2}([A-Z][A-Za-z0-9.'’\-]+(?:\s+[A-Z][A-Za-z0-9.'’\-]+){0,6})", text):
        phrase = clean_space(match.group(1))
        if phrase and not all(tok.lower() in STOP_WORDS for tok in phrase.split()):
            candidates.append(phrase)

    # Capitalized phrases after common markers.
    for marker in ["###", "##", "#", "name:", "title:", "aliases:", "id:"]:
        pattern = re.escape(marker) + r"\s*([A-Za-z0-9 .'’\-$begin:math:display$$end:math:display$/:]+)"
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            phrase = clean_space(match.group(1).split("|")[0])
            phrase = re.sub(r"\s{2,}.*", "", phrase).strip()
            if phrase and len(phrase) > 2:
                candidates.append(phrase)

    cleaned: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        c = re.sub(r"\s*$begin:math:display$\.\*\?$end:math:display$\s*", "", c).strip()
        c = c.strip(":-—–.,;")
        if not c:
            continue
        key = c.lower()
        if key in STOP_WORDS or key in seen:
            continue
        seen.add(key)
        cleaned.append(c)
        if len(cleaned) >= limit:
            break
    return cleaned


def load_spacy(model: str | None):
    if not model:
        model = "en_core_web_sm"
    try:
        import spacy  # type: ignore
    except Exception:
        return None, "spaCy not installed"
    try:
        return spacy.load(model), f"spaCy loaded: {model}"
    except Exception as exc:
        return None, f"spaCy unavailable or model missing: {exc}"


def spacy_candidates(nlp, text: str, limit: int = 10) -> list[str]:
    if nlp is None or not text:
        return []
    # Avoid huge docs.
    doc = nlp(text[:5000])
    candidates: list[str] = []

    for ent in doc.ents:
        if ent.label_ in {"PERSON", "ORG", "GPE", "LOC", "WORK_OF_ART", "EVENT", "PRODUCT", "NORP"}:
            candidates.append(ent.text)

    # noun_chunks may fail if parser absent.
    try:
        for chunk in doc.noun_chunks:
            phrase = clean_space(chunk.text)
            tokens = [t.text.lower() for t in chunk if not t.is_punct]
            if tokens and not all(t in STOP_WORDS for t in tokens):
                candidates.append(phrase)
    except Exception:
        pass

    out: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        c = clean_space(c).strip(":-—–.,;")
        if not c:
            continue
        if c.lower() in STOP_WORDS:
            continue
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
        if len(out) >= limit:
            break
    return out


def classify_unknown_candidate(candidate: str, record: dict[str, Any]) -> tuple[str, str]:
    c = candidate.lower()
    path = source_path(record).lower()

    # Hooplehopper names and common proper names.
    if "hooplehopper" in c or any(x in c for x in ["jake", "pop", "vorst", "vuorse", "weaver", "lisette", "eli", "cici"]):
        return "PERSON", "candidate names a character/person-like figure"

    if any(x in c for x in ["ranch", "rift", "cavern", "schloss", "club", "outpost", "basin", "wyoming", "berlin", "venice"]):
        return "PLACE", "candidate names a location or realm"

    if any(x in c for x in ["sigil", "suitcase", "shard", "crystal", "ring", "codex", "device", "quartz", "particle", "glamoron", "glamouron", "mic"]):
        return "THING", "candidate names an artifact/object/substance"

    if any(x in c for x in ["incident", "catastrophe", "fracture", "summit", "rite", "ritual", "activation", "sleep", "season", "arc"]):
        return "EVENT", "candidate names an event/ritual/happening"

    if any(x in c for x in ["prophecy", "cosmology", "doctrine", "thread", "field", "force", "energy", "diaspora", "lineage", "canon", "collapse"]):
        return "IDEA", "candidate names a doctrine/concept"

    if any(x in c for x in ["bible", "book", "charter", "transcript", "digest", "guide", "quickstart", "protocol", "process"]):
        if likely_process_text(record, record_text(record)):
            return "PROCESS", "candidate names a workflow/process document"
        return "CREATIVE_WORK", "candidate names a document/creative work"

    if "characters" in path:
        return "PERSON", "source path suggests character record"
    if "places" in path:
        return "PLACE", "source path suggests place record"
    if "artifacts" in path:
        return "THING", "source path suggests artifact record"
    if "timeline" in path:
        return "EVENT", "source path suggests timeline/event record"
    if "relationships" in path:
        return "RELATIONSHIP", "source path suggests relationship record"

    return "METADATA", "no reliable entity/concept signal"


def classify_record(record: dict[str, Any], nlp=None) -> Classification:
    text = record_text(record)
    title = title_text(record)
    combined = clean_space(f"{title} {text}")
    path = source_path(record)

    # 1. Source path hint first (Directory structure is the strongest ground truth).
    path_cls = class_from_source_path(record)
    if path_cls:
        if path_cls == "PROCESS" and not likely_process_text(record, combined):
            pass
        else:
            return Classification(
                semantic_class=path_cls,
                confidence="medium",
                reason=f"source path hint indicates {path_cls}: {path}",
                focus="workflow" if path_cls == "PROCESS" else "source_document",
                dominant=title or normalize(record.get("id")),
                secondary=[],
                needs_review=needs_review_for(record, path_cls, "source_path"),
            )

    # 2. Record type next.
    rt_cls = class_from_record_type(record)
    if rt_cls:
        if rt_cls == "PROCESS" and not likely_process_text(record, combined):
            pass
        else:
            return Classification(
                semantic_class=rt_cls,
                confidence="medium",
                reason=f"record_type/extraction_kind indicates {rt_cls}",
                focus="workflow" if rt_cls == "PROCESS" else "source_document",
                dominant=title or normalize(record.get("id")),
                secondary=[],
                needs_review=needs_review_for(record, rt_cls, "record_type"),
            )

    # 3. Dictionary match on TITLE only.
    cls, term, secondary = first_dictionary_class(title)
    if cls:
        if cls == "PROCESS" and not likely_process_text(record, combined):
            pass
        else:
            return Classification(
                semantic_class=cls,
                confidence="high",
                reason=f"explicit Slayverse dictionary match in TITLE: {term}",
                focus="workflow" if cls == "PROCESS" else "named_entity",
                dominant=term or title,
                secondary=secondary,
                needs_review=needs_review_for(record, cls, "dictionary"),
            )

    # 4. Dictionary match on COMBINED body text (fallback).
    cls, term, secondary = first_dictionary_class(combined)
    if cls:
        if cls == "PROCESS" and not likely_process_text(record, combined):
            pass
        else:
            return Classification(
                semantic_class=cls,
                confidence="high",
                reason=f"explicit Slayverse dictionary match in BODY: {term}",
                focus="workflow" if cls == "PROCESS" else "named_entity",
                dominant=term or title,
                secondary=secondary,
                needs_review=needs_review_for(record, cls, "dictionary"),
            )

    # spaCy candidates, then regex fallback.
    candidates = spacy_candidates(nlp, combined, limit=10) if nlp is not None else []
    if not candidates:
        candidates = extract_candidate_phrases_regex(combined, limit=10)

    if candidates:
        dominant = candidates[0]
        candidate_cls, reason = classify_unknown_candidate(dominant, record)
        return Classification(
            semantic_class=candidate_cls,
            confidence="low" if candidate_cls == "METADATA" else "medium",
            reason=reason,
            focus="unclear" if candidate_cls == "METADATA" else "noun_phrase",
            dominant=dominant,
            secondary=candidates[1:10],
            needs_review=True if candidate_cls == "METADATA" else needs_review_for(record, candidate_cls, "candidate"),
        )

    # Last resort: if true process by text, process. Otherwise unknown.
    if likely_process_text(record, combined):
        return Classification(
            semantic_class="PROCESS",
            confidence="low",
            reason="process/workflow keywords found but no stronger entity signal",
            focus="workflow",
            dominant=title or normalize(record.get("id")),
            secondary=[],
            needs_review=True,
        )

    return Classification(
        semantic_class="METADATA",
        confidence="low",
        reason="no meaningful dominant noun phrase or named entity identified",
        focus="unclear",
        dominant=title or normalize(record.get("id")),
        secondary=[],
        needs_review=True,
    )


def needs_review_for(record: dict[str, Any], cls: str, method: str) -> bool:
    text = record_text(record).lower()
    rank = normalize(record.get("canon_rank")) or normalize(record.get("canon_tier"))
    access = normalize(record.get("training_layer_access"))

    # Book One hidden / mythic locked material always deserves Weaver eye.
    if "mythic" in rank.lower() and "locked" in rank.lower():
        return True
    if "vuorse_private" in access.lower():
        return True
    if "[pending review]" in text or "pending review" in text:
        return True
    if cls == "METADATA":
        return True
    # Very broad source extracts should get review unless high confidence dictionary.
    if method not in {"dictionary"} and (normalize(record.get("record_type")) == "source_canon_extract" or normalize(record.get("extraction_kind")) == "source_canon_extract"):
        return True
    return bool(record.get("needs_weaver_review", False))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                raise ValueError(f"Blank line at {lineno}")
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {lineno}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Line {lineno} is not a JSON object")
            records.append(obj)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=False) + "\n")


def validate_jsonl(path: Path, expected_ids: set[str], expected_count: int) -> None:
    records = read_jsonl(path)
    if len(records) != expected_count:
        raise ValueError(f"Record count mismatch: expected {expected_count}, got {len(records)}")
    ids = [normalize(r.get("id")) for r in records]
    if len(set(ids)) != len(ids):
        duplicates = [item for item, count in collections.Counter(ids).items() if count > 1]
        raise ValueError(f"Duplicate ids in output: {duplicates[:20]}")
    if set(ids) != expected_ids:
        missing = expected_ids - set(ids)
        extra = set(ids) - expected_ids
        raise ValueError(f"ID set mismatch. missing={len(missing)} extra={len(extra)}")
    for i, rec in enumerate(records, start=1):
        cls = rec.get("semantic_class")
        conf = rec.get("semantic_confidence")
        if cls not in ALLOWED_CLASSES:
            raise ValueError(f"Line {i} invalid semantic_class: {cls}")
        if conf not in ALLOWED_CONFIDENCE:
            raise ValueError(f"Line {i} invalid semantic_confidence: {conf}")
        if not isinstance(rec.get("needs_weaver_review"), bool):
            raise ValueError(f"Line {i} needs_weaver_review is not boolean")
        if cls == "PROCESS" and rec.get("entity_focus") != "workflow":
            raise ValueError(f"Line {i} PROCESS record must have entity_focus='workflow'")


def top_records(records: list[dict[str, Any]], cls: str, limit: int = 100) -> list[dict[str, Any]]:
    out = [r for r in records if r.get("semantic_class") == cls]
    return out[:limit]


def md_table(rows: list[list[str]], headers: list[str]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        safe = [str(cell).replace("\n", " ").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    return "\n".join(lines)


def build_report(
    *,
    report_path: Path,
    input_path: Path,
    output_path: Path,
    records: list[dict[str, Any]],
    old_counts: dict[str, int],
    spacy_status: str,
    validation_result: str,
) -> None:
    new_counts = collections.Counter(r["semantic_class"] for r in records)
    conf_counts = collections.Counter(r["semantic_confidence"] for r in records)
    review_count = sum(1 for r in records if r.get("needs_weaver_review"))
    process_count = new_counts["PROCESS"]
    unknown_count = new_counts["UNKNOWN"]
    dictionary_count = sum(1 for r in records if "dictionary match" in normalize(r.get("semantic_reason")))
    fallback_count = sum(1 for r in records if r.get("semantic_confidence") in {"medium", "low"} and "dictionary match" not in normalize(r.get("semantic_reason")))

    def rows_for(cls: str, limit: int = 100) -> list[list[str]]:
        rows = []
        for r in top_records(records, cls, limit):
            rows.append([
                normalize(r.get("id")),
                normalize(r.get("dominant_noun_phrase")),
                normalize(r.get("semantic_confidence")),
                normalize(r.get("semantic_reason"))[:180],
                normalize(r.get("source_path") or r.get("source_file")),
            ])
        return rows

    lines = [
        "# Canon Corpus Entity Sift — Scripted Report",
        "",
        "## 1. Input / Output",
        "",
        f"- Input: `{input_path}`",
        f"- Output: `{output_path}`",
        f"- Records: {len(records)}",
        f"- NLP status: {spacy_status}",
        f"- Validation: {validation_result}",
        "",
        "## 2. Old counts by semantic_class",
        "",
        md_table([[k, str(v)] for k, v in sorted(old_counts.items())], ["semantic_class", "count"]),
        "",
        "## 3. New counts by semantic_class",
        "",
        md_table([[k, str(new_counts.get(k, 0))] for k in sorted(ALLOWED_CLASSES)], ["semantic_class", "count"]),
        "",
        "## 4. Counts by semantic_confidence",
        "",
        md_table([[k, str(conf_counts.get(k, 0))] for k in sorted(ALLOWED_CONFIDENCE)], ["confidence", "count"]),
        "",
        "## 5. Weaver review count",
        "",
        f"- Records needing Weaver review: {review_count}",
        "",
        "## 6. PROCESS / UNKNOWN",
        "",
        f"- PROCESS count: {process_count}",
        f"- UNKNOWN count: {unknown_count}",
        f"- Records with dictionary matches: {dictionary_count}",
        f"- Records classified by fallback/heuristics: {fallback_count}",
        "",
        "## 7. Top 100 PROCESS records and why they remain PROCESS",
        "",
        md_table(rows_for("PROCESS", 100), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 8. Top 100 UNKNOWN records and why",
        "",
        md_table(rows_for("UNKNOWN", 100), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 9. Top PERSON candidates",
        "",
        md_table(rows_for("PERSON", 50), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 10. Top PLACE candidates",
        "",
        md_table(rows_for("PLACE", 50), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 11. Top THING candidates",
        "",
        md_table(rows_for("THING", 50), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 12. Top IDEA candidates",
        "",
        md_table(rows_for("IDEA", 50), ["id", "dominant_noun_phrase", "confidence", "reason", "source"]),
        "",
        "## 13. Recommended next safe action",
        "",
        "Review the UNKNOWN and [VUORSE_PRIVATE] / mythic-rumor-locked records first. "
        "Do not move anything to `synthetic_enrichment/validated/` until the Weaver reviews it. "
        "Do not deduplicate or compress until after semantic review.",
        "",
    ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic semantic sift for Slayverse canon JSONL.")
    parser.add_argument("--input", required=True, type=Path, help="Input raw canon JSONL")
    parser.add_argument("--output", required=True, type=Path, help="Output scripted semantic sift JSONL")
    parser.add_argument("--report", required=True, type=Path, help="Output markdown report")
    parser.add_argument("--spacy-model", default="en_core_web_sm", help="Optional spaCy model name")
    parser.add_argument("--no-spacy", action="store_true", help="Disable spaCy even if installed")
    args = parser.parse_args(argv)

    records = read_jsonl(args.input)
    expected_ids = {normalize(r.get("id")) for r in records}
    if len(expected_ids) != len(records):
        raise ValueError("Input contains duplicate or missing ids; refusing to continue.")

    old_counts = collections.Counter(normalize(r.get("semantic_class")) or "UNCLASSIFIED" for r in records)

    nlp = None
    spacy_status = "spaCy disabled"
    if not args.no_spacy:
        nlp, spacy_status = load_spacy(args.spacy_model)

    output_records: list[dict[str, Any]] = []
    deleted_metadata_count = 0
    for rec in records:
        cls = classify_record(rec, nlp=nlp)
        if cls.semantic_class == "METADATA":
            deleted_metadata_count += 1
            continue
        out = dict(rec)
        out["semantic_class"] = cls.semantic_class
        out["semantic_confidence"] = cls.confidence
        out["semantic_reason"] = cls.reason
        out["entity_focus"] = cls.focus
        out["dominant_noun_phrase"] = cls.dominant
        out["secondary_entity_names"] = cls.secondary
        out["needs_weaver_review"] = cls.needs_review
        output_records.append(out)

    filtered_expected_ids = {normalize(r.get("id")) for r in output_records}

    write_jsonl(args.output, output_records)

    validation_result = "PASS"
    try:
        validate_jsonl(args.output, expected_ids=filtered_expected_ids, expected_count=len(output_records))
    except Exception as exc:
        validation_result = f"FAIL: {exc}"
        build_report(
            report_path=args.report,
            input_path=args.input,
            output_path=args.output,
            records=output_records,
            old_counts=dict(old_counts),
            spacy_status=spacy_status,
            validation_result=validation_result,
        )
        raise

    build_report(
        report_path=args.report,
        input_path=args.input,
        output_path=args.output,
        records=output_records,
        old_counts=dict(old_counts),
        spacy_status=spacy_status,
        validation_result=validation_result,
    )

    counts = collections.Counter(r["semantic_class"] for r in output_records)

    print(f"script path: {Path(__file__)}")
    print(f"output jsonl: {args.output}")
    print(f"report: {args.report}")
    print("counts by semantic_class:")
    for cls_name in sorted(ALLOWED_CLASSES):
        print(f"  {cls_name}: {counts.get(cls_name, 0)}")
    print(f"PROCESS count: {counts.get('PROCESS', 0)}")
    print(f"UNKNOWN count: {counts.get('UNKNOWN', 0)}")
    print(f"METADATA deleted count: {deleted_metadata_count}")
    print(f"validation: {validation_result}")
    print("recommended next safe action: Review UNKNOWN and VUORSE_PRIVATE/mythic-rumor-locked records before validation/training.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
