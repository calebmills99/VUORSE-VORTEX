#!/usr/bin/env bash
set -Eeuo pipefail

# Deploy the Windows-hosted ComfyUI Expert repository into a WSL-native
# OpenClaw workspace, configure the official Comfy provider, and prove the
# connection with a small image workflow.

agent_name="video-agent"
workspace="${HOME}/.openclaw/workspaces/video-agent"
model=""
comfyui_url="auto"
comfyui_path="/mnt/d/ComfyUI312/comfyui"
checkpoint=""
binding=""
image_workflow=""
image_prompt_node="6"
image_output_node="9"
image_seed_node="3"
video_workflow=""
video_prompt_node=""
video_output_node=""
video_seed_node=""
music_workflow=""
music_prompt_node=""
music_output_node=""
music_seed_node=""
restart_gateway=true
run_generation_test=true
skip_health_check=false
dry_run=false

log() { printf '[connect] %s\n' "$*"; }
warn() { printf '[connect] WARNING: %s\n' "$*" >&2; }
die() { printf '[connect] ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

usage() {
  cat <<'EOF'
Usage: connect-openclaw-comfyui.sh [options]

Deploy ComfyUI Expert from its Windows-mounted repository into a WSL-native
OpenClaw workspace, configure an isolated agent and the official Comfy provider,
and run an end-to-end smoke test.

Options:
  --agent-name NAME          Agent id (default: video-agent)
  --workspace PATH          WSL-native workspace destination
  --model ID                Agent model (default: current OpenClaw default)
  --comfyui-url URL          Explicit ComfyUI URL (default: auto-detect)
  --comfyui-path PATH        WSL-visible ComfyUI installation path
  --checkpoint NAME         Checkpoint for generated smoke workflow
  --bind CHANNEL[:ACCOUNT]  Optional direct channel binding

  --image-workflow PATH     Use an existing API-format image workflow instead
  --image-prompt-node ID    Prompt node (default: 6 for generated workflow)
  --image-output-node ID    Output node (default: 9 for generated workflow)
  --image-seed-node ID      Seed node (default: 3 for generated workflow)

  --video-workflow PATH     Optional API-format video workflow
  --video-prompt-node ID    Required with --video-workflow
  --video-output-node ID    Optional video output node
  --video-seed-node ID      Optional video seed node

  --music-workflow PATH     Optional API-format music workflow
  --music-prompt-node ID    Required with --music-workflow
  --music-output-node ID    Optional music output node
  --music-seed-node ID      Optional music seed node

  --no-generation-test      Skip the final real image generation
  --skip-health-check       Configure even when ComfyUI is currently offline
  --no-restart              Do not restart the Gateway
  --dry-run                 Show the resolved plan without changing anything
  -h, --help                Show this help

Examples:
  bash openclaw/connect-openclaw-comfyui.sh

  bash openclaw/connect-openclaw-comfyui.sh \
    --comfyui-url http://172.20.0.1:8188 \
    --checkpoint model.safetensors

  bash openclaw/connect-openclaw-comfyui.sh \
    --video-workflow workflows/wan-api.json \
    --video-prompt-node 12 --video-output-node 21
EOF
}

while (($#)); do
  case "$1" in
    --agent-name) agent_name="${2:?missing value for --agent-name}"; shift 2 ;;
    --workspace) workspace="${2:?missing value for --workspace}"; shift 2 ;;
    --model) model="${2:?missing value for --model}"; shift 2 ;;
    --comfyui-url) comfyui_url="${2:?missing value for --comfyui-url}"; shift 2 ;;
    --comfyui-path) comfyui_path="${2:?missing value for --comfyui-path}"; shift 2 ;;
    --checkpoint) checkpoint="${2:?missing value for --checkpoint}"; shift 2 ;;
    --bind) binding="${2:?missing value for --bind}"; shift 2 ;;
    --image-workflow) image_workflow="${2:?missing value for --image-workflow}"; shift 2 ;;
    --image-prompt-node) image_prompt_node="${2:?missing value for --image-prompt-node}"; shift 2 ;;
    --image-output-node) image_output_node="${2:?missing value for --image-output-node}"; shift 2 ;;
    --image-seed-node) image_seed_node="${2:?missing value for --image-seed-node}"; shift 2 ;;
    --video-workflow) video_workflow="${2:?missing value for --video-workflow}"; shift 2 ;;
    --video-prompt-node) video_prompt_node="${2:?missing value for --video-prompt-node}"; shift 2 ;;
    --video-output-node) video_output_node="${2:?missing value for --video-output-node}"; shift 2 ;;
    --video-seed-node) video_seed_node="${2:?missing value for --video-seed-node}"; shift 2 ;;
    --music-workflow) music_workflow="${2:?missing value for --music-workflow}"; shift 2 ;;
    --music-prompt-node) music_prompt_node="${2:?missing value for --music-prompt-node}"; shift 2 ;;
    --music-output-node) music_output_node="${2:?missing value for --music-output-node}"; shift 2 ;;
    --music-seed-node) music_seed_node="${2:?missing value for --music-seed-node}"; shift 2 ;;
    --no-generation-test) run_generation_test=false; shift ;;
    --skip-health-check) skip_health_check=true; shift ;;
    --no-restart) restart_gateway=false; shift ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
