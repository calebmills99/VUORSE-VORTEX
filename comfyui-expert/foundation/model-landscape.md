# Model Landscape

Quick reference for model selection. Full specs in `references/models.md`.
Full findings and sourcing in `references/research-log.md` (August 2026 section).

<!-- Updated: 2026-08-26 | Sources: docs.comfy.org/changelog, Comfy-Org/ComfyUI releases, HuggingFace org pages (Wan-AI, Lightricks), HF trending, independent comparisons -->

> ## Hardware constraints for THIS machine
>
> **GPU: RTX 5000 Ada Generation -- compute 8.9, 30 GB, torch 2.9.1+cu128.**
>
> - **NVFP4 is unavailable.** It needs Blackwell (compute 12.x) *and* a cu130 torch build.
>   Wherever a model offers an NVFP4 variant below, take the **FP8 or GGUF** one instead.
> - FP8 is natively supported and is the default choice above ~20 GB of weights.
> - Anything over ~28 GB of weights needs offloading, not `--highvram`.
>
> See `foundation/hardware-profile.md`. Validate every pick against `state/inventory.json`.

> ## Installed ComfyUI is v0.28.0; current is v0.33.4
>
> Five minor versions behind. This gates several models below:
> **LTX-2.5 and Qwen-Image 3.0 need >= v0.32.0**; **Wan-Animate2 needs >= v0.31.0**.
> Note v0.32.0 raised the **minimum PyTorch to 2.7** (this box has 2.9.1, so the upgrade
> is safe on that axis).

## Image Generation

No model swept this category. Pick by priority, not by rank.

| Priority | Model | VRAM | Notes |
|----------|-------|------|-------|
| **Prompt adherence, multi-reference** | **FLUX.2 [dev]** | 24GB+ | Leads prompt fidelity; heaviest VRAM in class. Up to 10 ref images. |
| **Speed / throughput** | **Z-Image Turbo** | 12-16GB | ~1s on datacenter GPUs; excellent quality per parameter. Installed here (bf16 + a useless nvfp4 copy). |
| **Text rendering (incl. CJK/Arabic)** | **Qwen-Image 2512 / 3.0** | 24GB+ bf16, ~8GB GGUF | Best-in-class typography. 3.0 native from ComfyUI v0.32.0. GGUF: `city96/Qwen-Image-gguf`. |
| Low VRAM / fast FLUX | FLUX.2 [klein] 9B | 12GB (fp8) / 20GB+ (bf16) | fp8 is the right variant for this card. |
| Iterative character editing | FLUX Kontext | 12-32GB | Multi-round editing chains. |
| Proven photorealism | FLUX.1-dev | 16GB+ (fp8) | Still solid; fp8 leaves headroom. |
| Fast SDXL | RealVisXL V5.0 / Juggernaut XL | 8GB+ | Installed here. |

## Identity Preservation

**No new gold standard emerged this cycle.** The three practical methods are unchanged,
all built on InsightFace.

| Method | Best For | VRAM | Notes |
|--------|----------|------|-------|
| **PuLID** | Loose generation -- full body, varied scenes | 24-40GB | Production default for anything not a closeup. |
| **InstantID** | Tight generation -- closeups, hero shots | 12GB | Distinctive/unusual faces often *only* land here. Legacy but not replaceable. |
| **IP-Adapter FaceID Plus V2** | General identity conditioning | 12GB+ | `cubiq/ComfyUI_IPAdapter_plus` is **maintenance-only since April 2025**. |
| PuLID Flux 2 | FLUX.2 family (Klein + Dev) | 24-40GB | `iFayens/ComfyUI-PuLID-Flux2`. |
| InfiniteYou | Highest single-shot identity fidelity | 24GB | ByteDance, ICCV 2025 Highlight. |
| Trained LoRA (15-30 images) | Maximum fidelity | varies | Still the ceiling. 30-90 min per character. |
| ReActor / Roop / FaceFusion | Fast post-hoc swap | low | Reads as fake; no influence on lighting or composition. |

> **This install has NO identity models.** `models/ipadapter`, `insightface`, `instantid`,
> `photomaker`, and `controlnet` are all empty, while `comfyui_ipadapter_plus` is installed.
> Every method in this table is currently unavailable. See `state/inventory.json` warnings.

## Video Generation

> ### Correction: Wan open weights stop at Wan 2.2
> The March 2026 landscape ranked **Wan 2.6** as a local model. That was wrong.
> Verified against `huggingface.co/Wan-AI` on 2026-08-26: there is no Wan 2.5, 2.6, 2.7,
> or 3.0 weight file. Wan 3.0 is an **API beta** (opened 2026-08-06, no weights); ComfyUI's
> "Wan 3.0" node in v0.33.4 is a partner API node. SEO sites publishing Wan 2.7 VRAM tables
> and ModelScope download commands are **fabricating them**.

