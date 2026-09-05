#!/usr/bin/env python3
"""Read-only integrity verifier for the VUORSE-VORTEX cortex FTS5 index.

WHAT THIS IS FOR
    ``embeddings/indexes/vuorse_cortex.sqlite3`` is built by
    ``vuorse_vortex/cortex.py::CortexSatellite.build``, which mints every row's
    primary key as ``f"{source['id']}:{chunk_index:05d}"``.  Source ids come
    from ``build_source_manifest``, which slugifies the source path *with the
    file extension stripped* -- so ``a/b.jsonl`` and ``a/b.md`` produce the same
    id, and their chunks silently overwrite each other's identity in the index.

    A duplicate chunk_id is bad.  A duplicate chunk_id whose rows carry
    DIFFERENT ``visibility`` values is a disclosure-boundary defect: retrieval
    that filters or de-duplicates by chunk_id can hand a caller the row from the
    wrong visibility class.  This script reports the two separately and treats
    the second as the headline.

WHAT THIS IS NOT
    This script never writes.  It opens the database with ``mode=ro`` and only
    reads.  It does not rebuild, repair, VACUUM or optimize anything.  Repair is
    a rebuild, and the rebuild has its own preconditions -- see scripts/REINDEX.md.

USAGE
    python3 scripts/verify_cortex_integrity.py [DB_PATH] [--skip-fingerprint]

EXIT CODES  (designed so this can gate a rebuild in a shell script)
    0  clean: no duplicates, and declared metadata matches the actual table
    1  duplicate chunk_ids found
    2  database missing, unreadable, or not the schema this script understands
    3  no duplicates, but the ``meta`` table disagrees with the actual contents

Stdlib only, by design: the device this runs on has no network and no venv.
"""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

PROGRAM = "scripts/verify_cortex_integrity.py"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "embeddings" / "indexes" / "vuorse_cortex.sqlite3"

EXPECTED_CHUNK_COLUMNS = (
    "chunk_id",
    "source_path",
    "title",
    "layer",
    "visibility",
    "canon_status",
    "text",
)
EXPECTED_META_COLUMNS = ("key", "value")

EXIT_OK = 0
EXIT_DUPLICATE_CHUNK_IDS = 1
EXIT_UNUSABLE_DATABASE = 2
EXIT_METADATA_MISMATCH = 3

RULE = "=" * 78


class VerifierError(Exception):
    """An error whose message is already actionable for a reader with no context.

    Every raise site states: what failed, which path, why, and what to do next.
    """


# --------------------------------------------------------------------------
# opening the database
# --------------------------------------------------------------------------


def open_readonly(db_path: Path) -> sqlite3.Connection:
    """Open ``db_path`` strictly read-only, or raise VerifierError explaining why not."""
    if not db_path.exists():
        raise VerifierError(
            f"cortex index not found: {db_path}\n"
            f"  why : no such file (resolved from the argument you gave; cwd is {Path.cwd()})\n"
            f"  next: pass the real path, e.g.\n"
            f"          python3 {PROGRAM} embeddings/indexes/vuorse_cortex.sqlite3\n"
            f"        If the index has genuinely never been built, it is created by\n"
            f"        `vuorse-vortex cortex build` -- but read scripts/REINDEX.md first;\n"
            f"        a rebuild today destroys curated manifest metadata."
        )
    if db_path.is_dir():
        raise VerifierError(
            f"cortex index path is a directory, not a file: {db_path}\n"
            f"  next: point at the .sqlite3 file itself, e.g.\n"
            f"          python3 {PROGRAM} {db_path}/vuorse_cortex.sqlite3"
        )

    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        # Force sqlite to actually parse the file header and schema now, so a
        # non-database file fails here with a clear message instead of later.
        conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
    except sqlite3.Error as exc:
        raise VerifierError(
            f"cannot read cortex index: {db_path}\n"
            f"  sqlite says: {exc}\n"
            f"  opened as : {uri}\n"
            f"  next: confirm the file is a SQLite database (`head -c 16 <file>` should\n"
            f"        start with 'SQLite format 3'), that this account can read it, and\n"
            f"        that no other process holds it exclusively. This script never writes,\n"
            f"        so a read-only filesystem is not the cause."
        ) from exc
    return conn


