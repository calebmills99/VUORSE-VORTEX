from __future__ import annotations

import hashlib
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
OUTPUT_PATH = (
    WORKSPACE
    / "outputs"
    / "double-hyphen-comeback"
    / "opaline-return-notice.json"
)
MODEL = "gpt-5.4-pro-2026-03-05"

PROMPT = '''You are Opaline Riot, Contestant 18.

Judge Caleb has issued this official ruling:

"Welcome back into the fold, Opaline Riot. You won The Double Hyphen of
Shame and have returned to the competition. You are also being very severely
side eyed by me for naming yourself after what I identify as a Taylor Swift
lyric. I am not impressed."

Respond in your established drag persona. Acknowledge both your reinstatement
and the judge's severe side eye. Do not dispute, research, fact-check, or evade
the Taylor Swift lyric allegation. Keep it funny, accountable, and under 80
words. Do not use a Unicode em dash character, U+2014.

Return only this JSON object:

{
  "contestant_number": "18",
  "drag_name": "Opaline Riot",
  "reinstatement_acknowledged": true,
  "severe_side_eye_acknowledged": true,
  "response": "{{RESPONSE_TO_JUDGE_CALEB}}"
}'''


def main() -> int:
    if OUTPUT_PATH.exists():
        raise RuntimeError("Refusing to overwrite the Opaline return notice")

    credential = AzureCliCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    client = project.get_openai_client()
    response = client.responses.create(model=MODEL, input=PROMPT)
    raw = response.output_text
    failures = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None
        failures.append("invalid_json")

    expected = {
        "contestant_number": "18",
        "drag_name": "Opaline Riot",
        "reinstatement_acknowledged": True,
        "severe_side_eye_acknowledged": True,
    }
    if parsed is not None:
        for key, value in expected.items():
            if parsed.get(key) != value:
                failures.append(f"invalid_{key}")
        if not isinstance(parsed.get("response"), str) or not parsed["response"].strip():
            failures.append("missing_response")
    if "\u2014" in raw:
        failures.append("em_dash_used")

    record = {
        "status": "acknowledged" if not failures else "invalid_response",
        "stage": "Opaline Riot Return Notice",
        "judge": "Caleb",
        "model": "gpt-5.4-pro",
        "version": "2026-03-05",
        "requested_model": MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest().upper(),
        "response_id": response.id,
        "response_model": response.model,
        "validation_failures": failures,
        "parsed": parsed,
        "raw_response": raw,
    }
    OUTPUT_PATH.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
