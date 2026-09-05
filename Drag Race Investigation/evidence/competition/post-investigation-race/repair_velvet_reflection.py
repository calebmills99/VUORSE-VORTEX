from __future__ import annotations

import json
import sys
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
DIR = WORKSPACE / "outputs" / "reading-challenge" / "cp-17r-self-read"
RECEIPTS = DIR / "reflection-receipts.jsonl"
REFLECTIONS = DIR / "reflections.json"

PROMPT = '''Your reflection passed every creative requirement, but the JSON schema failed because
portrait_concept.props was an array. Resubmit the exact same JSON and wording,
changing only portrait_concept.props into one semicolon-separated string. Do
not add, remove, or rewrite any creative content. Return JSON only. Use no
Unicode em dash character and no double hyphen token.'''


def main() -> int:
    doc = json.loads(REFLECTIONS.read_text(encoding="utf-8"))
    velvet = next(row for row in doc["reflections"] if row["drag_name"] == "Velvet Vespers")
    if velvet["status"] != "invalid_reflection" or velvet["validation_failures"] != ["missing_portrait_props"]:
        raise RuntimeError("Velvet reflection is not in the expected repair state")

    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()
    response = client.responses.create(
        model=velvet["requested_model"],
        previous_response_id=velvet["response_id"],
        input=PROMPT,
    )
    parsed = json.loads(response.output_text)
    props = parsed.get("portrait_concept", {}).get("props")
    failures = []
    if not isinstance(props, str) or not props.strip():
        failures.append("missing_portrait_props")
    if "\u2014" in response.output_text:
        failures.append("em_dash_used")
    if "--" in response.output_text:
        failures.append("double_hyphen_used")

    repair = {
        "checkpoint": "CP-17R",
        "record_type": "format_repair",
        "contestant_number": velvet["contestant_number"],
        "drag_name": velvet["drag_name"],
        "model": velvet["model"],
        "version": velvet["version"],
        "requested_model": velvet["requested_model"],
        "previous_response_id": velvet["response_id"],
        "response_id": response.id,
        "response_model": response.model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "ready_for_portrait" if not failures else "invalid_reflection",
        "validation_failures": failures,
        "parsed": parsed,
        "raw_response": response.output_text,
        "repair_scope": "props array converted to one string; creative content otherwise unchanged",
    }
    with RECEIPTS.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(repair, ensure_ascii=False, separators=(",", ":")) + "\n")

    velvet.update(repair)
    doc["valid_reflection_count"] = sum(row["status"] == "ready_for_portrait" for row in doc["reflections"])
    doc["status"] = "ready_for_image_generation" if doc["valid_reflection_count"] == 5 else "attention_required"
    REFLECTIONS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": doc["status"], "valid_reflection_count": doc["valid_reflection_count"], "velvet_failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
