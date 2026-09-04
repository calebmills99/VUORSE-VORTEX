"""Tests for corpus indexing.

The canon-critical case is NON_MERGEABLE: two entities that share a token must
never collapse into one another, because exact-surface-form matching is the only
thing keeping them apart.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vuorse_vortex.indexing import (
    FINALE_PREFIX,
    NonMergeableCollapseError,
    build_entity_index,
    build_relationship_index,
    build_source_manifest,
    is_current,
    is_distinctive,
    iter_source_files,
    route_for,
    slugify,
)


def _write_canon(tmp_path: Path, payload: dict) -> Path:
    index_path = tmp_path / "canon" / "slayverse_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload), encoding="utf-8")
    return Path("canon/slayverse_index.json")


class TestSlugify:
    def test_is_deterministic(self) -> None:
        assert slugify("Hildebrand von Hooplehopper") == slugify("Hildebrand von Hooplehopper")

    def test_matches_canon_index_convention(self) -> None:
        assert slugify("Hildebrand von Hooplehopper") == "hildebrand-von-hooplehopper"

    def test_collapses_punctuation_and_trims(self) -> None:
        assert slugify("  canon/places/places.md  ") == "canon-places-places-md"


class TestIsDistinctive:
    def test_allcaps_coined_name_qualifies_at_five(self) -> None:
        assert is_distinctive("VUORSE")

    def test_stoplisted_token_is_rejected_regardless_of_length(self) -> None:
        # Long enough to pass the length gate, but an ordinary word in a
        # software corpus, so the stoplist must win.
        assert not is_distinctive("archivist")
        assert not is_distinctive("Archivist")
        assert not is_distinctive("parallax")

    def test_coined_name_of_the_same_length_still_qualifies(self) -> None:
        assert is_distinctive("Hooplehopper")

    def test_short_ordinary_word_is_rejected(self) -> None:
        assert not is_distinctive("Pop")

    def test_long_surname_qualifies(self) -> None:
        assert is_distinctive("McCullen")


class TestRouting:
    def test_longest_prefix_wins(self) -> None:
        route = route_for("synthetic_enrichment/validated/x.jsonl")
        assert route is not None
        assert route.layer == "apocrypha"
        assert route.sealed

    def test_canon_is_public_and_unsealed(self) -> None:
        route = route_for("canon/characters/foo.md")
        assert route is not None
        assert route.visibility == "public"
        assert not route.sealed

    def test_canon_status_is_unknown_not_guessed(self) -> None:
        route = route_for("canon/characters/foo.md")
        assert route is not None
        assert route.canon_status == "unknown"

    def test_unknown_location_has_no_route(self) -> None:
        assert route_for("web/src/App.tsx") is None

    def test_backslash_paths_route_the_same(self) -> None:
        assert route_for("canon\\places\\places.md") == route_for("canon/places/places.md")


class TestFinaleWithholding:
    def _seed(self, tmp_path: Path) -> None:
        finale = tmp_path / FINALE_PREFIX
        finale.mkdir(parents=True)
        (finale / "slow_reveal.md").write_text("x", encoding="utf-8")
        (tmp_path / "roadmap" / "season_1").mkdir(parents=True)
        (tmp_path / "roadmap" / "season_1" / "README.md").write_text("x", encoding="utf-8")

    def test_finale_is_withheld_by_default(self, tmp_path: Path) -> None:
        self._seed(tmp_path)
        found = [p.name for p in iter_source_files(["roadmap"], base=tmp_path)]
        assert found == ["README.md"]

    def test_finale_included_only_on_explicit_opt_in(self, tmp_path: Path) -> None:
        self._seed(tmp_path)
        found = {
            p.name for p in iter_source_files(["roadmap"], base=tmp_path, include_finale=True)
        }
        assert found == {"README.md", "slow_reveal.md"}


class TestEntityIndex:
    def test_non_mergeable_collapse_raises(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [
                    {"id": "miss-slaytonia-vuorse", "name": "Miss Slaytonia", "aliases": []},
                    {"id": "miss-slaytonia-verse", "name": "Miss Slaytonia", "aliases": []},
                ],
            },
        )
        with pytest.raises(NonMergeableCollapseError):
            build_entity_index(rel, out_path=None, base=tmp_path)

    def test_distinct_surface_forms_survive(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [
                    {"id": "miss-slaytonia-vuorse", "name": "Miss Slaytonia VUORSE"},
                    {"id": "miss-slaytonia-verse", "name": "Miss Slaytonia Verse"},
                ],
            },
        )
        index = build_entity_index(rel, out_path=None, base=tmp_path)
        assert index["entity_count"] == 2

    def test_truncated_grand_alias_is_repaired(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [
                    {
                        "id": "miss-slaytonia-vuorse",
                        "name": "Miss Slaytonia VUORSE",
                        "aliases": ["Grand"],
                    }
                ],
            },
        )
        index = build_entity_index(rel, out_path=None, base=tmp_path)
        forms = index["entities"]["miss-slaytonia-vuorse"]["surface_forms"]
        assert "Grand Oracle of the Velvet Archive" in forms
        assert "Grand" not in forms
        assert index["repairs_applied"]


class TestRelationshipIndex:
    def test_dangling_edges_are_reported_not_dropped_silently(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [{"id": "a", "name": "A"}],
                "relationships": [{"from": "a", "to": "ghost", "type": "mentor"}],
            },
        )
        index = build_relationship_index(rel, out_path=None, base=tmp_path)
        assert index["edge_count"] == 0
        assert index["dangling_count"] == 1
        assert index["dangling_edges"][0]["missing"] == ["to"]

    def test_dangling_related_refs_are_caught(self, tmp_path: Path) -> None:
        # `related` is a second edge set. A clean `relationships` array must not
        # be allowed to report a clean graph while these point at nothing.
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [{"id": "a", "name": "A", "related": ["ghost", "b"]}],
                "relationships": [],
            },
        )
        index = build_relationship_index(rel, out_path=None, base=tmp_path)
        assert index["dangling_count"] == 0
        assert index["dangling_related_count"] == 2
        assert index["dangling_related"] == {"a": ["b", "ghost"]}

    def test_no_dangling_related_when_all_resolve(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [{"id": "a", "name": "A", "related": ["b"]}, {"id": "b", "name": "B"}],
                "relationships": [],
            },
        )
        index = build_relationship_index(rel, out_path=None, base=tmp_path)
        assert index["dangling_related"] == {}
        assert index["dangling_related_count"] == 0

    def test_adjacency_is_undirected_and_deduplicated(self, tmp_path: Path) -> None:
        rel = _write_canon(
            tmp_path,
            {
                "version": "test",
                "entities": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
                "relationships": [
                    {"from": "a", "to": "b", "type": "mentor"},
                    {"from": "a", "to": "b", "type": "soul-line-succession"},
                ],
            },
        )
        index = build_relationship_index(rel, out_path=None, base=tmp_path)
        assert index["adjacency"] == {"a": ["b"], "b": ["a"]}


class TestSourceManifest:
    def test_jsonl_metadata_outranks_the_routing_table(self, tmp_path: Path) -> None:
        target = tmp_path / "canon" / "records.jsonl"
        target.parent.mkdir(parents=True)
        record = {
            "layer": "hooplehopper_totality",
            "metadata": {"visibility": "weaver_only", "canon_status": "roadmap_private"},
        }
        target.write_text(json.dumps(record) + "\n", encoding="utf-8")

        manifest, report = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        entry = manifest["sources"][0]
        # Location says public canon; the record says sealed. The record wins.
        assert entry["layer"] == "hooplehopper_totality"
        assert entry["visibility"] == "weaver_only"
        assert report.sealed_entries == 1

    def test_mixed_privacy_posture_is_flagged(self, tmp_path: Path) -> None:
        target = tmp_path / "canon" / "mixed.jsonl"
        target.parent.mkdir(parents=True)
        rows = [
            {
                "layer": "canon",
                "metadata": {"visibility": "public", "canon_status": "locked"},
            },
            {
                "layer": "hooplehopper_totality",
                "metadata": {"visibility": "weaver_only", "canon_status": "roadmap_private"},
            },
        ]
        target.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

        _, report = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        assert "canon/mixed.jsonl" in report.mixed_files

    def test_missing_root_is_reported_as_stale(self, tmp_path: Path) -> None:
        _, report = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        assert any("canon (declared root does not exist)" in s for s in report.stale_paths)

    def test_uppercase_suffixes_are_indexed(self, tmp_path: Path) -> None:
        # Book One ships as Words_of_Weaver_BOOK_ONE.MD. A case-sensitive
        # suffix check silently drops the supreme doctrine from the corpus.
        canon = tmp_path / "canon" / "1_words_of_weaver_book_one"
        canon.mkdir(parents=True)
        (canon / "Words_of_Weaver_BOOK_ONE.MD").write_text("doctrine", encoding="utf-8")

        manifest, _ = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        assert [s["path"] for s in manifest["sources"]] == [
            "canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD"
        ]
        assert manifest["sources"][0]["source_type"] == "markdown"

    def test_uppercase_pdf_still_withheld_by_default(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "render.PDF").write_bytes(b"%PDF-1.4")
        manifest, _ = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        assert manifest["sources"] == []

    def test_pdf_renders_withheld_by_default(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "places.md").write_text("x", encoding="utf-8")
        (canon / "places.pdf").write_bytes(b"%PDF-1.4")

        manifest, _ = build_source_manifest(["canon"], out_path=None, base=tmp_path)
        assert [s["source_type"] for s in manifest["sources"]] == ["markdown"]

        with_pdf, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, include_pdf=True
        )
        assert {s["source_type"] for s in with_pdf["sources"]} == {"markdown", "pdf"}


class TestDriftCheck:
    def test_is_current_false_when_absent(self, tmp_path: Path) -> None:
        assert not is_current(tmp_path / "nope.json", {"a": 1})

    def test_is_current_true_after_write(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "a.md").write_text("x", encoding="utf-8")
        out = Path("manifests/corpus/source_manifest.json")
        manifest, _ = build_source_manifest(["canon"], out_path=out, base=tmp_path)
        assert is_current(tmp_path / out, manifest)
