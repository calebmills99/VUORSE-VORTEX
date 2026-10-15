---
name: comfyui-video-production
description: Plan and orchestrate multi-shot, batch, or project-scale ComfyUI video production with validation gates, retries, and state continuity. Use when coordinating several clips, keyframes, fallback paths, or production stages. Route a single clip to comfyui-video-pipeline and final editing or concatenation to video-assembly.
---

# ComfyUI Video Production Pipeline

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

End-to-end video production orchestration for ComfyUI with explicit validation,
evidence-based fallback paths, and optional instance-management patterns.

## Quick Start: Which Pipeline?

**Creating a multi-shot narrative video?**
→ **Keyframe Pipeline** - Generate keyframes → Animate → Stitch with transitions

**Animating existing images?**
→ **I2V Batch Pipeline** - Load images → Queue I2V jobs → Auto-validate → Combine

**Need smooth transitions between scenes?**
→ **Transition Pipeline** - Crossfades, motion blur, zoom effects via FFmpeg

**ComfyUI stuck or crashed?**
→ **Instance Management Pattern** - Health evidence and recovery planning when implemented

**Debugging video issues?**
→ **Validation Suite** - Check resolution, FPS, codec, face consistency, color grading

---

## Core Pipelines

### Pipeline 1: Keyframe-to-Video (Complete Narrative)

**Use when:** Creating story-driven videos with multiple distinct shots

```
1. Keyframe Generation Phase
   - Generate consistent keyframes with IP-Adapter/LoRA
   - Validate face consistency, lighting, pose progression
   - Save to organized directory structure
   - Auto-retry failed generations

2. I2V Animation Phase
   - Queue each keyframe to I2V model (Wan 2.2, LTX-2, AnimateDiff)
   - Monitor progress via ComfyUI API
   - Validate each clip (resolution, fps, duration)
   - Auto-retry with different seeds if failed

3. Concatenation Phase
   - Pre-flight validation (ensure all clips match)
   - Apply transition effects (crossfade, motion blur)
   - FFmpeg encoding with proper codec
   - Export final video with metadata

4. Quality Assurance
   - Face consistency check across clips
   - Color grading consistency
   - Audio sync validation (if applicable)
   - Generate QA report
```

**Expected output:** Single cohesive video with smooth transitions

---

### Pipeline 2: Batch I2V Processing

**Use when:** You have multiple images to animate independently

```
1. Image Discovery
   - Scan directory for source images
   - Validate image specs (resolution, format)
   - Generate processing manifest

2. Parallel I2V Queue
   - Queue all images to ComfyUI with appropriate prompts
   - Stagger submissions to avoid overload
   - Monitor queue depth and ETA

3. Progressive Validation
   - Check each completed video immediately
   - Flag issues (wrong resolution, fps, corruption)
   - Auto-retry flagged videos

4. Export & Organize
   - Move validated videos to output directory
   - Generate index with metadata
   - Create contact sheet (thumbnail preview grid)
```

**Expected output:** Directory of validated animated clips

---

### Pipeline 3: Assembly Handoff

After clip validation, pass ordered clips, timing, audio, and delivery requirements to
`video-assembly`. This skill owns production orchestration; it does not duplicate the
FFmpeg editing workflow.

---

## Model Selection Candidates

### Image-to-Video Models

| Candidate | Select only when |
|-----------|------------------|
| LTX family | The exact installed variant supports the requested resolution and features |
| Wan 2.2 A14B/MoE | Inventory and hardware validation show the exact files and precision fit |
| Wan 2.2 TI2V 5B | The installed workflow supports the requested conditioning mode |
| AnimateDiff | Required motion modules and node classes are inventoried |
| SVD | The installed checkpoint and requested clip constraints match |

---

## Optional Instance Management

Use instance-management patterns only when session state identifies the actual endpoints
and an implementation exists to perform them. Observe queue, process, disk, and VRAM
evidence before classifying a stall. Never describe restart, failover, queue restoration,
or load balancing as automatic merely because this document names the pattern.

---

## Validation Suite

### Pre-Generation Validation

```python
✓ Check ComfyUI is running and responsive
✓ Verify every model and node required by the selected workflow
✓ Confirm output directory has sufficient space
✓ Validate source images exist and are readable
✓ Check prompts are non-empty and formatted correctly
✓ Verify workflow JSON is valid
```

