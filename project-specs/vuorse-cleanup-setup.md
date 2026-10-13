# VUORSE-VORTEX Remediation — Project Spec

## Problem

A 2026-09-05 audit repaired the corpus manifest by hand: split a colliding
source id, triaged 48→54 sources out of `canon_status: "unknown"`, wrote
provenance into `notes`, retired a duplicate, promoted 7 archive files.

**All of it is volatile.** `vuorse_vortex/indexing.py::build_source_manifest`
regenerates `manifests/corpus/source_manifest.json` from a route table by
walking the disk. It does not read, merge, or preserve the existing file. The
next `cortex build` or `cli index --refresh` reverts every curated field.

## Root causes (evidence, not opinion)

1. **`indexing.py:370`** — `entry_id = slugify(rel.rsplit(".", 1)[0])` strips the
   file extension before slugifying, so `x.jsonl` and `x.md` mint the same id.
2. **`indexing.py:371-373`** — the collision IS detected, then appended to a
   `notes` string and emitted anyway. Detected failure, swallowed into prose.
   No raise, no disambiguation. (Code Quality Law 1.1 / 1.4.)
3. **`cortex.py:194`** — `chunk_id = f"{source['id']}:{chunk_index:05d}"`, so a
   duplicate source id becomes duplicate chunk ids. Observed: 8 collisions in
   `embeddings/indexes/vuorse_cortex.sqlite3`, each pairing a
   `private_to_vuorse` chunk with a `weaver_only` chunk. The id is a disclosure
   boundary and it is being minted unsafely.
4. **`indexing.py:178`** — `Route("canon", "public", "unknown")`. Regeneration
   sets every canon source back to `canon_status: "unknown"` and overwrites
   `notes` with `"; ".join(notes)`.

**Precedent to follow:** `tests/test_walled_build.py::test_build_disambiguates_duplicate_concept_ids`
proves `walled.py` already disambiguates duplicate ids correctly. The two
modules must not disagree about whether id collisions are acceptable.

## Requirements

- **R1** `build_source_manifest` must never emit two sources with the same `id`.
- **R2** An id collision must be a loud, diagnosable failure or a deterministic
  disambiguation — never a note on a duplicate row.
- **R3** Regeneration must preserve curated `canon_status` and `notes` for
  sources that still exist, without preventing new sources from being picked up
  or stale ones from being dropped.
- **R4** Curated state must survive a full regenerate → verify round trip.
- **R5** The 4 dangling entity references in `relationship_index.json`
  (`dustbrand-sigil → federkreis-devices`, `federstahl-lattice → seven-fissures`,
  `pscopy-pscat → temporal-displacement`, `schloss-federstahl → forbidden-suitcase`)
  must be resolved or explicitly recorded as intentional. Targets appear in
  9–16 files each, so material exists.
- **R6** Two locked canon documents cite the constitutional charter at
  `data/golden_wingers_charter.md`. No `data/` directory exists. Paths must
  resolve.
- **R7** `tests/test_manifest_integrity.py` (11 invariants) must stay green, and
  new behavior must be covered by new tests with real assertions.

## Constraints (environment, non-negotiable)

- `.git/index.lock` is stale and undeletable by this pipeline. **No Git writes.**
  No commits, no `git submodule add`. Deliver code and scripts only.
- The device VM has **no network** (proxy 403) and **no** typer/rich/pydantic.
  `.venv/` is a Windows venv and cannot execute from the Linux-side mount.
  Therefore: `vuorse_vortex.cli` cannot be run here. Anything requiring it ships
  as a runnable command for the Weaver plus a stdlib-only verification script.
- `sqlite3` with FTS5 IS available to stdlib Python in the device VM.
- **Never edit locked canon prose** except where R6 names a broken path.
- **Never delete.** Move to `_to_delete/`.

## Acceptance

Every requirement carries a test or a verifiable artifact. No requirement is
satisfied by assertion. If it wasn't proven, it didn't happen.
