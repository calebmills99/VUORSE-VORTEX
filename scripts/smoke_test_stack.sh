#!/usr/bin/env bash
set -euo pipefail

# VUORSE-VORTEX GPU Stack Smoke Test
# Checks torch + CUDA, then serves a tiny model via vLLM to verify compiler/runtime integrity.

say()  { printf '\033[1;35m%s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m%s\033[0m\n' "$1"; }
fail() { printf '\033[1;31m%s\033[0m\n' "$1" >&2; exit 1; }

# Find python/uv in our venv
VENV_DIR="/workspace/VUORSE-VORTEX/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  # Fallback to local .venv if not in Vast workspace
  VENV_DIR="./.venv"
fi
PYTHON_BIN="$VENV_DIR/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  fail "Python executable not found in virtualenv: $PYTHON_BIN"
fi

say "1. Testing PyTorch CUDA Visibility..."
"$PYTHON_BIN" -c "
import torch
print('Torch Version:', torch.__version__)
print('CUDA version:', torch.version.cuda)
if not torch.cuda.is_available():
    raise SystemExit('FAIL: PyTorch cannot see CUDA!')
print('✓ PyTorch CUDA is working. Device:', torch.cuda.get_device_name(0))
" || fail "PyTorch CUDA smoke test failed."

say "2. Testing vLLM Import..."
"$PYTHON_BIN" -c "
import vllm
print('✓ vLLM is installed. Version:', vllm.__version__)
" || fail "vLLM import test failed (mismatched libcudart/compile issue)."

say "3. Launching tiny model (Qwen/Qwen2.5-0.5B-Instruct) on vLLM server..."
# Run the vllm server in the background
"$PYTHON_BIN" -m vllm.entrypoints.openai.api_server \
  --model "Qwen/Qwen2.5-0.5B-Instruct" \
  --port 8000 \
  --gpu-memory-utilization 0.2 \
  --max-model-len 2048 > /tmp/vllm_smoke.log 2>&1 &
VLLM_PID=$!

cleanup() {
  say "Cleaning up background vLLM server (PID: $VLLM_PID)..."
  kill "$VLLM_PID" 2>/dev/null || true
  wait "$VLLM_PID" 2>/dev/null || true
}
trap cleanup EXIT

say "Waiting for server to spin up on port 8000 (timeout: 120s)..."
for i in {1..120}; do
  if curl -s http://localhost:8000/v1/models >/dev/null; then
    say "✓ vLLM Server is online!"
    break
  fi
  if ! kill -0 "$VLLM_PID" 2>/dev/null; then
    cat /tmp/vllm_smoke.log
    fail "FAIL: vLLM server crashed early. See logs above."
  fi
  sleep 1
done

if ! curl -s http://localhost:8000/v1/models >/dev/null; then
  cat /tmp/vllm_smoke.log
  fail "FAIL: vLLM server timed out starting up."
fi

say "4. Verifying Inference Completion..."
RESPONSE=$(curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "messages": [{"role": "user", "content": "Verify inference works. Respond with exactly the word COMPLETED."}]
  }')

echo "Response: $RESPONSE"

if [[ "$RESPONSE" == *"COMPLETED"* || "$RESPONSE" == *"completed"* ]]; then
  say "✓ SMOKE TEST SUCCESS: Full GPU stack (PyTorch, CUDA, vLLM inference) verified on this hardware!"
else
  fail "FAIL: Inference did not return the expected token."
fi
