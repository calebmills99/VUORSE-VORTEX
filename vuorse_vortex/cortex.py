"""Project-local, canon-aware retrieval satellite for VUORSE-VORTEX.

The satellite borrows Slay Cortex's durable SQLite FTS5 layer while keeping
VUORSE-VORTEX's source routing and sealed-layer policy authoritative. It has
no network dependency and makes no paid embedding calls.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vuorse_vortex.indexing import DEFAULT_ROOTS, build_source_manifest
from vuorse_vortex.settings import Settings, get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORTEX_DB = PROJECT_ROOT / "embeddings/indexes/vuorse_cortex.sqlite3"
DEFAULT_CHUNK_CHARS = 1600
DEFAULT_CHUNK_OVERLAP = 200


@dataclass(frozen=True)
class CortexHit:
    """One retrieval hit with enough provenance to audit the result."""

    chunk_id: str
    source_path: str
    title: str
    layer: str
    visibility: str
    canon_status: str
    text: str
    score: float


def _tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[0-9A-Za-z_'-]+", text) if len(token) > 1]


def _fts_query(text: str) -> str:
    seen: set[str] = set()
    terms: list[str] = []
    for token in _tokens(text):
        folded = token.casefold()
        if folded in seen:
            continue
        seen.add(folded)
        terms.append('"' + token.replace('"', '""') + '"')
    return " OR ".join(terms)


def _json_strings(value: Any) -> Iterable[str]:
    """Yield readable string values from a structured source in stable order."""

    if isinstance(value, str):
        text = value.strip()
        if text:
            yield text
    elif isinstance(value, list):
        for item in value:
            yield from _json_strings(item)
    elif isinstance(value, dict):
        for key in sorted(value):
            yield from _json_strings(value[key])


def _source_documents(path: Path, source_type: str) -> Iterable[str]:
    """Read a routed source as searchable prose rather than escaped JSON syntax."""

    if source_type == "jsonl":
        with path.open(encoding="utf-8-sig", errors="replace") as handle:
            for raw in handle:
                line = raw.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    yield line
                    continue
                text = "\n".join(_json_strings(value))
                if text:
                    yield text
        return
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    if source_type == "json":
        try:
            raw = "\n".join(_json_strings(json.loads(raw)))
        except json.JSONDecodeError:
            pass
    if raw.strip():
        yield raw


def _chunks(text: str, *, size: int, overlap: int) -> Iterable[str]:
    """Yield deterministic character windows without splitting words when possible."""

    cleaned = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").splitlines())
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if not cleaned:
        return

    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + size, length)
        if end < length:
            boundary = max(cleaned.rfind("\n\n", start, end), cleaned.rfind(" ", start, end))
            if boundary > start + size // 2:
                end = boundary
        chunk = cleaned[start:end].strip()
        if chunk:
            yield chunk
        if end >= length:
            break
        start = max(end - overlap, start + 1)


class CortexSatellite:
    """SQLite FTS5 satellite over the routed VUORSE-VORTEX corpus."""

    def __init__(
        self,
        db_path: Path = DEFAULT_CORTEX_DB,
        *,
        settings: Settings | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.settings = settings or get_settings()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def __enter__(self) -> CortexSatellite:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def _ensure_schema(self) -> None:
        self.conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5("
            "chunk_id UNINDEXED, source_path UNINDEXED, title UNINDEXED, "
            "layer UNINDEXED, visibility UNINDEXED, canon_status UNINDEXED, text, "
            "tokenize='unicode61')"
        )
        self.conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

    def build(
        self,
        *,
        base: Path = Path("."),
        roots: Sequence[str] = DEFAULT_ROOTS,
        chunk_chars: int = DEFAULT_CHUNK_CHARS,
        overlap_chars: int = DEFAULT_CHUNK_OVERLAP,
    ) -> dict[str, Any]:
        """Rebuild the satellite from routed sources, excluding PDFs and finale material."""

        if chunk_chars < 200:
            raise ValueError("chunk_chars must be at least 200")
        if overlap_chars < 0 or overlap_chars >= chunk_chars:
            raise ValueError("overlap_chars must be non-negative and smaller than chunk_chars")

        base = Path(base).resolve()
        manifest, report = build_source_manifest(
            roots=roots,
            out_path=None,
            base=base,
            include_pdf=False,
            include_finale=False,
        )
        rows: list[tuple[str, str, str, str, str, str, str]] = []
        sealed = set(self.settings.sealed_categories)
        sealed_chunks = 0

        for source in manifest["sources"]:
            source_path = str(source["path"])
            path = base / source_path
            chunk_index = 0
            for document in _source_documents(path, str(source["source_type"])):
                for chunk in _chunks(document, size=chunk_chars, overlap=overlap_chars):
                    chunk_index += 1
                    chunk_id = f"{source['id']}:{chunk_index:05d}"
                    rows.append(
                        (
                            chunk_id,
                            source_path,
                            str(source["title"]),
                            str(source["layer"]),
                            str(source["visibility"]),
                            str(source["canon_status"]),
                            chunk,
                        )
                    )
                    if source["layer"] in sealed:
                        sealed_chunks += 1

        fingerprint = hashlib.sha256(
            "\n".join(f"{row[0]}\0{row[-1]}" for row in rows).encode("utf-8")
        ).hexdigest()
        with self.conn:
            self.conn.execute("DELETE FROM chunks")
            self.conn.executemany(
                "INSERT INTO chunks "
                "(chunk_id, source_path, title, layer, visibility, canon_status, text) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            metadata = {
                "project": "VUORSE-VORTEX",
                "retrieval": "sqlite-fts5",
                "external_embedding_calls": "0",
                "source_count": str(manifest["source_count"]),
                "chunk_count": str(len(rows)),
                "sealed_chunk_count": str(sealed_chunks),
                "fingerprint": fingerprint,
            }
            self.conn.executemany(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", metadata.items()
            )
            self.conn.execute("INSERT INTO chunks(chunks) VALUES('optimize')")

        return {
            "source_count": manifest["source_count"],
            "chunk_count": len(rows),
            "sealed_chunk_count": sealed_chunks,
            "unrouted": report.unrouted,
            "mixed_files": report.mixed_files,
            "fingerprint": fingerprint,
            "db_path": str(self.db_path),
        }

    def search(self, query: str, *, top_k: int = 10, layer: str | None = None) -> list[CortexHit]:
        """Search the satellite while always withholding sealed layers."""

        if top_k < 1:
            raise ValueError("top_k must be positive")
        match = _fts_query(query)
        if not match:
            return []

        sealed = sorted(set(self.settings.sealed_categories))
        where = ["chunks MATCH ?"]
        params: list[Any] = [match]
        if sealed:
            placeholders = ",".join("?" for _ in sealed)
            where.append(f"layer NOT IN ({placeholders})")
            params.extend(sealed)
        if layer is not None:
            where.append("layer = ?")
            params.append(layer)
        params.append(top_k)

        rows = self.conn.execute(
            "SELECT chunk_id, source_path, title, layer, visibility, canon_status, text, "
            "bm25(chunks) AS rank FROM chunks WHERE "
            + " AND ".join(where)
            + " ORDER BY rank LIMIT ?",
            params,
        ).fetchall()
        return [
            CortexHit(
                chunk_id=str(row["chunk_id"]),
                source_path=str(row["source_path"]),
                title=str(row["title"]),
                layer=str(row["layer"]),
                visibility=str(row["visibility"]),
                canon_status=str(row["canon_status"]),
                text=str(row["text"]),
                score=-float(row["rank"]),
            )
            for row in rows
        ]

    def stats(self) -> dict[str, Any]:
        """Return satellite identity, counts, and per-layer distribution."""

        meta = {
            str(row["key"]): str(row["value"])
            for row in self.conn.execute("SELECT key, value FROM meta ORDER BY key")
        }
        layers = {
            str(row["layer"]): int(row["count"])
            for row in self.conn.execute(
                "SELECT layer, count(*) AS count FROM chunks GROUP BY layer ORDER BY layer"
            )
        }
        return {"meta": meta, "layers": layers, "db_path": str(self.db_path)}
