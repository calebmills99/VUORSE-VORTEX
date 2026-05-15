#!/usr/bin/env bash
set -euo pipefail

export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
uv run vuorse-vortex doctor --require-cuda
