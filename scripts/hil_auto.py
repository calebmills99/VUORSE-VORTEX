#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import textwrap
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DECISION_KEYS = {
    "a": "APPROVED_FOR_JSONL",
    "v": "VUORSE_PRIVATE",
    "w": "WEAVER_ONLY",
    "r": "REVISE_WITH_WEAVER_NOTES",
    "x": "REJECTED",
    "s": "SKIP",
    "p": "PUBLIC_SURFACE",
    "m": "WRITERS_ROOM",
}

HELP = """
a = APPROVED_FOR_JSONL
v = VUORSE_PRIVATE
w = WEAVER_ONLY
r = REVISE_WITH_WEAVER_NOTES
x = REJECTED
s = SKIP
p = PUBLIC_SURFACE
m = WRITERS_ROOM
n = add/edit note
b = back one
q = quit
? = help
"""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            records.append(obj)
    return records


def load_decisions(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    decisions: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            record_id = obj.get("id")
            if not record_id:
                raise ValueError(f"{path}: line {line_no} missing id")
            decisions[str(record_id)] = obj
    return decisions


def save_decisions(path: Path, decisions: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record_id in sorted(decisions):
            f.write(json.dumps(decisions[record_id], ensure_ascii=False) + "\n")


def load_progress(path: Path) -> int:
    if not path.exists():
        return 0
    obj = json.loads(path.read_text(encoding="utf-8"))
    return int(obj.get("index", 0))


def save_progress(path: Path, index: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "index": index,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def clear_screen() -> None:
    os.system("clear" if os.name != "nt" else "cls")


def as_text(value: Any, limit: int | None = None) -> str:
    if value is None:
        text = ""
    elif isinstance(value, (list, dict)):
        text = json.dumps(value, ensure_ascii=False, indent=2)
    else:
        text = str(value)

    text = text.replace("\r", "").strip()

    if limit is not None and len(text) > limit:
        text = text[:limit] + "\n...[truncated]"

    return text


def body_text(record: dict[str, Any], limit: int = 3200) -> str:
    for key in ("summary", "body", "content", "notes"):
        value = as_text(record.get(key), limit=limit)
        if value:
            return value
    return "[no body text]"


def title_for(record: dict[str, Any]) -> str:
    return (
        as_text(record.get("title"))
        or as_text(record.get("name"))
        or as_text(record.get("dominant_noun_phrase"))
        or as_text(record.get("id"))
    )


def source_for(record: dict[str, Any]) -> str:
    return as_text(record.get("source_path")) or as_text(record.get("source_file"))


def canon_for(record: dict[str, Any]) -> str:
    return as_text(record.get("canon_rank")) or as_text(record.get("canon_tier"))


def access_for(record: dict[str, Any]) -> str:
    return as_text(record.get("training_layer_access"))


def record_blob(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False).lower()


def flags_for(record: dict[str, Any]) -> list[str]:
    blob = record_blob(record)
    flags: list[str] = []

    if "mythic_rumor_locked" in blob or "mythic rumor that is also locked canon" in blob:
        flags.append("MYTHIC_RUMOR_LOCKED")
    if "vuorse_private" in blob or "[vuorse_private]" in blob:
        flags.append("VUORSE_PRIVATE")
    if "hooplehopper" in blob:
        flags.append("HOOPLEHOPPER")
    if "vorst" in blob or "federstahl" in blob:
        flags.append("VORST_FEDERSTAHL")
    if "vuorse" in blob:
        flags.append("VUORSE")

    return flags


def priority_score(record: dict[str, Any]) -> int:
    blob = record_blob(record)
    score = 0

    if "mythic_rumor_locked" in blob or "mythic rumor that is also locked canon" in blob:
        score += 100
    if "vuorse_private" in blob or "[vuorse_private]" in blob:
        score += 80
    if "hooplehopper" in blob:
        score += 50
    if "vorst" in blob or "federstahl" in blob:
        score += 40
    if "vuorse" in blob:
        score += 30
    if record.get("semantic_class") == "PERSON":
        score += 10

    return score


def apply_filter(records: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "all":
        return records

    if mode == "priority":
        out = [r for r in records if priority_score(r) > 0]
        out.sort(key=priority_score, reverse=True)
        return out

    if mode in {
        "PERSON",
        "PLACE",
        "THING",
        "IDEA",
        "EVENT",
        "RELATIONSHIP",
        "CREATIVE_WORK",
        "PROCESS",
        "UNKNOWN",
        "METADATA",
    }:
        return [r for r in records if r.get("semantic_class") == mode]

    raise ValueError(f"Unknown review mode: {mode}")


def render(record: dict[str, Any], index: int, total: int, existing: dict[str, Any] | None) -> None:
    clear_screen()

    print("=" * 100)
    print(f"WEAVER REVIEW {index + 1}/{total}")
    print("=" * 100)
    print(f"Title: {title_for(record)}")
    print(f"ID: {record.get('id')}")
    print(f"Class: {record.get('semantic_class')} | confidence: {record.get('semantic_confidence')}")
    print(f"Canon: {canon_for(record)}")
    print(f"Access: {access_for(record)}")
    print(f"Source: {source_for(record)}")
    print(f"Flags: {', '.join(flags_for(record)) or 'none'}")

    if existing:
        print("-" * 100)
        print(f"Existing decision: {existing.get('decision')}")
        note = existing.get("weaver_note")
        if note:
            print(f"Existing note: {note}")

    print("-" * 100)
    print(textwrap.fill(body_text(record), width=100))
    print("-" * 100)
    print("a approve | v vuorse | w weaver | r revise | x reject | s skip | p public | m room")
    print("n note | b back | q quit | ? help")


def write_summary(path: Path, decisions: dict[str, dict[str, Any]]) -> None:
    counts = Counter(d.get("decision", "") for d in decisions.values())

    lines = []
    lines.append("Weaver Review Summary")
    lines.append("=====================")
    lines.append("")
    lines.append(f"Total reviewed: {len(decisions)}")
    lines.append("")

    for decision, count in counts.most_common():
        lines.append(f"{decision}: {count}")

    lines.append("")
    lines.append("Generated at: " + datetime.now(timezone.utc).isoformat())
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="synthetic_enrichment/generated/canon_corpus_entity_sift_scripted.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--decisions",
        default="synthetic_enrichment/generated/weaver_review_decisions.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--progress",
        default="synthetic_enrichment/generated/weaver_review_progress.json",
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default="synthetic_enrichment/generated/weaver_review_summary.txt",
        type=Path,
    )
    parser.add_argument(
        "--mode",
        default="priority",
        choices=[
            "priority",
            "all",
            "PERSON",
            "PLACE",
            "THING",
            "IDEA",
            "EVENT",
            "RELATIONSHIP",
            "CREATIVE_WORK",
            "PROCESS",
            "UNKNOWN",
            "METADATA",
        ],
    )
    parser.add_argument("--start", type=int, default=None)
    args = parser.parse_args()

    all_records = load_jsonl(args.input)
    records = apply_filter(all_records, args.mode)

    decisions = load_decisions(args.decisions)
    index = args.start if args.start is not None else load_progress(args.progress)
    index = max(0, min(index, len(records)))

    note_buffer = ""

    while index < len(records):
        record = records[index]
        record_id = str(record.get("id"))

        render(record, index, len(records), decisions.get(record_id))
        command = input("\nWeaver ruling> ").strip().lower()

        if command == "?":
            print(HELP)
            input("Press ENTER...")
            continue

        if command == "q":
            save_decisions(args.decisions, decisions)
            save_progress(args.progress, index)
            write_summary(args.summary, decisions)
            print(f"Saved: {args.decisions}")
            print(f"Progress: {args.progress}")
            print(f"Summary: {args.summary}")
            return 0

        if command == "b":
            index = max(0, index - 1)
            save_progress(args.progress, index)
            continue

        if command == "n":
            note_buffer = input("Weaver note> ").strip()
            continue

        if command not in DECISION_KEYS:
            print("Unknown command. Use ? for help.")
            input("Press ENTER...")
            continue

        decision = DECISION_KEYS[command]

        if decision in {"REVISE_WITH_WEAVER_NOTES", "REJECTED", "WEAVER_ONLY"} and not note_buffer:
            note_buffer = input("Note> ").strip()

        decisions[record_id] = {
            "id": record_id,
            "decision": decision,
            "weaver_note": note_buffer,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "title": title_for(record),
            "semantic_class": record.get("semantic_class"),
            "canon_rank": canon_for(record),
            "training_layer_access": access_for(record),
            "source": source_for(record),
            "flags": flags_for(record),
        }

        note_buffer = ""

        save_decisions(args.decisions, decisions)
        write_summary(args.summary, decisions)

        index += 1
        save_progress(args.progress, index)

    clear_screen()
    save_decisions(args.decisions, decisions)
    save_progress(args.progress, index)
    write_summary(args.summary, decisions)

    print("Review complete.")
    print(f"Reviewed decisions: {len(decisions)}")
    print(f"Decisions: {args.decisions}")
    print(f"Summary: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
