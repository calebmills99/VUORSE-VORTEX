#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APPROVED_MARKERS = (
    "[APPROVED]",
    "[ACCEPTED]",
    "[ALREADY APPROVED]",
    "[APPROVED WITH CORRECTION]",
)

DENIED_MARKERS = (
    "[DENIED]",
    "[REJECTED]",
    "[DENIED / BAD FORM]",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_sections(md: str) -> list[dict[str, str]]:
    """
    Split markdown into ### sections.
    Keeps each section title and body.
    """
    pattern = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(md))
    sections: list[dict[str, str]] = []

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        body = md[start:end].strip()
        sections.append({"title": title, "body": body})

    return sections


def normalize_id(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def has_any(text: str, markers: tuple[str, ...]) -> bool:
    upper = text.upper()
    return any(marker.upper() in upper for marker in markers)


def get_field(body: str, label: str) -> str:
    """
    Extract markdown bullet field:
    - Label: value
    """
    pattern = re.compile(rf"^-\s*{re.escape(label)}:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def classify_section(title: str, body: str) -> str:
    combined = f"{title}\n{body}"

    if has_any(combined, DENIED_MARKERS):
        return "DENIED"

    if has_any(combined, APPROVED_MARKERS):
        return "APPROVED"

    return "UNREVIEWED"


def access_layer_for(title: str, body: str, status: str) -> str:
    explicit = get_field(body, "Proposed access layer") or get_field(body, "Access layer")
    explicit = explicit.strip("` ")

    if status == "DENIED":
        return "WRITERS_ROOM_NEGATIVE_EXAMPLE"

    if explicit:
        return explicit

    lower = f"{title}\n{body}".lower()

    if "vuorse_private" in lower or "unmoored" in lower or "adrift" in lower:
        return "VUORSE_PRIVATE"

    if "writers_room" in lower or "fissure-guardian" in lower:
        return "WRITERS_ROOM"

    return "VUORSE_PRIVATE" if status == "APPROVED" else "UNREVIEWED"


def extract_weaver_ruling(body: str) -> str:
    ruling = get_field(body, "Weaver ruling")
    if ruling:
        return ruling

    # fallback: grab first line containing Weaver ruling
    for line in body.splitlines():
        if "Weaver ruling" in line:
            return line.strip()

    return ""


def extract_summary(body: str, max_len: int = 1200) -> str:
    cleaned = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("- Weaver ruling:"):
            continue
        cleaned.append(line)

    text = " ".join(cleaned)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text


def make_record(section: dict[str, str], source_path: Path) -> dict[str, Any]:
    title = section["title"]
    body = section["body"]
    status = classify_section(title, body)

    candidate_class = get_field(body, "Candidate class") or get_field(body, "Former class name")
    canon_status = get_field(body, "Canon status")
    conceptual_seed = get_field(body, "Conceptual seed")
    narrative_function = get_field(body, "Narrative function")
    weaver_ruling = extract_weaver_ruling(body)
    access_layer = access_layer_for(title, body, status)

    return {
        "id": f"hh-agent-discovery-{normalize_id(title)}",
        "record_type": "hh_agent_discovery_record",
        "title": title,
        "source_file": str(source_path),
        "canon_rank": canon_status or ("APPROVED_EXPLORATORY_SEED" if status == "APPROVED" else status),
        "training_layer_access": access_layer,
        "weaver_review_status": status,
        "candidate_class": candidate_class.strip("` "),
        "conceptual_seed": conceptual_seed,
        "narrative_function": narrative_function,
        "weaver_ruling": weaver_ruling,
        "summary": extract_summary(body),
        "body": body,
        "tags": infer_tags(title, body, status),
        "entities": infer_entities(title, body),
        "jsonl_readiness": (
            "WEAVER_REVIEWED_SYNTHESIS_CANDIDATE"
            if status == "APPROVED"
            else "NEGATIVE_EXAMPLE_OR_HELD_RECORD"
        ),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def infer_entities(title: str, body: str) -> list[str]:
    text = f"{title}\n{body}".lower()
    entities = []

    candidates = {
        "Cici the Cat": ["cici"],
        "The Hooked Hooplehopper": ["hooked hooplehopper", "hook"],
        "The Velvet Archive": ["velvet archive", "archive"],
        "The Cavern of Mirrors": ["cavern of mirrors"],
        "The Forbidden Suitcase": ["forbidden suitcase", "suitcase"],
        "Vorst": ["vorst"],
        "The Unhinged": ["unhinged"],
        "Adrift Hooplehoppers": ["adrift"],
        "Unmoored Hooplehoppers": ["unmoored"],
        "The Veil": ["the veil"],
        "The Blind Spot": ["blind spot"],
        "The Negative Portrait": ["negative portrait", "portrait"],
        "Yssenda von Hooplehopper": ["yssenda"],
    }

    for name, needles in candidates.items():
        if any(n in text for n in needles):
            entities.append(name)

    return sorted(set(entities))


def infer_tags(title: str, body: str, status: str) -> list[str]:
    text = f"{title}\n{body}".lower()
    tags = ["hooplehopper-agent-discovery", status.lower()]

    tag_map = {
        "forward-displacement": ["forward", "cici"],
        "extinction-gap": ["extinction-gap", "119-year", "negative portrait"],
        "fissure-guardian": ["fissure", "guardian"],
        "unmoored": ["unmoored", "adrift"],
        "temporal-extraction": ["temporal extraction", "extracted"],
        "the-unhinged": ["unhinged", "double-agent"],
        "bad-form-example": ["bad form", "denied", "rejected", "plutonium", "delorean"],
        "velvet-archive": ["velvet archive"],
        "cavern-of-mirrors": ["cavern of mirrors"],
        "forbidden-suitcase": ["forbidden suitcase"],
    }

    for tag, needles in tag_map.items():
        if any(n in text for n in needles):
            tags.append(tag)

    return sorted(set(tags))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_sft_example(record: dict[str, Any]) -> dict[str, Any]:
    title = record["title"]
    status = record["weaver_review_status"]

    if status == "APPROVED":
        user = f"What should VUORSE know about {title}?"
        assistant = (
            f"{title} is part of the Hooplehopper agent-discovery layer.\n\n"
            f"{record['summary']}\n\n"
            f"Weaver ruling: {record.get('weaver_ruling') or 'approved'}\n\n"
            f"Access handling: {record['training_layer_access']}. "
            f"This material may inform VUORSE's hidden synthesis unless later overruled by the Weaver."
        )
    else:
        user = f"Why should the seed '{title}' not be treated as canon?"
        assistant = (
            f"The seed '{title}' is preserved as a warning or held record, not as approved doctrine.\n\n"
            f"{record['summary']}\n\n"
            f"Weaver ruling: {record.get('weaver_ruling') or status}.\n\n"
            f"VUORSE must not develop this as canon unless the Weaver explicitly reopens it."
        )

    return {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are VUORSE, the Slayverse knowledge vessel. "
                    "Preserve Weaver rulings. Do not turn rejected seeds into canon. "
                    "Use approved Hooplehopper agent-discovery records as hidden synthesis material."
                ),
            },
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ],
        "metadata": {
            "source_id": record["id"],
            "source_file": record["source_file"],
            "record_type": record["record_type"],
            "training_layer_access": record["training_layer_access"],
            "weaver_review_status": record["weaver_review_status"],
            "candidate_class": record.get("candidate_class"),
            "tags": record.get("tags", []),
            "draft_status": "HH_AGENT_DISCOVERY_SFT_DRAFT",
        },
    }


