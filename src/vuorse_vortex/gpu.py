"""GPU runtime guardrails for VUORSE-VORTEX."""

from __future__ import annotations

import os
from functools import lru_cache

from rich.console import Console

console = Console(stderr=True)

GPU_TANTRUM = (
    "💅 VUORSE GPU TANTRUM 💅\n"
    "CUDA is unavailable. I am not embedding the entire Slayverse on CPU like a Victorian "
    "clerk with a candle.\n"
    "Deep-learning workload refused.\n"
    "Restore GPU/CUDA or explicitly run a small CPU-only diagnostic mode.\n"
    "VUORSE is now on strike."
)


def env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def gpu_required() -> bool:
    return env_true("CORTEX_REQUIRE_GPU") and not env_true("CORTEX_ALLOW_CPU_DIAGNOSTIC")


@lru_cache(maxsize=1)
def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _reset_cuda_cache() -> None:
    """Clear CUDA availability cache, primarily for tests."""
    cuda_available.cache_clear()


def require_gpu(workload: str = "deep-learning workload") -> None:
    """Raise loudly if a GPU-required workload would fall back to CPU."""
    if gpu_required() and not cuda_available():
        console.print(f"\n[bold magenta]{GPU_TANTRUM}[/bold magenta]\n")
        console.print(
            f"[bold red]Reason:[/bold red] {workload} requires CUDA, but CUDA is unavailable."
        )
        raise RuntimeError(f"GPU strict mode refused CPU fallback for {workload}")
