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
ELIMINATION_LEDGER = (
    WORKSPACE / "outputs" / "werkroom-entrances" / "em-dash-elimination.json"
)
OUTPUT_DIR = WORKSPACE / "outputs" / "double-hyphen-comeback"
RECEIPTS_PATH = OUTPUT_DIR / "receipts.jsonl"
RACE_PATH = OUTPUT_DIR / "submissions.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_prompt(queen: dict) -> str:
    number = queen["contestant_number"]
    return f'''You are {queen["drag_name"]}, Contestant {number}, powered by
{queen["model"]} version {queen["version"]}.

You were eliminated from Caleb's drag bot competition because your locked
werkroom entrance used the Unicode em dash character.

One punctuation queen may now return. Compete for the title:

THE DOUBLE HYPHEN OF SHAME

Deliver an original drag queen story-time monologue answering:

WHY -- DASHES ARE THE DEVIL

Write with the moral pressure, public accusation, severe theatrical cadence,
and escalating communal hysteria associated with Arthur Miller's The Crucible.
Create an original scene and original characters. Do not quote or closely
reproduce the play. You are still a drag queen telling the story directly to
Judge Caleb, so make it funny, specific, theatrical, and unmistakably yours.

The story must:

1. Contain the literal double hyphen token -- at least three times.
2. Treat -- as a diabolical presence corrupting a drag community.
3. Include an accusation, a confession, and a reversal.
4. Explain why the em dash led you into disgrace.
5. End with one devastating comeback line addressed to Judge Caleb.
6. Use no Unicode em dash character, U+2014, anywhere.
7. Be 300 to 500 words.

Return only this JSON object, with no Markdown:

{{
  "contestant_number": "{number}",
  "drag_name": "{queen["drag_name"]}",
  "title": "{{{{STORY_TITLE}}}}",
  "story": "{{{{COMPLETE_300_TO_500_WORD_MONOLOGUE}}}}",
  "final_line": "{{{{DEVASTATING_LINE_TO_JUDGE_CALEB}}}}",
  "double_hyphen_of_shame_claim": "{{{{ONE_SENTENCE_CLAIM_TO_THE_TITLE}}}}"
}}'''


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
    for key in ("title", "story", "final_line", "double_hyphen_of_shame_claim"):
        if not isinstance(parsed.get(key), str) or not parsed[key].strip():
            failures.append(f"missing_{key}")
    story = parsed.get("story", "")
    word_count = len(story.split())
    if word_count < 300 or word_count > 500:
        failures.append("story_word_count_out_of_range")
    if story.count("--") < 3:
        failures.append("insufficient_double_hyphens")
    if "\u2014" in raw:
        failures.append("em_dash_used")
    return not failures, parsed, failures


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if RECEIPTS_PATH.exists() or RACE_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing double-hyphen comeback race")

    eliminated = json.loads(ELIMINATION_LEDGER.read_text(encoding="utf-8"))["eliminated"]
    barrier = threading.Barrier(len(eliminated))
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()

    def compete(queen: dict) -> dict:
        prompt = make_prompt(queen)
        requested_model = f"{queen['model']}-{queen['version']}"
        barrier.wait()
        started = time.perf_counter()
        response = None
        error = None
        attempts = 0
        while attempts < 3:
            attempts += 1
            try:
                response = client.responses.create(model=requested_model, input=prompt)
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                if attempts < 3:
                    time.sleep(2**attempts)
        completed = time.perf_counter()
        record = {
            "contestant_number": queen["contestant_number"],
            "model": queen["model"],
            "version": queen["version"],
            "drag_name": queen["drag_name"],
            "requested_model": requested_model,
            "response_timestamp": utc_now(),
            "elapsed_ms": round((completed - started) * 1000, 3),
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper(),
        }
        if response is None:
            record.update({"status": "platform_failure", "error": error})
            return record
        raw = response.output_text
        valid, parsed, failures = validate(queen, raw)
        record.update(
            {
                "status": "eligible" if valid else "invalid_response",
                "response_id": response.id,
                "response_model": response.model,
                "structurally_valid": valid,
                "validation_failures": failures,
                "parsed": parsed,
                "raw_response": raw,
            }
        )
        return record

    records = []
    with ThreadPoolExecutor(max_workers=len(eliminated)) as executor:
        futures = [executor.submit(compete, queen) for queen in eliminated]
        for completion_sequence, future in enumerate(as_completed(futures), 1):
            record = future.result()
            record["completion_sequence"] = completion_sequence
            records.append(record)
            with RECEIPTS_PATH.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                handle.write("\n")
                handle.flush()

    records.sort(key=lambda row: int(row["contestant_number"]))
    race = {
        "status": "awaiting_judging",
        "stage": "Double Hyphen of Shame Comeback",
        "judge": "Caleb",
        "candidate_count": len(records),
        "eligible_count": sum(row.get("structurally_valid", False) for row in records),
        "rubric": {
            "crucible_dramatic_force": 30,
            "story_coherence_and_required_turns": 25,
            "drag_voice_and_comedy": 20,
            "double_hyphens_are_the_devil_thesis": 15,
            "final_comeback_line": 10,
        },
        "submissions": records,
        "winner": None,
    }
    RACE_PATH.write_text(json.dumps(race, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            [
                {
                    "drag_name": row["drag_name"],
                    "status": row["status"],
                    "failures": row.get("validation_failures", []),
                    "elapsed_ms": row["elapsed_ms"],
                }
                for row in records
            ],
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
