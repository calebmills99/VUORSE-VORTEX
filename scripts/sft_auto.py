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


DECISIONS = {
    "a": "ACCEPT",
    "r": "REVISE",
    "x": "REJECT",
    "s": "SKIP",
}

HELP = """
a = ACCEPT
r = REVISE
x = REJECT
s = SKIP
n = add/edit note
b = back one
q = quit
? = help
"""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            rows.append(obj)
    return rows


def load_reviews(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    reviews: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            key = obj.get("example_id")
            if not key:
                raise ValueError(f"{path}: line {line_no} missing example_id")
            reviews[str(key)] = obj
    return reviews


def save_reviews(path: Path, reviews: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for key in sorted(reviews):
            f.write(json.dumps(reviews[key], ensure_ascii=False) + "\n")


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


def get_message(example: dict[str, Any], role: str) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == role:
            return str(msg.get("content", ""))
    return ""


def example_id(example: dict[str, Any], index: int) -> str:
    meta = example.get("metadata", {})
    return str(meta.get("source_id") or f"example_{index:06d}")


def short(text: str, limit: int = 3600) -> str:
    text = text.strip()
    if len(text) > limit:
        return text[:limit] + "\n...[truncated]"
    return text


def render(example: dict[str, Any], index: int, total: int, existing: dict[str, Any] | None) -> None:
    meta = example.get("metadata", {})
    eid = example_id(example, index)

    clear_screen()
    print("=" * 100)
    print(f"VUORSE SFT STYLE REVIEW {index + 1}/{total}")
    print("=" * 100)
    print(f"Example ID: {eid}")
    print(f"Semantic: {meta.get('semantic_class')}")
    print(f"Access: {meta.get('training_layer_access')}")
    print(f"Canon: {meta.get('canon_rank')}")
    print(f"Source: {meta.get('source_file')}")
    if existing:
        print("-" * 100)
        print(f"Existing decision: {existing.get('decision')}")
        if existing.get("weaver_note"):
            print(f"Existing note: {existing.get('weaver_note')}")
    print("-" * 100)
    print("USER:")
    print(textwrap.fill(short(get_message(example, "user"), 1200), width=100))
    print("-" * 100)
    print("ASSISTANT:")
    print(textwrap.fill(short(get_message(example, "assistant"), 4200), width=100))
    print("-" * 100)
    print("a accept | r revise | x reject | s skip | n note | b back | q quit | ? help")


def write_summary(path: Path, reviews: dict[str, dict[str, Any]]) -> None:
    counts = Counter(r.get("decision", "") for r in reviews.values())
    lines = [
        "VUORSE SFT Sample Review Summary",
        "================================",
        "",
        f"Total reviewed: {len(reviews)}",
        "",
    ]

    for decision, count in counts.most_common():
        lines.append(f"{decision}: {count}")

    lines.append("")
    lines.append("Generated at: " + datetime.now(timezone.utc).isoformat())

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="synthetic_enrichment/generated/vuorse_sft_training_examples_draft.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--reviews",
        default="synthetic_enrichment/generated/vuorse_sft_style_reviews.jsonl",
        type=Path,
    )
    parser.add_argument(
        "--progress",
        default="synthetic_enrichment/generated/vuorse_sft_style_review_progress.json",
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default="synthetic_enrichment/generated/vuorse_sft_style_review_summary.txt",
        type=Path,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of examples to review. Use 0 for all.",
    )
    parser.add_argument("--start", type=int, default=None)
    args = parser.parse_args()

    examples = load_jsonl(args.input)

    if args.limit and args.limit > 0:
        examples = examples[: args.limit]

    reviews = load_reviews(args.reviews)
    index = args.start if args.start is not None else load_progress(args.progress)
    index = max(0, min(index, len(examples)))

    note_buffer = ""

    while index < len(examples):
        example = examples[index]
        eid = example_id(example, index)
        render(example, index, len(examples), reviews.get(eid))

        cmd = input("\nWeaver style ruling> ").strip().lower()

        if cmd == "?":
            print(HELP)
            input("Press ENTER...")
            continue

        if cmd == "q":
            save_reviews(args.reviews, reviews)
            save_progress(args.progress, index)
            write_summary(args.summary, reviews)
            print(f"Saved reviews: {args.reviews}")
            print(f"Progress: {args.progress}")
            print(f"Summary: {args.summary}")
            return 0

        if cmd == "b":
            index = max(0, index - 1)
            save_progress(args.progress, index)
            continue

        if cmd == "n":
            note_buffer = input("Weaver note> ").strip()
            continue

        if cmd not in DECISIONS:
            print("Unknown command. Use ? for help.")
            input("Press ENTER...")
            continue

        decision = DECISIONS[cmd]

        if decision in {"REVISE", "REJECT"} and not note_buffer:
            note_buffer = input("Note> ").strip()

        meta = example.get("metadata", {})

        reviews[eid] = {
            "example_id": eid,
            "decision": decision,
            "weaver_note": note_buffer,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "source_id": meta.get("source_id"),
            "semantic_class": meta.get("semantic_class"),
            "training_layer_access": meta.get("training_layer_access"),
            "canon_rank": meta.get("canon_rank"),
            "source_file": meta.get("source_file"),
        }

        note_buffer = ""

        save_reviews(args.reviews, reviews)
        write_summary(args.summary, reviews)

        index += 1
        save_progress(args.progress, index)

    clear_screen()
    save_reviews(args.reviews, reviews)
    save_progress(args.progress, index)
    write_summary(args.summary, reviews)

    print("SFT style review complete.")
    print(f"Reviewed: {len(reviews)}")
    print(f"Reviews: {args.reviews}")
    print(f"Summary: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