| Rank | Model | Status | VRAM | Notes |
|------|-------|--------|------|-------|
| 1 | **LTX-2.5** | Open weights (HF `Lightricks/LTX-2.5`, ~Aug 17) | 32GB+ bf16; fp8/GGUF below | 19B -- *smaller* than LTX-2.3's 22B. Only open model with native single-pass audio+video. **Gated repo: accept the license on HF.** Needs ComfyUI >= v0.32.0. IC-LoRA ecosystem for camera control + spatial upscaling. |
| 2 | **Wan 2.2 + Animate-2** | Open weights | 14GB+ per expert (fp8) | Most versatile open MoE video model. `Wan2.2-Animate-2-14B` (~Aug 13) is the current head; needs ComfyUI >= v0.31.0. |
| 3 | **MiniMax-H3** | Open weights, 33B | high | Image-text-to-video, trending on HF. Native from ComfyUI v0.30.0. |
| 4 | LTX-2.3 | Open weights, still maintained | 24GB+ (22B distilled fp8) | Installed here. Valid until you upgrade ComfyUI for 2.5. |
| 5 | Wan 2.2 TI2V 5B | Open weights | ~10GB | Installed here. Comfortable fit. |
| 6 | HunyuanVideo 1.5 | Open weights | 24GB | 8.3B. |
| 7 | FramePack | Open weights | 6GB+ | Long videos (60s+), VRAM-invariant to length. |
| 8 | SkyReels V1 / Mochi 1 / MAGI-1 | Open weights | 24GB+ | Second tier; no movement this cycle. |
| -- | Wan 2.6 / 2.7 / 3.0, Kling | **API only** | Cloud | Kling v2 retires 2026-09-15. |

## Upscaling / Restoration

| Rank | Tool | Notes |
|------|------|-------|
| 1 | **SeedVR2 (native)** | **ComfyUI v0.28.0 added native SeedVR2 image + video upscaling.** This install has the models *and* the `seedvr2_videoupscaler` custom node -- the node is now redundant and a likely source of node-name conflicts. |
| 2 | FlashVSR | Installed here. Video super-resolution. |
| 3 | LTX-2.5 IC-LoRA Spatial Upscaler | Pairs with LTX-2.5. |
| 4 | RealESRGAN x4plus | Classic ESRGAN; installed here. |

## 3D Generation

| Rank | Model | Best For | VRAM | Notes |
|------|-------|----------|------|-------|
| 1 | Hunyuan 3D 3.0 | Text/image/sketch to 3D | 16GB+ | Partner Nodes; PBR materials |
| 2 | Hunyuan3D-2.1 | Open-source 3D with PBR | 16GB+ | Fully open-sourced with training code |
| 3 | **TRELLIS2 / Sam3d-body / Meshy-7** | Image-to-3D | Partner/varies | Added ComfyUI v0.33.x-v0.34.x |
| 4 | Rodin3D Gen-2 | Image-to-3D | Cloud/Partner | Via Partner Nodes |

New in v0.28.0: **Save 3D (Advanced), Save Splat, Save Point Cloud** nodes for direct export.

## Voice / TTS

`diodiogod/TTS-Audio-Suite` remains the single ComfyUI integration point, now spanning RVC,
Echo-TTS, Qwen3-TTS, CosyVoice 3, Step Audio EditX, IndexTTS-2, Chatterbox
(classic + multilingual), F5-TTS, Higgs Audio 2/3, and VibeVoice.

| Need | Pick | License | Notes |
|------|------|---------|-------|
| Peak quality for app integration | **F5-TTS** | MIT | Flow-matching DiT; works on 6GB. |
| Easiest / best demo | **Chatterbox (Turbo)** | MIT | Blind tests: 65.3% preferred it over ElevenLabs (24.5%). |
| Mandarin / Japanese / Korean | **IndexTTS-2** | Open | Also 8-emotion vector control. |
| Explicit emotional delivery | **CosyVoice 2** | Open | |
| Voice design from text, 10 languages | Qwen3-TTS | Open | Zero-shot clone. |
| Long-form (90 min), multi-speaker | VibeVoice | Microsoft | |
| Music | **MiniMax-Music3** (2B) | Open | Trending; ComfyUI nodes in v0.33.1. Fish Audio nodes in v0.33.2. |

## Lip-Sync

| Rank | Tool | Best For |
|------|------|----------|
| 1 | LatentSync 1.6 | Highest accuracy |
| 2 | Wan2.2-S2V-14B | Speech-to-video, open weights |
| 3 | Wav2Lip | Proven, works with any face |
| 4 | SadTalker | Head movement + expressions |

*(The March landscape listed "Wan 2.6 native" here. Removed -- no such open weights.)*

## Performance Optimization

| Tool | Speedup | VRAM Savings | Usable on this GPU? |
|------|---------|-------------|:-------------------:|
| **CUDA Graphs** (ComfyUI v0.33.1) | varies | -- | Yes -- worth testing after upgrade |
| Nunchaku (SVDQuant) | 2-3x | 3.5x reduction | Yes (INT4, RTX 20+) |
| WaveSpeed (FBCache) | Up to 2x | Minimal | Yes |
| TeaCache | ~30% | Minimal | Yes -- best for video |
| NVFP8 | 2x | 40% less | **Yes** -- the right choice here |
| int4 convrot (v0.28.0) | varies | more | Optimized for Turing; available |
| NVFP4 | 3x | 60% less | **NO** -- needs Blackwell + cu130 |

## LoRA Training Tools

| Tool | Best For | FLUX.2 Support | Notes |
|------|----------|:-:|-------|
| Kohya ss (sd-scripts) | Gold standard, most configurable | Yes | IP noise gamma, CFG sampling for FLUX |
| Musubi Tuner | Video LoRA (Wan/HunyuanVideo/FramePack) | Yes (dev+klein) | 20-30% VRAM savings with activation offload |
| Ostris AI Toolkit | Simple FLUX training | Yes (dev+klein) | Apple MPS support incoming |

At 30 GB, FLUX LoRA training needs an 8-bit optimizer plus gradient checkpointing.
SDXL trains comfortably at batch 2-4.