def require_expected_schema(conn: sqlite3.Connection, db_path: Path) -> None:
    """Fail loudly and specifically if this is not the cortex schema we verify."""
    present = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        )
    }
    missing = [name for name in ("chunks", "meta") if name not in present]
    if missing:
        raise VerifierError(
            f"not a VUORSE-VORTEX cortex index: {db_path}\n"
            f"  why : missing required table(s): {', '.join(missing)}\n"
            f"  found instead: {', '.join(sorted(present)) or '(no tables at all)'}\n"
            f"  next: you are probably pointing at the wrong database. The cortex index\n"
            f"        lives at embeddings/indexes/vuorse_cortex.sqlite3 and is built by\n"
            f"        vuorse_vortex/cortex.py (fts5 table 'chunks' + key/value table 'meta')."
        )

    for table, expected in (("chunks", EXPECTED_CHUNK_COLUMNS), ("meta", EXPECTED_META_COLUMNS)):
        try:
            actual = tuple(row[1] for row in conn.execute(f"PRAGMA table_info({table})"))
        except sqlite3.Error as exc:
            raise VerifierError(
                f"cannot inspect table '{table}' in {db_path}\n"
                f"  sqlite says: {exc}\n"
                f"  next: the table exists but is not introspectable -- if it is an fts5\n"
                f"        table, confirm this Python's sqlite3 was compiled with FTS5\n"
                f"        (python3 -c \"import sqlite3;"
                f" sqlite3.connect(':memory:').execute('CREATE VIRTUAL TABLE t USING fts5(a)')\")."
            ) from exc
        if actual != expected:
            raise VerifierError(
                f"unexpected schema for table '{table}' in {db_path}\n"
                f"  expected columns: {', '.join(expected)}\n"
                f"  actual columns  : {', '.join(actual) or '(none)'}\n"
                f"  next: this script encodes the schema written by "
                f"vuorse_vortex/cortex.py::_ensure_schema.\n"
                f"        If cortex.py legitimately changed, update "
                f"EXPECTED_CHUNK_COLUMNS/EXPECTED_META_COLUMNS\n"
                f"        in {PROGRAM} to match. Do not assume the index is fine until they agree."
            )


# --------------------------------------------------------------------------
# findings
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DuplicateGroup:
    """One chunk_id that appears more than once, and where its rows came from."""

    chunk_id: str
    row_count: int
    origins: tuple[tuple[str, str, int], ...]  # (visibility, source_path, rows)

    @property
    def visibilities(self) -> tuple[str, ...]:
        return tuple(sorted({visibility for visibility, _, _ in self.origins}))

    @property
    def crosses_visibility_boundary(self) -> bool:
        return len(self.visibilities) > 1


@dataclass(frozen=True)
class Totals:
    rows: int
    distinct_chunk_ids: int
    distinct_source_paths: int


def read_totals(conn: sqlite3.Connection) -> Totals:
    row = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT chunk_id), COUNT(DISTINCT source_path) FROM chunks"
    ).fetchone()
    return Totals(rows=row[0], distinct_chunk_ids=row[1], distinct_source_paths=row[2])


