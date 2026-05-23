import json
import re
from pathlib import Path
from collections import Counter

from vuorse_vortex.sifting import clean_concept_name, is_valid_concept_name


inp = Path("synthetic_enrichment/generated/canon_corpus_entity_sift_scripted.jsonl")
out = Path("synthetic_enrichment/generated/weaver_review_packet_001_mythic_and_hooplehopper.md")

records = [json.loads(line) for line in inp.read_text(encoding="utf-8").splitlines() if line.strip()]

def text(r):
    return " ".join(str(r.get(k, "")) for k in [
        "id", "title", "summary", "body", "content", "entities", "tags",
        "canon_rank", "training_layer_access", "semantic_class",
        "dominant_noun_phrase"
    ]).lower()

priority = []
for r in records:
    t = text(r)
    is_mythic_locked = "mythic_rumor_locked" in t or "mythic rumor that is also locked canon" in t
    is_private = "vuorse_private" in t or "[vuorse_private]" in t
    is_hoople = "hooplehopper" in t
    is_vorst = "vorst" in t or "federstahl" in t
    is_vuorse = "vuorse" in t

    if is_mythic_locked or is_private or is_hoople or is_vorst or is_vuorse:
        priority.append((r, is_mythic_locked, is_private, is_hoople, is_vorst, is_vuorse))

lines = []
lines.append("# Weaver Review Packet 001")
lines.append("")
lines.append("## Purpose")
lines.append("")
lines.append("First human review packet from the cleaned semantic corpus.")
lines.append("")
lines.append("This packet prioritizes Mythic-Rumor-and-Locked material, VUORSE-private doctrine, Hooplehopper records, Vorst/Federstahl records, and VUORSE records.")
lines.append("")
lines.append("Nothing in this packet is approved for training until the Weaver marks it.")
lines.append("")
lines.append("## Corpus Counts")
lines.append("")
lines.append(f"- Semantic records reviewed for packet: {len(records)}")
lines.append(f"- Records in this packet: {len(priority)}")
lines.append("")
lines.append("## Counts by semantic_class")
lines.append("")
for k, v in sorted(Counter(r.get("semantic_class", "UNKNOWN") for r in records).items()):
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Weaver Decision Labels")
lines.append("")
lines.append("Use one per record:")
lines.append("")
lines.append("- [APPROVED_FOR_JSONL]")
lines.append("- [REVISE_WITH_WEAVER_NOTES]")
lines.append("- [REJECTED]")
lines.append("- [WEAVER_ONLY]")
lines.append("- [VUORSE_PRIVATE]")
lines.append("- [PUBLIC_SURFACE]")
lines.append("- [WRITERS_ROOM]")
lines.append("")
lines.append("---")
lines.append("")

for i, (r, mythic, private, hoople, vorst, vuorse) in enumerate(priority, start=1):
    flags = []
    if mythic: flags.append("MYTHIC_RUMOR_LOCKED")
    if private: flags.append("VUORSE_PRIVATE")
    if hoople: flags.append("HOOPLEHOPPER")
    if vorst: flags.append("VORST_FEDERSTAHL")
    if vuorse: flags.append("VUORSE")

    t_raw = r.get("title") or r.get("dominant_noun_phrase") or r.get("id") or ""
    title = clean_concept_name(t_raw)
    if not title or not is_valid_concept_name(title):
        title = t_raw
    body = r.get("summary") or r.get("body") or r.get("content") or ""
    body = str(body).replace("\n", " ").strip()
    if len(body) > 900:
        body = body[:900] + "..."

    lines.append(f"## {i}. {title}")
    lines.append("")
    lines.append(f"- id: `{r.get('id')}`")
    lines.append(f"- semantic_class: `{r.get('semantic_class')}`")
    lines.append(f"- canon_rank: `{r.get('canon_rank') or r.get('canon_tier') or ''}`")
    lines.append(f"- training_layer_access: `{r.get('training_layer_access', '')}`")
    lines.append(f"- source: `{r.get('source_path') or r.get('source_file') or ''}`")
    lines.append(f"- flags: `{', '.join(flags)}`")
    lines.append("")
    lines.append("### Extract")
    lines.append("")
    lines.append(body or "[no body text]")
    lines.append("")
    lines.append("### Weaver Decision")
    lines.append("")
    lines.append("[ ] APPROVED_FOR_JSONL")
    lines.append("[ ] REVISE_WITH_WEAVER_NOTES")
    lines.append("[ ] REJECTED")
    lines.append("[ ] WEAVER_ONLY")
    lines.append("[ ] VUORSE_PRIVATE")
    lines.append("[ ] PUBLIC_SURFACE")
    lines.append("[ ] WRITERS_ROOM")
    lines.append("")
    lines.append("### Weaver Notes")
    lines.append("")
    lines.append("- ")
    lines.append("")
    lines.append("---")
    lines.append("")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {out}")
print(f"Packet records: {len(priority)}")
