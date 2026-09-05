# Model Reference Guide

Per-model specifications: download links, file paths, required companions, VRAM.

<!-- Updated: 2026-08-26 | Verified against state/inventory.json and publisher HuggingFace pages -->

**Legend** — status is against this machine's `state/inventory.json`:

| Mark | Meaning |
|:----:|---------|
| ✅ | Installed and usable |
| ⚠️ | Installed but blocked (missing companion, or needs a ComfyUI upgrade) |
| ❌ | Not installed |

Hardware ceiling: **RTX 5000 Ada, 30 GB, compute 8.9, torch cu128.** No NVFP4.
ComfyUI installed: **v0.28.0** (current is v0.33.4).

---

## Directory Structure

Modern ComfyUI layout, as it exists on this machine:

```
{COMFYUI_PATH}\models\
├── checkpoints/           # All-in-one checkpoints (SDXL, SD1.5, FLUX fp8)
├── diffusion_models/      # UNET-only weights — need a separate encoder + VAE
├── unet/                  # Legacy UNET location; GGUF often lands here
├── loras/                 # LoRA adapters
├── vae/                   # VAE decoders
├── text_encoders/         # T5, UMT5, Qwen, Gemma  ← NOT models/clip
├── clip_vision/           # CLIP/SigLIP vision encoders
├── controlnet/            # ControlNet models                      [EMPTY]
├── ipadapter/             # IP-Adapter models                      [EMPTY]
├── instantid/             # InstantID ip-adapter.bin               [absent]
├── insightface/           # Face analysis (antelopev2)             [absent]
├── ultralytics/bbox/      # FaceDetailer detection models          [absent]
├── upscale_models/        # ESRGAN-family upscalers
├── latent_upscale_models/ # LTX spatial upscalers
├── model_patches/         # ControlNet-Union style patches
├── sams/                  # Segment Anything
├── SEEDVR2/ FlashVSR/     # Node-pack-specific model dirs
└── LLM/                   # VLM / captioning models
```

> **Do not put text encoders in `models/clip/`.** Modern ComfyUI reads them from
> `models/text_encoders/`; the older guidance in pre-2026 tutorials is wrong and the
> loaders will simply not see the file. `models/clip` is empty here and should stay that way.

---

## Companion-File Matrix

UNET-only weights in `diffusion_models/` will not run alone. This is the pairing table
for what is installed:

| Diffusion model | Text encoder | VAE | Status |
|-----------------|--------------|-----|:------:|
| `flux-2-klein-9b-fp8.safetensors` | `qwen_3_8b_fp8mixed.safetensors` | `flux2-vae.safetensors` | ✅ complete |
| `flux-2-klein-base-9b-fp8.safetensors` | `qwen_3_8b_fp8mixed.safetensors` | `flux2-vae.safetensors` | ✅ complete |
| `z_image_turbo_bf16.safetensors` | `qwen_3_4b.safetensors` | `qwen_image_vae.safetensors` | ✅ complete |
| `qwen_image_2512_bf16.safetensors` | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | `qwen_image_vae.safetensors` | ⚠️ 38 GB > 30 GB VRAM — needs offload or a GGUF quant |
| `qwen_image_edit_2511_bf16.safetensors` | `qwen_2.5_vl_7b_fp8_scaled.safetensors` | `qwen_image_vae.safetensors` | ⚠️ same, 38 GB |
| `wan2.2_i2v_high/low_noise_14B_fp8_scaled` | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `wan2.2_vae.safetensors` | ✅ complete |
| `wan2.2_ti2v_5B_fp16.safetensors` | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `wan2.2_vae.safetensors` | ✅ complete |
| `acestep_v1.5_xl_turbo_bf16.safetensors` | `qwen_4b_ace15` / `qwen_0.6b_ace15` | `ace_1.5_vae.safetensors` | ✅ complete |

> **FLUX.2 VAE is not interchangeable.** Using the FLUX.1 `ae.safetensors` or an SDXL VAE
> with a Klein model produces heavily distorted colour. Always pair Klein with `flux2-vae`.

---

## Image Checkpoints

