"""Structural invariants for the corpus manifest.

These guard the disclosure boundary. A source `id` is not a label of
convenience: chunk ids in the embedding index derive from it, so two sources
sharing an id collapse into one retrieval key. When those two sources carry
different `visibility` values, the disclosure class of a retrieved chunk
becomes a function of iteration order.

Regression origin: `hooplehopper-totality-debriefing-walled` was claimed by
both `debriefing_walled.jsonl` (private_to_vuorse) and `debriefing_walled.md`
(weaver_only), producing 8 colliding chunk ids in
`embeddings/indexes/vuorse_cortex.sqlite3`.
"""

from __future__ import annotations

import collections
import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "manifests" / "corpus" / "source_manifest.json"

# Mirrors Settings.sealed_categories; asserted equal below so the two cannot drift.
SEALED_LAYERS = {"apocrypha", "roadmap_manifest", "hooplehopper_totality"}
SEALED_VISIBILITIES = {"weaver_only", "private_to_vuorse"}

# Visibility classes defined by policies/disclosure/README.md.
KNOWN_VISIBILITIES = {
    "public",
    "behavioral",
    "private_to_vuorse",
    "internal",
    "weaver_only",
}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sources(manifest: dict) -> list[dict]:
    return manifest["sources"]


def test_source_ids_are_unique(sources: list[dict]) -> None:
    counts = collections.Counter(s["id"] for s in sources)
    dupes = {k: v for k, v in counts.items() if v > 1}
    assert not dupes, (
        f"duplicate source ids collapse the disclosure boundary: {dupes}"
    )


def test_source_paths_are_unique(sources: list[dict]) -> None:
    counts = collections.Counter(s["path"] for s in sources)
    dupes = {k: v for k, v in counts.items() if v > 1}
    assert not dupes, f"duplicate source paths: {dupes}"


def test_declared_source_count_matches_contents(
    manifest: dict, sources: list[dict]
) -> None:
    assert manifest["source_count"] == len(sources)


def test_declared_sealed_count_matches_contents(
    manifest: dict, sources: list[dict]
) -> None:
    sealed = [s for s in sources if s["layer"] in SEALED_LAYERS]
    assert manifest["sealed_source_count"] == len(sealed)


def test_sealed_by_layer_and_by_visibility_agree(sources: list[dict]) -> None:
    """The firewall seals by layer; the disclosure policy seals by visibility.

    They are independent vocabularies over the same corpus and must not drift.
    """
    by_layer = {s["id"] for s in sources if s["layer"] in SEALED_LAYERS}
    by_visibility = {
        s["id"] for s in sources if s["visibility"] in SEALED_VISIBILITIES
    }
    assert by_layer == by_visibility, (
        "layer-sealed and visibility-sealed sets diverged; "
        f"layer-only={sorted(by_layer - by_visibility)} "
        f"visibility-only={sorted(by_visibility - by_layer)}"
    )


def test_sealed_layers_match_settings() -> None:
    from vuorse_vortex.settings import Settings

    assert set(Settings().sealed_categories) == SEALED_LAYERS


def test_visibility_values_are_declared_classes(sources: list[dict]) -> None:
    unknown = {s["visibility"] for s in sources} - KNOWN_VISIBILITIES
    assert not unknown, (
        f"visibility values absent from policies/disclosure/README.md: {unknown}"
    )


def test_every_source_path_exists(sources: list[dict]) -> None:
    missing = [s["path"] for s in sources if not (REPO_ROOT / s["path"]).exists()]
    assert not missing, f"manifest references paths not on disk: {missing}"


def test_manifest_roots_exist(manifest: dict) -> None:
    missing = [r for r in manifest["roots"] if not (REPO_ROOT / r).exists()]
    assert not missing, f"declared corpus roots not on disk: {missing}"


def test_no_source_is_untriaged(sources: list[dict]) -> None:
    """`canon_status: "unknown"` is the un-triaged default, not a classification.

    An unknown source may be read as material but may never be asserted as
    settled, which makes it invisible dead weight in every retrieval decision.
    Triage it to a real CanonStatus instead.
    """
    untriaged = [s["path"] for s in sources if s["canon_status"] == "unknown"]
    assert not untriaged, f"sources still awaiting canon_status triage: {untriaged}"


def test_canon_status_values_are_schema_members(sources: list[dict]) -> None:
    from vuorse_vortex.schemas import CanonStatus

    allowed = set(CanonStatus.__args__)
    unknown = {s["canon_status"] for s in sources} - allowed
    assert not unknown, f"canon_status values outside the schema Literal: {unknown}"
