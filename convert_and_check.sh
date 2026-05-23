#!/usr/bin/env bash
#
# convert_and_check.sh – safe wrapper around the VUORSE‑VORTEX pipeline
#
# Usage:
#   ./convert_and_check.sh <legacy-jsonl> [<clean-output>]
#
#   <legacy-jsonl>   Path to the original JSONL that failed validation.
#   <clean-output>   Optional path for the normalized file (default:
#                    "cleaned.jsonl" in the current directory).
#
# The script:
#   1️⃣ Runs the conversion utility (which validates each record).
#   2️⃣ If the conversion succeeds, it immediately runs the firewall
#      check on the cleaned file.
#   3️⃣ All error handling is done inside the Python code – the Bash
#      wrapper only reports success/failure.
#

set -euo pipefail

LEGACY_JSONL="${1:-}"
CLEAN_JSONL="${2:-cleaned.jsonl}"

if [[ -z "$LEGACY_JSONL" ]]; then
  echo "Error: you must provide the legacy JSONL file as the first argument."
  exit 1
fi

if [[ ! -f "$LEGACY_JSONL" ]]; then
  echo "Error: file not found → $LEGACY_JSONL"
  exit 1
fi

./.venv/bin/vuorse-vortex convert-jsonl "$LEGACY_JSONL" --output "$CLEAN_JSONL"

echo "[INFO] Conversion finished. Running firewall validation …"
./.venv/bin/vuorse-vortex firewall "$CLEAN_JSONL" || {
  echo "[ERROR] Firewall validation failed – see the messages above."
  exit 1
}

echo "[SUCCESS] All records passed the canon firewall."