### Post-Generation Validation

```python
✓ Video file exists and is non-zero size
✓ Resolution, FPS, and duration match the active project specification
✓ Codec is compatible (h264, h265)
✓ No corruption (can read all frames)
✓ Project-defined identity and color checks pass when their validators are available
```

### Quality Metrics

```python
Optional metrics, when an implementation is available:
- Face embedding distance (identity consistency)
- Optical flow magnitude (motion smoothness)
- Frame PSNR/SSIM (interpolation quality)
- Color histogram deviation (lighting consistency)
- Audio sync offset (if audio present)
```

---

## Error Handling & Recovery

### Retry Strategies

```python
1. Seed Randomization Retry
   - Failed generation? Try different seed
   - Max 3 attempts per keyframe
   - Track seeds that fail (avoid reuse)

2. Parameter Adjustment Retry
   - CFG too high causing artifacts? Lower it
   - Steps too low causing incompleteness? Increase
   - Resolution too high OOM? Downscale

3. Model Fallback Retry
   - Wan 2.2 A14B OOM? Fall back to an inventory-verified smaller engine
   - LTX-2 unavailable? Fall back to an inventory-verified Wan 2.2 variant
   - AnimateDiff motion broken? Switch motion LoRA

4. Checkpoint Resume
   - Save progress after each successful clip
   - Resume from last successful checkpoint
   - Skip already-generated clips
```

### Failure Logging

```python
logs/
├── 2026-02-16_pipeline.log       # Main pipeline log
├── 2026-02-16_comfyui.log        # ComfyUI stdout/stderr
├── 2026-02-16_validation.json    # Validation results
├── 2026-02-16_failures.json      # Failed attempts with reasons
└── 2026-02-16_recovery.json      # Recovery actions taken
```

---

## Directory Structure

### Organized Output

```
project_name/
├── 00_keyframes/                 # Source keyframe images
│   ├── kf01_scene_description.png
│   ├── kf02_scene_description.png
│   └── ...
├── 01_clips/                     # Individual animated clips
│   ├── clip_001_kf01.mp4
│   ├── clip_002_kf02.mp4
│   └── ...
├── 02_validated/                 # Clips that passed validation
│   ├── clip_001_kf01.mp4
│   ├── clip_002_kf02.mp4
│   └── ...
├── 03_transitions/               # Intermediate files for transitions
│   ├── transition_001_002.mp4
│   └── ...
├── 04_final/                     # Final combined video
│   ├── final_video_v1.mp4
│   ├── final_video_v2.mp4        # After revisions
│   └── ...
├── logs/                         # Execution logs
├── metadata/                     # JSON metadata for each asset
└── manifest.json                 # Complete project manifest
```

---

## Workflow Examples

### Example 1: 30-Second Narrative Video (5 keyframes)

```python
# Configuration
project_name = "character_intro"
keyframes = 5
i2v_model = "wan_2.2_moe"
target_duration = 30  # seconds
fps = 16

# Pipeline execution
1. Generate 5 keyframes (IP-Adapter + LoRA)
   → kf01_over_shoulder.png
   → kf02_turning.png
   → kf03_coat_removed.png
   → kf04_seated.png
   → kf05_close_up.png

2. Validate keyframes
   → Face consistency: 0.92 ✓
   → Lighting consistency: 0.88 ✓
   → Pose progression: logical ✓

3. Queue I2V for each keyframe
   → clip_001: 6s @ 16fps (96 frames) ✓
   → clip_002: 6s @ 16fps (96 frames) ✓
   → clip_003: 6s @ 16fps (96 frames) ✓
   → clip_004: 6s @ 16fps (96 frames) ✓
   → clip_005: 6s @ 16fps (96 frames) ✓

4. Apply 0.5s crossfade transitions
   → Total: 30s - 2s (4 transitions × 0.5s) = 28s net

5. Export final video
   → character_intro_final.mp4 (30s, 768x1024, 16fps)
```

### Example 2: Batch Process 20 Images

