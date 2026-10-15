from __future__ import annotations

import json
from pathlib import Path

from vuorse_vortex.lore_index import validate_lore_index

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_ROOT = REPO_ROOT / "worldforge" / "worldforge" / "lore-index-2.0"
INDEX_PATH = INDEX_ROOT / "slayverse_lore_index_2.0.json"
SCHEMA_PATH = INDEX_ROOT / "slayverse_lore_index_2.0.schema.json"
MANIFEST_PATH = REPO_ROOT / "manifests" / "corpus" / "source_manifest.json"


def test_shipped_lore_index_is_repository_complete() -> None:
    errors = validate_lore_index(
        INDEX_PATH,
        SCHEMA_PATH,
        MANIFEST_PATH,
        repo_root=REPO_ROOT,
    )
    assert errors == []


def test_validator_rejects_duplicate_ids(tmp_path: Path) -> None:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    index["documents"][0]["id"] = index["entities"][0]["id"]
    broken = tmp_path / "index.json"
    broken.write_text(json.dumps(index), encoding="utf-8")

    errors = validate_lore_index(
        broken,
        SCHEMA_PATH,
        MANIFEST_PATH,
        repo_root=REPO_ROOT,
    )

    assert any("global duplicate ids" in error for error in errors)


def test_validator_rejects_missing_governed_source(tmp_path: Path) -> None:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    index["sources"] = [
        source
        for source in index["sources"]
        if source.get("manifest_source_id")
        != "canon-1-words-of-weaver-book-one-words-of-weaver-book-one"
    ]
    broken = tmp_path / "index.json"
    broken.write_text(json.dumps(index), encoding="utf-8")

    errors = validate_lore_index(
        broken,
        SCHEMA_PATH,
        MANIFEST_PATH,
        repo_root=REPO_ROOT,
    )

    assert any("governed manifest sources absent" in error for error in errors)
