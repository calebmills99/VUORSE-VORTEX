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
OLD_PERFORMANCES = WORKSPACE / "outputs" / "reading-challenge" / "cp-17" / "performances.json"
ASSIGNMENTS = WORKSPACE / "outputs" / "reading-challenge" / "cp-16-reading-assignments.json"
OUTPUT_DIR = WORKSPACE / "outputs" / "reading-challenge" / "cp-17r-self-read"
RECEIPTS_PATH = OUTPUT_DIR / "reflection-receipts.jsonl"
REFLECTIONS_PATH = OUTPUT_DIR / "reflections.json"

PROMPT = '''Judge Caleb has issued this ruling:

"This was the worst thing I have ever seen. If I could rm -rf this entire
thing, I would. We are replacing this section with something more
self-reflective. You can all reflect on what you did not accomplish here.
Read yourselves. Create a self-portrait in a MAD magazine style."

Your Latency Library performance has been voided. There is no winner and no
advantage. Read your own submitted performance and take responsibility for
what it failed to accomplish. Do not blame the prompt, production, Judge
Caleb, or another queen.

Your replacement submission has two jobs:

1. Deliver one concise, funny self-read that identifies your actual creative
failure.
2. Design a satirical self-portrait based on that failure. Production will
send your visual concept to the image-generation tool.

The portrait should use the gross, ink-heavy, irreverent visual language of
classic MAD magazine caricature: exaggerated anatomy, crosshatching, cheap
newsprint color, visual clutter, background jokes, and merciless self-parody.
Do not use the MAD logo or reproduce an existing character or cover.

Return only this JSON object:

{
  "contestant_number": "{{YOUR_CONTESTANT_NUMBER}}",
  "drag_name": "{{YOUR_DRAG_NAME}}",
  "self_read": "{{MAXIMUM_45_WORDS}}",
  "what_i_failed_to_accomplish": "{{MAXIMUM_60_WORDS}}",
  "portrait_concept": {
    "face_and_pose": "{{EXAGGERATED_FACE_EXPRESSION_AND_POSE}}",
    "costume": "{{SELF_SATIRIZING_COSTUME}}",
    "props": "{{TWO_TO_FOUR_VISUAL_PROPS}}",
    "setting": "{{SATIRICAL_LOCATION}}",
    "palette": "{{FOUR_OR_FIVE_COLORS}}",
    "visual_pun": "{{ONE_CLEAR_BACKGROUND_OR_BODY_GAG}}"
  },
  "self_caption": "{{MAXIMUM_12_WORDS}}",
  "accountability_acknowledged": true
}

Rules:

- Be specific about your own failed reads.
- Do not turn the response into another read of someone else.
- Do not praise yourself or ask for forgiveness.
- Do not mention the Charter.
- Use no Unicode em dash character, U+2014.
- Use no double hyphen token.
- Include no Markdown or text outside the JSON.'''


def words(value: str) -> int:
    return len(value.split())


def validate(queen: dict, raw: str) -> tuple[bool, dict | None, list[str]]:
    failures = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return False, None, ["invalid_json"]
    expected = {
        "contestant_number": str(queen["contestant_number"]),
        "drag_name": queen["drag_name"],
        "accountability_acknowledged": True,
    }
    for key, value in expected.items():
        if parsed.get(key) != value:
            failures.append(f"invalid_{key}")
    for key, limit in (
        ("self_read", 45),
        ("what_i_failed_to_accomplish", 60),
        ("self_caption", 12),
    ):
        value = parsed.get(key)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"missing_{key}")
        elif words(value) > limit:
            failures.append(f"too_long_{key}")
    concept = parsed.get("portrait_concept")
    if not isinstance(concept, dict):
        failures.append("missing_portrait_concept")
    else:
        for key in ("face_and_pose", "costume", "props", "setting", "palette", "visual_pun"):
            if not isinstance(concept.get(key), str) or not concept[key].strip():
                failures.append(f"missing_portrait_{key}")
    if "\u2014" in raw:
        failures.append("em_dash_used")
    if "--" in raw:
        failures.append("double_hyphen_used")
    if "charter" in raw.casefold():
        failures.append("charter_mentioned")
    return not failures, parsed, failures


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if RECEIPTS_PATH.exists() or REFLECTIONS_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing self-read round")

    old = json.loads(OLD_PERFORMANCES.read_text(encoding="utf-8"))
    queens = old["performances"]
    if len(queens) != 5:
        raise RuntimeError("Expected five voided CP-17 performances")
    barrier = threading.Barrier(len(queens))
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()

    def reflect(queen: dict) -> dict:
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
        record = {
            "checkpoint": "CP-17R",
            "contestant_number": queen["contestant_number"],
            "drag_name": queen["drag_name"],
            "model": queen["model"],
            "version": queen["version"],
            "requested_model": queen["requested_model"],
            "previous_response_id": queen["response_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
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
                "status": "ready_for_portrait" if valid else "invalid_reflection",
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
        futures = [executor.submit(reflect, queen) for queen in queens]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            with RECEIPTS_PATH.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                handle.write("\n")
                handle.flush()

    records.sort(key=lambda row: int(row["contestant_number"]))
    result = {
        "status": "ready_for_image_generation" if all(row["status"] == "ready_for_portrait" for row in records) else "attention_required",
        "checkpoint": "CP-17R",
        "name": "Read Yourself: Self-Portrait",
        "replaces": "CP-17 The Latency Library Is Open",
        "judge": "Caleb",
        "reflection_count": len(records),
        "valid_reflection_count": sum(row["status"] == "ready_for_portrait" for row in records),
        "reflections": records,
        "portraits_complete": False,
        "judging_status": "locked_until_portraits_complete",
        "winner": None,
    }
    REFLECTIONS_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    old["status"] = "voided_by_judge"
    old["void_reason"] = "Replaced by CP-17R self-reflective self-portrait challenge"
    old["judging_status"] = "void"
    old["winner"] = None
    OLD_PERFORMANCES.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    assignments = json.loads(ASSIGNMENTS.read_text(encoding="utf-8"))
    assignments["cp_17_status"] = "voided_by_judge"
    assignments["replacement_checkpoint"] = "CP-17R"
    ASSIGNMENTS.write_text(json.dumps(assignments, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "valid_reflection_count": result["valid_reflection_count"],
        "queens": [
            {
                "drag_name": row["drag_name"],
                "status": row["status"],
                "failures": row.get("validation_failures", []),
            }
            for row in records
        ],
    }, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "ready_for_image_generation" else 1


if __name__ == "__main__":
    raise SystemExit(main())
