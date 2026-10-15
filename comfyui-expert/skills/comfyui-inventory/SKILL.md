---
name: comfyui-inventory
description: Discover and cache all installed ComfyUI models, custom nodes, and system capabilities. Works online (API queries) and offline (directory scanning). Use before generating workflows to verify available resources.
---

# ComfyUI Inventory Skill

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Discovers what's installed in the user's ComfyUI instance and caches results for workflow validation.

Live API and filesystem discovery outrank every illustrative value in this skill.

## Purpose

Every workflow generation MUST be preceded by an inventory check. This prevents:
- Referencing models that aren't downloaded
- Using nodes that aren't installed
- Exceeding VRAM limits

## Two Discovery Modes

### Online Mode (ComfyUI API Running)

Query the live server for authoritative information.

**1. System info:**
```bash
COMFYUI_URL="${COMFYUI_URL:-http://127.0.0.1:8188}"
curl "$COMFYUI_URL/system_stats"
```
Extracts: GPU name, total VRAM, free VRAM, ComfyUI version.

**2. Installed nodes:**
```bash
curl "$COMFYUI_URL/object_info"
```
Returns all registered node classes with their input/output specifications.

**3. Installed models (per type):**
```bash
curl "$COMFYUI_URL/models/checkpoints"
curl "$COMFYUI_URL/models/loras"
curl "$COMFYUI_URL/models/vae"
curl "$COMFYUI_URL/models/controlnet"
curl "$COMFYUI_URL/models/text_encoders"
curl "$COMFYUI_URL/models/clip_vision"
curl "$COMFYUI_URL/models/upscale_models"
curl "$COMFYUI_URL/models/diffusion_models"
```

### Offline Mode (Directory Scan)

When ComfyUI isn't running, scan the filesystem directly.

**Requires**: ComfyUI installation path resolved as `{COMFYUI_PATH}` from inventory or session state.

**Scan directories:**
```
{COMFYUI_PATH}/models/checkpoints/    → .safetensors, .ckpt
{COMFYUI_PATH}/models/loras/          → .safetensors
{COMFYUI_PATH}/models/vae/            → .safetensors, .pt
{COMFYUI_PATH}/models/controlnet/     → .safetensors, .pth
{COMFYUI_PATH}/models/clip/           → legacy CLIP encoder files
{COMFYUI_PATH}/models/text_encoders/  → .safetensors
{COMFYUI_PATH}/models/clip_vision/    → .safetensors
{COMFYUI_PATH}/models/upscale_models/ → .pth, .safetensors
{COMFYUI_PATH}/models/diffusion_models/ → .safetensors
{COMFYUI_PATH}/models/ipadapter/      → .safetensors, .bin
{COMFYUI_PATH}/models/instantid/      → .bin
{COMFYUI_PATH}/models/insightface/    → .onnx + folders
{COMFYUI_PATH}/models/facerestore_models/ → .pth
{COMFYUI_PATH}/models/ultralytics/bbox/ → .pt
{COMFYUI_PATH}/custom_nodes/          → folder names = node packages
```

Normalize legacy `models/clip/` encoder files and current `models/text_encoders/`
files into the `text_encoders` inventory category while preserving each source path.

**Custom node detection**: List directories under `custom_nodes/`. Each directory name corresponds to a node package (e.g., `ComfyUI_IPAdapter_plus`, `ComfyUI-Impact-Pack`).

## Cache Format

Save results to `state/inventory.json`. The following illustrates structure only;
never copy its values into a live inventory:

```json
{
  "last_updated": "<ISO-8601 timestamp>",
  "mode": "<online-or-offline>",
  "comfyui_version": "<detected version>",
  "comfyui_path": "<resolved installation path>",
  "system": {
    "gpu": "<detected GPU>",
    "compute_cap": "<detected capability>",
    "vram_total_gb": "<detected number>",
    "vram_free_gb": "<detected number>"
  },
  "models": {
    "checkpoints": ["<installed checkpoint filename>"],
    "loras": ["<installed LoRA filename>"],
    "vae": ["<installed VAE filename>"],
    "text_encoders": ["<installed text-encoder filename>"],
    "diffusion_models": ["<installed diffusion-model filename>"]
  },
  "custom_nodes": [
    "ComfyUI-Manager",
    "ComfyUI_IPAdapter_plus",
    "ComfyUI_InstantID",
    "ComfyUI-Impact-Pack",
    "ComfyUI-AnimateDiff-Evolved",
    "ComfyUI-VideoHelperSuite"
  ]
}
```

## Workflow Validation

Given a workflow JSON, validate against inventory:

```
For each node:
  1. Check class_type against known node classes
  2. If missing: identify which custom_node package provides it
  3. Suggest install: "Install via ComfyUI-Manager: {package_name}"

For each model reference:
  1. Check filename against inventory models of that type
  2. If missing: look up in references/models.md for download link
  3. Report: "Missing: {filename} - Download from {url} -> {path}"
```

## Common Node-to-Package Mapping

| Node Class | Package |
|-----------|---------|
| ApplyInstantID | ComfyUI_InstantID |
| IPAdapterUnifiedLoader | ComfyUI_IPAdapter_plus |
| FaceDetailer | ComfyUI-Impact-Pack |
| ReactorFaceSwap | ComfyUI-ReActor |
| AnimateDiffLoaderWithContext | ComfyUI-AnimateDiff-Evolved |
| VideoHelper* | ComfyUI-VideoHelperSuite |
| ControlNetApply* | comfyui_controlnet_aux |
| UltimateSDUpscale | ComfyUI_UltimateSDUpscale |
| VHS_* | ComfyUI-VideoHelperSuite |
| RIFE* | ComfyUI-Frame-Interpolation |

## Cache Freshness

- Treat the cache as stale when its timestamp or installation path is missing, the
  ComfyUI version changed, or models/nodes changed after the recorded scan.
- For executable workflow work, refresh whenever the cache cannot be shown to match
  the active installation.
- Refresh with `scripts/scan-inventory.ps1` or a live API re-query.

## Integration

- Called by `comfyui-workflow-builder` before generating workflows
- Called by `comfyui-character-gen` (via agent wrapper) for model selection
- Called by `comfyui-troubleshooter` when diagnosing missing model errors
- Results stored in `state/inventory.json` for all skills to reference
