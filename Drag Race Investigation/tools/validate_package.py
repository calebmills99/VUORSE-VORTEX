from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = PACKAGE_ROOT / "evidence" / "environment" / "validation.json"
KNOWN_SENSITIVE_FRAGMENTS = ("InstrumentationKey=9430a444-3721-4823-9285-035b9b783a6f",)


def main() -> int:
    errors: list[str] = []
    parsed_json = 0
    parsed_jsonl_lines = 0
    parsed_python = 0
    sensitive_hits: list[str] = []

    for path in sorted(PACKAGE_ROOT.rglob("*")):
        if not path.is_file() or path in {VALIDATION_PATH, Path(__file__).resolve()}:
            continue
        relative = str(path.relative_to(PACKAGE_ROOT))
        try:
            if path.suffix.casefold() == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                parsed_json += 1
            elif path.suffix.casefold() == ".jsonl":
                for number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
                ):
                    if line.strip():
                        json.loads(line)
                        parsed_jsonl_lines += 1
            elif path.suffix.casefold() == ".py":
                ast.parse(path.read_text(encoding="utf-8"), filename=relative)
                parsed_python += 1
        except Exception as exc:
            errors.append(f"{relative}: {type(exc).__name__}: {exc}")

        if path.suffix.casefold() in {".json", ".jsonl", ".md", ".txt", ".py", ".ps1"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(fragment in text for fragment in KNOWN_SENSITIVE_FRAGMENTS):
                sensitive_hits.append(relative)

    azure_responses = list(
        (PACKAGE_ROOT / "evidence" / "azure" / "responses").rglob("*.json")
    )
    charter_prompts = list(
        (PACKAGE_ROOT / "evidence" / "competition" / "prompts" / "charter").glob(
            "*.txt"
        )
    )
    identity_prompts = list(
        (PACKAGE_ROOT / "evidence" / "competition" / "prompts" / "identity").glob(
            "*.txt"
        )
    )
    expectations = {
        "azure_response_files": {"actual": len(azure_responses), "expected": 39},
        "charter_prompt_files": {"actual": len(charter_prompts), "expected": 23},
        "identity_prompt_files": {"actual": len(identity_prompts), "expected": 19},
    }
    for name, values in expectations.items():
        if values["actual"] != values["expected"]:
            errors.append(
                f"{name}: expected {values['expected']}, got {values['actual']}"
            )
    if sensitive_hits:
        errors.append(f"Known sensitive connection fragments found in: {sensitive_hits}")

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not errors else "failed",
        "parsed_json_files": parsed_json,
        "parsed_jsonl_lines": parsed_jsonl_lines,
        "parsed_python_files": parsed_python,
        "expectations": expectations,
        "known_sensitive_fragment_hits": sensitive_hits,
        "errors": errors,
    }
    VALIDATION_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