### FLUX.2 [klein] 9B ✅
- **Download**: https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-9b (companions)
- **Path**: `models/diffusion_models/`
- **VRAM**: ~8.8 GB (fp8) / ~16.9 GB (bf16)
- **Installed**: `flux-2-klein-9b-fp8.safetensors`, `flux-2-klein-base-9b-fp8.safetensors`, `flux-2-klein-9b.safetensors` (bf16)
- **Notes**: fp8 is the right variant for this card. `base` is the non-distilled variant —
  higher ceiling, more steps. Docs: https://docs.comfy.org/tutorials/flux/flux-2-klein

### FLUX.1-dev (fp8) ✅
- **Download**: https://huggingface.co/black-forest-labs/FLUX.1-dev
- **Path**: `models/checkpoints/` (the fp8 all-in-one bundles its encoders)
- **VRAM**: 16 GB+ (fp16), ~10 GB (fp8)
- **Installed**: `flux1-dev-fp8.safetensors` (16.1 GB)
- **Notes**: If you ever load the *split* FLUX.1 weights you additionally need
  `t5xxl_fp16` ✅ and `clip_l.safetensors` ❌ (not installed) plus `ae.safetensors` ✅.

### Z-Image Turbo ✅
- **Path**: `models/diffusion_models/`
- **VRAM**: ~11.5 GB (bf16)
- **Installed**: Resolve exact checkpoint, LoRA, and model-patch filenames from
  `state/inventory.json`; private filenames are not mirrored into this reference.
- **Notes**: 8-step turbo. Best throughput-per-watt in the lineup. The Controlnet-Union
  patch is the *only* ControlNet-equivalent on this machine.

### Z-Image Turbo NVFP4 ❌ (delete)
- **Installed**: `z_image_turbo_nvfp4.safetensors` (4.2 GB)
- **Status**: **Unusable on this GPU.** NVFP4 requires Blackwell (compute 12.x) + cu130.
  This box is 8.9 / cu128. Reclaim the 4.2 GB.

### Qwen-Image 2512 / Qwen-Image-Edit 2511 ⚠️
- **Download**: https://github.com/QwenLM/Qwen-Image
- **GGUF quants**: https://huggingface.co/city96/Qwen-Image-gguf ← **recommended here**
- **Path**: `models/diffusion_models/`
- **VRAM**: 38 GB bf16 (does not fit); ~8 GB in GGUF
- **Installed**: both bf16 files (38 GB each), plus `qwnImageEdit_v16Fp8Scaled` (19.1 GB,
  checkpoints) which *does* fit
- **Notes**: Best-in-class text rendering, incl. Chinese/Arabic. **Qwen-Image 3.0 is native
  from ComfyUI v0.32.0** — blocked until upgrade. The two bf16 files are 76 GB of weights
  you cannot load without heavy offloading; the fp8-scaled edit model is the practical one.

### SDXL Family ✅
- **Installed**: `RealVisXL_V5.0_fp16`, `Juggernaut-XL_v9_RunDiffusionPhoto_v2`,
  `juggernautXL_ragnarokBy`, `photorealisticAllPurpose_v40`, plus several Pony/Illustrious
  and adult-content finetunes
- **VRAM**: 8 GB+ — trivially comfortable at 30 GB, batch 4 at 1024×1024
- **Notes**: Every identity-preservation method below targets SDXL. These are your base
  models the moment the identity models are installed.

### SD 1.5 ✅
- **Installed**: `v1-5-pruned-emaonly-fp16`, `epicrealism_pureEvolutionV5-inpainting`
- **Notes**: Keep for inpainting and legacy ControlNet workflows.

---

## Identity Preservation — ALL MISSING ❌

> **This is the single largest gap on the machine.** `comfyui_ipadapter_plus` is installed
> and will throw at runtime because `models/ipadapter` is empty. No InstantID, no
> InsightFace, no PuLID. Every identity workflow the character-gen skill can produce is
> currently unrunnable.

### IP-Adapter FaceID Plus V2 (SDXL) ❌
Repo: https://github.com/cubiq/ComfyUI_IPAdapter_plus — **maintenance-only since April 2025**