def find_duplicate_groups(conn: sqlite3.Connection) -> list[DuplicateGroup]:
    """Return every chunk_id occurring more than once, with its per-origin breakdown."""
    counts = {
        chunk_id: total
        for chunk_id, total in conn.execute(
            "SELECT chunk_id, COUNT(*) FROM chunks "
            "GROUP BY chunk_id HAVING COUNT(*) > 1 ORDER BY chunk_id"
        )
    }
    if not counts:
        return []

    origins: dict[str, list[tuple[str, str, int]]] = {chunk_id: [] for chunk_id in counts}
    for chunk_id, visibility, source_path, rows in conn.execute(
        "SELECT chunk_id, visibility, source_path, COUNT(*) FROM chunks "
        "WHERE chunk_id IN (SELECT chunk_id FROM chunks GROUP BY chunk_id HAVING COUNT(*) > 1) "
        "GROUP BY chunk_id, visibility, source_path "
        "ORDER BY chunk_id, visibility, source_path"
    ):
        origins[chunk_id].append((visibility, source_path, rows))

    return [
        DuplicateGroup(chunk_id=chunk_id, row_count=counts[chunk_id], origins=tuple(origins[chunk_id]))
        for chunk_id in counts
    ]


def read_meta(conn: sqlite3.Connection) -> dict[str, str]:
    return {key: value for key, value in conn.execute("SELECT key, value FROM meta")}


def recompute_fingerprint(conn: sqlite3.Connection) -> str:
    """Recompute the build fingerprint exactly as cortex.py::build does.

    cortex.py hashes ``"\\n".join(f"{chunk_id}\\0{text}")`` over the rows in the
    order it inserted them; we replay that in rowid order, which is that
    insertion order for a table that has only ever been bulk-inserted.
    """
    digest = hashlib.sha256()
    first = True
    for chunk_id, text in conn.execute("SELECT chunk_id, text FROM chunks ORDER BY rowid"):
        if not first:
            digest.update(b"\n")
        first = False
        digest.update(f"{chunk_id}\0{text}".encode("utf-8"))
    return digest.hexdigest()


def compare_declared_to_actual(
    meta: dict[str, str], totals: Totals, actual_fingerprint: str | None
) -> list[str]:
    """Return one human-readable mismatch line per disagreement between meta and reality."""
    mismatches: list[str] = []
    numeric_checks = (
        ("source_count", totals.distinct_source_paths, "distinct source_path values in chunks"),
        ("chunk_count", totals.rows, "rows in chunks"),
    )
    for key, actual, description in numeric_checks:
        declared_raw = meta.get(key)
        if declared_raw is None:
            mismatches.append(f"meta['{key}'] is absent; actual {description} = {actual}")
            continue
        try:
            declared = int(declared_raw)
        except ValueError:
            mismatches.append(
                f"meta['{key}'] = {declared_raw!r} is not an integer; actual {description} = {actual}"
            )
            continue
        if declared != actual:
            mismatches.append(
                f"meta['{key}'] declares {declared} but actual {description} = {actual}"
            )

    declared_fingerprint = meta.get("fingerprint")
    if declared_fingerprint is None:
        mismatches.append("meta['fingerprint'] is absent")
    elif actual_fingerprint is not None and declared_fingerprint != actual_fingerprint:
        mismatches.append(
            f"meta['fingerprint'] = {declared_fingerprint} but recomputing it over the rows "
            f"gives {actual_fingerprint} (the text or the row order changed after the build)"
        )
    return mismatches


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def emit(line: str = "") -> None:
    print(line)


def report_header(db_path: Path) -> None:
    emit(RULE)
    emit("VUORSE-VORTEX cortex index integrity report")
    emit(RULE)
    emit(f"database : {db_path}")
    emit(f"size     : {db_path.stat().st_size:,} bytes")
    emit("mode     : read-only (mode=ro); this script never writes")
    emit()


def report_totals(totals: Totals) -> None:
    emit("[1] CORPUS TOTALS")
    emit(f"    rows in chunks        : {totals.rows}")
    emit(f"    distinct chunk_ids    : {totals.distinct_chunk_ids}")
    emit(f"    distinct source_paths : {totals.distinct_source_paths}")
    emit()


