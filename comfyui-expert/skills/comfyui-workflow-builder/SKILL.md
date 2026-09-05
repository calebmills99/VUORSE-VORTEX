---
name: comfyui-workflow-builder
description: Generate, build, create, or design ComfyUI workflow JSON from natural language descriptions. Produces valid node graphs with correct class_types, connections, output indices, and model-appropriate settings. Handles txt2img, img2img, inpainting, ControlNet, LoRA stacking, upscaling, and face detailing pipelines. Does NOT cover ComfyUI installation, custom node development, Python scripting, model training, hardware advice, or architectural explanations.
---

# ComfyUI Workflow Builder

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Translates natural language requests into executable ComfyUI workflow JSON. Always validates against inventory before generating.

## Workflow Generation Process

### Step 1: Understand the Request

Parse the user's intent into:
- **Output type**: Image, video, or audio
- **Source material**: Text-only, reference image(s), existing video
- **Identity method**: None, zero-shot (InstantID/PuLID), LoRA, Kontext
- **Quality level**: Draft (fast iteration) vs production (maximum quality)
- **Special requirements**: ControlNet, inpainting, upscaling, lip-sync

### Step 2: Check Inventory

Read `state/inventory.json` to determine:
- Available checkpoints → select best match for task
- Available identity models → determine which methods are possible
- Available ControlNet models → enable pose/depth control if available
- Custom nodes installed → verify all required nodes exist
- VRAM available → optimize settings accordingly

### Step 3: Select Pipeline Pattern

Based on request + inventory, choose from:

| Pattern | When | Key Nodes |
|---------|------|-----------|
| Text-to-Image | Simple generation | Checkpoint → CLIP → KSampler → VAE |
| Identity-Preserved Image | Character consistency | + InstantID/PuLID/IP-Adapter |
| LoRA Character | Trained character | + LoRA Loader |
| Image-to-Video (Wan) | High-quality video | Diffusion Model → Wan I2V → Video Combine |
| Image-to-Video (AnimateDiff) | Fast video, motion control | + AnimateDiff Loader + Motion LoRAs |
| Talking Head | Character speaks | Image → Video → Voice → Lip-Sync |
| Upscale | Enhance resolution | Image → UltimateSDUpscale → Save |
| Inpainting | Edit regions | Image + Mask → Inpaint Model → KSampler |

These rows describe graph intent only. Emit no named node until its exact `class_type`,
inputs, and output indices have been confirmed through inventory or `/object_info`.

### Step 4: Generate Workflow JSON

**ComfyUI workflow format:**

```json
{
  "{node_id}": {
    "class_type": "{NodeClassName}",
    "inputs": {
      "{param_name}": "{value}",
      "{connected_param}": ["{source_node_id}", {output_index}]
    }
  }
}
```

**Rules:**
- Node IDs are strings (typically "1", "2", "3"...)
- Connected inputs use array format: `["source_node_id", output_index]`
- Output index is 0-based integer
- Filenames must match exactly what's in inventory
- Seed values: use random large integer or fixed for reproducibility

### Step 5: Validate

Before presenting to user:

1. Every `class_type` exists in inventory's node list
2. Every model filename exists in inventory's model list
3. All required connections are present (no dangling inputs)
4. VRAM estimate doesn't exceed available VRAM
5. Resolution is compatible with the exact selected model and workflow version

### Step 6: Output

**If online mode**: Queue via `comfyui-api` skill
**If offline mode**: Save JSON to `projects/{project}/workflows/` with descriptive name

## Workflow Templates

### Basic Text-to-Image (Checkpoint-Based)

Illustrative API shape only. Replace the filename and validate every node schema before
execution.

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {"ckpt_name": "<exact checkpoint filename from inventory>"}
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "{positive_prompt}", "clip": ["1", 1]}
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {"text": "{negative_prompt}", "clip": ["1", 1]}
  },
  "4": {
    "class_type": "EmptyLatentImage",
    "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
  },
  "5": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 25,
      "cfg": 3.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["4", 0]
    }
  },
  "6": {
    "class_type": "VAEDecode",
    "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
  },
  "7": {
    "class_type": "SaveImage",
    "inputs": {"filename_prefix": "output", "images": ["6", 0]}
  }
}
```

### With Identity Preservation

When inventory proves the selected identity stack is complete, extend the basic template
with its exact installed classes. Candidate stages include:
- Load reference image node
- InstantID Model Loader + Apply InstantID
- IPAdapter Unified Loader + Apply IPAdapter
- FaceDetailer post-processing

See `references/workflows.md` for complete node settings.

### Video Generation (Wan I2V)

Uses a different loader chain:
- Inventory-reported diffusion-model loader (not `CheckpointLoaderSimple`)
- Wan I2V Conditioning
- EmptySD3LatentImage (with frame count)
- Video Combine (VHS)

See `references/workflows.md` Workflow 4 for complete settings.

## VRAM Validation

Do not validate a workflow from a static VRAM table. Fit depends on the exact model
file, precision, resolution, frame count, loaded auxiliary models, node implementation,
and execution mode. Use inventory plus the hardware profile, then benchmark when the
margin is tight.

## Common Mistakes to Avoid

1. **Assumed output index**: Read the installed class schema; do not transfer indices between loaders
2. **Transferred CFG**: Derive CFG from the exact model and identity implementation
3. **Transferred resolution**: Use dimensions supported by the selected model/workflow
4. **Assumed VAE packaging**: Confirm whether the selected loader supplies a VAE or requires an explicit one
5. **Wrong model in wrong loader**: Use the exact loader class reported by inventory for the installed model type

## Reference Files

- `references/workflows.md` - Detailed node-by-node templates
- `references/models.md` - Model files and paths
- `references/prompt-templates.md` - Model-specific prompts
- `state/inventory.json` - Current inventory cache
