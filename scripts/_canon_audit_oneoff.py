#!/usr/bin/env python3
"""One-off canon audit.

Reads synthetic_enrichment/generated/canon_corpus_raw.jsonl and produces
synthetic_enrichment/generated/canon_corpus_raw_audit.md per the audit
ticket. Read-only against the corpus; writes only the audit markdown.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path("/Users/Apple/VUORSE-VORTEX")
IN_PATH = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_raw.jsonl"
OUT_PATH = ROOT / "synthetic_enrichment" / "generated" / "canon_corpus_raw_audit.md"

REQUIRED_FIELDS = ["id", "source_path", "content", "canon_tier", "extraction_kind"]


def synth_layer(rec: dict[str, Any]) -> str:
    kind = rec.get("extraction_kind") or ""
    tier = rec.get("canon_tier") or "unlabeled"
    if kind == "provenance_skip":
        return "[REVISE_WITH_WEAVER_NOTES]"
    if tier == "mythic_rumor_locked":
        return "[VUORSE_PRIVATE]"
    if tier == "locked_canon":
        return "[APPROVED_FOR_JSONL]"
    if tier == "development_canon":
        return "[WRITERS_ROOM]"
    if tier == "mythic_rumor":
        return "[WRITERS_ROOM]"
    if tier == "unlabeled":
        if rec.get("weaver_review_required") is True:
            return "[REVISE_WITH_WEAVER_NOTES]"
        return "[WRITERS_ROOM]"
    return "[WRITERS_ROOM]"


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
                raise RuntimeError(f"line {ln} not JSON: {e}") from e
    return out


WYOMING_TOKENS = re.compile(
    r"\b(Jake|McCullen|prairie mother|Pop|ranch|mother'?s name|Wyoming)\b", re.IGNORECASE
)
HOOPLE_TOKENS = re.compile(
    r"(Hooplehopper|Huppelhopper|lattice refugee|soul-line|return rather than descend|"
    r"do not descend\.? They return)",
    re.IGNORECASE,
)
VORST_TOKENS = re.compile(
    r"(Vorst|Federstahl|Crystal Lattice|Lattice Incident|Catastrophe|Professor A\.?)",
    re.IGNORECASE,
)
VUORSE_TOKENS = re.compile(
    r"(VUORSE|Velvet Archive|drag oracle|cosmic drag)", re.IGNORECASE
)
FINALE_TOKENS = re.compile(
    r"(finale|Immaculate Slayception|Forbidden Suitcase|119-year|seam-rip|Eden)", re.IGNORECASE
)
PENDING_LIKE = {"PENDING REVIEW", "EXPLORATORY", "HOOK ONLY", "SKETCHED"}


def matches(rec: dict[str, Any], pat: re.Pattern[str]) -> bool:
    content = rec.get("content") or ""
    ents = " ".join(safe_strs(rec.get("entities")))
    tags = " ".join(safe_strs(rec.get("tags")))
    blob = " ".join([str(content), ents, tags])
    return bool(pat.search(blob))


def main() -> None:
    records = load_records(IN_PATH)
    total = len(records)

    kind_counts = Counter(r.get("extraction_kind") or "(none)" for r in records)
    tier_counts = Counter(r.get("canon_tier") or "unlabeled" for r in records)

    layer_for = {r.get("id"): synth_layer(r) for r in records}
    layer_counts = Counter(layer_for.values())

    mrl = [r for r in records if r.get("canon_tier") == "mythic_rumor_locked"]
    vuorse_private = [r for r in records if layer_for.get(r.get("id")) == "[VUORSE_PRIVATE]"]

    flagged: list[tuple[dict[str, Any], str]] = []
    for r in records:
        why = []
        if r.get("weaver_review_required") is True:
            why.append("weaver_review_required=true")
        notes = (r.get("notes") or "").strip()
        if notes:
            why.append("has notes")
        if why:
            flagged.append((r, "; ".join(why)))

    unlabeled = [r for r in records if (r.get("canon_tier") or "unlabeled") == "unlabeled"]
    unlabeled_src_counts = Counter(r.get("source_path") or "(none)" for r in unlabeled)

    by_src: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        by_src[r.get("source_path") or "(none)"].append(r)

    id_counts = Counter(r.get("id") for r in records)
    dup_ids = [(i, c) for i, c in id_counts.items() if c > 1]

    missing_field_rows: list[tuple[str, list[str]]] = []
    empty_content_rows: list[str] = []
    type_problems: list[tuple[str, str]] = []
    for r in records:
        missing = [f for f in REQUIRED_FIELDS if f not in r]
        if missing:
            missing_field_rows.append((r.get("id") or "(no id)", missing))
        c = r.get("content")
        if c is None or (isinstance(c, str) and not c.strip()):
            empty_content_rows.append(r.get("id") or "(no id)")
        if "entities" in r and not isinstance(r["entities"], list):
            type_problems.append((r.get("id") or "(no id)", "entities not list"))
        if "tags" in r and not isinstance(r["tags"], list):
            type_problems.append((r.get("id") or "(no id)", "tags not list"))
        if "weaver_review_required" in r and not isinstance(r["weaver_review_required"], bool):
            type_problems.append((r.get("id") or "(no id)", "weaver_review_required not bool"))

    def review_score(r: dict[str, Any]) -> int:
        a = 1 if r.get("canon_tier") == "mythic_rumor_locked" else 0
        label = (r.get("canon_status_label") or "").upper()
        b = 1 if label in PENDING_LIKE else 0
        c = 1 if (r.get("weaver_review_required") is True and len((r.get("content") or "")) > 80) else 0
        d = 1 if matches(r, WYOMING_TOKENS) else 0
        e = 1 if matches(r, FINALE_TOKENS) else 0
        return a * 16 + b * 8 + c * 4 + d * 2 + e

    scored_all = [(r, review_score(r)) for r in records]
    scored_all = [(r, s) for r, s in scored_all if s > 0]
    scored_all.sort(key=lambda x: -x[1])
    review_top25 = [r for r, _ in scored_all[:25]]

    def why_chosen(r: dict[str, Any]) -> str:
        bits = []
        if r.get("canon_tier") == "mythic_rumor_locked":
            bits.append("mythic_rumor_locked")
        label = (r.get("canon_status_label") or "").upper()
        if label in PENDING_LIKE:
            bits.append(f"label={label}")
        if r.get("weaver_review_required") is True:
            bits.append("review_required")
        if matches(r, WYOMING_TOKENS):
            bits.append("wyoming")
        if matches(r, FINALE_TOKENS):
            bits.append("finale-adjacent")
        return ",".join(bits) or "general"

    hh = [r for r in records if matches(r, HOOPLE_TOKENS)]
    vorst = [r for r in records if matches(r, VORST_TOKENS)]
    vuorse = [r for r in records if matches(r, VUORSE_TOKENS)]

    lines: list[str] = []
    L = lines.append

    L("# Canon Corpus Raw — Audit Report")
    L("")
    L(f"- Input: `{IN_PATH.relative_to(ROOT)}`")
    L(f"- Total records: **{total}**")
    L("- Generated by: `scripts/_canon_audit_oneoff.py` (read-only against corpus)")
    L("")
    L("## Field-mapping note (read first)")
    L("")
    L("The raw extraction did not write MemoryRecord fields. The ticket's audit names")
    L("are mapped onto the extraction fields actually present:")
    L("")
    L("| Audit name | Field in record |")
    L("|---|---|")
    L("| `record_type` | `extraction_kind` |")
    L("| `canon_rank` | `canon_tier` |")
    L("| `training_layer_access` | **derived** (not stored); rule below |")
    L("")
    L("Synthetic training-layer rule used in section 4 and section 6:")
    L("")
    L("- `extraction_kind == provenance_skip` → `[REVISE_WITH_WEAVER_NOTES]`")
    L("- `canon_tier == mythic_rumor_locked` → `[VUORSE_PRIVATE]`")
    L("- `canon_tier == locked_canon` → `[APPROVED_FOR_JSONL]`")
    L("- `canon_tier == development_canon` → `[WRITERS_ROOM]`")
    L("- `canon_tier == mythic_rumor` (non-locked) → `[WRITERS_ROOM]`")
    L("- `canon_tier == unlabeled` → `[WRITERS_ROOM]`, unless `weaver_review_required: true` → `[REVISE_WITH_WEAVER_NOTES]`")
    L("")
    L("Conflicts between mapping and an explicit label inside `notes`/body are noted")
    L("inline where observed.")
    L("")

    L("## 1. Total record count")
    L("")
    L(f"**{total}** records.")
    L("")

    L("## 2. Counts by `record_type` (= `extraction_kind`)")
    L("")
    L("| extraction_kind | count |")
    L("|---|---:|")
    for k, c in kind_counts.most_common():
        L(f"| `{k}` | {c} |")
    L("")

    L("## 3. Counts by `canon_rank` (= `canon_tier`)")
    L("")
    L("| canon_tier | count |")
    L("|---|---:|")
    for k, c in tier_counts.most_common():
        L(f"| `{k}` | {c} |")
    L("")

    L("## 4. Counts by `training_layer_access` (synthetic, derived)")
    L("")
    L("Derivation rule is stated in the field-mapping note above; reproduced inline:")
    L("")
    L("> `provenance_skip` → `[REVISE_WITH_WEAVER_NOTES]`; `mythic_rumor_locked` → `[VUORSE_PRIVATE]`;")
    L("> `locked_canon` → `[APPROVED_FOR_JSONL]`; `development_canon` / `mythic_rumor` → `[WRITERS_ROOM]`;")
    L("> `unlabeled` → `[WRITERS_ROOM]` unless `weaver_review_required: true` → `[REVISE_WITH_WEAVER_NOTES]`.")
    L("")
    L("| synthetic_training_layer | count |")
    L("|---|---:|")
    for k, c in layer_counts.most_common():
        L(f"| `{k}` | {c} |")
    L("")

    L("## 5. Mythic Rumor That Is Also Locked Canon")
    L("")
    L(f"Count: **{len(mrl)}** (`canon_tier == mythic_rumor_locked`).")
    L("")
    if mrl:
        L("| id | source_path | source_anchor | gist |")
        L("|---|---|---|---|")
        for r in mrl:
            L(
                f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
                f"| {md_escape(r.get('source_anchor',''))} | {md_escape(gist(r.get('content','')))} |"
            )
    L("")

    L("## 6. `[VUORSE_PRIVATE]` records (synthetic rule)")
    L("")
    if {r.get("id") for r in vuorse_private} == {r.get("id") for r in mrl}:
        L(
            f"Count: **{len(vuorse_private)}**. Identical to section 5 — every "
            "`[VUORSE_PRIVATE]` record under the synthetic rule is a "
            "`mythic_rumor_locked` row. See section 5 for the table."
        )
    else:
        mrl_ids = {r.get("id") for r in mrl}
        only_here = [r for r in vuorse_private if r.get("id") not in mrl_ids]
        L(
            f"Count: **{len(vuorse_private)}**. Differs from section 5 by "
            f"{len(only_here)} rows; listing the deltas:"
        )
        L("")
        L("| id | source_path | source_anchor | gist |")
        L("|---|---|---|---|")
        for r in only_here:
            L(
                f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
                f"| {md_escape(r.get('source_anchor',''))} | {md_escape(gist(r.get('content','')))} |"
            )
    L("")

    L("## 7. Records with Weaver warnings or notes")
    L("")
    L(
        f"Count: **{len(flagged)}** "
        "(rule: `weaver_review_required == true` OR non-empty `notes`)."
    )
    L("")
    if flagged:
        L("| id | source_path | why |")
        L("|---|---|---|")
        for r, why in flagged:
            L(
                f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
                f"| {md_escape(why)}: {md_escape(gist(r.get('notes',''), 110))} |"
            )
    L("")

    L("## 8. Unlabeled records — source distribution")
    L("")
    L(f"Total unlabeled (`canon_tier in {{unlabeled, (missing)}}`): **{len(unlabeled)}**")
    L("")
    if unlabeled_src_counts:
        L("Top source files for unlabeled rows:")
        L("")
        L("| source_path | unlabeled count |")
        L("|---|---:|")
        for src, c in unlabeled_src_counts.most_common(20):
            L(f"| `{md_escape(src)}` | {c} |")
    L("")

    L("## 9. Source-file coverage")
    L("")
    L("| source_path | records | locked | development | mythic_rumor | mythic_rumor_locked | unlabeled | flagged |")
    L("|---|---:|---:|---:|---:|---:|---:|---:|")
    for src in sorted(by_src):
        rs = by_src[src]
        ct = Counter(r.get("canon_tier") or "unlabeled" for r in rs)
        flag_n = sum(
            1
            for r in rs
            if (r.get("weaver_review_required") is True) or (r.get("notes") or "").strip()
        )
        L(
            f"| `{md_escape(src)}` | {len(rs)} | {ct.get('locked_canon',0)} | "
            f"{ct.get('development_canon',0)} | {ct.get('mythic_rumor',0)} | "
            f"{ct.get('mythic_rumor_locked',0)} | {ct.get('unlabeled',0)} | {flag_n} |"
        )
    L("")

    L("## 10. Duplicate `id` check")
    L("")
    if not dup_ids:
        L("**PASS** — all `id` values are unique.")
    else:
        L(f"**FAIL** — {len(dup_ids)} collisions:")
        L("")
        L("| id | count |")
        L("|---|---:|")
        for i, c in dup_ids:
            L(f"| `{md_escape(i)}` | {c} |")
    L("")

    L("## 11. Schema consistency")
    L("")
    L(f"- Required fields checked: {', '.join(f'`{f}`' for f in REQUIRED_FIELDS)}")
    L(f"- Records missing one or more required fields: **{len(missing_field_rows)}**")
    L(f"- Records with empty `content`: **{len(empty_content_rows)}**")
    L(f"- Field-type problems detected: **{len(type_problems)}**")
    L("")
    if missing_field_rows:
        L("Missing-field rows (first 50):")
        L("")
        L("| id | missing |")
        L("|---|---|")
        for i, m in missing_field_rows[:50]:
            L(f"| `{md_escape(i)}` | {', '.join(m)} |")
        L("")
    if empty_content_rows:
        L("Empty-content rows (first 50):")
        L("")
        L("| id |")
        L("|---|")
        for i in empty_content_rows[:50]:
            L(f"| `{md_escape(i)}` |")
        L("")
    if type_problems:
        L("Type problems (first 50):")
        L("")
        L("| id | problem |")
        L("|---|---|")
        for i, p in type_problems[:50]:
            L(f"| `{md_escape(i)}` | {p} |")
        L("")
    if not (missing_field_rows or empty_content_rows or type_problems):
        L("**PASS** — schema consistency clean on the audited dimensions.")
    L("")

    L("## 12. Top 25 records recommended for first Weaver review")
    L("")
    L(
        "Selection signals (descending weight): "
        "Mythic-Rumor-Locked > status label in {PENDING REVIEW, EXPLORATORY, HOOK ONLY, SKETCHED} > "
        "`weaver_review_required: true` with substantive content > Wyoming-wound tokens > finale-adjacent tokens."
    )
    L("")
    L("| rank | id | source_path | source_anchor | why-chosen |")
    L("|---:|---|---|---|---|")
    for i, r in enumerate(review_top25, 1):
        L(
            f"| {i} | `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| {md_escape(r.get('source_anchor',''))} | {md_escape(why_chosen(r))} |"
        )
    L("")

    L("## 13. Top 25 Hooplehopper-related records")
    L("")
    L(
        "Selector: text/entities/tags matching `Hooplehopper`, `Huppelhopper`, "
        "`lattice refugee`, `soul-line`, `return rather than descend`."
    )
    L(f"Total matches: **{len(hh)}**. Showing first 25.")
    L("")
    L("| id | source_path | gist |")
    L("|---|---|---|")
    for r in hh[:25]:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| {md_escape(gist(r.get('content','')))} |"
        )
    L("")

    L("## 14. Top 25 Vorst / Federstahl-related records")
    L("")
    L("Selector: tokens `Vorst`, `Federstahl`, `Crystal Lattice`, `Lattice Incident`, `Catastrophe`, `Professor A.`")
    L(f"Total matches: **{len(vorst)}**. Showing first 25.")
    L("")
    L("| id | source_path | sealed? | gist |")
    L("|---|---|---|---|")
    for r in vorst[:25]:
        sealed = "yes (mythic_rumor_locked)" if r.get("canon_tier") == "mythic_rumor_locked" else "no"
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| {sealed} | {md_escape(gist(r.get('content','')))} |"
        )
    L("")

    L("## 15. Top 25 VUORSE-related records")
    L("")
    L("Selector: tokens `VUORSE`, `Velvet Archive`, `drag oracle`, `cosmic drag`.")
    L(f"Total matches: **{len(vuorse)}**. Showing first 25.")
    L("")
    L("| id | source_path | gist |")
    L("|---|---|---|")
    for r in vuorse[:25]:
        L(
            f"| `{md_escape(r.get('id',''))}` | `{md_escape(r.get('source_path',''))}` "
            f"| {md_escape(gist(r.get('content','')))} |"
        )
    L("")

    L("## 16. Recommended next safe action")
    L("")
    L(
        "Weaver review of the section 12 top-25 list before any movement to "
        "`synthetic_enrichment/validated/`. Until the Weaver passes through that "
        "list and rules on the sealed (mythic_rumor_locked) rows in section 5, "
        "the corpus stays in `synthetic_enrichment/generated/` with default "
        "`weaver_review_status = UNREVIEWED` and `jsonl_readiness = "
        "RAW_CANON_EXTRACT`. No record may cross the firewall, no record may be "
        "marked `[APPROVED_FOR_JSONL]`, and no derived training corpus may be "
        "produced from these rows without explicit Weaver invocation per the "
        "Human-in-the-Loop Quickstart."
    )
    L("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(lines)} lines)")
    print(
        "summary: "
        f"total={total} kinds={len(kind_counts)} tiers={len(tier_counts)} "
        f"mrl={len(mrl)} flagged={len(flagged)} unlabeled={len(unlabeled)} "
        f"hh={len(hh)} vorst={len(vorst)} vuorse={len(vuorse)} "
        f"dup_ids={len(dup_ids)} missing={len(missing_field_rows)} empty={len(empty_content_rows)}"
    )


if __name__ == "__main__":
    main()
