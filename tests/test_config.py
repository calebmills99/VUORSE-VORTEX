"""Tests for config management."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from vuorse_vortex.config import LogLevel, Settings, VectorBackend, get_settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.archive_name == "velvet-archive"
        assert settings.vector_backend == VectorBackend.CHROMADB
        assert settings.require_cuda is True
        assert settings.firewall_strict_mode is True
        assert "roadmap_manifest" in settings.sealed_categories

    def test_env_override(self):
        with patch.dict(os.environ, {"VORTEX_ARCHIVE_NAME": "test-archive"}):
            settings = Settings()
            assert settings.archive_name == "test-archive"

    def test_vector_backend_enum(self):
        with patch.dict(os.environ, {"VORTEX_VECTOR_BACKEND": "qdrant"}):
            settings = Settings()
            assert settings.vector_backend == VectorBackend.QDRANT

    def test_log_level_enum(self):
        with patch.dict(os.environ, {"VORTEX_LOG_LEVEL": "DEBUG"}):
            settings = Settings()
            assert settings.log_level == LogLevel.DEBUG

    def test_manifests_dir_is_path(self):
        settings = Settings()
        assert isinstance(settings.manifests_dir, Path)

    def test_get_settings_returns_settings(self):
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_sealed_categories_default(self):
        settings = Settings()
        assert "roadmap_manifest" in settings.sealed_categories

    def test_embedding_dimension_default(self):
        settings = Settings()
        assert settings.embedding_dimension == 384

    def test_cuda_device_id_default(self):
        settings = Settings()
        assert settings.cuda_device_id == 0
