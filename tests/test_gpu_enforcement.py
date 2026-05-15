"""Tests for GPU enforcement utilities."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pytest

from vuorse_vortex.gpu import (
    CUDANotAvailableError,
    cuda_device_count,
    enforce_cuda,
    get_device,
    gpu_status_report,
    is_cuda_available,
)


class TestGPUEnforcement:
    def test_is_cuda_available_no_torch(self):
        """When torch is not importable, CUDA is unavailable."""
        with patch.dict("sys.modules", {"torch": None}):
            result = is_cuda_available()
            assert result is False

    def test_cuda_device_count_no_torch(self):
        with patch.dict("sys.modules", {"torch": None}):
            result = cuda_device_count()
            assert result == 0

    def test_get_device_cuda_available(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.device_count.return_value = 2
        with patch.dict("sys.modules", {"torch": mock_torch}):
            device = get_device(device_id=0, require_cuda=False)
            assert device == "cuda:0"

    def test_get_device_cuda_unavailable_no_require(self):
        """When CUDA is unavailable and require_cuda=False, returns 'cpu' with warning."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                device = get_device(device_id=0, require_cuda=False)
            assert device == "cpu"
            assert any(issubclass(warning.category, RuntimeWarning) for warning in w)

    def test_get_device_cuda_unavailable_require_raises(self):
        """When CUDA is unavailable and require_cuda=True, raises CUDANotAvailableError."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            with pytest.raises(CUDANotAvailableError):
                get_device(device_id=0, require_cuda=True)

    def test_enforce_cuda_raises_when_unavailable(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": mock_torch}):
            with pytest.raises(CUDANotAvailableError):
                enforce_cuda()

    def test_get_device_fallback_on_out_of_range_device_id(self):
        """Out-of-range device_id falls back to device 0."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.device_count.return_value = 1
        with patch.dict("sys.modules", {"torch": mock_torch}):
            device = get_device(device_id=5, require_cuda=False)
            assert device == "cuda:0"

    def test_gpu_status_report_no_cuda(self):
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.cuda.device_count.return_value = 0
        with patch.dict("sys.modules", {"torch": mock_torch}):
            report = gpu_status_report()
        assert report["cuda_available"] is False
        assert report["device_count"] == 0

    def test_gpu_status_report_with_cuda(self):
        mock_props = MagicMock()
        mock_props.name = "NVIDIA RTX 4090"
        mock_props.total_memory = 24 * 1024**3
        mock_props.major = 8
        mock_props.minor = 9

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.device_count.return_value = 1
        mock_torch.cuda.get_device_properties.return_value = mock_props

        with patch.dict("sys.modules", {"torch": mock_torch}):
            report = gpu_status_report()

        assert report["cuda_available"] is True
        assert report["device_count"] == 1
        devices = report["devices"]
        assert isinstance(devices, list)
        assert len(devices) == 1
        assert devices[0]["name"] == "NVIDIA RTX 4090"