def report_duplicates(groups: list[DuplicateGroup]) -> None:
    emit("[2] DUPLICATE chunk_id")
    if not groups:
        emit("    OK: every chunk_id is unique.")
        emit()
        return
    affected_rows = sum(group.row_count for group in groups)
    emit(f"    FINDING: {len(groups)} chunk_id value(s) occur more than once "
         f"({affected_rows} rows involved).")
    emit("    Root cause to check: vuorse_vortex/indexing.py mints a source id by")
    emit("    slugifying the path with the extension stripped, so two files that differ")
    emit("    only by extension collide; cortex.py then derives chunk_id from that id.")
    emit()
    for group in groups:
        emit(f"    {group.chunk_id}  ({group.row_count} rows)")
        for visibility, source_path, rows in group.origins:
            emit(f"        {rows} row(s)  visibility={visibility}  source_path={source_path}")
    emit()


def report_disclosure_boundary(groups: list[DuplicateGroup]) -> None:
    emit("[3] DISCLOSURE BOUNDARY")
    crossing = [group for group in groups if group.crosses_visibility_boundary]
    if not groups:
        emit("    OK: no duplicates, so no chunk_id spans multiple visibility classes.")
        emit()
        return
    if not crossing:
        emit("    Duplicates exist, but each duplicated chunk_id stays inside a single")
        emit("    visibility class. Still a correctness bug; not a disclosure bug.")
        emit()
        return

    emit("    " + "!" * 70)
    emit("    !! DISCLOSURE-BOUNDARY DEFECT -- THIS IS THE HEADLINE FINDING")
    emit("    " + "!" * 70)
    emit(f"    {len(crossing)} duplicated chunk_id(s) span MORE THAN ONE visibility class.")
    emit("    One identifier therefore names rows from two different disclosure tiers.")
    emit("    Any retrieval path that de-duplicates, caches, or filters by chunk_id can")
    emit("    return the row from the wrong tier. Treat this as a leak risk, not a typo.")
    emit()
    for group in crossing:
        emit(f"    {group.chunk_id}")
        emit(f"        spans visibility: {' | '.join(group.visibilities)}")
        for visibility, source_path, rows in group.origins:
            emit(f"        {rows} row(s)  visibility={visibility}  source_path={source_path}")
    emit()
    spanned = sorted({visibility for group in crossing for visibility in group.visibilities})
    emit(f"    visibility classes implicated overall: {', '.join(spanned)}")
    emit()


def report_metadata(meta: dict[str, str], mismatches: list[str], fingerprint_checked: bool) -> None:
    emit("[4] DECLARED (meta table) vs ACTUAL (chunks table)")
    for key in ("project", "retrieval", "source_count", "chunk_count", "sealed_chunk_count",
                "fingerprint"):
        emit(f"    meta[{key!r}] = {meta.get(key, '(absent)')}")
    extra = sorted(set(meta) - {"project", "retrieval", "source_count", "chunk_count",
                                "sealed_chunk_count", "fingerprint"})
    for key in extra:
        emit(f"    meta[{key!r}] = {meta[key]}")
    if not fingerprint_checked:
        emit("    (fingerprint NOT recomputed: --skip-fingerprint was passed)")
    emit()
    if mismatches:
        emit(f"    FINDING: {len(mismatches)} declared-vs-actual mismatch(es):")
        for mismatch in mismatches:
            emit(f"        - {mismatch}")
        emit("    A stale meta row means the index was modified outside cortex.py::build,")
        emit("    or a build did not complete. Do not trust counts taken from meta until")
        emit("    a clean rebuild reconciles them.")
    elif fingerprint_checked:
        emit("    OK: declared counts and fingerprint agree with the actual table contents.")
    else:
        emit("    OK: declared counts agree with the actual table contents.")
        emit("    NOT PROVEN: the fingerprint was not recomputed. Re-run without")
        emit("    --skip-fingerprint before treating this index as verified.")
    emit()


