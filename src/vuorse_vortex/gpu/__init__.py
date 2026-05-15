"""GPU enforcement utilities for VUORSE-VORTEX.

All embedding and inference tasks are GPU-first. This module enforces
CUDA availability and provides device resolution utilities.
"""

from __future__ import annotations

import warnings

from vuorse_vortex.logging_utils import get_logger

logger = get_logger(__name__)


class CUDANotAvailableError(RuntimeError):
    """Raised when CUDA is required but not available."""


def is_cuda_available() -> bool:
    """Return True if CUDA is available via PyTorch."""
    try:
        import torch  # type: ignore[import]

        return torch.cuda.is_available()
    except ImportError:
        return False


def cuda_device_count() -> int:
    """Return the number of available CUDA devices."""
    try:
        import torch  # type: ignore[import]

        return torch.cuda.device_count()
    except ImportError:
        return 0


def get_device(device_id: int = 0, require_cuda: bool = True) -> str:
    """Resolve the appropriate torch device string.

    Args:
        device_id: CUDA device index.
        require_cuda: If True, raise CUDANotAvailableError when CUDA is absent.
                      If False, fall back to CPU with a warning.

    Returns:
        A torch device string: "cuda:N" or "cpu".

    Raises:
        CUDANotAvailableError: If require_cuda=True and CUDA is unavailable.
    """
    if is_cuda_available():
        count = cuda_device_count()
        if device_id >= count:
            logger.warning(
                "Requested CUDA device index out of range; falling back to device 0",
                requested=device_id,
                available=count,
            )
            device_id = 0
        device = f"cuda:{device_id}"
        logger.info("GPU device resolved", device=device)
        return device

    message = (
        "CUDA is not available. "
        "VUORSE-VORTEX requires a CUDA-capable GPU for embedding and inference tasks."
    )
    if require_cuda:
        logger.error("CUDA enforcement failed", reason=message)
        raise CUDANotAvailableError(message)

    warnings.warn(
        f"{message} Falling back to CPU — performance will be significantly degraded.",
        RuntimeWarning,
        stacklevel=2,
    )
    logger.warning("GPU not available, falling back to CPU", performance_impact="severe")
    return "cpu"


def enforce_cuda(device_id: int = 0) -> str:
    """Strictly enforce CUDA availability.

    Raises CUDANotAvailableError if no GPU is present.

    Returns:
        A "cuda:N" device string.
    """
    return get_device(device_id=device_id, require_cuda=True)


def gpu_status_report() -> dict[str, object]:
    """Generate a GPU status report for diagnostics.

    Returns:
        Dict with CUDA availability, device count, and per-device info.
    """
    report: dict[str, object] = {
        "cuda_available": is_cuda_available(),
        "device_count": cuda_device_count(),
        "devices": [],
    }

    if is_cuda_available():
        try:
            import torch  # type: ignore[import]

            devices = []
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                devices.append(
                    {
                        "index": i,
                        "name": props.name,
                        "total_memory_gb": round(props.total_memory / 1024**3, 2),
                        "compute_capability": f"{props.major}.{props.minor}",
                    }
                )
            report["devices"] = devices
        except Exception as exc:  # noqa: BLE001
            report["error"] = str(exc)

    return report
