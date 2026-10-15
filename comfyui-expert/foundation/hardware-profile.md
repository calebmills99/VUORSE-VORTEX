# Hardware Profile

<!-- Verified: 2026-08-26 via nvidia-smi + ComfyUI requirements.txt on the live install -->

## GPU

- **Model**: NVIDIA RTX 5000 Ada Generation
- **VRAM**: 30 GB GDDR6 ECC (30712 MiB reported)
- **Architecture**: Ada Lovelace
- **Compute Capability**: 8.9
- **Driver**: 596.86
- **Torch**: 2.9.1+cu128 (CUDA 12.8)

## Precision Support — read this before picking a checkpoint

| Format | Supported | Notes |
|--------|:---------:|-------|
| FP32 / TF32 | Yes | `NVIDIA_TF32_OVERRIDE=1` is set in the launcher |
| FP16 / BF16 | Yes | Native tensor-core support |
| FP8 (e4m3fn / e5m2) | Yes | Ada has native FP8 tensor cores |
| **NVFP4** | **No** | Requires Blackwell (compute 12.0) **and** a cu130 torch build. This box is compute 8.9 on cu128. NVFP4 checkpoints will fall back to slow emulation or fail to load. |

> **Do not recommend NVFP4 checkpoints for this machine.** Current guidance in
> `foundation/model-landscape.md` prefers FP8 (`*_fp8_scaled`, `*_fp8_e4m3fn`) or GGUF
> quants for this Ada-generation GPU.

## Capabilities at 30 GB VRAM

| Workload | Status | Notes |
|----------|--------|-------|
| SDXL / Pony / Illustrious | Native | Full FP16, batch 4x at 1024x1024 |
| FLUX.1-dev FP8 | Native | ~17 GB, comfortable headroom |
| FLUX.1-dev FP16 | Tight | 23 GB weights; works solo, no concurrent models |
| FLUX.2 klein 9B FP8 | Native | ~9.4 GB — the right klein variant for this card |
| FLUX.2 klein 9B BF16 | Tight | 18 GB; works solo |
| Z-Image Turbo BF16 | Native | ~12 GB |
| Qwen-Image 2512 BF16 | **Offload required** | 40.8 GB weights exceed VRAM. Needs `--lowvram`/block-swap or an FP8/GGUF quant. |
| Qwen-Image-Edit 2511 BF16 | **Offload required** | Same — 40.8 GB. |
| Wan 2.2 I2V 14B FP8 | Native | ~14.3 GB per expert; high+low noise sequentially, not simultaneously |
| Wan 2.2 TI2V 5B FP16 | Native | ~10 GB |
| LTX-2.3 22B distilled FP8 | Tight | 29.5 GB weights — essentially the whole card. Expect offload. |
| SeedVR2 3B FP8 | Native | ~3.4 GB |
| FlashVSR | Native | ~5.7 GB |
| LoRA Training (SDXL) | Native | Batch 2-4 |
| LoRA Training (FLUX) | Possible | Use 8-bit optimizer + gradient checkpointing at 30 GB |

## Current Launch Configuration

`D:\ComfyUI312\run_comfyui.bat`:

```bat
set PYTORCH_ALLOC_CONF=expandable_segments:True
set CUDA_MODULE_LOADING=LAZY
set NVIDIA_TF32_OVERRIDE=1
set CUDA_VISIBLE_DEVICES=0
set TORCH_COMPILE_DISABLE=1

python comfyui\main.py --fast fp16_accumulation
```

### Notes on these flags

- `--fast fp16_accumulation` — good call on Ada; meaningful speedup with negligible quality cost.
- `TORCH_COMPILE_DISABLE=1` — leaves performance on the table. If the WanVideoWrapper /
  KJNodes torch.compile paths were disabled to fix a crash, keep it; otherwise try removing it.
- No `--highvram`. At 30 GB that is the right default: several installed models
  (Qwen-Image bf16, LTX-2.3) exceed VRAM and need ComfyUI's offloading to run at all.

## Performance Tips

- Prefer FP8 and GGUF variants over BF16 for anything above ~20 GB.
- Enable tiled VAE for 4K+ decode; the 30 GB budget is mostly consumed by weights.
- Wan 2.2 high-noise and low-noise experts load sequentially — do not try to hold both.
- Idle VRAM was 15.7 GB used at scan time; check for a stray process before large runs.