source_skills="$repo_root/skills"

[[ "${workspace:0:1}" == "/" ]] || die "--workspace must be an absolute WSL path"
case "$workspace" in
  /mnt/*) die "Workspace must use WSL-native storage, not /mnt/*: $workspace" ;;
esac

[[ -d "$source_skills" ]] || die "Skills directory not found: $source_skills"
[[ -f "$repo_root/AGENT.md" ]] || die "Canonical AGENT.md not found: $repo_root/AGENT.md"
[[ -f "$script_dir/AGENTS.md" ]] || die "OpenClaw AGENTS.md not found: $script_dir/AGENTS.md"
[[ -d "$comfyui_path" ]] || warn "ComfyUI filesystem path is not currently visible: $comfyui_path"

need openclaw
need python3
need curl
need rsync
need jq

if [[ -n "$video_workflow" && -z "$video_prompt_node" ]]; then
  die "--video-prompt-node is required with --video-workflow"
fi
if [[ -n "$music_workflow" && -z "$music_prompt_node" ]]; then
  die "--music-prompt-node is required with --music-workflow"
fi
for workflow in "$image_workflow" "$video_workflow" "$music_workflow"; do
  [[ -z "$workflow" || -f "$workflow" ]] || die "Workflow not found: $workflow"
done

if [[ -z "$model" ]]; then
  model="$(openclaw agents list --json | jq -r '.[] | select(.isDefault == true) | .model // empty' | head -n1)"
  [[ -n "$model" ]] || model="openai/gpt-5.6-sol"
fi

probe_comfyui() {
  curl -fsS --max-time 4 "$1/system_stats" >/dev/null 2>&1
}

windows_powershell=""
for candidate in \
  "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe" \
  "/mnt/c/Windows/System32/powershell.exe"; do
  if [[ -x "$candidate" ]]; then
    windows_powershell="$candidate"
    break
  fi
done

windows_comfyui_listener() {
  [[ -n "$windows_powershell" ]] || return 0
  (
    cd /mnt/c 2>/dev/null || exit 0
    "$windows_powershell" -NoProfile -Command '
      $listeners = Get-NetTCPConnection -LocalPort 8188 -State Listen -ErrorAction SilentlyContinue
      if (-not $listeners) { "NO_LISTENER"; exit }
      ($listeners | Select-Object -ExpandProperty LocalAddress -Unique) -join ","
    ' 2>/dev/null | tr -d '\r'
  )
}

resolve_comfyui_url() {
  if [[ "$comfyui_url" != "auto" ]]; then
    comfyui_url="${comfyui_url%/}"
    if [[ "$skip_health_check" == false ]] && ! probe_comfyui "$comfyui_url"; then
      die "ComfyUI did not answer at $comfyui_url/system_stats"
    fi
    return
  fi

  local candidate host_ip listener
  local -a candidates=("http://127.0.0.1:8188" "http://localhost:8188")
  host_ip="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"
  [[ -n "$host_ip" ]] && candidates+=("http://${host_ip}:8188")

  if [[ "$skip_health_check" == true ]]; then
    comfyui_url="${candidates[0]}"
    return
  fi

  for candidate in "${candidates[@]}"; do
    if probe_comfyui "$candidate"; then
      comfyui_url="$candidate"
      return
    fi
  done

  listener="$(windows_comfyui_listener)"
  if [[ "$listener" == "NO_LISTENER" ]]; then
    die "Windows has no ComfyUI listener on port 8188. Start D:\\ComfyUI312\\run_comfyui.bat. Under WSL NAT, its Python launch line must include --listen 0.0.0.0."
  fi
  if [[ "$listener" == "127.0.0.1" || "$listener" == "::1" || "$listener" == "127.0.0.1,::1" || "$listener" == "::1,127.0.0.1" ]]; then
    die "ComfyUI is listening only on Windows localhost ($listener). Restart it with --listen 0.0.0.0 so WSL can use http://${host_ip:-WINDOWS_HOST_IP}:8188."
  fi
  if [[ -n "$listener" ]]; then
    die "Windows reports a ComfyUI listener on $listener:8188, but WSL cannot reach it at http://${host_ip:-WINDOWS_HOST_IP}:8188. Check the Windows Hyper-V/WSL firewall path, or pass --comfyui-url URL."
  fi

  die "ComfyUI was not reachable from WSL. Start it with --listen 0.0.0.0, or pass --comfyui-url URL. Tried: ${candidates[*]}"
}

resolve_comfyui_url

select_checkpoint() {
  if [[ -n "$checkpoint" ]]; then
    return
  fi
  local inventory="$repo_root/state/inventory.json"
  [[ -f "$inventory" ]] || die "No checkpoint supplied and inventory is missing: $inventory"
  checkpoint="$(python3 - "$inventory" <<'PY'
import json, re, sys
with open(sys.argv[1], encoding="utf-8-sig") as handle:
    data = json.load(handle)
items = data.get("models", {}).get("checkpoints", [])
names = [item.get("name") for item in items if isinstance(item, dict) and item.get("name")]
preferred = [
    name for name in names
    if not re.search(r"(?:inpaint|flux|ltx|wan|video|prompt)", name, re.I)
]
if preferred:
    print(preferred[0])
elif names:
    print(names[0])
PY
)"
  [[ -n "$checkpoint" ]] || die "No checkpoint found in state/inventory.json; pass --checkpoint NAME"
}

if [[ -z "$image_workflow" ]]; then
  select_checkpoint
fi

log "Resolved plan"
printf '  source:      %s\n' "$repo_root"
printf '  workspace:   %s\n' "$workspace"
printf '  agent:       %s\n' "$agent_name"
printf '  model:       %s\n' "$model"
printf '  ComfyUI URL: %s\n' "$comfyui_url"
printf '  ComfyUI path:%s\n' " $comfyui_path"
printf '  image:       %s\n' "${image_workflow:-generated smoke workflow using $checkpoint}"
printf '  video:       %s\n' "${video_workflow:-not configured}"
printf '  music:       %s\n' "${music_workflow:-not configured}"
printf '  binding:     %s\n' "${binding:-none, main may delegate explicitly}"

if [[ "$dry_run" == true ]]; then
  log "Dry run complete; nothing changed"
  exit 0
fi

config_file="$(openclaw config file)"
backup_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -f "$config_file" ]]; then
  config_backup="${config_file}.before-comfyui-${backup_stamp}"
  cp -p -- "$config_file" "$config_backup"
  log "Backed up OpenClaw config to $config_backup"
fi

workspace_parent="$(dirname -- "$workspace")"
mkdir -p -- "$workspace_parent"
stage="$(mktemp -d "${workspace_parent}/.${agent_name}.stage.XXXXXX")"
cleanup_stage() { [[ ! -d "$stage" ]] || rm -rf -- "$stage"; }
trap cleanup_stage EXIT

log "Building staged WSL-native workspace"
install -m 0644 "$repo_root/AGENT.md" "$stage/AGENT.md"
for file in AGENTS.md SOUL.md TOOLS.md USER.md IDENTITY.md HEARTBEAT.md; do
  [[ -f "$script_dir/$file" ]] && install -m 0644 "$script_dir/$file" "$stage/$file"
done

for dir in agent foundation references scripts skills state projects; do
  if [[ -d "$repo_root/$dir" ]]; then
    mkdir -p "$stage/$dir"
    rsync -a "$repo_root/$dir/" "$stage/$dir/"
  fi
done

# Preserve agent-local memory that is not part of the Windows source tree.
if [[ -d "$workspace/memory" && ! -d "$repo_root/memory" ]]; then
  mkdir -p "$stage/memory"
  rsync -a "$workspace/memory/" "$stage/memory/"
fi
[[ -f "$workspace/MEMORY.md" && ! -f "$repo_root/MEMORY.md" ]] && cp -p "$workspace/MEMORY.md" "$stage/MEMORY.md"

cat >>"$stage/TOOLS.md" <<EOF

## Managed ComfyUI connection

This deployed workspace uses the official OpenClaw Comfy provider at
\`${comfyui_url}\`. For native generation, call \`image_generate\`,
\`video_generate\`, or \`music_generate\` with \`model: comfy/workflow\`.
Use the repository's raw REST instructions only for operations not represented
by those native tools.
EOF

mkdir -p "$stage/workflows"
image_runtime_path="$workspace/workflows/image-api.json"
if [[ -n "$image_workflow" ]]; then
  cp -- "$image_workflow" "$stage/workflows/image-api.json"
else
  python3 - "$checkpoint" "$stage/workflows/image-api.json" <<'PY'
import json, sys
checkpoint, destination = sys.argv[1:]
workflow = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 1,
            "steps": 12,
            "cfg": 6.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
        },
    },
    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "OpenClaw and ComfyUI connection test", "clip": ["4", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "text, watermark, low quality", "clip": ["4", 1]}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "OpenClaw_connection_test", "images": ["8", 0]}},
}
with open(destination, "w", encoding="utf-8") as handle:
    json.dump(workflow, handle, indent=2)
    handle.write("\n")
PY
fi

video_runtime_path=""
if [[ -n "$video_workflow" ]]; then
  cp -- "$video_workflow" "$stage/workflows/video-api.json"
  video_runtime_path="$workspace/workflows/video-api.json"
fi
music_runtime_path=""
if [[ -n "$music_workflow" ]]; then
  cp -- "$music_workflow" "$stage/workflows/music-api.json"
  music_runtime_path="$workspace/workflows/music-api.json"
fi

python3 - "$stage/workflows/image-api.json" "$image_prompt_node" "$image_output_node" <<'PY'
import json, sys
path, prompt_node, output_node = sys.argv[1:]
with open(path, encoding="utf-8-sig") as handle:
    workflow = json.load(handle)
if not isinstance(workflow, dict):
    raise SystemExit(f"Workflow must be a JSON object: {path}")
if prompt_node not in workflow:
    raise SystemExit(f"Prompt node {prompt_node!r} is absent from {path}")
if output_node and output_node not in workflow:
    raise SystemExit(f"Output node {output_node!r} is absent from {path}")
PY

cat >"$stage/.openclaw-deployment.json" <<EOF
{
  "source": $(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$repo_root"),
  "deployedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agent": $(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$agent_name"),
  "comfyuiUrl": $(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$comfyui_url")
}
EOF

if [[ -d "$workspace" ]]; then
  workspace_backup="${workspace}.backup-${backup_stamp}"
  mv -- "$workspace" "$workspace_backup"
  log "Moved previous workspace to $workspace_backup"
fi
mv -- "$stage" "$workspace"
trap - EXIT
log "Installed WSL-native workspace at $workspace"

if ! openclaw plugins inspect comfy --json >/dev/null 2>&1; then
  log "Installing official Comfy provider"
  openclaw plugins install @openclaw/comfy-provider --accept-capabilities --pin
else
  log "Official Comfy provider is already installed"
fi

agent_exists=false
if openclaw agents list --json | jq -e --arg id "$agent_name" '.[] | select(.id == $id)' >/dev/null; then
  agent_exists=true
fi

restore_skip_bootstrap_needed=false
restore_skip_bootstrap() {
  if [[ "$restore_skip_bootstrap_needed" == true ]]; then
    if [[ "$skip_bootstrap_was_set" == true ]]; then
      openclaw config set agents.defaults.skipBootstrap "$skip_bootstrap_original" --strict-json >/dev/null
    else
      openclaw config unset agents.defaults.skipBootstrap >/dev/null 2>&1 || true
    fi
    restore_skip_bootstrap_needed=false
  fi
}

if [[ "$agent_exists" == false ]]; then
  log "Creating isolated OpenClaw agent $agent_name"
  skip_bootstrap_was_set=false
  skip_bootstrap_original=""
  if skip_bootstrap_original="$(openclaw config get agents.defaults.skipBootstrap --json 2>/dev/null)"; then
    skip_bootstrap_was_set=true
  fi
  restore_skip_bootstrap_needed=true
  trap 'restore_skip_bootstrap; exit 1' ERR INT TERM
  openclaw config set agents.defaults.skipBootstrap true --strict-json >/dev/null
  openclaw agents add "$agent_name" --workspace "$workspace" --model "$model" --non-interactive
  restore_skip_bootstrap
  trap - ERR INT TERM
else
  log "Agent $agent_name already exists; updating its workspace configuration"
fi

skills_json="$(find "$workspace/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -printf '%h\n' \
  | sed 's#.*/##' | LC_ALL=C sort -u | jq -Rsc 'split("\n") | map(select(length > 0))')"

