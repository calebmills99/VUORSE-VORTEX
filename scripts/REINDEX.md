# Rebuilding `embeddings/indexes/vuorse_cortex.sqlite3`

Companion to `scripts/verify_cortex_integrity.py`.
Audience: the Weaver, on the Windows box, where the venv works.

---

## STOP — DO NOT RUN THE REBUILD YET

> A rebuild today makes things **worse**, not better. Two defects are still open.
> Run the rebuild only after **both** are fixed and this section has been deleted
> by whoever fixed them.

### Blocker 1 — the rebuild regenerates the source manifest and discards curation

`vuorse_vortex/cortex.py::CortexSatellite.build` opens with:

```python
manifest, report = build_source_manifest(
    roots=roots, out_path=None, base=base,
    include_pdf=False, include_finale=False,
)
```

It does **not** read `manifests/corpus/source_manifest.json`. It regenerates the
manifest from scratch by walking the corpus, and in `vuorse_vortex/indexing.py`
every entry's `canon_status` comes from `route.canon_status` (the route table /
the JSONL's own records) and every entry's `notes` is rebuilt as
`"; ".join(notes)` from machine-generated strings.

Curated values that exist in the on-disk manifest **today** and are not derivable
from the route table would therefore be silently replaced in the rebuilt index.
Measured from `manifests/corpus/source_manifest.json` on 2026-09-05:

| field | current on-disk values |
|---|---|
| `canon_status` | `locked` ×15, `roadmap_private` ×14, `draft` ×13, `system_rule` ×9, `synthetic_behavioral` ×3 (54 sources) |
| `notes` | 17 sources carry a non-empty note |

> Note on the numbers: the task brief for this work stated "13 `locked`, 15
> `draft`". The file on disk says the opposite way round — **15 `locked`, 13
> `draft`**. The table above is what the file actually contains, read directly.
> Either way, 28 curated classifications and 17 notes are at stake.

A parallel remediation task is fixing this. **Wait for it.**

Nuance worth knowing, because it changes what you must back up:

* `cortex build` passes `out_path=None`, so it does **not** overwrite
  `manifests/corpus/source_manifest.json` on disk. It ignores it. The damage is
  that the *index* is built from regenerated metadata, not from the curated file.
* `vuorse-vortex build-index --what sources` **without** `--check` *does* pass
  `SOURCE_MANIFEST_OUT` and physically overwrites the curated file.
  **Do not run that command.** Use `--check` if you want a drift report.

### Blocker 2 — the id collision comes back on rebuild

The source manifest was hand-repaired: the two colliding entries now read
`hooplehopper-totality-debriefing-walled-jsonl` and `...-md`.

That repair does not survive a rebuild, because nothing reads it.
`vuorse_vortex/indexing.py::build_source_manifest` mints the id as:

```python
entry_id = slugify(rel.rsplit(".", 1)[0])   # extension stripped
```

`hooplehopper_totality/debriefing_walled.jsonl` and
`hooplehopper_totality/debriefing_walled.md` both slugify to
`hooplehopper-totality-debriefing-walled`. `cortex.py` then mints
`chunk_id = f"{source['id']}:{chunk_index:05d}"`, so the 8 duplicate chunk_ids —
each one spanning `private_to_vuorse` and `weaver_only` — are **reproduced by
any rebuild** until the id-minting code itself disambiguates by extension (or by
full path). Note that `build_source_manifest` already *detects* the collision
(`notes.append(f"id collides with {seen_ids[entry_id]}")`) and then proceeds
anyway.

Rebuilding before this lands = same defect, new file, wasted downtime.

---

## Why the index does need rebuilding, eventually

The index is stale relative to the corpus. Comparing distinct `source_path` in
the index against the on-disk manifest (2026-09-05):

* 7 sources are in the manifest but **not** in the index, e.g.
  `canon/cosmology/slayton_particle_discovery.md`,
  `canon/open_threads/Continutity_Audit.md`.
* 1 source is in the index but **no longer** in the manifest:
  `canon/2-words-of_weaver_book_two/Words_of_Weaver_Book_Two_Exodus_Boogoaloo.md`.

