---
name: comfyui-lora-training
description: Prepare datasets and configure LoRA training for character consistency. Covers FLUX (AI-Toolkit, SimpleTuner, FluxGym) and SDXL (Kohya_ss) training with step-by-step guidance. Use when training custom character LoRAs.
---

# ComfyUI LoRA Training

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Guide the user through dataset preparation, training configuration, and evaluation for character LoRAs.

## When to Train vs Zero-Shot

| Scenario | Recommendation |
|----------|---------------|
| Need absolute consistency across many images | Train LoRA |
| Building a character series or ongoing project | Train LoRA |
| Quick one-off generation | Use zero-shot (InstantID/PuLID) |
| Limited references (1-5 images) | Use zero-shot |
| Testing concepts | Use zero-shot first, train if committing |

## Training Pipeline

```
1. DATASET PREP
   |-- Collect/generate 15-30 reference images
   |-- Preprocess (crop, resize, diversify styles)
   |-- Caption with trigger word + descriptions
   |
2. CONFIGURE TRAINING
   |-- Select training tool (Kohya/AI-Toolkit/FluxGym)
   |-- Set hyperparameters based on model type
   |-- Configure checkpointing
   |
3. TRAIN
   |-- Monitor loss curve
   |-- Save checkpoints every 250-500 steps
   |
4. EVALUATE
   |-- Test each checkpoint with identical prompts
   |-- Check identity accuracy, flexibility, overfitting
   |-- Select best checkpoint
   |
5. INTEGRATE
   |-- Copy to ComfyUI models/loras/
   |-- Update character profile with trigger word + strength
   |-- Test in full workflow (LoRA + identity method)
```

## Dataset Preparation

### Image Requirements

| Aspect | Minimum | Optimal | Maximum |
|--------|---------|---------|---------|
| Count | 10-15 | 20-30 | 50+ |
| Resolution | 512x512 | 1024x1024 | - |
| Format | PNG/high JPEG | PNG | - |

### Content Diversity Checklist

- [ ] Multiple angles (front, 3/4, profile, back)
- [ ] Various expressions (neutral, smile, serious, laugh, etc.)
- [ ] Different lighting conditions (studio, natural, dramatic)
- [ ] Varied backgrounds (or transparent/solid)
- [ ] Multiple outfits/contexts
- [ ] Some close-ups, some medium shots
- [ ] If from 3D renders: include style variations (see below)

### Preprocessing 3D Renders

**Problem**: Training directly on 3D renders bakes in the "3D" aesthetic.

**Solution**: Generate style variations first:
1. Run each render through img2img with varied style prompts
2. Mix: 60% style variations, 40% original renders
3. This teaches identity, not style

Style prompts for variation:
```
"photorealistic portrait, dslr photo"
"oil painting portrait"
"digital illustration"
"pencil sketch"
"watercolor portrait"
```

### Captioning Rules

**Trigger word**: ALWAYS use a unique token as first word.
- Good: `char_token`, `ohwx_person`, `sks_subject`
- Bad: `woman`, `redhead`, `character` (too generic)

**Caption structure:**
```
{trigger}, {subject type}, {clothing}, {pose}, {setting}, {lighting}, {style}
```

**DO NOT describe face features** (let the model learn them):
- Bad: "person with a detailed physical description but no unique trigger token"
- Good: "char_token, person, indoor portrait, wearing blue sweater"

**DO describe everything else**: clothing, pose, background, lighting, expression.

### Folder Structure

```
dataset/{character_name}/{repeats}_{trigger_word}/
  001.png + 001.txt
  002.png + 002.txt
  ...
```

Folder naming: `10_char_token` = each image repeated 10x per epoch.

## Training Configurations

Before emitting a configuration, identify the exact trainer, trainer version, base model,
dataset shape, and supported precision. The fragments below are schematic starting
profiles; validate every key against that trainer version.

### FLUX LoRA (AI-Toolkit Family)