patch_file="$(mktemp)"
trap 'rm -f -- "$patch_file"' EXIT
python3 - \
  "$agent_name" "$workspace" "$model" "$skills_json" \
  "$comfyui_url" \
  "$image_runtime_path" "$image_prompt_node" "$image_output_node" "$image_seed_node" \
  "$video_runtime_path" "$video_prompt_node" "$video_output_node" "$video_seed_node" \
  "$music_runtime_path" "$music_prompt_node" "$music_output_node" "$music_seed_node" \
  >"$patch_file" <<'PY'
import json, sys
(
    agent, workspace, model, skills_json,
    base_url,
    image_path, image_prompt, image_output, image_seed,
    video_path, video_prompt, video_output, video_seed,
    music_path, music_prompt, music_output, music_seed,
) = sys.argv[1:]

def capability(path, prompt, output, seed):
    if not path:
        return None
    value = {"workflowPath": path, "promptNodeId": prompt}
    if output:
        value["outputNodeId"] = output
    if seed:
        value["seedNodeId"] = seed
    return value

comfy = {
    "mode": "local",
    "baseUrl": base_url,
    "image": capability(image_path, image_prompt, image_output, image_seed),
}
video = capability(video_path, video_prompt, video_output, video_seed)
music = capability(music_path, music_prompt, music_output, music_seed)
if video:
    comfy["video"] = video
