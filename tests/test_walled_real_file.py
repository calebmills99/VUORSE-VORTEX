"""Real-file gate: when the committed walled JSONL exists, prove it loads cleanly.

Skips if the file is absent (pre-T5 merge state), so the test silently passes
in any clone that hasn't authored the walled markdown yet.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vuorse_vortex.jsonl import validate_jsonl
from vuorse_vortex.walled import load_walled_atoms

_JSONL_PATH = Path("hooplehopper_totality/debriefing_walled.jsonl")


@pytest.mark.skipif(
    not _JSONL_PATH.exists(),
    reason="hooplehopper_totality/debriefing_walled.jsonl absent.",
)
def test_real_walled_jsonl_validates_and_loads() -> None:
    errors = validate_jsonl(_JSONL_PATH)
    assert errors == [], errors

    atoms = load_walled_atoms(_JSONL_PATH)
    assert len(atoms) >= 1
