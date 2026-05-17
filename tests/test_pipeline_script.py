"""Smoke gate for scripts/run_synthetic_pipeline.py — imports without GPU."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_synthetic_pipeline.py"


def _load_module() -> object:
    spec = importlib.util.spec_from_file_location(
        "_run_synthetic_pipeline_under_test", SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_exists() -> None:
    assert SCRIPT_PATH.is_file(), f"missing pipeline script: {SCRIPT_PATH}"


def test_script_exposes_main_entry() -> None:
    module = _load_module()
    main = getattr(module, "main", None)
    assert callable(main), "scripts/run_synthetic_pipeline.py must expose a callable main()"