if music:
    comfy["music"] = music

patch = {
    "agents": {
        "entries": {
            agent: {
                "workspace": workspace,
                "model": model,
                "skills": json.loads(skills_json),
            }
        }
    },
    "plugins": {
        "entries": {
            "comfy": {
                "enabled": True,
                "config": comfy,
            }
        }
    },
}
print(json.dumps(patch))
PY

log "Validating the OpenClaw configuration patch"
openclaw config patch --file "$patch_file" --dry-run >/dev/null
openclaw config patch --file "$patch_file" >/dev/null
rm -f -- "$patch_file"
trap - EXIT

# Remove only this repository's legacy globally loaded skill path. Preserve every
# unrelated extra directory.
if old_extra_dirs="$(openclaw config get skills.load.extraDirs --json 2>/dev/null)"; then
  filtered_extra_dirs="$(python3 - "$old_extra_dirs" "$repo_root/skills" "/mnt/c/runb2/ComfyUI-Expert/skills" <<'PY'
import json, os, sys
items = json.loads(sys.argv[1])
remove = {os.path.normcase(os.path.normpath(x)) for x in sys.argv[2:]}
print(json.dumps([x for x in items if os.path.normcase(os.path.normpath(x)) not in remove]))
PY
)"
  if [[ "$filtered_extra_dirs" != "$old_extra_dirs" ]]; then
    if [[ "$filtered_extra_dirs" == "[]" ]]; then
      openclaw config unset skills.load.extraDirs >/dev/null
    else
      openclaw config set skills.load.extraDirs "$filtered_extra_dirs" --strict-json >/dev/null
    fi
    log "Removed the repository from global skills.load.extraDirs"
  fi