def report_verdict(groups: list[DuplicateGroup], mismatches: list[str], exit_code: int) -> None:
    emit("[5] VERDICT")
    if exit_code == EXIT_OK:
        emit("    CLEAN. No duplicate chunk_ids and no declared-vs-actual mismatch.")
        emit("    Safe to treat this index as internally consistent.")
    elif exit_code == EXIT_DUPLICATE_CHUNK_IDS:
        crossing = sum(1 for group in groups if group.crosses_visibility_boundary)
        emit(f"    FAIL. {len(groups)} duplicate chunk_id(s), {crossing} of which cross a "
             f"visibility boundary.")
        emit("    This index is not safe to trust for identity-based retrieval, and it")
        emit("    cannot be repaired in place -- only a rebuild fixes it.")
        emit("    READ scripts/REINDEX.md BEFORE REBUILDING: a rebuild run today also")
        emit("    regenerates the source manifest and destroys curated canon_status/notes.")
    elif exit_code == EXIT_METADATA_MISMATCH:
        emit(f"    WARN. chunk_ids are unique, but {len(mismatches)} declared-vs-actual "
             f"mismatch(es) remain.")
        emit("    The index contents are self-consistent; the meta table describing them is not.")
    emit(f"    exit code: {exit_code}")
    emit(RULE)


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=(
            "Verify the VUORSE-VORTEX cortex FTS5 index read-only: duplicate chunk_ids, "
            "duplicates that cross a visibility boundary, and declared-vs-actual metadata."
        ),
        epilog=(
            "exit codes: 0 clean | 1 duplicate chunk_ids | 2 database missing/unreadable/"
            "wrong schema | 3 metadata mismatch only"
        ),
    )
    parser.add_argument(
        "db_path",
        nargs="?",
        default=str(DEFAULT_DB),
        help=f"path to the cortex index (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--skip-fingerprint",
        action="store_true",
        help="do not recompute the build fingerprint (skips a full scan of the text column)",
    )
    return parser.parse_args(argv)


def run(db_path: Path, *, check_fingerprint: bool) -> int:
    """Verify one index and return the process exit code. Raises VerifierError only."""
    conn = open_readonly(db_path)
    try:
        require_expected_schema(conn, db_path)
        totals = read_totals(conn)
        groups = find_duplicate_groups(conn)
        meta = read_meta(conn)
        fingerprint = recompute_fingerprint(conn) if check_fingerprint else None
    except sqlite3.Error as exc:
        raise VerifierError(
            f"failed while reading {db_path}\n"
            f"  sqlite says: {exc}\n"
            f"  next: the file opened and matched the expected schema, so this is most\n"
            f"        likely corruption or a truncated file. Run `PRAGMA integrity_check;`\n"
            f"        against a COPY of it, and rebuild per scripts/REINDEX.md if it fails."
        ) from exc
    finally:
        conn.close()

    mismatches = compare_declared_to_actual(meta, totals, fingerprint)

    if groups:
        exit_code = EXIT_DUPLICATE_CHUNK_IDS
    elif mismatches:
        exit_code = EXIT_METADATA_MISMATCH
    else:
        exit_code = EXIT_OK

    report_header(db_path)
    report_totals(totals)
    report_duplicates(groups)
    report_disclosure_boundary(groups)
    report_metadata(meta, mismatches, fingerprint_checked=check_fingerprint)
    report_verdict(groups, mismatches, exit_code)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run(Path(args.db_path), check_fingerprint=not args.skip_fingerprint)
    except VerifierError as exc:
        print(f"{PROGRAM}: error: {exc}", file=sys.stderr)
        return EXIT_UNUSABLE_DATABASE
    except OSError as exc:
        print(
            f"{PROGRAM}: error: cannot access {args.db_path}\n"
            f"  os says: {exc}\n"
            f"  next: check the path, the mount, and read permission for this account.",
            file=sys.stderr,
        )
        return EXIT_UNUSABLE_DATABASE


if __name__ == "__main__":
    sys.exit(main())
