from pathlib import Path

from vuorse_vortex.debrief_import import extract_strongest_private_theses
from vuorse_vortex.jsonl import validate_jsonl


def test_extract_strongest_private_theses(tmp_path: Path) -> None:
    source = Path("hooplehopper_totality/debriefing_walled.jsonl")
    if not source.exists():
        return

    out = tmp_path / "private.jsonl"
    records = extract_strongest_private_theses(source, out, limit=3, id_prefix="test_private")

    assert len(records) == 3
    assert out.exists()
    assert validate_jsonl(out) == []
    assert all(r.layer == "hooplehopper_totality" for r in records)
    assert all(r.behavior.may_state_as_fact is False for r in records)
    assert all(r.behavior.may_reveal_to_user is False for r in records)
    assert records[0].id == "test_private_001"
