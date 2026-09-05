#!/usr/bin/env bash
set -euo pipefail

agent_name="video-agent"
model="openai/gpt-5.5"
comfyui_url="${COMFYUI_URL:-http://127.0.0.1:8188}"
comfyui_path="${COMFYUI_PATH:-/mnt/d/ComfyUI312/comfyui}"
restart_gateway=true

usage() {
  cat <<'EOF'
Usage: setup-wsl.sh [options]

Configure this repository as an isolated OpenClaw agent.

Options:
  --agent-name NAME     Agent id (default: video-agent)
  --model ID            OpenClaw model id (default: openai/gpt-5.5)
  --comfyui-url URL     ComfyUI API URL (default: http://127.0.0.1:8188)
  --comfyui-path PATH   ComfyUI path visible inside WSL
  --no-restart          Validate without restarting the gateway
  -h, --help            Show this help
EOF
}

while (($#)); do
  case "$1" in
    --agent-name)
      agent_name="${2:?missing value for --agent-name}"
      shift 2
      ;;
    --model)
      model="${2:?missing value for --model}"
      shift 2
      ;;
    --comfyui-url)
      comfyui_url="${2:?missing value for --comfyui-url}"
      shift 2
      ;;
    --comfyui-path)
      comfyui_path="${2:?missing value for --comfyui-path}"
      shift 2
      ;;
    --no-restart)
      restart_gateway=false
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
skills_dir="$repo_root/skills"

for command_name in openclaw python3; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$command_name" >&2
    exit 1
  fi
done

for required_path in \
  "$repo_root/AGENT.md" \
  "$script_dir/AGENTS.md" \
  "$script_dir/SOUL.md" \
  "$script_dir/TOOLS.md" \
  "$skills_dir"; do
  if [[ ! -e "$required_path" ]]; then
    printf 'Required repository path is missing: %s\n' "$required_path" >&2
    exit 1
  fi
done

agents_json="$(openclaw agents list --json)"
existing_workspace="$(
  python3 -c '
import json
import sys

agent_id = sys.argv[1]
for agent in json.load(sys.stdin):
    if agent.get("id") == agent_id:
        print(agent.get("workspace", ""))
        break
' "$agent_name" <<<"$agents_json"
)"

if [[ -z "$existing_workspace" ]]; then
  skip_bootstrap_was_set=false
  skip_bootstrap_original=""
  if skip_bootstrap_original="$(
    openclaw config get agents.defaults.skipBootstrap --json 2>/dev/null
  )"; then
    skip_bootstrap_was_set=true
  fi

  restore_skip_bootstrap() {
    if [[ "$skip_bootstrap_was_set" == true ]]; then
      openclaw config set agents.defaults.skipBootstrap \
        "$skip_bootstrap_original" --strict-json >/dev/null
    else
      openclaw config unset agents.defaults.skipBootstrap >/dev/null 2>&1 || true
    fi
  }

  openclaw config set agents.defaults.skipBootstrap true --strict-json >/dev/null
  trap restore_skip_bootstrap EXIT
  openclaw agents add "$agent_name" \
    --workspace "$script_dir" \
    --model "$model" \
    --non-interactive
  restore_skip_bootstrap
  trap - EXIT
elif [[ "$existing_workspace" != "$script_dir" ]]; then
  printf 'Agent %s already uses workspace %s; expected %s\n' \
    "$agent_name" "$existing_workspace" "$script_dir" >&2
  exit 1
else
  printf 'Agent already configured: %s -> %s\n' "$agent_name" "$script_dir"
fi

extra_dirs_json="$(
  openclaw config get skills.load.extraDirs --json 2>/dev/null || printf '[]'
)"

python3 - \
  "$skills_dir" \
  "$comfyui_url" \
  "$comfyui_path" \
  "$extra_dirs_json" <<'PY' \
  | openclaw config patch --stdin
import json
import sys

skills_dir, comfyui_url, comfyui_path, extra_dirs_json = sys.argv[1:]
extra_dirs = json.loads(extra_dirs_json)
if skills_dir not in extra_dirs:
    extra_dirs.append(skills_dir)

print(json.dumps({
    "env": {
        "vars": {
            "COMFYUI_URL": comfyui_url,
            "COMFYUI_PATH": comfyui_path,
        }
    },
    "skills": {
        "load": {
            "extraDirs": extra_dirs,
            "watch": True,
        }
    },
}))
PY

openclaw config validate

if [[ "$restart_gateway" == true ]]; then
  openclaw gateway restart
fi

printf '\nConfigured OpenClaw agent: %s\n' "$agent_name"
printf 'Workspace: %s\n' "$script_dir"
printf 'Skills:    %s\n' "$skills_dir"
printf 'ComfyUI:   %s\n' "$comfyui_url"
printf 'Models:    openclaw models --agent %s status\n' "$agent_name"
printf 'Auth:      openclaw models auth --agent %s login --provider openai --device-code\n' "$agent_name"
printf 'Run:       openclaw agent --agent %s --message "Read the canon and report readiness."\n' "$agent_name"
