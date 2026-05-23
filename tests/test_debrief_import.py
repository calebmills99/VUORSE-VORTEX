from pathlib import Path

import pytest

from vuorse_vortex.debrief_import import extract_strongest_private_theses
from vuorse_vortex.jsonl import validate_jsonl


def test_extract_strongest_private_theses(tmp_path: Path) -> None:
    source = Path("hooplehopper_totality/debriefing_walled.jsonl")
    if not source.exists():
        pytest.skip(
            f"Debrief source file not present: {source}. "
            "Run `uv run vuorse-vortex build-walled` to generate it."
        )

    out = tmp_path / "private.jsonl"
    records = extract_strongest_private_theses(source, out, limit=3, id_prefix="test_private")

    assert len(records) == 3
    assert out.exists()
    assert validate_jsonl(out) == []
    assert all(r.layer == "hooplehopper_totality" for r in records)
    assert all(r.behavior.may_state_as_fact is False for r in records)
    assert all(r.behavior.may_reveal_to_user is False for r in records)
    assert records[0].id == "test_private_001"


def test_extract_empty_source_produces_empty_file(tmp_path: Path) -> None:
    """When source JSONL is empty, output file should be empty (not a blank line)."""
    source = tmp_path / "empty_source.jsonl"
    source.write_text("", encoding="utf-8")

    out = tmp_path / "empty_out.jsonl"
    records = extract_strongest_private_theses(source, out, limit=5, id_prefix="empty_test")

    assert records == []
    assert out.exists()
    assert out.read_text(encoding="utf-8") == ""
