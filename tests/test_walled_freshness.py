"""CI gate: committed walled JSONL must match what build_walled produces from the .md.

Skips if either file is absent so this test passes immediately after a refactor
that merges before the real walled markdown is authored.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vuorse_vortex.walled import build_walled_check

_MD_PATH = Path("hooplehopper_totality/debriefing_walled.md")
_JSONL_PATH = Path("hooplehopper_totality/debriefing_walled.jsonl")


@pytest.mark.skipif(
    not (_MD_PATH.exists() and _JSONL_PATH.exists()),
    reason="walled .md or .jsonl absent (pre-T5 merge state).",
)
def test_walled_jsonl_matches_markdown_source() -> None:
    assert build_walled_check(_MD_PATH, _JSONL_PATH), (
        f"{_JSONL_PATH} is out of sync with {_MD_PATH}. "
        "Run `uv run vuorse-vortex build-walled` to regenerate."
    )
