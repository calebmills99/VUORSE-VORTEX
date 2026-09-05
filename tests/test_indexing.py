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
    CurationFileError,
    DuplicateSourceIdError,
    NonMergeableCollapseError,
    build_entity_index,
    build_relationship_index,
    build_source_manifest,
    is_current,
    is_distinctive,
    iter_source_files,
    load_source_curation,
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


class TestSourceIdCollisions:
    """`x.jsonl` and `x.md` in one routed directory used to mint the same id.

    Regression origin: `hooplehopper_totality/debriefing_walled.{jsonl,md}` both
    reduced to `hooplehopper-totality-debriefing-walled`. The collision was
    detected, written into `notes` as prose, and the duplicate row emitted
    anyway -- which put 8 colliding chunk ids into the cortex index, each one
    pairing a `private_to_vuorse` chunk with a `weaver_only` chunk.
    """

    @staticmethod
    def _same_stem_pair(tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir(parents=True, exist_ok=True)
        (canon / "debriefing_walled.md").write_text("prose", encoding="utf-8")
        record = {
            "layer": "canon",
            "metadata": {"visibility": "public", "canon_status": "locked"},
        }
        (canon / "debriefing_walled.jsonl").write_text(
            json.dumps(record) + "\n", encoding="utf-8"
        )

    def test_same_stem_different_suffix_yields_distinct_ids(self, tmp_path: Path) -> None:
        self._same_stem_pair(tmp_path)
        manifest, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        ids = [s["id"] for s in manifest["sources"]]
        assert len(ids) == 2, f"expected both files indexed, got {ids}"
        assert len(set(ids)) == 2, f"duplicate ids survived: {ids}"
        # Disambiguation convention borrowed from walled._build_jsonl_text: the
        # first claimant in walk order keeps the base id, the next takes `-2`.
        assert ids == ["canon-debriefing-walled", "canon-debriefing-walled-2"]

    def test_ids_are_deterministic_across_two_runs(self, tmp_path: Path) -> None:
        self._same_stem_pair(tmp_path)
        first, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        second, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        assert [s["id"] for s in first["sources"]] == [s["id"] for s in second["sources"]]
        assert [(s["id"], s["path"]) for s in first["sources"]] == [
            (s["id"], s["path"]) for s in second["sources"]
        ]

    def test_disambiguated_ids_keep_their_own_visibility(self, tmp_path: Path) -> None:
        """The two rows must stay two rows, on their own sides of the boundary."""
        canon = tmp_path / "canon"
        canon.mkdir(parents=True)
        (canon / "walled.md").write_text("prose", encoding="utf-8")
        record = {
            "layer": "hooplehopper_totality",
            "metadata": {"visibility": "weaver_only", "canon_status": "roadmap_private"},
        }
        (canon / "walled.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

        manifest, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        by_id = {s["id"]: s for s in manifest["sources"]}
        assert len(by_id) == 2
        assert by_id["canon-walled"]["visibility"] == "weaver_only"
        assert by_id["canon-walled-2"]["visibility"] == "public"

    def test_collision_is_reported_not_narrated_into_notes(self, tmp_path: Path) -> None:
        self._same_stem_pair(tmp_path)
        manifest, report = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        assert len(report.disambiguated_ids) == 1
        message = report.disambiguated_ids[0]
        assert "canon/debriefing_walled.md" in message
        assert "canon-debriefing-walled-2" in message
        assert all(
            "collides" not in (s["notes"] or "") for s in manifest["sources"]
        ), "a detected collision must not be swallowed into a note on a duplicate row"

    def test_duplicate_ids_raise_rather_than_ship(self) -> None:
        """The last-line guard: private, but it is the invariant being defended."""
        from vuorse_vortex.indexing import _assert_unique_ids

        with pytest.raises(DuplicateSourceIdError) as excinfo:
            _assert_unique_ids(
                [
                    {"id": "twin", "path": "canon/a.md"},
                    {"id": "twin", "path": "canon/b.md"},
                ],
                Path("manifests/corpus/source_manifest.json"),
            )
        text = str(excinfo.value)
        assert "twin" in text
        assert "canon/a.md" in text and "canon/b.md" in text
        assert "manifests/corpus/source_manifest.json" in text


class TestSourceCurationOverlay:
    """Regeneration must not revert hand-audited `canon_status` and `notes`."""

    CURATION_REL = Path("manifests/corpus/source_curation.json")

    @classmethod
    def _write_curation(cls, tmp_path: Path, payload: object) -> Path:
        target = tmp_path / cls.CURATION_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            target.write_text(payload, encoding="utf-8")
        else:
            target.write_text(json.dumps(payload), encoding="utf-8")
        return cls.CURATION_REL

    def test_route_default_applies_without_an_overlay(self, tmp_path: Path) -> None:
        """Baseline: this is exactly the state T2 has to stop being permanent."""
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "artifacts.md").write_text("x", encoding="utf-8")
        manifest, report = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=None
        )
        assert manifest["sources"][0]["canon_status"] == "unknown"
        assert manifest["sources"][0]["notes"] == ""
        assert report.curated_paths == []

    def test_curation_survives_a_regeneration_round_trip(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "artifacts.md").write_text("x", encoding="utf-8")
        (canon / "retired.md").write_text("x", encoding="utf-8")
        provenance = "Self-declared 'Locked Canon' in frontmatter; corroborated by entity_index.json."
        curation = self._write_curation(
            tmp_path,
            {
                "sources": {
                    "canon/artifacts.md": {
                        "canon_status": "locked",
                        "notes": provenance,
                    },
                    "canon/retired.md": {"canon_status": "draft"},
                }
            },
        )
        out = Path("manifests/corpus/source_manifest.json")

        first, first_report = build_source_manifest(
            ["canon"], out_path=out, base=tmp_path, curation_path=curation
        )
        assert sorted(first_report.curated_paths) == [
            "canon/artifacts.md",
            "canon/retired.md",
        ]
        assert first_report.orphaned_curation == []

        # The corpus moves on: a file is added, a curated file is removed.
        (canon / "brand_new.md").write_text("x", encoding="utf-8")
        (canon / "retired.md").unlink()

        second, second_report = build_source_manifest(
            ["canon"], out_path=out, base=tmp_path, curation_path=curation
        )
        by_path = {s["path"]: s for s in second["sources"]}

        # R3/R4: curated fields survive.
        assert by_path["canon/artifacts.md"]["canon_status"] == "locked"
        assert by_path["canon/artifacts.md"]["notes"] == provenance
        # New sources still appear, at the route default until triaged.
        assert "canon/brand_new.md" in by_path
        assert by_path["canon/brand_new.md"]["canon_status"] == "unknown"
        # Removed sources still drop, and their curation is reported, not hidden.
        assert "canon/retired.md" not in by_path
        assert second_report.orphaned_curation == ["canon/retired.md"]
        # The written file agrees with the returned payload.
        on_disk = json.loads((tmp_path / out).read_text(encoding="utf-8"))
        assert on_disk["sources"] == second["sources"]
        assert first["sources"] != second["sources"]

    def test_curation_does_not_overrule_a_self_declared_status(
        self, tmp_path: Path
    ) -> None:
        """Record metadata is the source speaking for itself; the overlay is not."""
        canon = tmp_path / "canon"
        canon.mkdir()
        record = {
            "layer": "hooplehopper_totality",
            "metadata": {"visibility": "weaver_only", "canon_status": "roadmap_private"},
        }
        (canon / "records.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
        curation = self._write_curation(
            tmp_path, {"sources": {"canon/records.jsonl": {"canon_status": "locked"}}}
        )
        manifest, _ = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=curation
        )
        assert manifest["sources"][0]["canon_status"] == "roadmap_private"

    def test_curated_notes_cannot_hide_a_privacy_warning(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        rows = [
            {"layer": "canon", "metadata": {"visibility": "public", "canon_status": "locked"}},
            {
                "layer": "hooplehopper_totality",
                "metadata": {"visibility": "weaver_only", "canon_status": "roadmap_private"},
            },
        ]
        (canon / "mixed.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
        )
        curation = self._write_curation(
            tmp_path, {"sources": {"canon/mixed.jsonl": {"notes": "reviewed 2026-09-05"}}}
        )
        manifest, report = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=curation
        )
        notes = manifest["sources"][0]["notes"]
        assert "reviewed 2026-09-05" in notes
        assert "MIXED privacy posture" in notes
        assert "canon/mixed.jsonl" in report.mixed_files

    def test_missing_overlay_is_not_an_error(self, tmp_path: Path) -> None:
        canon = tmp_path / "canon"
        canon.mkdir()
        (canon / "artifacts.md").write_text("x", encoding="utf-8")
        manifest, report = build_source_manifest(
            ["canon"], out_path=None, base=tmp_path, curation_path=self.CURATION_REL
        )
        assert manifest["sources"][0]["canon_status"] == "unknown"
        assert report.curated_paths == []

    def test_unparseable_overlay_raises_with_the_path_and_reason(
        self, tmp_path: Path
    ) -> None:
        curation = self._write_curation(tmp_path, "{not json")
        with pytest.raises(CurationFileError) as excinfo:
            build_source_manifest(
                ["canon"], out_path=None, base=tmp_path, curation_path=curation
            )
        text = str(excinfo.value)
        assert "source_curation.json" in text
        assert "line 1" in text

    def test_overlay_without_a_sources_object_raises(self, tmp_path: Path) -> None:
        curation = self._write_curation(tmp_path, {"sources": ["canon/artifacts.md"]})
        with pytest.raises(CurationFileError) as excinfo:
            load_source_curation(curation, base=tmp_path)
        assert "'sources' object mapping repo-relative path" in str(excinfo.value)

    def test_overlay_entry_with_an_unsupported_field_raises(
        self, tmp_path: Path
    ) -> None:
        curation = self._write_curation(
            tmp_path, {"sources": {"canon/a.md": {"visibility": "public"}}}
        )
        with pytest.raises(CurationFileError) as excinfo:
            load_source_curation(curation, base=tmp_path)
        text = str(excinfo.value)
        assert "canon/a.md" in text
        assert "visibility" in text

    def test_overlay_entry_with_a_non_string_value_raises(self, tmp_path: Path) -> None:
        curation = self._write_curation(
            tmp_path, {"sources": {"canon/a.md": {"canon_status": 7}}}
        )
        with pytest.raises(CurationFileError) as excinfo:
            load_source_curation(curation, base=tmp_path)
        text = str(excinfo.value)
        assert "canon_status" in text
        assert "int" in text


class TestShippedCurationOverlay:
    """The overlay that ships in this repo must be loadable and on-corpus."""

    def test_shipped_overlay_loads_and_matches_the_manifest(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        overlay = load_source_curation(base=repo)
        assert overlay, "manifests/corpus/source_curation.json is empty or missing"

        manifest = json.loads(
            (repo / "manifests" / "corpus" / "source_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        by_path = {s["path"]: s for s in manifest["sources"]}
        unknown = sorted(set(overlay) - set(by_path))
        assert not unknown, f"overlay curates paths absent from the manifest: {unknown}"

        for rel, curated in overlay.items():
            if curated.canon_status is not None:
                assert by_path[rel]["canon_status"] == curated.canon_status, (
                    f"overlay and manifest disagree on canon_status for {rel}"
                )
