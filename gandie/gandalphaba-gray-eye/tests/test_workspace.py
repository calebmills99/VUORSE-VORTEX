from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVICE_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / ("agent-framework-agent-with-local-tools-responses")
)
sys.path.insert(0, str(SERVICE_DIR))

from workspace import (  # noqa: E402
    inspect_prune_target,
    prune_exact_file,
    read_working_file,
    resolve_working_path,
    restore_pruned_file,
    visible_hit_payloads,
    write_working_file,
)


def _make_repository(root: Path) -> Path:
    for required in (
        "policies/disclosure/README.md",
        "manifests/corpus/source_manifest.json",
        "vuorse_vortex/__init__.py",
    ):
        path = root / required
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    return root


def test_working_path_allows_only_configured_outputs(tmp_path: Path) -> None:
    root = _make_repository(tmp_path)

    assert resolve_working_path("worldforge/gandalphaba/run/report.md", root) == (
        root / "worldforge" / "gandalphaba" / "run" / "report.md"
    )
    assert (
        resolve_working_path("worldforge/worldforge/lore-index-2.0/proposal.json", root)
        == root / "worldforge" / "worldforge" / "lore-index-2.0" / "proposal.json"
    )
    with pytest.raises(PermissionError):
        resolve_working_path("canon/characters/characters.md", root)
    with pytest.raises(PermissionError):
        resolve_working_path("policies/disclosure/README.md", root)
    with pytest.raises(PermissionError):
        resolve_working_path(
            "worldforge/2026-09-05-vuorse-vortex-reassessment/SEALED-REPORT.md",
            root,
        )
    with pytest.raises(ValueError):
        resolve_working_path("worldforge/../../roadmap/finale/secret.md", root)
    with pytest.raises(ValueError):
        resolve_working_path(r"C:\outside\report.md", root)


def test_write_and_hash_checked_replace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _make_repository(tmp_path)
    monkeypatch.setenv("VUORSE_REPO_ROOT", str(root))

    created = write_working_file("manifests/runs/gandalphaba/run-1.json", '{"state":"proposed"}')
    assert created["operation"] == "created"

    before = read_working_file("manifests/runs/gandalphaba/run-1.json")
    replaced = write_working_file(
        "manifests/runs/gandalphaba/run-1.json",
        '{"state":"reviewed"}',
        expected_sha256=before["sha256"],
    )
    assert replaced["operation"] == "replaced"
    assert read_working_file("manifests/runs/gandalphaba/run-1.json")["content"] == (
        '{"state":"reviewed"}'
    )


def test_existing_file_requires_a_current_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_repository(tmp_path)
    monkeypatch.setenv("VUORSE_REPO_ROOT", str(root))
    write_working_file("worldforge/gandalphaba/run/report.md", "draft")

    with pytest.raises(FileExistsError):
        write_working_file("worldforge/gandalphaba/run/report.md", "replacement")
    with pytest.raises(RuntimeError, match="changed since it was read"):
        write_working_file(
            "worldforge/gandalphaba/run/report.md",
            "replacement",
            expected_sha256="not-the-current-hash",
        )


def test_search_filters_visibility_and_sealed_layers() -> None:
    hits = [
        {
            "visibility": "public",
            "layer": "canon",
            "source_path": "canon/places/place.md",
        },
        {
            "visibility": "behavioral",
            "layer": "persona",
            "source_path": "persona/voice.md",
        },
        {
            "visibility": "private_to_vuorse",
            "layer": "synthetic_enrichment",
            "source_path": "synthetic_enrichment/private.jsonl",
        },
        {
            "visibility": "public",
            "layer": "hooplehopper_totality",
            "source_path": "hooplehopper_totality/private.jsonl",
        },
    ]

    visible = visible_hit_payloads(hits, {"hooplehopper_totality"})

    assert [hit["source_path"] for hit in visible] == [
        "canon/places/place.md",
        "persona/voice.md",
    ]


def test_pruning_requires_exact_in_repo_file_and_current_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_repository(tmp_path)
    monkeypatch.setenv("VUORSE_REPO_ROOT", str(root))
    target = root / "canon" / "retired.md"
    target.parent.mkdir(parents=True)
    target.write_text("retired record", encoding="utf-8")

    inspected = inspect_prune_target("canon/retired.md")
    with pytest.raises(ValueError):
        inspect_prune_target("canon/*.md")
    with pytest.raises(PermissionError):
        inspect_prune_target(".agent-quarantine/README.md")
    with pytest.raises(RuntimeError, match="changed since inspection"):
        prune_exact_file("canon/retired.md", expected_sha256="stale-hash")

    result = prune_exact_file("canon/retired.md", expected_sha256=inspected["sha256"])
    assert result["operation"] == "pruned"
    assert not target.exists()
    assert (root / result["archive_path"]).is_file()

    restored = restore_pruned_file(result["archive_id"])
    assert restored["operation"] == "restored"
    assert target.read_text(encoding="utf-8") == "retired record"

    with pytest.raises(PermissionError):
        read_working_file(result["archive_path"])
