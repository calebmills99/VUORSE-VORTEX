# Skill Evolution & Update Protocol

This skill is designed to evolve continuously. Monitor these sources and update accordingly.

> **Historical changelog.** Older entries record the guidance available at that time. Current
> inventory, hardware, model-landscape, and version constraints always take precedence.

---

## Sources to Monitor

### Model Releases (Check Weekly)

**HuggingFace Trending**
- https://huggingface.co/models?sort=trending
- Filter: diffusers, video, audio
- Watch for: New FLUX variants, Wan updates, voice models

**Civitai New Models**
- https://civitai.com/models?sort=Newest
- Filter: Checkpoint, LoRA, ControlNet
- Watch for: New photorealistic checkpoints, face LoRAs

**GitHub Releases**
- https://github.com/comfyanonymous/ComfyUI/releases
- https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved/releases
- https://github.com/cubiq/ComfyUI_IPAdapter_plus/releases
- https://github.com/cubiq/ComfyUI_InstantID/releases
- https://github.com/ltdrdata/ComfyUI-Impact-Pack/releases

### Research & Techniques (Check Monthly)

**Papers**
- https://huggingface.co/papers (daily ML papers)
- https://arxiv.org/list/cs.CV/recent (computer vision)
- Search terms: "identity preservation", "video generation", "voice cloning", "diffusion"

**Community Knowledge**
- r/StableDiffusion
- r/comfyui
- ComfyUI Discord
- Civitai articles/guides

### Video Model Landscape (Check Bi-Weekly)

**Open Source**
- Wan series (Alibaba) - watch for 2.3+
- HunyuanVideo (Tencent)
- CogVideoX (Zhipu)
- LTX Video (Lightricks)
- Mochi (Genmo)

**Commercial (for benchmarking)**
- Kling (Kuaishou)
- Runway Gen-3
- Pika
- Sora (OpenAI)

### Voice/Audio (Check Monthly)

- https://github.com/SWivid/F5-TTS/releases
- https://github.com/resemble-ai/chatterbox/releases
- ElevenLabs blog for new features
- Fish Audio, Cartesia for emerging options

---

## Update Protocol

### When New Model Drops

1. **Evaluate relevance**: Does it improve on current recommendations?
2. **Test compatibility**: Works with ComfyUI? Required nodes available?
3. **Benchmark**: Compare quality/speed vs current options
4. **Update files**:
   - `models.md`: Add download links, paths, requirements
   - `workflows.md`: Add/modify workflow if needed
   - `SKILL.md`: Update recommendation tables if it becomes new default
5. **Log change**: Add to changelog below

### When User Reports Issue

1. **Document the issue**: What workflow, what settings, what result
2. **Research solutions**: Community fixes, parameter adjustments
3. **Test fix**: Verify solution works
4. **Update relevant file**: Add troubleshooting entry or modify settings
5. **Log change**: Add to changelog

### When User Discovers Better Approach

1. **Document the discovery**: What worked better and why
2. **Validate**: Test in multiple scenarios
3. **Integrate**: Update workflows.md with new approach
4. **Promote if significant**: Update SKILL.md recommendations

---

## Changelog

### v1.3.0 (2026-08-26 Research Run)

**CORRECTIONS (both were actively misleading guidance):**
- **Wan open weights stop at Wan 2.2.** The March run ranked Wan 2.6 as a local video
  model; it has no weight file. Wan 2.6/2.7/3.0 are API-only. Verified against
  `huggingface.co/Wan-AI`. A cluster of SEO sites publishes fabricated Wan 2.7 VRAM
  tables and ModelScope commands -- do not cite them.
- **NVFP4 guidance never applied to this machine.** Hardware is RTX 5000 Ada
  (compute 8.9, 30GB, cu128), not the RTX 5090 the profile claimed. NVFP4 needs
  Blackwell + cu130. All NVFP4 recommendations replaced with FP8/GGUF.

**NEW MODELS:**
- **LTX-2.5** (open weights, ~Aug 17) -- 19B, *smaller* than LTX-2.3's 22B. Native
  single-pass audio+video. Gated HF repo. Needs ComfyUI >= v0.32.0.
- **Wan2.2-Animate-2-14B** (~Aug 13) -- the genuine Wan upgrade path. Needs >= v0.31.0.
- **MiniMax-H3** -- 33B image-text-to-video, native from v0.30.0.
- **Qwen-Image 3.0** -- native from v0.32.0; GGUF quants run at ~8GB.
- **MiniMax-Music3** -- 2B text-to-audio, nodes in v0.33.1.

**PLATFORM:**
- ComfyUI current is **v0.33.4** (Aug 24). This install is on **v0.28.0**.
- **BREAKING (v0.32.0): minimum PyTorch is now 2.7.**
- v0.28.0 added **native SeedVR2** upscaling -- makes the `seedvr2_videoupscaler`
  custom node redundant here.
- CUDA Graphs support (v0.33.1); streaming video transcode replaced RAM buffering (v0.29.0).
- Deprecated: Runway Gen3a, Ideogram V1/V2, Reve, legacy Kling. Kling v2 retires 2026-09-15.

**IDENTITY PRESERVATION -- no change:**
- PuLID / InstantID / IP-Adapter FaceID Plus V2 remain the three practical methods.
  Production pattern: PuLID for loose framing, InstantID for closeups.
