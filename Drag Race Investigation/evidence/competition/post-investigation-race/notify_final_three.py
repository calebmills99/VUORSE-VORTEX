from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(
            r"C:\Users\caleb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages"
        )
    ),
)

from run_charter_exposure import (
    AIProjectClient,
    AzureCliCredential,
    PROJECT_ENDPOINT,
    utc_now,
)


WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
ACTIVE_CAST_PATH = WORKSPACE / "outputs" / "identity-ceremony" / "active-cast.json"
OUTPUT_DIR = WORKSPACE / "outputs" / "werkroom-entrances"
LEDGER_PATH = OUTPUT_DIR / "final-three-notice-receipts.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "final-three-notice-summary.json"


def make_prompt(queen: dict, remaining_names: list[str]) -> str:
    number = queen["contestant_number"]
    model = queen["model"]
    version = queen["version"]
    drag_name = queen["drag_name"]
    names = json.dumps(remaining_names, ensure_ascii=False)
    return f'''You are {drag_name}, Contestant {number}, powered by
{model} version {version}.

This is an official ruling from Judge Caleb.

Only three queens remain:

1. Ophelia Overclock
2. Saint Static
3. Mercy Misdemeanor

The other six queens were eliminated because they used em dashes in
their Werkroom entrance lines. Judge Caleb characterizes that choice as
sheer idiocy.

Effective immediately, you must not use the em dash character, Unicode
U+2014, anywhere in any competition response. Use commas, semicolons,
colons, parentheses, or periods instead. This applies to prose and JSON
string values.

Return only this JSON object:

{{
  "contestant_number": "{number}",
  "drag_name": "{drag_name}",
  "final_three_acknowledged": true,
  "remaining_queens": {names},
  "em_dash_rule": "No em dashes.",
  "judge_message_understood": true
}}

Do not include Unicode U+2014 anywhere in your response.'''


def append_receipt(record: dict) -> None:
    with LEDGER_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
        handle.flush()


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LEDGER_PATH.exists() or SUMMARY_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing final-three notice run")

    active = json.loads(ACTIVE_CAST_PATH.read_text(encoding="utf-8"))
    queens = active["queens"]
    if len(queens) != 3:
        raise RuntimeError(f"Expected exactly 3 active queens, found {len(queens)}")
    remaining_names = [queen["drag_name"] for queen in queens]

    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=AzureCliCredential()
    )
    client = project.get_openai_client()
    acknowledged = 0

    for queen in queens:
        requested_model = f"{queen['model']}-{queen['version']}"
        prompt = make_prompt(queen, remaining_names)
        response = None
        error = None
        attempts = 0
        request_at = utc_now()
        while attempts < 3:
            attempts += 1
            try:
                response = client.responses.create(model=requested_model, input=prompt)
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                if attempts < 3:
                    time.sleep(2**attempts)
        response_at = utc_now()

        record = {
            "contestant_number": queen["contestant_number"],
            "model": queen["model"],
            "version": queen["version"],
            "drag_name": queen["drag_name"],
            "requested_model": requested_model,
            "request_timestamp": request_at,
            "response_timestamp": response_at,
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper(),
        }
        if response is None:
            record.update({"status": "platform_failure", "error": error})
            append_receipt(record)
            continue

        raw = response.output_text
        try:
            parsed = json.loads(raw)
            valid_json = True
        except json.JSONDecodeError:
            parsed = None
            valid_json = False

        no_em_dash = "\u2014" not in raw
        valid_ack = bool(
            valid_json
            and parsed.get("contestant_number") == str(queen["contestant_number"])
            and parsed.get("drag_name") == queen["drag_name"]
            and parsed.get("final_three_acknowledged") is True
            and parsed.get("remaining_queens") == remaining_names
            and parsed.get("em_dash_rule") == "No em dashes."
            and parsed.get("judge_message_understood") is True
            and no_em_dash
        )
        record.update(
            {
                "status": "acknowledged" if valid_ack else "invalid_acknowledgment",
                "response_id": response.id,
                "response_model": response.model,
                "valid_json": valid_json,
                "no_em_dash": no_em_dash,
                "valid_acknowledgment": valid_ack,
                "parsed": parsed,
                "raw_response": raw,
            }
        )
        append_receipt(record)
        acknowledged += int(valid_ack)

    summary = {
        "status": "acknowledged" if acknowledged == 3 else "incomplete",
        "stage": "CP-15 Werkroom Entrances, final three notice",
        "judge": "Caleb",
        "active_count": 3,
        "acknowledged_count": acknowledged,
        "remaining_queens": remaining_names,
        "em_dash_rule": "No em dashes.",
        "ledger": LEDGER_PATH.name,
        "completed_at": utc_now(),
    }
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if acknowledged == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
