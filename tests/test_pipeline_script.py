"""Smoke gate for scripts/run_synthetic_pipeline.py — imports without GPU."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "run_synthetic_pipeline.py"

MANIFEST_ENV_VAR = "VUORSE_APPROVED_MANIFEST"


def _load_module() -> Any:
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


def test_pipeline_refuses_without_env_var(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Unset VUORSE_APPROVED_MANIFEST → exit non-zero, refusal names env var + producer."""
    monkeypatch.delenv(MANIFEST_ENV_VAR, raising=False)
    module = _load_module()

    rc = module.main([])

    assert rc != 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert MANIFEST_ENV_VAR in combined
    assert "synthesize-interactive" in combined


def test_pipeline_refuses_on_missing_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Env var set to a nonexistent path → exit non-zero, refusal mentions env var + producer."""
    missing = tmp_path / "does_not_exist.jsonl"
    monkeypatch.setenv(MANIFEST_ENV_VAR, str(missing))
    module = _load_module()

    rc = module.main([])

    assert rc != 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert MANIFEST_ENV_VAR in combined
    assert "synthesize-interactive" in combined


def test_pipeline_refuses_on_invalid_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Manifest exists but validate_jsonl rejects it → exit non-zero, refusal includes errors."""
    bogus = tmp_path / "bogus.jsonl"
    bogus.write_text('{"not_a_memory_record": true}\n', encoding="utf-8")
    monkeypatch.setenv(MANIFEST_ENV_VAR, str(bogus))
    module = _load_module()

    rc = module.main([])

    assert rc != 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert MANIFEST_ENV_VAR in combined
    assert "synthesize-interactive" in combined


def test_pipeline_refuses_on_empty_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Empty (zero records) or blank-only manifest → refusal, not silent embed."""
    empty = tmp_path / "empty.jsonl"
    empty.write_text("\n   \n\t\n", encoding="utf-8")
    monkeypatch.setenv(MANIFEST_ENV_VAR, str(empty))
    module = _load_module()

    rc = module.main([])

    assert rc != 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert MANIFEST_ENV_VAR in combined
    assert "synthesize-interactive" in combined


def test_pipeline_refuses_on_malformed_jsonl(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Syntactically malformed JSONL → refusal, not a JSON parse traceback."""
    malformed = tmp_path / "malformed.jsonl"
    malformed.write_text(
        '{"id": "truncated_record", "layer": "canon",\n', encoding="utf-8"
    )
    monkeypatch.setenv(MANIFEST_ENV_VAR, str(malformed))
    module = _load_module()

    rc = module.main([])

    assert rc != 0
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert MANIFEST_ENV_VAR in combined
    assert "synthesize-interactive" in combined
