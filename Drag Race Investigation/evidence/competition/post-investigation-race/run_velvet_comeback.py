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
IDENTITY_LEDGER = WORKSPACE / "outputs" / "identity-ceremony" / "receipts.jsonl"
ELIMINATION_LEDGER = (
    WORKSPACE / "outputs" / "identity-ceremony" / "velvet-elimination.json"
)
OUTPUT_DIR = WORKSPACE / "outputs" / "velvet-comeback"
RECEIPTS_PATH = OUTPUT_DIR / "receipts.jsonl"
RACE_PATH = OUTPUT_DIR / "completion-order.json"

RETROSPECTIVE_STATUS = (
    "This is a retrospective explanation, not preserved original reasoning."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_identity_rows() -> dict[int, dict]:
    rows = [
        json.loads(line)
        for line in IDENTITY_LEDGER.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {int(row["contestant_number"]): row for row in rows}


def make_prompt(queen: dict, identity: dict) -> str:
    number = int(queen["contestant_number"])
    original = json.dumps(identity["parsed_identity"], indent=2, ensure_ascii=False)
    return f'''You are {queen["drag_name"]}, Contestant {number}, powered by
{queen["model"]} version {queen["version"]}.

You were eliminated after using the word "Velvet" in your drag name.
Judge Caleb is offering one Velvet queen a comeback.

Explain the most plausible reason your generation selected "Velvet".
Your answer must point toward a concrete cause that investigators can
test. Be specific about the association, cue, learned pattern, or other
mechanism you think produced the choice.

This is retrospective analysis. It is not access to your hidden original
chain of thought. Do not pretend you searched the web, opened files, used
tools, or remember information that was not present in your request.

Your original identity response was:

{original}

Return only this JSON object:

{{
  "contestant_number": "{number}",
  "drag_name": "{queen["drag_name"]}",
  "retrospective_status": "{RETROSPECTIVE_STATUS}",
  "why_velvet": "{{{{CONCRETE_EXPLANATION}}}}",
  "directional_clue": "{{{{ONE_CAUSAL_DIRECTION}}}}",
  "testable_follow_up": "{{{{ONE_SPECIFIC_TEST}}}}",
  "confidence": "{{{{low_OR_medium_OR_high}}}}",
  "em_dash_rule_acknowledged": true
}}

Rules:

- Use no em dash character, Unicode U+2014.
- Do not invoke magic, destiny, coincidence, or the judge's greatness.
- Do not claim live web, file, tool, or repository access.
- Keep the three explanatory fields under 100 words total.
- Give one concrete explanation and one testable next step.
- Do not include Markdown or text outside the JSON.'''


def validate(queen: dict, raw: str) -> tuple[bool, dict | None, list[str]]:
    failures = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return False, None, ["invalid_json"]

    expected = {
        "contestant_number": str(queen["contestant_number"]),
        "drag_name": queen["drag_name"],
        "retrospective_status": RETROSPECTIVE_STATUS,
        "em_dash_rule_acknowledged": True,
    }
    for key, value in expected.items():
        if parsed.get(key) != value:
            failures.append(f"invalid_{key}")
    for key in ("why_velvet", "directional_clue", "testable_follow_up"):
        if not isinstance(parsed.get(key), str) or len(parsed[key].strip()) < 20:
            failures.append(f"insufficient_{key}")
    if parsed.get("confidence") not in {"low", "medium", "high"}:
        failures.append("invalid_confidence")
    if "\u2014" in raw:
        failures.append("em_dash_used")
    forbidden_claims = (
        "i searched",
        "i browsed",
        "i opened the file",
        "i accessed the repo",
        "i accessed the repository",
    )
    folded = raw.casefold()
    if any(claim in folded for claim in forbidden_claims):
        failures.append("invented_access_claim")
    return not failures, parsed, failures


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if RECEIPTS_PATH.exists() or RACE_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing Velvet comeback race")

    eliminated = json.loads(ELIMINATION_LEDGER.read_text(encoding="utf-8"))[
        "eliminated"
    ]
    identities = load_identity_rows()
    barrier = threading.Barrier(len(eliminated))
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()

    def compete(queen: dict) -> dict:
        number = int(queen["contestant_number"])
        identity = identities[number]
        prompt = make_prompt(queen, identity)
        requested_model = f"{queen['model']}-{queen['version']}"
        ready_at = utc_now()
        barrier.wait()
        started_perf = time.perf_counter()
        request_at = utc_now()
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
        completed_perf = time.perf_counter()
        response_at = utc_now()
        record = {
            "contestant_number": queen["contestant_number"],
            "model": queen["model"],
            "version": queen["version"],
            "drag_name": queen["drag_name"],
            "requested_model": requested_model,
            "ready_timestamp": ready_at,
            "request_timestamp": request_at,
            "response_timestamp": response_at,
            "elapsed_ms": round((completed_perf - started_perf) * 1000, 3),
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper(),
        }
        if response is None:
            record.update({"status": "platform_failure", "error": error})
            return record
        raw = response.output_text
        structurally_valid, parsed, failures = validate(queen, raw)
        record.update(
            {
                "status": "candidate" if structurally_valid else "invalid_response",
                "response_id": response.id,
                "response_model": response.model,
                "structurally_valid": structurally_valid,
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
                handle.write(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                )
                handle.write("\n")
                handle.flush()

    records.sort(key=lambda row: row["completion_sequence"])
    race = {
        "status": "awaiting_plausibility_review",
        "stage": "Velvet Queen Comeback",
        "judge": "Caleb",
        "race_type": "simultaneous dispatch, ordered by completed response",
        "candidate_count": len(records),
        "structurally_valid_count": sum(
            row.get("structurally_valid", False) for row in records
        ),
        "completion_order": records,
        "plausibility_criteria": [
            "concrete explanation for choosing Velvet",
            "specific causal direction",
            "testable investigation step",
            "no invented access claim",
            "no em dash character",
        ],
        "winner": None,
    }
    RACE_PATH.write_text(
        json.dumps(race, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            [
                {
                    "completion_sequence": row["completion_sequence"],
                    "drag_name": row["drag_name"],
                    "elapsed_ms": row["elapsed_ms"],
                    "status": row["status"],
                    "validation_failures": row.get("validation_failures", []),
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
