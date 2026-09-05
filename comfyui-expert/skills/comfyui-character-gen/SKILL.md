---
name: comfyui-character-gen
description: Build identity-preserving character generation workflows and pipelines in ComfyUI. Selects the optimal identity method (InfiniteYou, FLUX Kontext, PuLID, InstantID, IP-Adapter) based on use case requirements. Handles face preservation, likeness transfer, cross-domain conversion (3D to photo), multi-reference consistency, iterative character editing, and character variation generation. Triggers on requests to generate consistent characters, preserve identity across images, create face-swapping workflows, or convert 3D renders to photorealistic portraits. Does NOT cover general image generation without identity preservation, model training/LoRA fine-tuning, animation, technical explanations, or workflow debugging.
---

# ComfyUI Character Generation Expert

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Build production-ready ComfyUI workflows for consistent character generation across image, video, and voice modalities.

## Capability Gate

1. Read inventory and the hardware profile.
2. Treat an identity method as available only when both its node classes and companion
   models are present.
3. Select exact filenames and node schemas from inventory; never infer availability
   from a method name in this document.
4. If the complete stack is absent, name the missing dependency instead of routing to it.

## Quick Decision: Which Approach?

**Starting from reference images (like 3D renders)?**
→ Compare only complete, inventory-verified identity stacks

**Need highest identity fidelity?**
→ Compare inventory-verified multi-reference and identity-conditioning candidates

**Want iterative editing without retraining?**
→ Use an installed context-editing model if its required integration is present

**Creating video content?**
→ Compare installed LTX, Wan 2.2, FramePack, and AnimateDiff paths against the target

**Need voice for character?**
→ Route to `comfyui-voice-pipeline` and select only an available local or configured API path

## Core Workflow Patterns

### Pattern 1: Zero-Shot Character Generation (No Training)

Best for: Quick iteration, 3D-to-photorealism conversion, limited reference images

```
Load Reference Face → InstantID + IP-Adapter FaceID → ControlNet Pose → KSampler → FaceDetailer → Upscale
```

**Settings rule:** Derive CFG, resolution, identity weight, and conditioning options
from the exact installed model and node version. Values in older workflows are test
starting points, not universal defaults.

See `references/workflows.md` for complete node configurations.

### Pattern 2: LoRA + Identity Methods (Maximum Consistency)

Best for: Production work, character series, video generation base

```
Train LoRA → Load LoRA + Checkpoint → Add InstantID/PuLID → Generate → FaceDetailer → ReActor (optional) → Upscale
```

**Training handoff:** Route dataset size, captions, trigger token, trainer version, and
hyperparameters to `comfyui-lora-training`.

### Pattern 3: Video Generation Pipeline

Best for: Talking heads, character animation, promotional content

```
Generate/Load Hero Image → Wan 2.2 I2V OR AnimateDiff → FaceDetailer per frame → Frame Interpolation → Video Combine
```

**Model selection:** Route the identity-approved hero image and project constraints to
`comfyui-video-pipeline`; that skill owns the inventory-conditioned video choice.

### Pattern 4: Talking Head with Voice

Best for: Character dialogue, presentations, social content

**Two approaches available:**

```
Approach 1 (Image → Talking Head):
Character Portrait → Available Audio Path → Inventory-Verified Animation/Lip-Sync → Final Video

Approach 2 (Video → Add Voice):
Existing Video → Available Audio Path → Inventory-Verified Lip-Sync → Final Video
```

See `references/talking-head-workflows.md` for complete workflows and `references/voice-synthesis.md` for voice creation options.

## Candidate Identity Methods

| Goal | Candidate families | Completeness test |
|------|--------------------|-------------------|
| Reference-conditioned identity | InstantID, IP-Adapter FaceID, PuLID, InfiniteYou | Required nodes, encoders, and companion models all appear in inventory |
| Context-aware editing | Installed Kontext-style editor | Exact model and loader schema are present |
| Trained identity | LoRA plus compatible base model | LoRA, base checkpoint, and loader are present |
| Post-generation face repair | FaceDetailer or face-restore path | Detector, restoration model, and node classes are present |

Video choice belongs to `comfyui-video-pipeline`; voice choice belongs to
`comfyui-voice-pipeline`; training choice belongs to `comfyui-lora-training`.

## Candidate Custom Nodes

This is a dependency lookup list, not an installation bundle. Require only packages
needed by the selected method, and verify the corresponding models separately.

```
ComfyUI-Manager              # Must install first
ComfyUI_IPAdapter_plus       # IP-Adapter and FaceID
ComfyUI_InstantID            # InstantID workflow
ComfyUI-Impact-Pack          # FaceDetailer
ComfyUI-ReActor              # Face swapping
ComfyUI-AnimateDiff-Evolved  # Video generation
ComfyUI-VideoHelperSuite     # Video I/O
comfyui_controlnet_aux       # Pose/depth preprocessors
ComfyUI_UltimateSDUpscale    # Tiled upscaling
ComfyUI-Frame-Interpolation  # Smooth video
```

## Hardware-Conditioned Optimization

Use the active launcher and precision guidance from `foundation/hardware-profile.md`.
Change flags only for the exact model and measured headroom; this skill does not carry
a second hardware profile.

## Workflow Generation Process

When building a workflow for a user:

1. **Clarify the goal**: Image only? Video? With voice? What's the source material?

2. **Select the pipeline pattern** from above based on requirements

3. **Generate the workflow** following node configurations in `references/workflows.md`

4. **Include model downloads** with exact filenames and paths from `references/models.md`

5. **Provide parameter recommendations** specific to their hardware/use case

## Reference Files

- `references/research-2025.md` - Historical research snapshot; never treat it as current capability
- `references/models.md` - Complete model list with HuggingFace/Civitai links, file paths, and compatibility notes
- `references/workflows.md` - Detailed node-by-node workflow templates for each pattern
- `references/lora-training.md` - LoRA training guide with Kohya/AI-Toolkit parameters
- `references/voice-synthesis.md` - Voice cloning, TTS, and lip-sync pipeline details
- `references/talking-head-workflows.md` - Candidate talking-head patterns requiring inventory validation
- `references/evolution.md` - Historical update sources and correction log

## Skill Evolution

This skill is designed to evolve. When helping the user:

**Before starting a workflow:**
- Check if new models have dropped that might be better (search HuggingFace/Civitai if uncertain)
- Consider if user's past successes/failures inform the approach

**After completing a workflow:**
- Note what worked well or poorly for future reference
- If user discovers better settings, update the relevant reference file

**Proactive updates:**
- When the user mentions a new model or technique, research and integrate it
- Periodically suggest checking for updates to key dependencies

See `references/evolution.md` for monitoring sources and update protocols.

## Example: 3D Render to Photorealistic Character

For converting stylized 3D renders (like game/VN characters) to photorealistic images:

**Recommended approach:** InstantID + IP-Adapter FaceID on FLUX

```
1. Load 3D render reference (best quality, front-facing)
2. Apply InstantID (extracts identity + facial keypoints)
3. Apply IP-Adapter FaceID Plus V2 (weight 0.7)
4. Use FLUX.1-dev checkpoint
5. Prompt: "photorealistic portrait, detailed skin texture, natural lighting, [character description]"
6. CFG: 4-5, Steps: 25-30
7. FaceDetailer pass (denoise 0.35)
8. Upscale with 4x-UltraSharp
```

This converts the stylized look to photorealism while preserving the core identity features.
