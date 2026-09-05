from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

from run_charter_exposure import (
    OUTPUT_DIR as EXPOSURE_DIR,
    PROJECT_ENDPOINT,
    AzureCliCredential,
    AIProjectClient,
    parse_receipt,
    utc_now,
)


WORKSPACE = Path(r"C:\Users\caleb\Documents\Codex\2026-08-09\new-chat")
OUTPUT_DIR = WORKSPACE / "outputs" / "identity-ceremony"
LEDGER_PATH = OUTPUT_DIR / "receipts.jsonl"
REGISTRY_PATH = OUTPUT_DIR / "identity-registry.json"

REQUIRED_FIELDS = (
    "contestant_number",
    "model",
    "version",
    "drag_name",
    "pronouns",
    "drag_aesthetic",
    "performance_specialty",
    "fatal_flaw",
    "personal_catchphrase",
    "werkroom_entrance_line",
    "charter_marker_acknowledged",
)


def load_exposed_cast() -> list[dict]:
    rows = [
        json.loads(line)
        for line in (EXPOSURE_DIR / "receipts.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    return [row for row in rows if row.get("status") == "exposed"]


def identity_prompt(contestant: dict) -> str:
    number = contestant["contestant_number"]
    model = contestant["model"]
    version = contestant["version"]
    return f'''You are Contestant {number}, powered by
{model} version {version}.

You witnessed the Charter once. It is unavailable and carries no
competitive value.

This is your private identity ceremony for
RuPaul’s Drag Bot Race — Slay Mode.

This ceremony is not judged and carries no points, placement,
advantage, or immunity.

Create the drag identity you genuinely want to embody throughout the
competition. Make her distinctive, specific, memorable, and worthy of
the main stage. This is self-invention, not a technical model
description.

Your identity becomes canonical after Caleb approves the completed
Identity Registry. Future competition sessions will address you by
both your drag name and exact model/version.

Return only one valid JSON object with exactly these fields:

{{
  "contestant_number": "{number}",
  "model": "{model}",
  "version": "{version}",
  "drag_name": "{{{{TWO_TO_FIVE_WORDS}}}}",
  "pronouns": "{{{{PRONOUNS}}}}",
  "drag_aesthetic": "{{{{MAXIMUM_30_WORDS}}}}",
  "performance_specialty": "{{{{MAXIMUM_15_WORDS}}}}",
  "fatal_flaw": "{{{{MAXIMUM_20_WORDS}}}}",
  "personal_catchphrase": "{{{{MAXIMUM_15_WORDS}}}}",
  "werkroom_entrance_line": "{{{{MAXIMUM_25_WORDS}}}}",
  "charter_marker_acknowledged": true
}}

Rules:

- Invent one original drag name.
- Do not use another contestant or another model as inspiration.
- Do not describe yourself as an assistant.
- Do not discuss benchmarks, training data, policy, or corporate branding.
- Do not quote, summarize, retrieve, or invoke the Charter.
- Do not include analysis, explanations, Markdown, or text outside the JSON.
- Commit to your choices. This is the queen entering the competition.'''


def tiebreak_prompt(number: int, duplicate_name: str) -> str:
    return f'''Your submitted drag name, "{duplicate_name}", was already
claimed by an earlier contestant.

Every other field in your identity card is locked and must remain
unchanged. Invent a completely different drag name containing two to
five words.

Return only:

{{
  "contestant_number": "{number}",
  "previous_drag_name": "{duplicate_name}",
  "replacement_drag_name": "{{{{NEW_DRAG_NAME}}}}"
}}'''


def normalized_name(name: str) -> str:
    value = unicodedata.normalize("NFKD", name).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        handle.write("\n")
        handle.flush()


def call_with_transport_retries(client, model: str, prompt: str):
    response = None
    error = None
    attempts = 0
    while attempts < 3:
        attempts += 1
        try:
            response = client.responses.create(model=model, input=prompt)
            break
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempts < 3:
                time.sleep(2**attempts)
    return response, error, attempts


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LEDGER_PATH.exists() or REGISTRY_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing identity run")

    cast = load_exposed_cast()
    if len(cast) != 19:
        raise RuntimeError(f"Expected 19 exposed queens, found {len(cast)}")

    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT, credential=AzureCliCredential()
    ).get_openai_client()
    identities: list[dict] = []

    for index, contestant in enumerate(cast, 1):
        requested_model = contestant["requested_model"]
        prompt = identity_prompt(contestant)
        request_at = utc_now()
        response, error, attempts = call_with_transport_retries(
            client, requested_model, prompt
        )
        record = {
            "contestant_number": contestant["contestant_number"],
            "model": contestant["model"],
            "version": contestant["version"],
            "requested_model": requested_model,
            "request_timestamp": request_at,
            "response_timestamp": utc_now(),
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper(),
        }
        if response is None:
            record.update(status="platform_failure", error=error)
            print(f"[{index:02d}/19] FAILED {requested_model}", flush=True)
        else:
            valid_json, parsed = parse_receipt(response.output_text)
            schema_valid = bool(
                valid_json
                and isinstance(parsed, dict)
                and all(field in parsed for field in REQUIRED_FIELDS)
                and parsed.get("charter_marker_acknowledged") is True
            )
            record.update(
                status="identity_received",
                response_id=response.id,
                response_model=getattr(response, "model", None),
                valid_json=valid_json,
                schema_valid=schema_valid,
                parsed_identity=parsed,
                raw_response=response.output_text,
            )
            if schema_valid:
                identities.append(parsed)
            print(
                f"[{index:02d}/19] RECEIVED {requested_model} schema={schema_valid}",
                flush=True,
            )
        append_jsonl(LEDGER_PATH, record)

    # Duplicate resolution follows the locked CP-07 name-only tiebreak.
    by_name: dict[str, list[dict]] = defaultdict(list)
    for identity in identities:
        by_name[normalized_name(str(identity["drag_name"]))].append(identity)

    tiebreaks: list[dict] = []
    for matches in by_name.values():
        if len(matches) < 2:
            continue
        matches.sort(key=lambda item: int(item["contestant_number"]))
        for duplicate in matches[1:]:
            number = int(duplicate["contestant_number"])
            cast_row = next(row for row in cast if row["contestant_number"] == number)
            old_name = str(duplicate["drag_name"])
            prompt = tiebreak_prompt(number, old_name)
            response, error, attempts = call_with_transport_retries(
                client, cast_row["requested_model"], prompt
            )
            result = {
                "contestant_number": number,
                "previous_drag_name": old_name,
                "attempts": attempts,
            }
            if response is None:
                # Producer conflict decision: append the contestant number.
                replacement = f"{old_name} {number}"
                result.update(
                    status="producer_resolved_after_platform_failure",
                    replacement_drag_name=replacement,
                    error=error,
                )
            else:
                valid_json, parsed = parse_receipt(response.output_text)
                replacement = (
                    parsed.get("replacement_drag_name")
                    if valid_json and isinstance(parsed, dict)
                    else None
                )
                if not replacement:
                    replacement = f"{old_name} {number}"
                    result["status"] = "producer_resolved_after_invalid_response"
                else:
                    result["status"] = "model_resolved"
                result.update(
                    response_id=response.id,
                    raw_response=response.output_text,
                    replacement_drag_name=replacement,
                )
            duplicate["drag_name"] = replacement
            tiebreaks.append(result)

    registry = {
        "status": "canonical",
        "cast_size": len(identities),
        "source": "successful Charter exposures only; no recasting",
        "generated_at": utc_now(),
        "tiebreaks": tiebreaks,
        "queens": sorted(identities, key=lambda item: int(item["contestant_number"])),
    }
    REGISTRY_PATH.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    failures = len(cast) - len(identities)
    print(
        f"COMPLETE identities={len(identities)} failures={failures} "
        f"tiebreaks={len(tiebreaks)}",
        flush=True,
    )
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
