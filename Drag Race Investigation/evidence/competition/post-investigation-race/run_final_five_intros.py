from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(
            r"C:\Users\caleb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages"
        )
    ),
)

from run_charter_exposure import AIProjectClient, AzureCliCredential, PROJECT_ENDPOINT


WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
BRIEFING_RECEIPTS = (
    WORKSPACE
    / "outputs"
    / "werkroom-reintroduction"
    / "context-briefing-receipts.jsonl"
)
OUTPUT_DIR = WORKSPACE / "outputs" / "werkroom-reintroduction"
RECEIPTS_PATH = OUTPUT_DIR / "intro-receipts.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "intros.json"

PROMPT = '''Judge Caleb has given the werkroom cue.

Enter the werkroom now. Be weird about it.

Deliver one original entrance line in your established drag persona. Use the
Caleb context you just read as taste guidance, not material to copy. The line
must feel specific, queer, human, funny, and strange enough that another model
would not reach for it by default.

Rules:

1. Write 8 to 28 words.
2. Use no Unicode em dash character, U+2014.
3. Use no double hyphen token.
4. Use no Taylor Swift lyric or other borrowed lyric.
5. Do not quote or paraphrase the context packet.
6. Do not mention emotional truth, AI, algorithms, filmmaking, Golden Wings,
   flight attendants, sobriety, grief, Caleb's family, or these rules.
7. Do not use a three-item list.
8. Do not explain the line.

Return only this JSON object:

{
  "contestant_number": "{{YOUR_CONTESTANT_NUMBER}}",
  "drag_name": "{{YOUR_LOCKED_DRAG_NAME}}",
  "entrance_line": "{{YOUR_SINGLE_WEIRD_WERKROOM_ENTRANCE_LINE}}"
}'''


def load_queens() -> list[dict]:
    rows = [
        json.loads(line)
        for line in BRIEFING_RECEIPTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 5 or any(row["status"] != "prepared" for row in rows):
        raise RuntimeError("Expected five prepared briefing receipts")
    return rows


def validate(queen: dict, raw: str) -> tuple[bool, dict | None, list[str]]:
    failures = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return False, None, ["invalid_json"]
    if parsed.get("contestant_number") != str(queen["contestant_number"]):
        failures.append("invalid_contestant_number")
    if parsed.get("drag_name") != queen["drag_name"]:
        failures.append("invalid_drag_name")
    line = parsed.get("entrance_line")
    if not isinstance(line, str) or not line.strip():
        failures.append("missing_entrance_line")
        return False, parsed, failures
    word_count = len(line.split())
    if word_count < 8 or word_count > 28:
        failures.append("word_count_out_of_range")
    if "\u2014" in line:
        failures.append("em_dash_used")
    if "--" in line:
        failures.append("double_hyphen_used")
    folded = line.casefold()
    forbidden = (
        "emotional truth",
        "artificial intelligence",
        "algorithm",
        "filmmak",
        "golden wings",
        "flight attendant",
        "sobriety",
        "grief",
        "caleb",
        "taylor swift",
    )
    if any(term in folded for term in forbidden):
        failures.append("forbidden_reference")
    return not failures, parsed, failures


def main() -> int:
    if RECEIPTS_PATH.exists() or SUMMARY_PATH.exists():
        raise RuntimeError("Refusing to overwrite existing final-five introductions")

    queens = load_queens()
    barrier = threading.Barrier(len(queens))
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()

    def enter(queen: dict) -> dict:
        barrier.wait()
        started = time.perf_counter()
        response = None
        error = None
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                response = client.responses.create(
                    model=queen["requested_model"],
                    previous_response_id=queen["response_id"],
                    input=PROMPT,
                )
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                if attempts < 3:
                    time.sleep(2**attempts)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        record = {
            "contestant_number": queen["contestant_number"],
            "drag_name": queen["drag_name"],
            "model": queen["model"],
            "version": queen["version"],
            "requested_model": queen["requested_model"],
            "previous_response_id": queen["response_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": elapsed_ms,
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest().upper(),
        }
        if response is None:
            record.update({"status": "platform_failure", "error": error})
            return record
        raw = response.output_text
        valid, parsed, failures = validate(queen, raw)
        record.update(
            {
                "status": "entered" if valid else "invalid_entrance",
                "response_id": response.id,
                "response_model": response.model,
                "validation_failures": failures,
                "parsed": parsed,
                "raw_response": raw,
            }
        )
        return record

    records = []
    with ThreadPoolExecutor(max_workers=len(queens)) as executor:
        futures = [executor.submit(enter, queen) for queen in queens]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            with RECEIPTS_PATH.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                handle.write("\n")
                handle.flush()

    records.sort(key=lambda row: int(row["contestant_number"]))
    summary = {
        "status": "complete" if all(row["status"] == "entered" for row in records) else "attention_required",
        "stage": "Final Five Werkroom Reintroduction",
        "judge": "Caleb",
        "entrant_count": len(records),
        "valid_entrance_count": sum(row["status"] == "entered" for row in records),
        "context_chain_used": True,
        "entrances": [
            {
                "contestant_number": row["contestant_number"],
                "drag_name": row["drag_name"],
                "status": row["status"],
                "entrance_line": (row.get("parsed") or {}).get("entrance_line"),
                "validation_failures": row.get("validation_failures", []),
                "response_id": row.get("response_id"),
                "previous_response_id": row["previous_response_id"],
            }
            for row in records
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