```yaml
network:
  type: lora
  linear: "{chosen_rank}"
  linear_alpha: "{chosen_alpha}"

train:
  batch_size: 1
  gradient_accumulation_steps: 4
  steps: "{chosen_steps}"
  lr: "{chosen_learning_rate}"
  optimizer: "{trainer-supported_optimizer}"
  dtype: "{hardware-supported_precision}"

datasets:
  - resolution: [1024]
    caption_ext: "txt"

sample:
  sample_every: 250
  prompts:
    - "{trigger}, photorealistic portrait"
```

Use sample checkpoints to detect convergence and overfitting. Do not infer step count or
VRAM fit from the model family alone.

### SDXL LoRA (Kohya_ss Family)

```yaml
pretrained_model: "{exact inventory-verified checkpoint}"
network_dim: "{chosen_rank}"
network_alpha: "{chosen_alpha}"
resolution: "1024,1024"
train_batch_size: 1
gradient_accumulation_steps: 4
learning_rate: "{chosen_learning_rate}"
lr_scheduler: "cosine_with_restarts"
lr_scheduler_num_cycles: 3
max_train_epochs: "{chosen_epochs}"
optimizer_type: "{trainer-supported-optimizer}"
mixed_precision: "{hardware-supported-precision}"
enable_bucket: true
min_snr_gamma: 5
```

**Step calculation:**
```
total_steps = (images x repeats x epochs) / batch_size
Choose the target from dataset size, repeats, validation samples, and approved hyperparameters.
```

### Memory-Constrained Training (FluxGym / SimpleTuner)

Use only keys supported by the selected trainer version and precision supported by the
hardware profile:
```yaml
use_8bit_adam: true
gradient_checkpointing: true
cache_latents_to_disk: true
max_data_loader_n_workers: 0
train_batch_size: 1
gradient_accumulation_steps: 8
quantize_base_model: nf4    # SimpleTuner only
```

## Evaluation Protocol

### Test Each Checkpoint

Use identical prompts across all checkpoints:

```
Prompt 1: "{trigger}, photorealistic portrait, neutral expression"
Prompt 2: "{trigger}, photorealistic portrait, smiling, outdoor"
Prompt 3: "{trigger}, wearing formal suit, standing, office"
Prompt 4: "a person standing in a park"  (WITHOUT trigger - should NOT produce character)
```

### Quality Indicators

**Good training:**
- Character recognizable from trigger word alone
- Responds to different prompts/contexts
- Doesn't always produce same pose/expression
- Prompt 4 does NOT produce the character

**Overfitting signs:**
- Same exact pose/expression regardless of prompt
- Training backgrounds appearing in outputs
- Ignores clothing/setting prompts
- Prompt 4 produces the character (too strong)

### Best Epoch Selection

If using sample_every: 250 with 1500 steps:
- Checkpoint 250: Usually underfit
- Checkpoint 500-750: Often sweet spot for FLUX
- Checkpoint 1000-1500: May be overfitting

Compare visually and select the checkpoint with best identity + prompt flexibility balance.

## Post-Training Integration

1. Copy the selected checkpoint to `{COMFYUI_PATH}/models/loras/`
2. Update character profile:
   ```yaml
   lora:
     trained: true
     model_file: "character_lora.safetensors"
     trigger_word: "char_token"
     best_strength: null  # Fill from the evaluation result
   ```
3. Test in the full workflow; add a second identity method only when its complete stack is inventoried
4. Record successful settings in character's `generation_history`

## Combining LoRA with Zero-Shot Methods

Treat a second identity method as an experiment, not a universal enhancement.

```
[Load Checkpoint] → [Load LoRA (measured weight)] → [Optional installed identity method] → [Generate]
```

Record the measured interaction and retain the simpler stack when the second method does not improve identity.

## Troubleshooting

| Issue | Solution |
|-------|---------|
| LoRA not activating | Check trigger word spelling, ensure loaded before KSampler |
| Identity drift at angles | Add more angle variety to dataset, reduce network_dim |
| Overfitting | Reduce epochs, increase dataset, lower network_dim |
| Style contamination | Better caption diversity, don't describe style in captions |
| Poor quality/artifacts | Check training images for compression, reduce LR |

## Reference

- `references/lora-training.md` - Full parameter reference
- `references/models.md` - Training tool download links
- Character profiles in `projects/` for trigger words and reference images
