#!/usr/bin/env bash
# Setup Python interpreter for VUORSE-VORTEX
# This script creates a .venv using uv, ensures python3 is on PATH, and writes VS Code settings.

# Exit on any error
set -e

# 1. Ensure python3 is in PATH (common macOS locations)
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH. Adding common locations..."
  export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 still not found. Install Python 3.12+ or adjust PATH manually."
    exit 1
  fi
fi

# 2. Create .venv using uv (force direct interpreter link)
PROJECT_ROOT=$(pwd)
uv venv .venv --python "$(command -v python3)"

echo "Virtual environment created at $PROJECT_ROOT/.venv"

# 3. Write VS Code workspace settings to point to the venv interpreter
SETTINGS_DIR="$PROJECT_ROOT/.vscode"
mkdir -p "$SETTINGS_DIR"
cat > "$SETTINGS_DIR/settings.json" <<JSON
{
  "python.defaultInterpreterPath": "${PROJECT_ROOT}/.venv/bin/python",
  "python.venvPath": ".venv"
}
JSON

echo "VS Code settings written to $SETTINGS_DIR/settings.json"

echo "Setup complete. Restart VS Code (preferably from terminal: 'code .') to pick up the new interpreter."
