"""CPU-safe tests for the `vuorse-vortex embed` CLI command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from vuorse_vortex import cli
from vuorse_vortex.synthesis import theses_as_jsonl
from vuorse_vortex.vector import VectorDBBackend


class _FakeBackend(VectorDBBackend):
    """Captures ingest calls without loading any GPU stack."""

    def __init__(self) -> None:
        super().__init__()
        self.ingested: list[dict[str, Any]] = []

    def ingest(self, records: list[Any]) -> int:
        # Normalize: accept dicts straight from the JSONL iterator.
        self.ingested.extend(records)
        return len(records)


@pytest.fixture
def synthetic_jsonl(tmp_path: Path) -> Path:
    path = tmp_path / "theses.jsonl"
    path.write_text(theses_as_jsonl() + "\n", encoding="utf-8")
    return path


def test_embed_command_validates_and_ingests(
    synthetic_jsonl: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _FakeBackend()
    monkeypatch.setattr(cli, "get_backend", lambda settings=None: fake)

    runner = CliRunner()
    result = runner.invoke(cli.app, ["embed", str(synthetic_jsonl)])

    assert result.exit_code == 0, result.output
    assert "Ingested 3 records." in result.output
    assert len(fake.ingested) == 3


def test_embed_command_rejects_invalid_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    runner = CliRunner()
    result = runner.invoke(cli.app, ["embed", str(missing)])
    assert result.exit_code == 1
    assert "File not found" in result.output


def test_embed_command_surfaces_firewall_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Build a record that violates the canon firewall: a sealed layer with
    # may_state_as_fact=True should be rejected before any ingest happens.
    bad = (
        '{"id":"bad-1","layer":"apocrypha","record_type":"test","title":"x","text":"y",'
        '"metadata":{"canon_status":"locked","visibility":"public","tags":[]},'
        '"retrieval":{"priority":5,"embedding_weight":"low","query_hints":[]},'
        '"behavior":{"may_state_as_fact":true,"may_use_for_voice":true,'
        '"may_reveal_to_user":false}}'
    )
    path = tmp_path / "bad.jsonl"
    path.write_text(bad + "\n", encoding="utf-8")

    fake = _FakeBackend()
    monkeypatch.setattr(cli, "get_backend", lambda settings=None: fake)

    runner = CliRunner()
    result = runner.invoke(cli.app, ["embed", str(path)])
    assert result.exit_code == 1
    assert "may_state_as_fact" in result.output
    assert fake.ingested == []


def test_embed_command_rejects_unsupported_faiss_backend(synthetic_jsonl: Path) -> None:
    """`--backend faiss` must fail loudly, not silently swap to ChromaDB.

    Pre-fix the FAISS backend accepted ``ingest()`` calls and reported success
    while persisting nothing. The Settings literal is now narrowed to
    ``"chromadb"`` so Pydantic rejects the override at ``model_copy`` time.
    Surface that failure as a non-zero CLI exit so automation notices.
    """
    runner = CliRunner()
    result = runner.invoke(cli.app, ["embed", str(synthetic_jsonl), "--backend", "faiss"])
    assert result.exit_code != 0
    # Either the typer wrapper or the Pydantic ValidationError needs to be on
    # stdout/stderr — both are acceptable, what matters is the loud failure.
    combined = (result.output or "") + (str(result.exception) if result.exception else "")
    assert "faiss" in combined.lower() or "vector_backend" in combined.lower()
