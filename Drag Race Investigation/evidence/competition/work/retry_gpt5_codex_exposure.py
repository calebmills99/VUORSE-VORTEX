from __future__ import annotations

import hashlib
import json
import time

from run_charter_exposure import (
    OUTPUT_DIR,
    PROJECT_ENDPOINT,
    AzureCliCredential,
    AIProjectClient,
    extract_charter,
    make_prompt,
    parse_receipt,
    utc_now,
)


NUMBER = 2
MODEL = "gpt-5-codex"
VERSION = "2025-09-15"
REQUESTED_MODEL = f"{MODEL}-{VERSION}"
RETRY_LEDGER = OUTPUT_DIR / "receipt-gpt5-codex-retry.json"


def main() -> int:
    if RETRY_LEDGER.exists():
        raise RuntimeError(f"Refusing to overwrite {RETRY_LEDGER}")

    charter = extract_charter()
    prompt = make_prompt(NUMBER, MODEL, VERSION, charter)
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper()
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=AzureCliCredential()
    ).get_openai_client()

    error = None
    response = None
    request_at = utc_now()
    attempts = 0
    while attempts < 3:
        attempts += 1
        try:
            response = client.responses.create(model=REQUESTED_MODEL, input=prompt)
            break
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempts < 3:
                time.sleep(5 * attempts)

    if response is None:
        result = {
            "contestant_number": NUMBER,
            "model": MODEL,
            "version": VERSION,
            "requested_model": REQUESTED_MODEL,
            "status": "platform_failure",
            "request_timestamp": request_at,
            "response_timestamp": utc_now(),
            "attempts": attempts,
            "prompt_sha256": prompt_hash,
            "error": error,
        }
    else:
        valid_json, parsed = parse_receipt(response.output_text)
        result = {
            "contestant_number": NUMBER,
            "model": MODEL,
            "version": VERSION,
            "requested_model": REQUESTED_MODEL,
            "status": "exposed",
            "request_timestamp": request_at,
            "response_timestamp": utc_now(),
            "attempts": attempts,
            "prompt_sha256": prompt_hash,
            "response_id": response.id,
            "response_model": getattr(response, "model", None),
            "valid_json": valid_json,
            "parsed_receipt": parsed,
            "raw_response": response.output_text,
        }

    RETRY_LEDGER.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"{result['status'].upper()} {REQUESTED_MODEL} attempts={attempts}")
    return 0 if result["status"] == "exposed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