- `cubiq/ComfyUI_IPAdapter_plus` still maintenance-only (since April 2025).

**FILES UPDATED:**
- `foundation/model-landscape.md` -- rewritten with verified data + hardware constraints
- `foundation/hardware-profile.md` -- rebuilt from `nvidia-smi`
- `references/research-log.md` -- August 2026 section appended
- `references/staleness-report.md` -- new run, corrections, outstanding Tier-3 work

### v1.2.0 (2026-02-18 Research Run)
**NEW MODELS:**
- **Z-Image**: Day-0 ComfyUI support (Feb 2, 2026) — non-distilled, flexible quality, NVFP4/NVFP8
- **Hunyuan 3D 3.0**: Text/image/sketch → 3D assets via Partner Nodes (Feb 16, 2026)
- **Kling 3.0**: Commercial-quality video via Partner Nodes (Feb 16, 2026)
- **Stable Video Infinity 2.0 Pro**: Infinite-length video with Wan 2.2 I2V A14B

**IDENTITY & CHARACTER:**
- **PuLID Flux Chroma**: New fork extending PuLID to FLUX + Chroma models
- **USO (ByteDance)**: FLUX.1-dev based unified style+subject generation — no more fighting the model for style fidelity
- **FLUX Kontext**: Confirmed community gold standard for single-reference consistent character editing

**PERFORMANCE (CRITICAL):**
- NVFP4 requires PyTorch cu130 — without it, NVFP4 is up to 2x SLOWER than FP8
- ComfyUI +40% on all NVIDIA GPUs (async offload + pinned memory now default)
- NVFP4 = 3x faster / 60% VRAM reduction on RTX 50 Series
- NVFP8 = 2x faster / 40% VRAM reduction (any NVIDIA GPU)
- AMD ROCm native integration: 5.4x faster for AMD GPUs

**NEW FEATURE:**
- Added `comfyui-prompt-interview` skill — conversational guided interview that synthesizes a perfect model-appropriate prompt from user answers

**FILES UPDATED:**
- `references/staleness-report.md` — first full research run logged
- `foundation/model-landscape.md` — Z-Image, SVI 2.0 Pro, Kling 3.0, Hunyuan 3D 3.0 added
- `references/research-log.md` — 2026 section appended
- `foundation/skill-registry.md` — new prompt-interview skill registered

### v1.1.0 (February 2026 Update)
**NEW MODELS & FEATURES:**
- **FLUX.2**: Up to 10 reference images for maximum identity consistency
- **LTX-2**: First production-ready open-source 4K audio+video generation
- **AuraFace**: Commercial-friendly identity encoder (ArcFace alternative)
- **F5-TTS Cross-Lingual**: Cross-lingual voice cloning without transcripts
- **DiffSwap++**: 3D latent-controlled face swapping

**PLATFORM UPDATES:**
- **ComfyUI v0.8.1**: NVFP4/NVFP8 support (3x faster, 60% VRAM reduction on RTX 50 Series)
- Native AMD ROCm integration for AMD GPUs
- Audio recording node for direct audio capture
- Weight streaming memory management

**DOCUMENTATION:**
- Added 2026 updates section to research-log.md
- Updated all model recommendation tables
- Updated Quick Decision guide with 2026 options
- Updated RTX optimization section for v0.8.1

### v1.0.0 (Initial Release)
- Core workflows: InstantID, IP-Adapter, PuLID, AnimateDiff, Wan 2.1
- Model reference with 2024-2025 state of the art
- LoRA training guide for SDXL and FLUX
- Voice synthesis covering Chatterbox, F5-TTS, RVC, ElevenLabs
- Lip-sync pipelines: Wav2Lip, SadTalker, LivePortrait

---

## User-Specific Learnings

Track what works best for this user's specific setup and preferences.

### Hardware Profile
See `foundation/hardware-profile.md` for the verified GPU profile -- it is the single
source of truth and is regenerated from `nvidia-smi`. Do not restate VRAM or launch
flags here; they drift.

- Can run: derive from `state/inventory.json` (`system` block) plus hardware-profile.md
- Optimization: see hardware-profile.md "Precision Support"

### Project: [Your Character Name]
- Source: [e.g., photos, 3D renders, illustrations]
- Target: [e.g., photorealistic, stylized]
- Key features: [appearance details]
- Recommended approach: [fill in after testing]

### Workflow Preferences
(To be filled as user works with skill)
- Preferred checkpoint: [TBD]
- Preferred upscaler: [TBD]
- CFG sweet spot: [TBD]
- Face detailer settings: [TBD]

### What Worked Well
(Document successful approaches)

### What Didn't Work
(Document failed approaches to avoid repeating)

---

## Scheduled Research Tasks

**Weekly**
- [ ] Check HuggingFace trending for new models
- [ ] Check ComfyUI releases for breaking changes
- [ ] Review any user feedback from recent sessions

**Monthly**
- [ ] Deep dive on any major new releases
- [ ] Review video model landscape
- [ ] Check voice synthesis developments
- [ ] Update changelog if needed

**Quarterly**
- [ ] Full skill audit - are recommendations still current?
- [ ] Remove deprecated models/methods
- [ ] Add any new paradigm shifts
