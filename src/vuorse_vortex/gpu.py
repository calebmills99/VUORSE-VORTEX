"""GPU runtime guardrails for VUORSE-VORTEX."""

from __future__ import annotations

import os

from rich.console import Console

console = Console(stderr=True)

GPU_TANTRUM = """
💅 VUORSE GPU TANTRUM 💅
CUDA is unavailable. I am not embedding the entire Slayverse on CPU like a Victorian
clerk with a candle.
Deep-learning workload refused.
Restore GPU/CUDA or explicitly run a small CPU-only diagnostic mode.
VUORSE is now on strike.
""".strip()


def env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def gpu_required() -> bool:
    return env_true("CORTEX_REQUIRE_GPU") and not env_true("CORTEX_ALLOW_CPU_DIAGNOSTIC")


def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def require_gpu(workload: str = "deep-learning workload") -> None:
    """Raise loudly if a GPU-required workload would fall back to CPU."""
    if gpu_required() and not cuda_available():
        console.print(f"\n[bold magenta]{GPU_TANTRUM}[/bold magenta]\n")
        console.print(
            f"[bold red]Reason:[/bold red] {workload} requires CUDA, but CUDA is unavailable."
        )
        raise RuntimeError(f"GPU strict mode refused CPU fallback for {workload}")