fi

if [[ -n "$binding" ]]; then
  log "Adding channel binding $binding"
  openclaw agents bind --agent "$agent_name" --bind "$binding" --json >/dev/null
fi

openclaw config validate

if [[ "$restart_gateway" == true ]]; then
  log "Restarting OpenClaw Gateway"
  openclaw gateway restart
else
  warn "Gateway restart skipped; plugin and agent changes may not be active yet"
fi

log "Verifying agent skills"
openclaw skills check --agent "$agent_name" --json \
  | jq -e --argjson expected "$skills_json" '
      (.eligible as $eligible |
       $expected | all(. as $skill | $eligible | index($skill) != null))
    ' >/dev/null

log "Verifying Comfy provider runtime"
openclaw plugins inspect comfy --runtime --json >/dev/null
openclaw models list --provider comfy --json >/dev/null

if [[ "$skip_health_check" == false ]]; then
  probe_comfyui "$comfyui_url" || die "ComfyUI stopped answering during final verification"
fi

if [[ "$run_generation_test" == true ]]; then
  if [[ "$restart_gateway" == false ]]; then
    warn "Generation test skipped because --no-restart was used"
  elif [[ "$skip_health_check" == true ]]; then
    warn "Generation test skipped because --skip-health-check was used"
  else
    log "Running one real OpenClaw to ComfyUI image-generation test"
    openclaw agent --agent "$agent_name" --timeout 600 --message \
      "Use image_generate exactly once with model comfy/workflow. Prompt: a simple studio test card reading OpenClaw plus ComfyUI, clean white background. Return the generated media and a one-line success confirmation." \
      >/dev/null
  fi
fi

log "Connection complete"
printf '  Agent:     %s\n' "$agent_name"
printf '  Workspace: %s\n' "$workspace"
printf '  ComfyUI:   %s\n' "$comfyui_url"
printf '  Invoke:    openclaw agent --agent %s --message "Generate an image of ..."\n' "$agent_name"
