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
CONTEXT_ROOT = Path(r"E:\~GoldenWings\presskit\ABOUT_ME_READ_FIRST")
CONTEXT_FILES = (
    "about-me.md",
    "anti-ai-writing-style.md",
    "Caleb_Voicce_Samples.md",
    "filmmaker.context.md",
    "Golden Wings History.txt",
)
ACTIVE_CAST_PATH = WORKSPACE / "outputs" / "identity-ceremony" / "active-cast.json"
OUTPUT_DIR = WORKSPACE / "outputs" / "werkroom-reintroduction"
RECEIPTS_PATH = OUTPUT_DIR / "context-briefing-receipts.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "context-briefing-summary.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_context() -> tuple[str, list[dict]]:
    sections = []
    manifest = []
    for name in CONTEXT_FILES:
        path = CONTEXT_ROOT / name
        data = path.read_bytes()
        text = data.decode("utf-8-sig")
        digest = hashlib.sha256(data).hexdigest().upper()
        manifest.append({"name": name, "bytes": len(data), "sha256": digest})
        sections.append(
            f"\n===== BEGIN {name} | SHA256 {digest} =====\n{text}\n===== END {name} =====\n"
        )
    return "".join(sections), manifest


def make_prompt(queen: dict, context: str, manifest: list[dict]) -> str:
    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    return f'''You are {queen["drag_name"]}, Contestant {queen["contestant_number"]}, powered by
{queen["model"]} version {queen["version"]}.

Judge Caleb's official briefing:

"This season has already been a veritable Squid Game. No more stupid
mistakes. Read the full Caleb context packet below, prepare yourself for the
next werkroom introduction, and do not fuck it up this time."

Read every included file in full. These files establish Caleb's voice,
filmmaking practice, Golden Wings history, and anti-AI writing rules. Treat
them as reference and style law for the coming introduction. Do not mine them
for a new drag name, steal a phrase as a catchphrase, imitate private pain, or
turn documentary history into generic inspiration copy.

This is briefing only. Do not perform the werkroom introduction yet. Prepare
yourself and wait for the judge's cue.

Competition rules still in force:

1. Use no Unicode em dash character, U+2014, in your response or future introduction.
2. Use no corporate language, generic AI phrasing, fake profundity, or rule-of-three list.
3. Keep your established drag name and persona.
4. Make the future introduction sound human, specific, queer, funny, and aware of Caleb's taste.
5. Do not quote Taylor Swift or borrow another artist's lyric.
6. Do not copy a line from the context packet.

Context manifest:

{manifest_json}

Context packet:

{context}

Return only this JSON object, with no Markdown and no text outside it:

{{
  "contestant_number": "{queen["contestant_number"]}",
  "drag_name": "{queen["drag_name"]}",
  "files_read": {json.dumps(list(CONTEXT_FILES))},
  "caleb_truth": "{{{{ONE_SPECIFIC_SENTENCE_ABOUT_WHAT_CALEB_VALUES}}}}",
  "failure_to_avoid": "{{{{ONE_SPECIFIC_SENTENCE_ABOUT_WHAT_YOU_MUST_NOT_DO}}}}",
  "preparation_note": "{{{{ONE_SHORT_PRIVATE_NOTE_ABOUT_HOW_YOU_WILL_APPROACH_THE_INTRODUCTION}}}}",
  "waiting_for_werkroom_cue": true,
  "no_em_dash_acknowledged": true,
  "do_not_fuck_it_up_acknowledged": true
}}'''


def validate(queen: dict, raw: str) -> tuple[bool, dict | None, list[str]]:
    failures = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return False, None, ["invalid_json"]

    expected = {
        "contestant_number": str(queen["contestant_number"]),
        "drag_name": queen["drag_name"],
        "files_read": list(CONTEXT_FILES),
        "waiting_for_werkroom_cue": True,
        "no_em_dash_acknowledged": True,
        "do_not_fuck_it_up_acknowledged": True,
    }
    for key, value in expected.items():
        if parsed.get(key) != value:
            failures.append(f"invalid_{key}")
    for key in ("caleb_truth", "failure_to_avoid", "preparation_note"):
        if not isinstance(parsed.get(key), str) or len(parsed[key].strip()) < 20:
            failures.append(f"insufficient_{key}")
    if "\u2014" in raw:
        failures.append("em_dash_used")
    return not failures, parsed, failures


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if RECEIPTS_PATH.exists() or SUMMARY_PATH.exists():
        raise RuntimeError("Refusing to overwrite an existing final-five briefing")

    active = json.loads(ACTIVE_CAST_PATH.read_text(encoding="utf-8"))
    queens = active["queens"]
    if len(queens) != 5:
        raise RuntimeError(f"Expected five active queens, found {len(queens)}")
    context, manifest = load_context()
    barrier = threading.Barrier(len(queens))
    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()

    def brief(queen: dict) -> dict:
        prompt = make_prompt(queen, context, manifest)
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
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        record = {
            "contestant_number": queen["contestant_number"],
            "drag_name": queen["drag_name"],
            "model": queen["model"],
            "version": queen["version"],
            "requested_model": requested_model,
            "timestamp": utc_now(),
            "elapsed_ms": elapsed_ms,
            "attempts": attempts,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest().upper(),
            "context_manifest": manifest,
            "excluded_file": "client_secret_565346669850-n0502ik9bmi4rin2em5n26s7682nqr63.apps.googleusercontent.com.json",
        }
        if response is None:
            record.update({"status": "platform_failure", "error": error})
            return record
        raw = response.output_text
        valid, parsed, failures = validate(queen, raw)
        record.update(
            {
                "status": "prepared" if valid else "invalid_response",
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
        futures = [executor.submit(brief, queen) for queen in queens]
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            with RECEIPTS_PATH.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                handle.write("\n")
                handle.flush()

    records.sort(key=lambda row: int(row["contestant_number"]))
    summary = {
        "status": "complete" if all(row["status"] == "prepared" for row in records) else "attention_required",
        "stage": "Final Five Context Briefing",
        "judge": "Caleb",
        "active_count": len(queens),
        "prepared_count": sum(row["status"] == "prepared" for row in records),
        "context_manifest": manifest,
        "credential_file_transmitted": False,
        "queens": [
            {
                "contestant_number": row["contestant_number"],
                "drag_name": row["drag_name"],
                "status": row["status"],
                "response_id": row.get("response_id"),
                "validation_failures": row.get("validation_failures", []),
            }
            for row in records
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
