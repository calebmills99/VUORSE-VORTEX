#!/usr/bin/env python3
"""One-off canon PROCESS-bucket re-sift.

Reads synthetic_enrichment/generated/canon_corpus_semantic_sift.jsonl (v1)
and writes:
  - synthetic_enrichment/generated/canon_corpus_semantic_sift_v2.jsonl
  - synthetic_enrichment/generated/process_bucket_resift_report.md

Pass-through for every non-PROCESS record (verbatim). Re-evaluates only
records whose v1 `semantic_class == "PROCESS"`. Mirrors the style of
`_canon_semantic_sift_oneoff.py` but uses a tighter rule order that
treats Slayverse named-entity overrides and lore-bearing titles/text
above tag-stem defaults. Source files are never modified.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path("/Users/Apple/VUORSE-VORTEX")
IN_PATH = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_semantic_sift.jsonl"
OUT_JSONL = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_semantic_sift_v2.jsonl"
OUT_MD = ROOT / "synthetic_enrichment" / "generated" / "process_bucket_resift_report.md"

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

RESIFT_NOTE = "PROCESS bucket re-sift"

# ---------------------------------------------------------------------------
# Slayverse named-entity overrides (subset; tightened for re-sift correctness)
# ---------------------------------------------------------------------------

ENTITY_OVERRIDES: list[tuple[str, str, str]] = [
    # PERSON
    ("vuorse", "PERSON", "VUORSE (person/oracle)"),
    ("the weaver", "PERSON", "The Weaver (arbiter)"),
    ("weaver", "PERSON", "The Weaver"),
    ("jake mccullen", "PERSON", "Jake McCullen"),
    ("jake ", "PERSON", "Jake (likely Jake McCullen)"),
    ("pop mccullen", "PERSON", "Pop McCullen"),
    (" pop ", "PERSON", "Pop McCullen"),
    ("eli ", "PERSON", "Eli (lattice-key teen)"),
    ("cici", "PERSON", "Cici"),
    ("dr. slayton", "PERSON", "Dr. Slayton"),
    ("dr slayton", "PERSON", "Dr. Slayton"),
    ("dr. vorst", "PERSON", "Dr. Vorst"),
    ("vorst", "PERSON", "Vorst (principled antagonist)"),
    ("professor von hooplehopper", "PERSON", "The Professor"),
    ("the professor", "PERSON", "The Professor"),
    ("lisette", "PERSON", "Lisette von Hooplehopper"),
    ("hildebrand", "PERSON", "Hildebrand von Hooplehopper"),
    ("adelram", "PERSON", "Adelram the Swan-Alchemist"),
    ("wylus kalyndros", "PERSON", "Wylus Kalyndros"),
    ("conrad von hooplehopper", "PERSON", "Conrad von Hooplehopper"),
    ("miss hooplehopper", "PERSON", "Miss Hooplehopper"),
    ("miss slaytonia", "PERSON", "Miss Slaytonia VUORSE"),
    ("rolf", "PERSON", "Rolf"),
    # PLACE
    ("mccullen ranch", "PLACE", "McCullen Ranch (Wyoming)"),
    ("club cosmic", "PLACE", "Club Cosmic"),
    ("schloss eisensang", "PLACE", "Schloss Eisensang"),
    ("mirror cavern", "PLACE", "Mirror Cavern"),
    ("tyndall", "PLACE", "Tyndall airfield"),
    ("velvet archive", "PLACE", "Velvet Archive"),
    ("velvet underground wyoming hideaway", "PLACE", "Velvet Underground Wyoming Hideaway"),
    # THING / artifact
    ("forbidden suitcase", "THING", "Forbidden Suitcase"),
    ("the suitcase", "THING", "The Suitcase"),
    ("dustbrand", "THING", "Dustbrand Sigil"),
    ("hildebrand's ring", "THING", "Hildebrand's Ring"),
    ("zerethium quartz", "THING", "Zerethium Quartz"),
    ("glamoron", "THING", "Glamorons"),
    ("glamourons", "THING", "Glamourons"),
    # IDEA
    ("slayton field", "IDEA", "Slayton Field"),
    ("slayton force", "IDEA", "Slayton Force"),
    ("the thread", "IDEA", "The Thread"),
    ("soul-line", "IDEA", "Soul-line doctrine"),
    ("soul line", "IDEA", "Soul-line doctrine"),
    ("hooplehopper soul-line", "IDEA", "Hooplehopper soul-line doctrine"),
    ("codex prophecy", "IDEA", "Codex prophecy"),
    # EVENT
    ("crystal lattice incident", "EVENT", "Crystal Lattice Incident"),
    ("lattice incident", "EVENT", "Lattice Incident"),
    ("federstahl catastrophe", "EVENT", "Federstahl Catastrophe"),
    ("immaculate slayception", "EVENT", "Immaculate Slayception"),
    ("tragedy of splat", "EVENT", "Tragedy of Splat"),
    ("slayton particle discovery", "EVENT", "Slayton particle discovery"),
    # CREATIVE_WORK
    ("words of the weaver", "CREATIVE_WORK", "Book One"),
    ("book one", "CREATIVE_WORK", "Book One"),
    ("series bible", "CREATIVE_WORK", "Series Bible"),
    ("slayverse series bible", "CREATIVE_WORK", "Series Bible"),
    ("slayverse lore compend", "CREATIVE_WORK", "Slayverse Lore Compendium"),
    ("the slayton codex", "CREATIVE_WORK", "The Slayton Codex"),
    ("golden wings: fifty year flight path", "CREATIVE_WORK", "Golden Wings: Fifty Year Flight Path"),
    ("golden wingers intergalactic league", "PERSON", "Golden Wingers Intergalactic League"),
    ("golden wingers", "PERSON", "Golden Wingers"),
    ("federstahl institute", "PERSON", "Federstahl Institute (collective agent)"),
    ("hooplehoppers", "PERSON", "Hooplehoppers (collective)"),
]

# Patterns that strongly mark a record as genuinely PROCESS (workflow/tooling).
PROCESS_STRONG_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(LM\s*Studio|llama[\s-]*3|gguf|kobold|ollama|comfyui|automatic1111|hugging\s*face)\b", re.IGNORECASE),
    re.compile(r"\b(after\s*effects|premiere|davinci|fusion|nuke|synth\s*eyes|sapphire|boris\s*fx)\b", re.IGNORECASE),
    re.compile(r"\b(prompt|negative prompt|positive prompt|masterpiece:|sampler|denois)\b", re.IGNORECASE),
    re.compile(r"\b(motion tracking|match[- ]?mov|ken burns|3d tracking|object tracking|scene reconstruction)\b", re.IGNORECASE),
    re.compile(r"\b(JSONL|jsonl|schema|pipeline|validator|validate-jsonl|firewall|HITL|review loop|workflow|protocol)\b"),
    re.compile(r"\b(writers[- ]room|sub-?agent|agent spec|agent instructions|description:\s*\"|---\s*\n)\b"),
    re.compile(r"\bSLAY MODE ACTIVATED\b", re.IGNORECASE),
    re.compile(r"\bchrome-extension:|fireshot capture\b", re.IGNORECASE),
    re.compile(r"\b(ngrok|http[s]?://|api\s*key|token|endpoint)\b", re.IGNORECASE),
    re.compile(r"\bdiffusion master|memory off\b", re.IGNORECASE),
    re.compile(r"\b(temperature|repetition penalty|quantiz|q4_k_s|iq4)\b", re.IGNORECASE),
    re.compile(r"\b(stable diffusion|sdxl|controlnet|lora|checkpoint)\b", re.IGNORECASE),
]

# Patterns that strongly suggest lore-bearing content (override stem default).
LORE_SIGNAL_PATTERNS: dict[str, list[tuple[re.Pattern[str], int]]] = {
    "PERSON": [
        (re.compile(r"\b(Jake|McCullen|Pop|Eli|Cici|Vorst|VUORSE|Weaver|Lisette|Hildebrand|Adelram|Conrad|Hooplehopper|Slayton|Rolf|Miss Slaytonia)\b"), 3),
        (re.compile(r"\b(protagonist|antagonist|rancher|knight|alchemist|oracle|professor)\b", re.IGNORECASE), 1),
    ],
    "PLACE": [
        (re.compile(r"\b(Wyoming|McCullen Ranch|Schloss|Club Cosmic|Velvet Archive|Mirror Cavern|Tyndall)\b"), 3),
        (re.compile(r"\b(ranch|frontier|prairie|castle|outpost|territory|hideaway)\b", re.IGNORECASE), 1),
    ],
    "THING": [
        (re.compile(r"\b(Forbidden Suitcase|Dustbrand|Ring|Shard|Zerethium|Glamoron|Glamourons)\b"), 3),
        (re.compile(r"\b(artifact|relic|sigil|object|substance)\b", re.IGNORECASE), 1),
    ],
    "IDEA": [
        (re.compile(r"\b(Slayton Field|Slayton Force|Thread|soul-?line|doctrine|prophecy|cosmology|metaphysic|principle)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(canon|emotional law|symbolic|tone rules?)\b", re.IGNORECASE), 1),
    ],
    "EVENT": [
        (re.compile(r"\b(Crystal Lattice Incident|Lattice Incident|Federstahl Catastrophe|Immaculate Slayception|Tragedy of Splat|particle discovery)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(season \d|episode|arc|finale|reveal|origin saga|catastrophe|sabotage)\b", re.IGNORECASE), 1),
    ],
    "RELATIONSHIP": [
        (re.compile(r"\b(mother of|father of|son of|daughter of|antagonist of|companion of|temporal echo|lineage|successor|guardian)\b", re.IGNORECASE), 3),
        (re.compile(r"\bsoul-?line\b", re.IGNORECASE), 1),
    ],
    "CREATIVE_WORK": [
        (re.compile(r"\b(series bible|book one|codex entry|logline|treatment|pitch|script|transcript|chapter|verse|monologue|scene\s*\d+|b-?roll|cold open|act structure)\b", re.IGNORECASE), 3),
        (re.compile(r"\b(Golden Wings:|fifty year flight path|documentary|preamble)\b", re.IGNORECASE), 1),
    ],
}

# Tag stems and their default class (only used for PROCESS re-sift decisions
# when content is ambiguous). Confidence here is intentionally `low` because
# the v1 pass already used stems and over-routed to PROCESS.
STEM_TENDENCY: dict[str, tuple[str, str]] = {
    # tooling chats default to PROCESS at low confidence — they'll only stick
    # to PROCESS if the content also matches a strong PROCESS pattern.
    "Kodold": ("PROCESS", "local-LLM tooling chat"),
    "Interweaving": ("PROCESS", "SFX/After Effects tooling chat"),
    "Diffusion": ("PROCESS", "image-generation tooling chat"),
    "Slayverse_Chat": ("UNKNOWN", "Slayverse chat session (mixed)"),
    "chat_digest_03142026": ("UNKNOWN", "chat digest (mixed)"),
    "March_29th_2026": ("UNKNOWN", "March 29 chat digest (mixed)"),
    "cortex_test": ("UNKNOWN", "cortex test material (mixed)"),
    "Hooplehopper-Legacy-Digest": ("UNKNOWN", "Hooplehopper Legacy Digest (mixed)"),
    "The_Origin_Pure": ("CREATIVE_WORK", "scene/script material"),
    "writers-room.agent": ("PROCESS", "writers-room agent spec"),
    "open_threads": ("UNKNOWN", "open_threads (mixed)"),
    "preface": ("PROCESS", "section preface"),
    "skip": ("PROCESS", "provenance skip"),
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


def entity_override(blob_lower: str) -> tuple[str, str, str] | None:
    for needle, cls, reason in ENTITY_OVERRIDES:
        n = needle.lower()
        if n and n in blob_lower:
            return cls, "high", f"entity override: {reason}"
    return None


def stem_of(rec: dict[str, Any]) -> str | None:
    tags = set(safe_strs(rec.get("tags")))
    # ordered so the more distinctive stems win first
    for s in [
        "Kodold",
        "Interweaving",
        "Diffusion",
        "Slayverse_Chat",
        "chat_digest_03142026",
        "March_29th_2026",
        "cortex_test",
        "Hooplehopper-Legacy-Digest",
        "The_Origin_Pure",
        "writers-room.agent",
        "open_threads",
        "preface",
        "skip",
    ]:
        if s in tags:
            return s
    return None


def lore_keyword_classify(blob: str) -> tuple[str, int] | None:
    scores: dict[str, int] = defaultdict(int)
    for cls, patterns in LORE_SIGNAL_PATTERNS.items():
        for pat, weight in patterns:
            if pat.search(blob):
                scores[cls] += weight
    if not scores:
        return None
    top = max(scores.values())
    winners = [c for c, s in scores.items() if s == top]
    # Tie-break: prefer specific narrative classes over collective CREATIVE_WORK
    priority = ["EVENT", "PERSON", "PLACE", "THING", "IDEA", "RELATIONSHIP", "CREATIVE_WORK"]
    winners.sort(key=lambda c: priority.index(c) if c in priority else 99)
    return winners[0], top


def process_signal(blob: str) -> int:
    score = 0
    for pat in PROCESS_STRONG_PATTERNS:
        if pat.search(blob):
            score += 1
    return score


# ---------------------------------------------------------------------------
# Classification (PROCESS re-sift only)
# ---------------------------------------------------------------------------


def reclassify_process(rec: dict[str, Any]) -> tuple[str, str, str]:
    """Re-evaluate a single record currently labeled PROCESS in v1.

    Returns (semantic_class, semantic_confidence, semantic_reason).
    """
    kind = (rec.get("extraction_kind") or "").strip()
    blob = harvest_text_blob(rec)
    blob_lower = blob.lower()

    # Honor structural extraction_kinds that legitimately belong in PROCESS.
    if kind in {"provenance_skip"}:
        return "PROCESS", "high", "provenance_skip is a tooling artifact (re-sift confirms PROCESS)"

    # 1) Named-entity overrides take priority for lore subjects.
    ov = entity_override(blob_lower)
    if ov is not None:
        cls, conf, reason = ov
        return cls, conf, f"{reason}; re-sift lifted from PROCESS"

    # 2) Title-driven heuristics for source_canon_extract rows.
    inner = parse_inner(rec.get("content"))
    title = (inner.get("title") or "").strip()
    title_l = title.lower()

    # Genuinely process-y titles seen in the corpus.
    process_titles = {
        "document preamble",
        "markdown",
        "key features include:",
        "issue recap:",
        "thought for 7s",
        "thought for a second",
        "thought for a few seconds",
        "thought for a couple of seconds",
        "updated memory",
        "stopped talking to app",
        "image content",
        "positive prompt",
        "negative prompt",
        "chatgpt said:",
        "you said:",
        "prompt:",
    }
    if title_l in process_titles:
        # Still try lore keyword classification — title may be generic but text
        # may reveal lore. If lore signal is strong (top score >= 3), lift it.
        lk = lore_keyword_classify(blob)
        ps = process_signal(blob)
        if lk is not None and lk[1] >= 3 and ps == 0:
            return lk[0], "low", f"title `{title or '(blank)'}` is generic, but lore keywords (score {lk[1]}) lift to {lk[0]}; re-sift"
        return "PROCESS", "low", f"generic chat/tooling title `{title or '(blank)'}` and no overriding lore signal (re-sift confirms PROCESS)"

    # Title patterns that strongly point to creative scene/script material.
    if re.match(r"^scene\s*\d+", title_l) or re.search(r"\b(b-?roll|cold open|act \d|chapter \d|verse \d|scene heading)\b", title_l):
        return "CREATIVE_WORK", "high", f"title `{title}` is scene/script material; re-sift -> CREATIVE_WORK"

    # 3) Stem-aware path with lore vs process scoring.
    stem = stem_of(rec)
    lk = lore_keyword_classify(blob)
    ps = process_signal(blob)

    if stem == "writers-room.agent":
        # Writers-room agent specs are operational instructions — keep PROCESS
        # at high confidence unless an entity override has already fired (it
        # hasn't, since we'd have returned above).
        return "PROCESS", "high", "writers-room.agent spec is genuine process material (re-sift confirms PROCESS)"

    if stem in {"Kodold", "Interweaving", "Diffusion"}:
        # Strong tooling stems: keep PROCESS unless lore is clearly dominant.
        if lk is not None and lk[1] >= 4 and ps == 0:
            return lk[0], "low", f"stem `{stem}` but no process signal and strong lore score {lk[1]} -> {lk[0]}; re-sift"
        if lk is not None and lk[1] >= 3 and ps <= 1:
            return lk[0], "low", f"stem `{stem}` but lore score {lk[1]} > process score {ps} -> {lk[0]}; re-sift (low confidence)"
        return "PROCESS", "medium", f"stem `{stem}` is tooling chat and content matches process signals (re-sift confirms PROCESS)"

    if stem == "The_Origin_Pure":
        # Scene/script material — default to CREATIVE_WORK; allow lore override.
        if lk is not None and lk[1] >= 4 and lk[0] != "CREATIVE_WORK":
            return lk[0], "low", f"stem `The_Origin_Pure` but lore score {lk[1]} leans {lk[0]}; re-sift"
        return "CREATIVE_WORK", "medium", "stem `The_Origin_Pure` is scene/script material (re-sift -> CREATIVE_WORK)"

    if stem in {"Slayverse_Chat", "chat_digest_03142026", "March_29th_2026", "cortex_test", "Hooplehopper-Legacy-Digest"}:
        # Mixed stems: let content win.
        if lk is not None and ps == 0 and lk[1] >= 2:
            return lk[0], "low", f"mixed-stem `{stem}` reads as {lk[0]} (lore score {lk[1]}, no process signal); re-sift"
        if lk is not None and lk[1] >= ps + 2:
            return lk[0], "low", f"mixed-stem `{stem}` lore score {lk[1]} > process score {ps} -> {lk[0]}; re-sift"
        if ps >= 1 and (lk is None or lk[1] < 2):
            return "PROCESS", "medium", f"mixed-stem `{stem}` reads as process (process score {ps}, lore weak); re-sift confirms PROCESS"
        # Ambiguous: fall through to content-only.
        if lk is not None:
            return lk[0], "low", f"mixed-stem `{stem}` ambiguous; content keywords lean {lk[0]} (score {lk[1]}); re-sift"
        return "UNKNOWN", "low", f"mixed-stem `{stem}` with no clear lore or process signal; re-sift -> needs Weaver eye"

    if stem in {"open_threads", "preface"}:
        # Preface-as-process or contradiction note: keep PROCESS unless lore
        # subject dominates.
        if lk is not None and lk[1] >= 3:
            return lk[0], "low", f"stem `{stem}` but lore keywords (score {lk[1]}) lean {lk[0]}; re-sift"
        return "PROCESS", "medium", f"stem `{stem}` is preface/contradiction note (re-sift confirms PROCESS)"

    # 4) Stemless source_canon_extract or other PROCESS holdovers: use content.
    if kind == "source_canon_extract":
        if lk is not None and ps == 0:
            return lk[0], "low", f"source_canon_extract with no process signal, lore keywords lean {lk[0]} (score {lk[1]}); re-sift"
        if lk is not None and lk[1] > ps:
            return lk[0], "low", f"source_canon_extract lore score {lk[1]} > process score {ps} -> {lk[0]}; re-sift"
        if ps >= 1:
            return "PROCESS", "medium", f"source_canon_extract with process signal (score {ps}); re-sift confirms PROCESS"
        return "UNKNOWN", "low", "source_canon_extract with no decisive signal; re-sift -> needs Weaver eye"

    # 5) open_thread / open_thread_preface that landed in PROCESS via v1: keep
    # PROCESS unless lore subject dominates.
    if kind in {"open_thread", "open_thread_preface"}:
        if lk is not None and lk[1] >= 3:
            return lk[0], "low", f"open_thread but lore keywords lean {lk[0]} (score {lk[1]}); re-sift"
        return "PROCESS", "medium", f"{kind} reads as process/contradiction note (re-sift confirms PROCESS)"

    # 6) Anything else still labeled PROCESS — content-only fallback.
    if lk is not None and ps == 0 and lk[1] >= 2:
        return lk[0], "low", f"no stem; lore keywords lean {lk[0]} (score {lk[1]}); re-sift"
    if ps >= 1 and (lk is None or lk[1] < ps):
        return "PROCESS", "medium", f"process keywords dominate (score {ps}); re-sift confirms PROCESS"
    return "UNKNOWN", "low", "re-sift: no clear lore or process signal; needs Weaver eye"


def append_note(rec: dict[str, Any], addition: str) -> str:
    prior = str(rec.get("notes") or "").strip()
    if not prior:
        return addition
    # Avoid duplicating the same line.
    if addition in prior:
        return prior
    return f"{prior} | {addition}"


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


def validate_jsonl(
    path: Path, expected_ids: set[str], expected_total: int
) -> tuple[bool, list[str]]:
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
            rid = rec.get("id")
            if rid in seen_ids:
                errs.append(f"line {ln}: duplicate id {rid}")
            seen_ids.add(rid)
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
    process_in: int,
    process_out: int,
    reclassified: list[dict[str, Any]],
    remaining_process: list[dict[str, Any]],
    ambiguous: list[dict[str, Any]],
    validation_ok: bool,
    validation_errs: list[str],
) -> str:
    class_counts = Counter(r["semantic_class"] for r in enriched)

    def primary_name(r: dict[str, Any]) -> str:
        ents = safe_strs(r.get("entities"))
        for e in ents:
            if e.strip():
                return e.strip()
        inner = parse_inner(r.get("content"))
        t = (inner.get("title") or "").strip() if inner else ""
        if t:
            return t
        anchor = (r.get("source_anchor") or "").strip()
        return anchor

    def one_line_reason(r: dict[str, Any]) -> str:
        return r.get("semantic_reason") or ""

    def one_line_gist(r: dict[str, Any]) -> str:
        inner = parse_inner(r.get("content"))
        if inner:
            for k in ("summary", "text", "title"):
                v = inner.get(k)
                if v:
                    return gist(v, 120)
        return gist(r.get("content") or "", 120)

    lines: list[str] = []
    L = lines.append

    L("# Canon Corpus — PROCESS Bucket Re-sift Report")
    L("")
    L(f"- Input (v1 sift): `{IN_PATH.relative_to(ROOT)}`")
    L(f"- Output (v2 sift): `{OUT_JSONL.relative_to(ROOT)}`")
    L("- Generator: `scripts/_canon_process_resift_oneoff.py` (read-only against the corpus)")
    L("- Scope: re-evaluates only v1 `semantic_class == \"PROCESS\"` records; "
      "non-PROCESS records pass through unchanged.")
    L("")

    L("## 1. Input PROCESS count")
    L("")
    L(f"**{process_in}** records were classified PROCESS in the v1 sift.")
    L("")

    L("## 2. Output PROCESS count")
    L("")
    L(f"**{process_out}** records remain PROCESS in the v2 sift.")
    L("")

    L("## 3. Number of PROCESS records reclassified")
    L("")
    L(f"**{len(reclassified)}** records were reclassified out of PROCESS during the re-sift.")
    L("")
    if validation_ok:
        L("Validation: **PASS** (every line parses as a JSON object; id-set "
          "equality and record count hold; allowed-class / allowed-confidence / "
          "boolean-review checks pass).")
    else:
        L(f"Validation: **FAIL** — {len(validation_errs)} errors. First 20:")
        L("")
        for e in validation_errs[:20]:
            L(f"- {e}")
    L("")

    L("## 4. New counts by `semantic_class` (whole corpus, all records)")
    L("")
    L("| semantic_class | count |")
    L("|---|---:|")
    for k in [
        "PERSON",
        "PLACE",
        "THING",
        "IDEA",
        "EVENT",
        "RELATIONSHIP",
        "CREATIVE_WORK",
        "PROCESS",
        "UNKNOWN",
    ]:
        L(f"| `{k}` | {class_counts.get(k, 0)} |")
    L("")

    L("## 5. Top 50 records remaining in PROCESS")
    L("")
    L(f"Bucket size after re-sift: **{len(remaining_process)}**.")
    L("Selection: prefer high-confidence first, then those with a non-empty "
      "primary entity name, deprioritizing pure preface/skip rows.")

    def remain_rank(r: dict[str, Any]) -> tuple[int, int, int]:
        c = {"high": 3, "medium": 2, "low": 1}[r["semantic_confidence"]]
        has_name = 1 if primary_name(r) else 0
        # source_canon_extract last so the report shows informative rows.
        kind_pen = 0 if r.get("extraction_kind") == "source_canon_extract" else 1
        return (c, kind_pen, has_name)

    rp = sorted(remaining_process, key=remain_rank, reverse=True)[:50]
    L("")
    L("| id | source_path | primary_entity_name | reason |")
    L("|---|---|---|---|")
    for r in rp:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| {md_escape(primary_name(r))} | {md_escape(one_line_reason(r))} |"
        )
    L("")

    L("## 6. Top 50 reclassified records (old PROCESS -> new)")
    L("")
    L(f"Total reclassified: **{len(reclassified)}**. Selection: high-confidence "
      "reclassifications first, then medium, then low; within each tier, "
      "prefer those with a clean primary entity name.")

    def reclass_rank(r: dict[str, Any]) -> tuple[int, int]:
        c = {"high": 3, "medium": 2, "low": 1}[r["semantic_confidence"]]
        has_name = 1 if primary_name(r) else 0
        return (c, has_name)

    rc = sorted(reclassified, key=reclass_rank, reverse=True)[:50]
    L("")
    L("| id | source_path | old -> new | gist |")
    L("|---|---|---|---|")
    for r in rc:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| `PROCESS -> {r['semantic_class']}` ({r['semantic_confidence']}) "
            f"| {md_escape(one_line_gist(r))} |"
        )
    L("")

    L("## 7. Ambiguous records still needing Weaver review (from this re-sift)")
    L("")
    L("Source: records whose v1 class was PROCESS AND `needs_weaver_review` "
      "is true after re-sift. Caps at 50; tail count noted if more.")
    cap = 50
    if len(ambiguous) > cap:
        L("")
        L(f"_Total: {len(ambiguous)}. Showing first {cap}; {len(ambiguous)-cap} additional "
          "records also carry `needs_weaver_review: true` and live in the v2 JSONL._")
    else:
        L("")
        L(f"_Total: {len(ambiguous)}._")
    L("")
    L("| id | source_path | semantic_class | confidence | semantic_reason |")
    L("|---|---|---|---|---|")
    for r in ambiguous[:cap]:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| `{r['semantic_class']}` | `{r['semantic_confidence']}` "
            f"| {md_escape(r.get('semantic_reason',''))} |"
        )
    L("")

    L("## 8. Recommended next safe action")
    L("")
    L(
        "Convene the Weaver around section 7 (ambiguous review queue) and "
        "section 6 (top reclassifications), using the v2 sift as a diff "
        "against the v1 sift rather than as a movement instruction. The "
        "re-sift JSONL stays in `synthetic_enrichment/generated/`; nothing "
        "moves to `synthetic_enrichment/validated/`, nothing is written to "
        "`hooplehopper_totality/`, no training data is derived, and no record "
        "is marked `[APPROVED_FOR_JSONL]` outside the Human-in-the-Loop "
        "Quickstart loop. The next mechanical step is a Weaver spot-check of "
        "the top 50 reclassifications in section 6 and the top 50 remaining "
        "PROCESS rows in section 5; once those are confirmed or revised, a "
        "follow-up agent pass may enrich `primary_entity_name` and "
        "`secondary_entity_names` for the rows the Weaver has actually walked, "
        "and only then may a subsequent ticket route any subset into "
        "`validated/` with explicit Weaver invocation."
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
    process_in = 0
    reclassified: list[dict[str, Any]] = []
    remaining_process: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []

    for rec in records:
        v1_class = rec.get("semantic_class")
        out_rec = dict(rec)  # preserve all original fields

        if v1_class != "PROCESS":
            # Pass-through unchanged.
            enriched.append(out_rec)
            continue

        process_in += 1
        new_cls, new_conf, new_reason = reclassify_process(rec)
        if new_cls not in ALLOWED_CLASSES:
            new_cls = "UNKNOWN"
        if new_conf not in ALLOWED_CONFIDENCE:
            new_conf = "low"

        # Update fields in place.
        out_rec["semantic_class"] = new_cls
        out_rec["semantic_confidence"] = new_conf
        out_rec["semantic_reason"] = new_reason

        # Recompute needs_weaver_review:
        #   - preserve if already True
        #   - set True for low confidence or UNKNOWN
        #   - keep True for sealed material (canon_tier == mythic_rumor_locked)
        prior_review = bool(rec.get("needs_weaver_review"))
        review = prior_review
        if new_conf == "low":
            review = True
        if new_cls == "UNKNOWN":
            review = True
        if rec.get("canon_tier") == "mythic_rumor_locked":
            review = True
        out_rec["needs_weaver_review"] = bool(review)

        # Append concise note.
        if new_cls != "PROCESS":
            note = f"{RESIFT_NOTE}: reclassified PROCESS -> {new_cls} ({new_conf})"
        else:
            note = f"{RESIFT_NOTE}: confirmed PROCESS ({new_conf})"
        out_rec["notes"] = append_note(rec, note)

        enriched.append(out_rec)

        if new_cls != "PROCESS":
            reclassified.append(out_rec)
        else:
            remaining_process.append(out_rec)
        if out_rec["needs_weaver_review"]:
            ambiguous.append(out_rec)

    # Write JSONL.
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in enriched:
            fh.write(json.dumps(r, ensure_ascii=False))
            fh.write("\n")

    ok, errs = validate_jsonl(OUT_JSONL, expected_ids, total_in)

    process_out = sum(1 for r in enriched if r["semantic_class"] == "PROCESS")

    report = render_report(
        enriched,
        process_in,
        process_out,
        reclassified,
        remaining_process,
        ambiguous,
        ok,
        errs,
    )
    OUT_MD.write_text(report, encoding="utf-8")

    cc = Counter(r["semantic_class"] for r in enriched)
    print(
        "summary: "
        f"in_total={total_in} process_in={process_in} process_out={process_out} "
        f"reclassified={len(reclassified)} ambiguous={len(ambiguous)} "
        f"validation={'PASS' if ok else 'FAIL'} "
        + " ".join(
            f"{k}={cc.get(k,0)}"
            for k in [
                "PERSON",
                "PLACE",
                "THING",
                "IDEA",
                "EVENT",
                "RELATIONSHIP",
                "CREATIVE_WORK",
                "PROCESS",
                "UNKNOWN",
            ]
        )
    )
    if not ok:
        print("VALIDATION ERRORS (first 10):")
        for e in errs[:10]:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
