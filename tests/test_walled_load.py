"""Tests for the walled JSONL -> LoreAtom load path."""

from __future__ import annotations

from pathlib import Path

import orjson
import pytest

from vuorse_vortex.walled import (
    WalledFileEmptyError,
    WalledFileMissingError,
    WalledFileParseError,
    build_walled,
    load_walled_atoms,
)

FIXTURE_MD = """\
# Walled Atoms

## Velvet Archive

```yaml
concept: velvet archive
layer_affinity: hooplehopper_totality
tags:
  - velvet-archive
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
"""


@pytest.fixture()
def walled_jsonl(tmp_path: Path) -> Path:
    md = tmp_path / "walled.md"
    md.write_text(FIXTURE_MD, encoding="utf-8")
    out = tmp_path / "walled.jsonl"
    build_walled(md, out)
    return out


def test_load_happy_path(walled_jsonl: Path) -> None:
    atoms = load_walled_atoms(walled_jsonl)
    assert len(atoms) == 4


def test_load_sort_by_concept_default(walled_jsonl: Path) -> None:
    atoms = load_walled_atoms(walled_jsonl)
    concepts = [a.concept for a in atoms]
    assert concepts == sorted(concepts)


def test_load_preserve_order(walled_jsonl: Path) -> None:
    atoms = load_walled_atoms(walled_jsonl, preserve_order=True)
    # Source order matches FIXTURE_MD sections
    concepts = [a.concept for a in atoms]
    assert concepts == [
        "velvet archive",
        "apocryphal wound",
        "soul line recurrence",
        "ritual anchor",
    ]


def test_load_premise_synthesis_roundtrip(walled_jsonl: Path) -> None:
    atoms = load_walled_atoms(walled_jsonl, preserve_order=True)
    velvet = atoms[0]
    assert velvet.concept == "velvet archive"
    assert velvet.layer_affinity == "hooplehopper_totality"
    assert velvet.premise_fragment == "Continuity can be attacked through retrievability."
    assert velvet.synthesis_fragment == "Velvet survives as distributed memory."
    assert "velvet-archive" in velvet.tags


def test_load_null_layer_affinity_raises(tmp_path: Path, walled_jsonl: Path) -> None:
    # Mutate the first record to drop layer_affinity
    raw_lines = walled_jsonl.read_text(encoding="utf-8").splitlines()
    parsed = [orjson.loads(ln) for ln in raw_lines if ln.strip()]
    parsed[0]["metadata"]["layer_affinity"] = None
    mutated = "\n".join(orjson.dumps(obj).decode("utf-8") for obj in parsed) + "\n"
    walled_jsonl.write_text(mutated, encoding="utf-8")
    with pytest.raises(WalledFileParseError) as ei:
        load_walled_atoms(walled_jsonl)
    assert "layer_affinity" in str(ei.value)


def test_load_missing_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "nope.jsonl"
    with pytest.raises(WalledFileMissingError):
        load_walled_atoms(p)


def test_load_empty_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    with pytest.raises(WalledFileEmptyError):
        load_walled_atoms(p)


def test_load_malformed_line_raises(tmp_path: Path, walled_jsonl: Path) -> None:
    raw = walled_jsonl.read_text(encoding="utf-8")
    # Inject a bad line at position 2 (line 3 in the file).
    lines = raw.splitlines()
    lines.insert(1, "{not valid json")
    walled_jsonl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(WalledFileParseError) as ei:
        load_walled_atoms(walled_jsonl)
    # Bad JSON is on the 2nd line of file after insert.
    assert ":2:" in str(ei.value)
