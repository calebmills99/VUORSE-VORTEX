---
name: comfyui-video-pipeline
description: Design or execute a single-shot ComfyUI video path using inventory-verified engines. Handle image-to-video, text-to-video, talking heads, and motion-controlled clips. Use for one clip or one shot; route multi-shot, batch, retry, and project orchestration to comfyui-video-production.
---

# ComfyUI Video Pipeline

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Orchestrates video generation across inventory-verified engines. The names below are
selection candidates, not claims that an engine or node is installed.

## Engine Selection

```
VIDEO REQUEST
    |
    |-- Need maximum local quality?
    |   |-- Wan 2.2 A14B/MoE installed and verified to fit? → Use it
    |   |-- Smaller Wan 2.2 TI2V 5B installed and verified to fit? → Use it
    |
    |-- Need long-form generation?
    |   |-- FramePack installed and compatible? → Benchmark it on this machine
    |
    |-- Need fast iteration?
    |   |-- Yes + compatible AnimateDiff stack installed → Benchmark the installed variant
    |
    |-- Need camera/motion control?
    |   |-- Yes + compatible motion modules installed → Select from inventory
    |
    |-- Need first+last frame control?
    |   |-- Yes → Select an installed workflow that exposes both inputs
    |
    |-- Default → Highest-quality inventory-verified engine that fits
```

## Pipeline 1: Wan 2.2

### Image-to-Video

**Prerequisites:**
- Exact compatible Wan 2.2 diffusion-model filename from inventory
- Exact compatible text encoder from `models/text_encoders/`
- Exact compatible vision encoder and VAE from inventory
- Installed node classes matching the selected upstream workflow

**Settings rule:** Read supported dimensions, frame-count constraints, conditioning mode,
steps, CFG, sampler, scheduler, and output FPS from the selected model/workflow version.
Calculate duration from that verified FPS; do not transplant a static Wan settings table.

**VRAM optimization:**
- Use only precision modes supported by the hardware profile and installed model
- Use SageAttention only when the installed torch/CUDA/node stack supports it
- Reduce frames if OOM

### Text-to-Video

Select a T2V-capable model and latent node from inventory. Do not substitute an I2V
filename or invent a loader class from display-name memory.

### First+Last Frame Control

When the installed workflow exposes both first- and last-frame inputs:
1. Generate two hero images with consistent character
2. Use first as start frame, second as end frame
3. Wan interpolates the motion between them

## Pipeline 2: FramePack (Long-Form Candidate)

### Selection Rule

Treat FramePack's memory-efficiency claims as upstream capability claims, not a local
guarantee. Verify the installed implementation, model, resolution, and runtime here.

### Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | Installed workflow's supported range | Validate against measured headroom |
| Duration | Set from the installed workflow's supported range | Benchmark before batch work |
| Quality | Validate against the chosen local baseline | Do not infer from model family |

### When to Use

- Sequences longer than the selected single-clip path handles cleanly
- Limited VRAM systems (check hardware-profile.md before assuming you have headroom)
- When VRAM is needed for parallel operations
- Batch video generation

## Pipeline 3: AnimateDiff Candidate

### Capability Check

- Verify the base checkpoint, motion module, loader classes, and any motion/effect LoRAs
- Verify that every component targets the same base-model family
- Derive steps, CFG, sampler, resolution, context length, and overlap from the installed workflow version

Do not emit remembered motion-module or LoRA filenames. Use exact inventory entries.

## Post-Processing Pipeline

After any video generation:

### 1. Frame Interpolation (RIFE)

Doubles or quadruples frame count for smoother motion:
```
Input (16fps) → RIFE 2x → Output (32fps)
Input (16fps) → RIFE 4x → Output (64fps)
```

Use only the interpolation model and node class shown in inventory.

### 2. Face Enhancement (if character video)

Apply a face-detailing pass only when its node, detector, and restoration model are all
inventoried. Derive denoise and guide size from a short temporal-consistency test.

### 3. Deflicker (if needed)

Reduces temporal inconsistencies between frames.

### 4. Color Correction

Maintain consistent color grading across frames.

### 5. Video Combine

Use an inventoried video-combine node or hand frames to `video-assembly`. Match frame
rate, codec, and quality settings to the active delivery target.

## Talking Head Pipeline

Complete pipeline for character dialogue:

```
1. Generate audio → comfyui-voice-pipeline
2. Generate base video → This skill (Wan I2V or AnimateDiff)
   - Prompt: "{character}, talking naturally, slight head movement"
   - Duration: match audio length
3. Apply lip-sync → Wav2Lip or LatentSync
4. Enhance faces → FaceDetailer + CodeFormer
5. Final output → video-assembly
```

## Quality Checklist

Before marking video as complete:
- [ ] Character identity consistent across frames
- [ ] No flickering or temporal artifacts
- [ ] Motion looks natural (not jerky or frozen)
- [ ] Face enhancement applied if character video
- [ ] Frame rate is smooth (24+ fps for delivery)
- [ ] Audio synced (if talking head)
- [ ] Resolution matches delivery target

## Reference

- `references/workflows.md` - Workflow templates for Wan and AnimateDiff
- `references/models.md` - Video model download links
- `references/research-log.md` - Latest video generation advances
- `state/inventory.json` - Available video models
