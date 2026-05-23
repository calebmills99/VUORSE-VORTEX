"""Tests for private debrief MemoryRecord imports."""

from __future__ import annotations

import json
from pathlib import Path

import orjson
from typer.testing import CliRunner

from vuorse_vortex import cli
from vuorse_vortex.debrief_import import import_debrief_theses, resolve_debrief_source
from vuorse_vortex.jsonl import validate_jsonl

DEBRIEF_MD = """\
# Debrief

## Small

```yaml
concept: small
layer_affinity: persona
tags: [small]
premise_fragment: A small idea.
synthesis_fragment: It matters less than the wound.
```

## Wound Signal

```yaml
concept: wound signal
layer_affinity: apocrypha
tags: [wound, silence, jake, wyoming, hooplehopper-gap]
premise_fragment: The wound and silence are joined.
synthesis_fragment: Jake's denial should preserve pressure rather than solve the wound.
```

## Ritual Memory

```yaml
concept: ritual memory
layer_affinity: ritual_logic
tags: [ritual, memory, anti-erasure]
premise_fragment: Ritual operates where official history has been scrubbed.
synthesis_fragment: Repetition keeps private memory alive through embodied action.
```
"""


def _write_session(path: Path, relative: str) -> Path:
    session = {
        "timestamp": "2026-05-23T13:07:38.840Z",
        "events": [{"relativePath": relative, "eventType": "file_edit"}],
    }
    path.write_text(json.dumps(session), encoding="utf-8")
    return path


def test_resolve_debrief_source_from_frolic_session(tmp_path: Path) -> None:
    source = tmp_path / "notes" / "session_debrief.md"
    source.parent.mkdir()
    source.write_text(DEBRIEF_MD, encoding="utf-8")
    session = _write_session(tmp_path / ".frolic-session.json", "notes/session_debrief.md")

    assert resolve_debrief_source(session) == source


def test_import_debrief_theses_writes_valid_private_records(tmp_path: Path) -> None:
    source = tmp_path / "debrief.md"
    source.write_text(DEBRIEF_MD, encoding="utf-8")
    session = _write_session(tmp_path / ".frolic-session.json", "debrief.md")
    output = tmp_path / "synthetic_enrichment" / "validated" / "private.jsonl"

    result = import_debrief_theses(session_path=session, output_path=output, limit=2)

    assert result.record_count == 2
    assert validate_jsonl(output) == []
    records = [
        orjson.loads(line)
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert records[0]["id"].startswith("debrief_private_20260523_")
    assert {record["layer"] for record in records} == {"hooplehopper_totality"}
    assert all(record["behavior"]["may_state_as_fact"] is False for record in records)
    assert all(record["behavior"]["may_reveal_to_user"] is False for record in records)
    assert any(record["title"] == "Wound Signal" for record in records)


def test_import_debrief_cli(tmp_path: Path) -> None:
    source = tmp_path / "debrief.md"
    source.write_text(DEBRIEF_MD, encoding="utf-8")
    session = _write_session(tmp_path / ".frolic-session.json", "debrief.md")
    output = tmp_path / "out.jsonl"

    result = CliRunner().invoke(
        cli.app,
        [
            "import-debrief",
            "--session",
            str(session),
            "--output",
            str(output),
            "--limit",
            "1",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Imported 1 private theses" in result.output
    assert validate_jsonl(output) == []
