"""Shared pytest fixtures for VUORSE-VORTEX tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from vuorse_vortex.walled import build_walled

WALLED_FIXTURE_MD = """\
# Walled Atoms Fixture

## Velvet Archive

```yaml
concept: velvet archive
layer_affinity: hooplehopper_totality
tags:
  - velvet-archive
  - anti-erasure
premise_fragment: Continuity can be attacked through retrievability.
synthesis_fragment: Velvet survives as distributed memory.
```

## Apocryphal Wound

```yaml
concept: apocryphal wound
layer_affinity: apocrypha
tags:
  - silence
  - wound
premise_fragment: The wound and the silence are the same wound.
synthesis_fragment: Unspoken truths manifest geographically.
```

## Soul Line Recurrence

```yaml
concept: soul line recurrence
layer_affinity: canon
tags:
  - soul-line
  - recurrence
premise_fragment: Blood reproduces. The soul-line recurs.
synthesis_fragment: The Hooplehoppers do not descend. They return.
```

## Ritual Anchor

```yaml
concept: ritual anchor
layer_affinity: ritual_logic
tags:
  - ritual
  - memory
premise_fragment: Ritual operates where official history has been scrubbed.
synthesis_fragment: Repetition of the rite acts as a structural anchor.
```

## Performance Survival

```yaml
concept: performance survival
layer_affinity: persona
tags:
  - performance
  - drag
  - survival-tech
premise_fragment: Hooplehopper aesthetics intensify around erasure pressure.
synthesis_fragment: Camp and drag are survival technologies, not decoration.
```
"""


@pytest.fixture()
def walled_jsonl(tmp_path: Path) -> Path:
    """Build a walled JSONL fixture (5 atoms, 5 distinct layer_affinity values)."""
    md = tmp_path / "walled_fixture.md"
    md.write_text(WALLED_FIXTURE_MD, encoding="utf-8")
    out = tmp_path / "walled_fixture.jsonl"
    build_walled(md, out)
    return out


@pytest.fixture()
def patch_walled_pool(
    walled_jsonl: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Point ``synthesis._DEFAULT_WALLED_JSONL`` at the in-fixture walled JSONL."""
    monkeypatch.setattr(
        "vuorse_vortex.synthesis._DEFAULT_WALLED_JSONL",
        walled_jsonl,
    )
    return walled_jsonl