So: the rebuild is necessary. It is just not yet safe.

---

## The command that rebuilds this file

```
vuorse-vortex cortex build
```

### Why this one and not `index` or `embed`

| CLI command | What it actually touches | Rebuilds `vuorse_cortex.sqlite3`? |
|---|---|---|
| `cortex build` (`cli.py:96`) | `CortexSatellite(db_path).build(base=base)`; `db_path` defaults to `_CORTEX_DB_OPTION = typer.Option(DEFAULT_CORTEX_DB, "--db", ...)` and `cortex.py:23` sets `DEFAULT_CORTEX_DB = PROJECT_ROOT / "embeddings/indexes/vuorse_cortex.sqlite3"` | **YES** — this is the one |
| `index` (`cli.py:435`) | `from vuorse_vortex.graphd import build_graph, refresh_graph` — the LSP/semantic *graph*, a different artefact | no |
| `embed` (`cli.py:368`) | validates a JSONL then `get_backend(settings).ingest(records)` — the ChromaDB vector store, external backend | no |
| `build-index` (`cli.py:511`) | source manifest + entity index + relationship index under `manifests/corpus/` | no — and in write mode it **overwrites the curated manifest** |

Decisive evidence for `cortex build`: it is the only command whose default path
option resolves to `DEFAULT_CORTEX_DB`, and `CortexSatellite.build` is the only
code path that executes `DELETE FROM chunks` followed by `executemany(INSERT ...)`
and rewrites the `meta` rows (`cortex.py`, in the `with self.conn:` block).

---

## Prerequisites (Windows)

1. **Python ≥ 3.11** (`pyproject.toml`: `requires-python = ">=3.11"`).
2. **`uv`** — the repo ships `uv.lock`, and `README.md` documents `uv sync`.
3. A working venv. The `.venv/` currently committed in the working tree is a
   **Linux** uv venv (`.venv/pyvenv.cfg` → `home = /home/nobby/.local/share/uv/
   python/cpython-3.11-linux-x86_64-gnu/bin`). It is not usable from Windows and
   not usable from the Linux verification VM either — its interpreter path does
   not exist there. Recreate it on the Windows box.
4. Disk: the current index is ~27 MB; keep at least a few hundred MB free.
5. No network is required by `cortex build` — `meta['external_embedding_calls']`
   is `0` by design, retrieval is local FTS5.

```powershell
cd <repo root>
uv sync --extra dev
```

`uv sync` installs the `vuorse-vortex` console script declared in
`pyproject.toml [project.scripts]` into the venv.

> `README.md` line 68 suggests `uv run python -m vuorse_vortex.cli --help`.
> **That invocation does nothing.** There is no `vuorse_vortex/__main__.py` and
> `cli.py` has no `if __name__ == "__main__": app()` guard, so the module is
> imported and the process exits without running Typer. Use the console script.

---

## The rebuild, step by step

### 0. Back up first. Never delete; move or copy.

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item embeddings\indexes\vuorse_cortex.sqlite3 `
          "embeddings\indexes\vuorse_cortex.sqlite3.bak-$stamp"
Copy-Item manifests\corpus\source_manifest.json `
          "manifests\corpus\source_manifest.json.bak-$stamp"