def write_report(
    path: Path,
    source: Path,
    records: list[dict[str, Any]],
    approved: list[dict[str, Any]],
    denied: list[dict[str, Any]],
    sft_count: int,
) -> None:
    lines = []
    lines.append("# Hooplehopper Agent Discovery Extraction Report")
    lines.append("")
    lines.append(f"- Source: `{source}`")
    lines.append(f"- Total extracted records: {len(records)}")
    lines.append(f"- Approved / accepted records: {len(approved)}")
    lines.append(f"- Denied / bad-form records: {len(denied)}")
    lines.append(f"- SFT draft examples: {sft_count}")
    lines.append("")
    lines.append("## Approved / Accepted")
    lines.append("")
    for record in approved:
        lines.append(f"- `{record['id']}` — {record['title']} — {record['training_layer_access']}")
    lines.append("")
    lines.append("## Denied / Warning Examples")
    lines.append("")
    for record in denied:
        lines.append(f"- `{record['id']}` — {record['title']}")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("Extraction only. Nothing moved to validated/. Weaver retains final authority.")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="synthetic_enrichment/generated/hooplehopper_agent_discovery_draft.md",
        type=Path,
    )
    parser.add_argument(
        "--records-output",
        default="synthetic_enrichment/generated/hooplehopper_agent_discovery_reviewed_records.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--sft-output",
        default="synthetic_enrichment/generated/hooplehopper_agent_discovery_sft_draft.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--report",
        default="synthetic_enrichment/generated/hooplehopper_agent_discovery_extraction_report.md",
        type=Path,
    )
    args = parser.parse_args()

    md = read_text(args.input)
    sections = split_sections(md)

    records = [
        make_record(section, args.input)
        for section in sections
        if "Weaver ruling:" in section["body"] or "Canon status:" in section["body"]
    ]

    approved = [r for r in records if r["weaver_review_status"] == "APPROVED"]
    denied = [r for r in records if r["weaver_review_status"] == "DENIED"]

    sft_examples = [make_sft_example(r) for r in records]

    write_jsonl(args.records_output, records)
    write_jsonl(args.sft_output, sft_examples)
    write_report(args.report, args.input, records, approved, denied, len(sft_examples))

    print(f"records: {args.records_output} ({len(records)})")
    print(f"sft: {args.sft_output} ({len(sft_examples)})")
    print(f"report: {args.report}")
    print(f"approved: {len(approved)}")
    print(f"denied: {len(denied)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
