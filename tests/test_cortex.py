from __future__ import annotations

from pathlib import Path

from vuorse_vortex.cortex import CortexSatellite


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_build_and_search_withholds_sealed_layers(tmp_path: Path) -> None:
    _write(tmp_path / "canon" / "characters" / "oracle.md", "Velvet Oracle guards the VUORSE gate.")
    _write(
        tmp_path / "roadmap" / "secret.md",
        "Velvet Oracle secretly destroys the gate in the private roadmap.",
    )

    with CortexSatellite(tmp_path / "satellite.sqlite3") as satellite:
        built = satellite.build(base=tmp_path, roots=("canon", "roadmap"), chunk_chars=240)
        hits = satellite.search("Velvet Oracle", top_k=10)
        stats = satellite.stats()

    assert built["source_count"] == 2
    assert built["sealed_chunk_count"] == 1
    assert len(hits) == 1
    assert hits[0].layer == "canon"
    assert hits[0].source_path == "canon/characters/oracle.md"
    assert stats["meta"]["external_embedding_calls"] == "0"


def test_build_is_deterministic_and_replaces_old_content(tmp_path: Path) -> None:
    source = tmp_path / "canon" / "places" / "hall.md"
    _write(source, "The Velvet Hall contains the first silver bell.")

    with CortexSatellite(tmp_path / "satellite.sqlite3") as satellite:
        first = satellite.build(base=tmp_path, roots=("canon",), chunk_chars=240)
        second = satellite.build(base=tmp_path, roots=("canon",), chunk_chars=240)
        assert first["fingerprint"] == second["fingerprint"]
        assert len(satellite.search("silver")) == 1

        _write(source, "The Velvet Hall contains the final golden bell.")
        third = satellite.build(base=tmp_path, roots=("canon",), chunk_chars=240)
        assert third["fingerprint"] != first["fingerprint"]
        assert satellite.search("silver") == []
        assert len(satellite.search("golden")) == 1


def test_empty_query_returns_no_hits(tmp_path: Path) -> None:
    with CortexSatellite(tmp_path / "satellite.sqlite3") as satellite:
        assert satellite.search(" ... ") == []
