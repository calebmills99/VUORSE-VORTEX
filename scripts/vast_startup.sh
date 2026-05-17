#!/usr/bin/env bash
set -euo pipefail

# VUORSE-VORTEX Vast.ai startup script.
#
# Intended image: a Vast.ai PyTorch template with CUDA + torch already installed.
# This script deliberately does not install torch. It installs OS/runtime tooling,
# prepares the repo, installs project dependencies, and runs smoke checks.
#
# Common Vast.ai on-start command:
#   bash /workspace/VUORSE-VORTEX/scripts/vast_startup.sh
#
# Optional environment variables:
#   REPO_URL=https://github.com/calebmills99/VUORSE-VORTEX.git
#   REPO_DIR=/workspace/VUORSE-VORTEX
#   STARTUP_RUN_CHECKS=1
#   STARTUP_PULL=1

export DEBIAN_FRONTEND=noninteractive

REPO_URL="${REPO_URL:-https://github.com/calebmills99/VUORSE-VORTEX.git}"
REPO_DIR="${REPO_DIR:-/workspace/VUORSE-VORTEX}"
STARTUP_RUN_CHECKS="${STARTUP_RUN_CHECKS:-1}"
STARTUP_PULL="${STARTUP_PULL:-1}"

say() {
  printf '\033[1;35m%s\033[0m\n' "$1"
}

warn() {
  printf '\033[1;33m%s\033[0m\n' "$1"
}

fail() {
  printf '\033[1;31m%s\033[0m\n' "$1" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command after install: $1"
}

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  fail "Run this startup script as root so apt update/upgrade can complete"
fi

say "VUORSE-VORTEX Vast.ai startup: apt update + upgrade"
apt-get update
apt-get upgrade -y

say "Installing system dependencies"
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  git \
  build-essential \
  pkg-config \
  python3-dev \
  python3-venv \
  python3-pip \
  jq \
  rsync \
  unzip \
  htop \
  tmux \
  ffmpeg \
  libgl1 \
  libglib2.0-0

node_major="0"
if command -v node >/dev/null 2>&1; then
  node_major="$(node --version | sed -E 's/^v([0-9]+).*/\1/')"
fi

if [[ "$node_major" -lt 24 ]]; then
  say "Installing Node.js 24.x for the canonical web frontend"
  curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
  apt-get install -y --no-install-recommends nodejs
else
  say "Node.js already present: $(node --version)"
fi

require_cmd git
require_cmd curl
require_cmd python3
require_cmd node
require_cmd npm

if ! command -v uv >/dev/null 2>&1; then
  say "Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

export PATH="$HOME/.local/bin:$PATH"
require_cmd uv

say "Writing VUORSE GPU environment defaults"
cat >/etc/profile.d/vuorse-vortex.sh <<'ENV'
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export HF_HOME=${HF_HOME:-/workspace/.cache/huggingface}
export UV_LINK_MODE=copy
ENV

export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
export UV_LINK_MODE=copy

mkdir -p /workspace/.cache/huggingface

if [[ ! -d "$REPO_DIR/.git" ]]; then
  say "Cloning VUORSE-VORTEX into $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone "$REPO_URL" "$REPO_DIR"
elif [[ "$STARTUP_PULL" == "1" ]]; then
  say "Updating existing repo at $REPO_DIR"
  git -C "$REPO_DIR" pull --ff-only
else
  warn "Repo exists and STARTUP_PULL!=1; skipping git pull"
fi

cd "$REPO_DIR"

say "Creating project virtualenv with access to PyTorch template packages"
uv venv --system-site-packages .venv

say "Installing Python project dependencies without reinstalling torch"
uv sync --extra dev
uv pip install \
  "sentence-transformers>=3.0" \
  "chromadb>=0.5" \
  "faiss-cpu>=1.8"

say "Installing canonical web frontend dependencies"
npm ci --prefix web

if [[ "$STARTUP_RUN_CHECKS" == "1" ]]; then
  say "Running GPU and project smoke checks"
  uv run python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable in the PyTorch template")

print("CUDA available:", torch.cuda.get_device_name(0))
PY

  uv run vuorse-vortex doctor --require-cuda
  uv run ruff check .
  uv run mypy src
  uv run pytest
  npm run --prefix web lint
  npm run --prefix web build
else
  warn "STARTUP_RUN_CHECKS!=1; skipping verification checks"
fi

say "VUORSE-VORTEX Vast.ai startup complete"
say "Repo: $REPO_DIR"
say "API:  cd $REPO_DIR && uv run uvicorn vuorse_vortex.api:app --host 0.0.0.0 --port 8000"
say "Web:  cd $REPO_DIR/web && npm run dev -- --host 0.0.0.0"
