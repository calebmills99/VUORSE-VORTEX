#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/validate_jsonl.sh path/to/file.jsonl" >&2
  exit 2
fi

uv run vuorse-vortex validate-jsonl "$1"
