from __future__ import annotations

import re
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONVERSATION_ROOT = PACKAGE_ROOT / "evidence" / "conversation"
SOURCE = CONVERSATION_ROOT / "codex-session-rollout.jsonl"
DESTINATION = CONVERSATION_ROOT / "codex-session-rollout.redacted.jsonl"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    patterns = (
        (r"InstrumentationKey=[^;\"\\\s]+", "InstrumentationKey=[REDACTED]"),
        (
            r"(?i)(api[-_ ]?key[\"']?\s*[:=]\s*[\"']?)[A-Za-z0-9_\-]{20,}",
            r"\1[REDACTED]",
        ),
        (r"(?i)(Bearer\s+)[A-Za-z0-9._\-]{20,}", r"\1[REDACTED]"),
    )
    counts = []
    for pattern, replacement in patterns:
        text, count = re.subn(pattern, replacement, text)
        counts.append(count)
    DESTINATION.write_text(text, encoding="utf-8", newline="\n")
    print(f"Redaction counts: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