| File | → Directory | Source |
|------|-------------|--------|
| `ip-adapter-faceid-plusv2_sdxl.bin` | `models/ipadapter/` | `huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl.bin` |
| `ip-adapter-faceid-plusv2_sdxl_lora.safetensors` | `models/loras/` | `huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sdxl_lora.safetensors` |
| `ip-adapter-faceid_sdxl.bin` | `models/ipadapter/` | `huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin` |
| `ip-adapter-faceid_sdxl_lora.safetensors` | `models/loras/` | `huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl_lora.safetensors` |
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | `models/clip_vision/` | `huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors` |
| `CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors` | `models/clip_vision/` | `huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors` |

- **FaceID variants additionally require `insightface`** (below).
- The unified loader matches on **exact filenames** — rename the downloads as shown.
- Standard (non-face) IP-Adapter models also live under `huggingface.co/h94/IP-Adapter`.

### InstantID ❌
Repo: https://github.com/cubiq/ComfyUI_InstantID

| File | → Directory |
|------|-------------|
| `ip-adapter.bin` | `models/instantid/` |
| antelopev2 set: `1k3d68.onnx`, `2d106det.onnx`, `genderage.onnx`, `glintr100.onnx`, `scrfd_10g_bnkps.onnx` | `models/insightface/models/antelopev2/` |
| InstantID ControlNet | `models/controlnet/` |

- **Path gotcha**: the final path must be `...insightface/models/antelopev2/`, **not**
  `.../antelopev2/antelopev2/`. The InstantID Face Analysis node auto-downloads but
  frequently nests it one level too deep — check and move it manually.
- **VRAM**: ~12 GB. **Best for closeups and hero shots**; distinctive or unusual faces
  often only land properly here.

### PuLID / PuLID Flux 2 ❌
- FLUX.2 family: https://github.com/iFayens/ComfyUI-PuLID-Flux2
- **VRAM**: 24–40 GB
- **Best for** loose framing — full body, varied scenes. The production pattern is
  **PuLID for loose, InstantID for tight**.

### InsightFace (required by all face methods) ❌
- Backing library for FaceID, InstantID, and PuLID alike.
- Install: `pip install insightface onnxruntime-gpu` into the ComfyUI venv
  (`{COMFYUI_PATH}/.venv`).
- Models land under `models/insightface/`.

---

## ControlNet — MISSING ❌

`models/controlnet/` is empty. `comfyui_controlnet_aux` is installed, but that package
provides **preprocessors only** (pose, depth, canny extraction) — not the ControlNet
models themselves. Preprocessing will work; conditioning will not.

| Target | Download |
|--------|----------|
| SDXL ControlNet (union) | https://huggingface.co/xinsir/controlnet-union-sdxl-1.0 |
| SDXL OpenPose | https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0 |
| FLUX ControlNet Union | https://huggingface.co/InstantX/FLUX.1-dev-Controlnet-Union |
| SD 1.5 ControlNet | https://huggingface.co/lllyasviel/ControlNet-v1-1 |

Path: `models/controlnet/`.

**Partial exception**: `Z-Image-Turbo-Fun-Controlnet-Union.safetensors` ✅ is installed in
`model_patches/` and gives Z-Image ControlNet-style conditioning today.

---

## Detection Models (FaceDetailer) — MISSING ❌

`comfyui-impact-pack` is installed; `models/ultralytics/bbox/` does not exist, so
**FaceDetailer will fail**.

| File | → Directory | Source |
|------|-------------|--------|
| `bbox/face_yolov8m.pt` | `models/ultralytics/bbox/` | https://huggingface.co/Bingsu/adetailer |
| `bbox/hand_yolov8s.pt` | `models/ultralytics/bbox/` | same |
| `segm/person_yolov8m-seg.pt` | `models/ultralytics/segm/` | same |

**SAM** ✅ — `sam_vit_b_01ec64.pth` is installed in `models/sams/`. Consider `sam_vit_h`
for better masks if you use SAM heavily.

---

## Face Restoration — MISSING ❌

`models/facerestore_models/` is empty.

| Model | Source | Notes |
|-------|--------|-------|
| CodeFormer | https://github.com/sczhou/CodeFormer | Best quality/identity balance; `codeformer.pth` |
| GFPGAN v1.4 | https://github.com/TencentARC/GFPGAN | Faster, softer |