```

The manifest backup matters even though `cortex build` does not write to it —
it is your only copy of the curated `canon_status` / `notes` if something else
in the session touches it.

### 1. Record the "before" state

```powershell
uv run python scripts\verify_cortex_integrity.py > reindex-before.txt
```

Expected today: exit code **1**, 8 duplicate chunk_ids, all 8 crossing
`private_to_vuorse` / `weaver_only`.

### 2. Confirm the manifest is what you expect, without writing it

```powershell
uv run vuorse-vortex build-index --what sources --check
```

`--check` passes `out_path=None`, so nothing is written. It only reports drift.
**Never run this without `--check`** until Blocker 1 is fixed.

### 3. Rebuild

```powershell
uv run vuorse-vortex cortex build
```

Optional explicit form (both options have the same defaults as above):

```powershell
uv run vuorse-vortex cortex build --db embeddings\indexes\vuorse_cortex.sqlite3 --base .
```

It prints a JSON object: `source_count`, `chunk_count`, `sealed_chunk_count`,
`unrouted`, `mixed_files`, `fingerprint`, `db_path`. Keep that output — the
`fingerprint` and the counts are exactly what step 4 re-derives independently.

### 4. Confirm success

```powershell
uv run python scripts\verify_cortex_integrity.py
echo $LASTEXITCODE
```

Success is **all** of:

* exit code `0`;
* section `[2]` reads `OK: every chunk_id is unique.`;
* section `[3]` reads `OK: no duplicates, so no chunk_id spans multiple visibility classes.`;
* section `[4]` reads `OK: declared counts and fingerprint agree with the actual table contents.` —
  the verifier recomputes the SHA-256 fingerprint from the rows using the same
  formula `cortex.py` uses, so this also proves `meta` matches the build output;
* `[1] distinct source_paths` equals the `source_count` printed by step 3;
* section `[4]` `meta['fingerprint']` equals the `fingerprint` printed by step 3.

Verifier exit codes:

| code | meaning | what to do |
|---|---|---|
| 0 | clean | done |
| 1 | duplicate chunk_ids | **Blocker 2 is not fixed.** Restore the backup, stop. |
| 2 | DB missing / unreadable / wrong schema | the message names the file and the next step; the build did not produce a usable index |
| 3 | metadata mismatch only | contents are self-consistent, `meta` is not — a build did not complete, or something wrote to the index outside `cortex.py` |

Because it exits non-zero on any finding, it gates cleanly:

```powershell
uv run python scripts\verify_cortex_integrity.py; if ($LASTEXITCODE -ne 0) { throw "cortex index failed verification" }
```

```bash
python3 scripts/verify_cortex_integrity.py || { echo "cortex index failed verification"; exit 1; }
```

### 5. If it went wrong

```powershell
Move-Item embeddings\indexes\vuorse_cortex.sqlite3 `
          "_to_delete\vuorse_cortex.sqlite3.failed-$stamp"
Copy-Item "embeddings\indexes\vuorse_cortex.sqlite3.bak-$stamp" `
          embeddings\indexes\vuorse_cortex.sqlite3
```

Move into `_to_delete\`. Do not `rm` / `Remove-Item` anything in this repo.

---

## Verifying from the Linux VM instead

`scripts/verify_cortex_integrity.py` is stdlib-only and read-only. It needs no
venv and no network — the system `python3` is enough:

```bash
python3 scripts/verify_cortex_integrity.py
```

The **rebuild** cannot run there: `.venv` is unusable and the third-party
dependencies (`typer`, `pydantic`, `rich`) are not installed and cannot be
fetched. Verification and rebuilding are deliberately split this way.

---

## Assumptions and unverified claims

* **Verified by execution** on the Linux VM: verifier output against the real
  index (8 duplicates, both visibility classes), against a missing path, a
  non-SQLite file, a valid SQLite file with the wrong tables, a valid SQLite
  file with the right tables but wrong columns, a clean fixture (exit 0), and a
  stale-`meta` fixture (exit 3).
* **Verified by reading source**: which CLI command rebuilds the index; that
  `cortex build` regenerates the manifest with `out_path=None`; that ids are
  minted from the extension-stripped path; that `cli.py` has no `__main__` guard.
* **UNVERIFIED**: the Windows commands in this document have not been executed —
  no Windows host was reachable from the environment this was written in. They
  are derived from `pyproject.toml`, `README.md` and `cli.py`. Treat the exact
  `uv` invocations as needing one careful first run.
* **UNVERIFIED**: how long a full rebuild takes, and whether any source added
  since the last build fails to chunk. The current index is 6806 chunks over
  48 sources; the manifest now lists 54 sources, so expect the counts to change.
* **Assumption**: the fingerprint recomputation in the verifier replays rows in
  `rowid` order, which equals `cortex.py`'s insertion order for a table only ever
  bulk-inserted after a `DELETE FROM chunks`. This held exactly against the
  current index (recomputed hash == stored hash). If a future build ever inserts
  incrementally, that check would need revisiting.
