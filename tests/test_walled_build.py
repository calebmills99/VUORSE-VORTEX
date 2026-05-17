"""Tests for the walled markdown -> JSONL build path."""

from __future__ import annotations

from pathlib import Path

import pytest

from vuorse_vortex.jsonl import validate_jsonl
from vuorse_vortex.walled import (
    WalledFileEmptyError,
    WalledFileMissingError,
    WalledFileParseError,
    build_walled,
    build_walled_check,
)

VALID_TWO_SECTIONS = """\
# Walled Atoms

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
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_build_happy_path(tmp_path: Path) -> None:
    md = _write(tmp_path, "walled.md", VALID_TWO_SECTIONS)
    out = tmp_path / "walled.jsonl"
    count = build_walled(md, out)
    assert count == 2
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    errors = validate_jsonl(out)
    assert errors == []


def test_build_missing_file(tmp_path: Path) -> None:
    md = tmp_path / "does_not_exist.md"
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileMissingError) as ei:
        build_walled(md, out)
    assert str(md) in str(ei.value)


def test_build_empty_file(tmp_path: Path) -> None:
    md = _write(tmp_path, "empty.md", "# title only\n\nNo sections.\n")
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileEmptyError):
        build_walled(md, out)


def test_build_malformed_yaml(tmp_path: Path) -> None:
    bad = """\
## Broken

```yaml
concept: foo
layer_affinity: canon
tags: [unterminated
premise_fragment: x
synthesis_fragment: y
```
"""
    md = _write(tmp_path, "bad.md", bad)
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileParseError) as ei:
        build_walled(md, out)
    assert "Broken" in str(ei.value)


def test_build_missing_required_key(tmp_path: Path) -> None:
    missing = """\
## Missing Key

```yaml
concept: foo
layer_affinity: canon
tags: [a]
premise_fragment: x
```
"""
    md = _write(tmp_path, "miss.md", missing)
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileParseError) as ei:
        build_walled(md, out)
    assert "synthesis_fragment" in str(ei.value)
    assert "Missing Key" in str(ei.value)


def test_build_unknown_yaml_key(tmp_path: Path) -> None:
    extra = """\
## Extra Key

```yaml
concept: foo
layer_affinity: canon
tags: [a]
premise_fragment: x
synthesis_fragment: y
forbidden_extra: 42
```
"""
    md = _write(tmp_path, "extra.md", extra)
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileParseError) as ei:
        build_walled(md, out)
    assert "forbidden_extra" in str(ei.value)
    assert "Extra Key" in str(ei.value)


def test_build_multiple_yaml_blocks_per_heading(tmp_path: Path) -> None:
    dup = """\
## Two Blocks

```yaml
concept: a
layer_affinity: canon
tags: []
premise_fragment: p
synthesis_fragment: s
```

```yaml
concept: b
layer_affinity: canon
tags: []
premise_fragment: p
synthesis_fragment: s
```
"""
    md = _write(tmp_path, "dup.md", dup)
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileParseError) as ei:
        build_walled(md, out)
    assert "Two Blocks" in str(ei.value)
    assert "2 yaml fenced blocks" in str(ei.value)


def test_build_zero_yaml_blocks_per_heading(tmp_path: Path) -> None:
    zero = """\
## No Block

Just prose here, no fence.

## Another No Block

Also no fence.
"""
    md = _write(tmp_path, "zero.md", zero)
    out = tmp_path / "walled.jsonl"
    with pytest.raises(WalledFileParseError) as ei:
        build_walled(md, out)
    assert "No Block" in str(ei.value) or "Another No Block" in str(ei.value)
    assert "zero yaml fenced blocks" in str(ei.value)


def test_build_check_mode_clean(tmp_path: Path) -> None:
    md = _write(tmp_path, "walled.md", VALID_TWO_SECTIONS)
    out = tmp_path / "walled.jsonl"
    build_walled(md, out)
    assert build_walled_check(md, out) is True


def test_build_check_mode_drifted(tmp_path: Path) -> None:
    md = _write(tmp_path, "walled.md", VALID_TWO_SECTIONS)
    out = tmp_path / "walled.jsonl"
    build_walled(md, out)
    # Mutate md so regen will differ
    mutated = VALID_TWO_SECTIONS.replace(
        "Continuity can be attacked through retrievability.",
        "Continuity can be attacked through scrubbed indexes.",
    )
    md.write_text(mutated, encoding="utf-8")
    assert build_walled_check(md, out) is False


def test_build_record_passes_validate_jsonl(tmp_path: Path) -> None:
    md = _write(tmp_path, "walled.md", VALID_TWO_SECTIONS)
    out = tmp_path / "walled.jsonl"
    build_walled(md, out)
    assert validate_jsonl(out) == []


def test_build_source_order_preserved(tmp_path: Path) -> None:
    md = _write(tmp_path, "walled.md", VALID_TWO_SECTIONS)
    out = tmp_path / "walled.jsonl"
    build_walled(md, out)
    import orjson

    lines = [
        orjson.loads(ln)
        for ln in out.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert lines[0]["id"] == "walled_velvet_archive"
    assert lines[1]["id"] == "walled_soul_line_recurrence"