Path: `models/facerestore_models/`.

---

## Video Models

### LTX-2.5 ⚠️ (not installed; blocked by ComfyUI version)
- **Download**: https://huggingface.co/Lightricks/LTX-2.5 — **gated repo, accept the
  licence on the model page first**
- **Path**: `models/checkpoints/` or `diffusion_models/` per variant
- **VRAM**: 32 GB+ bf16 → **use fp8 or GGUF on this card**
- **Size**: 19B — *smaller* than the 22B LTX-2.3 already installed
- **Requires ComfyUI ≥ v0.32.0** (installed: 0.28.0)
- **Notes**: Only open model with native single-pass audio+video. IC-LoRA ecosystem for
  camera control and spatial upscaling.

### LTX-2.3 ✅
- **Installed**: `ltx-2.3-22b-distilled-fp8.safetensors` (27.5 GB),
  `ltx-2.3-22b-distilled-lora-384-1.1.safetensors` (7.1 GB, loras),
  `ltx-2.3-spatial-upscaler-x2-1.1.safetensors` (latent_upscale_models)
- **VRAM**: 27.5 GB of weights against 30 GB — expect offloading, little room for anything else.
- **Notes**: Still maintained upstream. Valid until you upgrade for 2.5.

### Wan 2.2 ✅
- **Download**: https://huggingface.co/Wan-AI
- **Installed**: `wan2.2_i2v_high_noise_14B_fp8_scaled` + `low_noise` (13.3 GB each),
  `wan2.2_ti2v_5B_fp16` (9.3 GB), Lightning 4-step LoRAs, SVI PRO LoRAs, lightx2v LoRAs
- **Companions**: `umt5_xxl_fp8_e4m3fn_scaled` ✅ + `wan2.2_vae` ✅
- **VRAM**: ~14 GB per expert. **High-noise and low-noise load sequentially — never both.**
- **Notes**: MoE architecture. The 4-step Lightning LoRAs cut inference dramatically.

### Wan2.2-Animate-2-14B ❌ (the real upgrade path)
- **Download**: https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B (updated ~2026-08-13)
- **Requires ComfyUI ≥ v0.31.0** (installed: 0.28.0)
- **Notes**: Current head of the Wan line.

> ### Wan 2.6 / 2.7 / 3.0 do not exist as weights
> Verified against https://huggingface.co/Wan-AI on 2026-08-26. Open weights stop at
> **Wan 2.2 (+ Animate-2)**. Wan 3.0 is an API beta (opened 2026-08-06). A cluster of SEO
> sites publishes fabricated Wan 2.7 VRAM tables and ModelScope download commands —
> **do not follow them**.

### MiniMax-H3 ❌
- 33B image-text-to-video, open weights, trending on HF.
- **Requires ComfyUI ≥ v0.30.0.**

### Other installed video weights

Read exact local and private filenames from `state/inventory.json`. Validate any GGUF
workflow against the inventoried loader nodes before recommending it.

---

## Upscaling & Restoration

### SeedVR2 ✅ — but drop the custom node
- **Installed**: `seedvr2_ema_3b_fp16`, `_3b_fp8_e4m3fn`, `_7b_fp8_e4m3fn` (in both
  `checkpoints/` and `SEEDVR2/`), plus the `seedvr2_videoupscaler` custom node
- **ComfyUI v0.28.0 added NATIVE SeedVR2 image + video upscaling.** The custom node is now
  redundant and a plausible source of node-name collisions. Prefer the built-in nodes.
- **VRAM**: 3.2 GB (3B fp8) / 7.7 GB (7B fp8) — all comfortable.

### FlashVSR ✅
- **Installed**: `FlashVSR1_1.safetensors` + `LQ_proj_in` + `TCDecoder` + `Wan2.1_VAE`
  (in `FlashVSR/`, duplicated into `checkpoints/`)
- Node: `ComfyUI-FlashVSR` ✅