```python
# Configuration
input_dir = "{COMFYUI_PATH}/input/character_expressions"
i2v_model = "ltx_2"
motion_prompt = "gentle breathing, subtle movement, natural"
batch_size = 4  # Process 4 at a time

# Pipeline execution
1. Scan input directory
   → Found 20 PNG files

2. Queue 4 at a time to ComfyUI
   → Batch 1: expr_001.png → expr_004.png ✓
   → Batch 2: expr_005.png → expr_008.png ✓
   → Batch 3: expr_009.png → expr_012.png ✓
   → Batch 4: expr_013.png → expr_016.png ✓
   → Batch 5: expr_017.png → expr_020.png ✓

3. Validate each output
   → 19/20 passed (expr_011 failed - wrong resolution)
   → Retry expr_011 with corrected settings ✓

4. Export batch
   → 20 validated clips in output/expressions/
   → Generated contact sheet: expressions_preview.png
```

---

## Reference Files

### Detailed Guides

- `references/concatenation.md` - FFmpeg commands, transition effects, audio handling
- `references/instance-management.md` - ComfyUI health checks, restart scripts, multi-instance setup
- `references/api-reference.md` - ComfyUI API endpoints, queue management, workflow submission
- `references/workflows.md` - Mirrored shared workflow guidance
- `references/troubleshooting.md` - Mirrored shared error guidance

---

## Integration with Other Skills

**Pair with:**
- `comfyui-character-gen` - For generating initial keyframes with identity preservation
- `video-assembly` - For advanced editing and post-production
- `video-publisher` - For a validated publishing handoff

---

## Advanced Features

### Adaptive Quality

```python
# Pseudocode: select only models that inventory proves are installed and compatible
if inventory_has("wan_2.2_a14b") and model_fits("wan_2.2_a14b", hardware):
    use_model = "wan_2.2_moe_14b"
    resolution = (832, 1216)
    batch_size = 1
elif inventory_has("wan_2.2_ti2v_5b") and model_fits("wan_2.2_ti2v_5b", hardware):
    use_model = "wan_2.2_ti2v_5b"
    resolution = (768, 1024)
    batch_size = 1
else:
    use_model = select_inventory_verified_fallback()
    resolution = (512, 768)
    batch_size = 1
```

### Progress and Versioning

Report only progress exposed by the active API or runner. Version outputs through the
project manifest; do not imply rollback automation exists without an implementation.

---

## Workflow Generation

When asked to create a video production workflow:

1. **Assess Requirements**
   - Number of shots/keyframes
   - Target duration per shot
   - I2V model preference
   - Transition style
   - Quality vs speed tradeoff

2. **Generate Pipeline Config**
   - Model selection based on VRAM/quality needs
   - Resolution and FPS settings
   - Validation thresholds
   - Retry policies

3. **Provide Execution Scripts**
   - Python scripts for API submission
   - Assembly handoff for `video-assembly`
   - Validation checks
   - Recovery procedures

4. **Monitor & Adapt When Executing Live**
   - Track only progress exposed by the active API
   - Detect failures early
   - Apply recovery strategies
   - Report final metrics

---

## Best Practices

### For Keyframe Videos
- Reuse seeds or conditioning only when tests show they improve this character
- Derive identity weights and clip duration from the installed model and project tests
- Validate keyframes before I2V
- Pass transition choices to `video-assembly`

### For Batch Processing
- Size batches from measured headroom
- Validate immediately after each batch
- Save checkpoint after each successful batch
- Use priority queue for important clips

### For Instance Management
- Resolve actual endpoints and process ownership from session state
- Treat a timeout as evidence to diagnose, not permission to restart
- Log any recovery action that actually occurs

---

## Performance Optimization

### Hardware-Conditioned Execution

Read `foundation/hardware-profile.md` and `state/inventory.json`, then select only
precision modes and launch flags supported by that GPU, torch build, and ComfyUI
version. Benchmark the exact model, resolution, frame count, and node graph locally;
static timing claims are not execution evidence.

### AMD GPUs (ROCm)

Use the current upstream installation path for the detected platform and verify the
installed torch/ROCm build before choosing flags.

---

## Skill Evolution

This skill adapts to new I2V models and techniques. When new models release:
1. Add verified model guidance to canonical root `references/workflows.md`, then mirror it
2. Update model selection logic only after inventory and version validation
3. Test with a representative project
4. Record measured performance characteristics

See `references/evolution.md` for update protocol.
