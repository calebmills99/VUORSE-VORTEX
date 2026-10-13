# VideoAgent Tools

This file contains OpenClaw tool and environment deltas only. In the in-place WSL layout, canonical behavior lives in `../AGENT.md` and the platform-neutral API reference lives in `../foundation/api-quick-ref.md`. In a flattened native workspace, use `AGENT.md` and `foundation/api-quick-ref.md`.

## ComfyUI REST API

Base URL: configured via `COMFYUI_URL` environment variable (default `http://127.0.0.1:8188`).

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/system_stats` | GET | GPU info, VRAM usage, ComfyUI version |
| `/queue` | GET | Current queue status |
| `/interrupt` | POST | Cancel current generation |
| `/free` | POST | Free VRAM (`{"unload_models": true}`) |
| `/object_info` | GET | All installed node classes |
| `/models/{type}` | GET | List models (checkpoints, loras, vae, controlnet, etc.) |
| `/prompt` | POST | Queue a workflow (`{"prompt": {...}}`) |
| `/history/{prompt_id}` | GET | Execution result for a queued workflow |
| `/view` | GET | Retrieve output image (`?filename=...&type=output`) |
| `/upload/image` | POST | Upload image (multipart) |

## Polling Pattern

```bash
# 1. Queue workflow
curl -s -X POST $COMFYUI_URL/prompt -H "Content-Type: application/json" -d '{"prompt": WORKFLOW_JSON}'
# Returns: {"prompt_id": "abc-123"}

# 2. Poll for completion (every 5s)
curl -s $COMFYUI_URL/history/abc-123
# When complete: {"abc-123": {"outputs": {...}, "status": {"completed": true}}}

# 3. Retrieve output
curl -s "$COMFYUI_URL/view?filename=output.png&subfolder=&type=output" --output result.png
```

## Scripts

All scripts are in the repo's `scripts/` directory. When installed via `setup.ps1`, they're accessible at `{baseDir}/../../scripts/`.

| Script | Purpose |
|--------|---------|
| `scan-inventory.ps1` | Scan ComfyUI models & nodes offline |
| `connect-comfyui.ps1` | Test ComfyUI connection & diagnostics |

## Skill Runtime Deltas

Canonical skill frontmatter remains platform-neutral. OpenClaw should apply these
runtime requirements when exposing repository skills:

| Skills | Requirement | Primary environment |
|--------|-------------|---------------------|
| `comfyui-api`, `comfyui-video-pipeline`, `comfyui-voice-pipeline`, `comfyui-workflow-builder` | `curl` or `wget` | `COMFYUI_URL` |
| `comfyui-inventory` | `pwsh` | `COMFYUI_PATH` |
| `comfyui-lora-training` | `python` | `COMFYUI_PATH` |
| `video-assembly` | `ffmpeg` | none |
| All other repository skills | no runner-specific binary requirement | none |

## FFmpeg (for video assembly)

Required for video-assembly skill. Must be on PATH.

```bash
ffmpeg -version
```