### RealESRGAN x4plus ✅
- `models/upscale_models/RealESRGAN_x4plus.pth` (67 MB). The only classic ESRGAN installed.
- Worth adding: **4x-UltraSharp** (https://huggingface.co/uwg/upscaler) for detail-preserving
  photo upscales.

---

## Voice / TTS ❌ (nothing installed)

No TTS engine is installed. `TTS-Audio-Suite` is the single ComfyUI integration point:
https://github.com/diodiogod/TTS-Audio-Suite — spans RVC, Echo-TTS, Qwen3-TTS, CosyVoice 3,
Step Audio EditX, IndexTTS-2, Chatterbox (classic + multilingual), F5-TTS, Higgs Audio 2/3,
VibeVoice.

| Need | Engine | Licence |
|------|--------|---------|
| Peak quality | F5-TTS | MIT |
| Easiest / best demo | Chatterbox Turbo | MIT |
| Mandarin / Japanese / Korean | IndexTTS-2 | Open |
| Emotional delivery | CosyVoice 2 | Open |

**Audio generation** ✅ — `acestep_v1.5_xl_turbo_bf16` (ACE-Step, music) is installed with
its encoders and VAE. That is music, not speech.

---

## LoRA Training Tools

| Tool | Best For | FLUX.2 | Source |
|------|----------|:------:|--------|
| Kohya_ss (sd-scripts) | Gold standard, most configurable | Yes | https://github.com/kohya-ss/sd-scripts |
| Musubi Tuner | Video LoRA (Wan / HunyuanVideo / FramePack) | Yes | https://github.com/kohya-ss/musubi-tuner |
| Ostris AI-Toolkit | Simple FLUX training | Yes | https://github.com/ostris/ai-toolkit |
| FluxGym | Low-VRAM FLUX | — | https://github.com/cocktailpeanut/fluxgym |

At 30 GB: SDXL trains comfortably at batch 2–4. FLUX LoRA needs an 8-bit optimizer plus
gradient checkpointing.

**Installed LoRAs**: Read from `state/inventory.json`; project-private names and
discarded-checkpoint history are intentionally not duplicated in this reference.

---

## Text Encoders ✅ (well covered)

| File | Used by |
|------|---------|
| `umt5_xxl_fp8_e4m3fn_scaled` | Wan 2.2 |
| `qwen_2.5_vl_7b_fp8_scaled` | Qwen-Image / Qwen-Image-Edit |
| `qwen_3_8b_fp8mixed` | FLUX.2 klein 9B |
| `qwen_3_4b` | Z-Image, FLUX.2 klein 4B |
| `t5xxl_fp16` / `t5xxl_fp8_e4m3fn_scaled` | FLUX.1, SD3 |
| `qwen_4b_ace15` / `qwen_0.6b_ace15` | ACE-Step |
| `gemma_3_12B_it_fp4_mixed` | Gemma-conditioned models |
| `byt5_small_glyphxl_fp16` | Glyph/typography conditioning |

**Missing**: `clip_l.safetensors` ❌ — only needed if you load split FLUX.1 weights rather
than the fp8 all-in-one. Source: `huggingface.co/comfyanonymous/flux_text_encoders`.

---

## Priority Shopping List

Ordered by how much capability each unlocks per GB:

| # | What | Size | Unlocks |
|---|------|------|---------|
| 1 | InsightFace + antelopev2 + InstantID `ip-adapter.bin` | < 1 GB | All closeup identity work |
| 2 | IP-Adapter FaceID Plus V2 + LoRA + 2 CLIP-Vision encoders | ~5 GB | Identity conditioning; stops `comfyui_ipadapter_plus` erroring |
| 3 | `bbox/face_yolov8m.pt` | ~50 MB | FaceDetailer / Impact Pack |
| 4 | SDXL ControlNet Union | ~2.5 GB | Pose/depth/canny conditioning on your SDXL stack |
| 5 | CodeFormer | ~360 MB | Face restoration after upscale |
| 6 | 4x-UltraSharp | ~67 MB | Better photo upscales than RealESRGAN alone |
| 7 | Qwen-Image GGUF (Q4/Q5) | ~8 GB | Makes Qwen-Image actually loadable on 30 GB |

Items 1–3 total under 6 GB and convert the machine from "cannot do identity work at all"
to "fully equipped".
