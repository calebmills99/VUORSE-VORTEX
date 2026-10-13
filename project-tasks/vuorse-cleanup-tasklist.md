# VUORSE-VORTEX Remediation — Task List

Derived from `project-specs/vuorse-cleanup-setup.md` by direct source inspection.
Boxes are flipped to `### [x]` by Susie only after an explicit QA PASS.

### [ ] T1 — Make source id minting collision-proof
**Requirements:** R1, R2
**Files:** `vuorse_vortex/indexing.py` (lines 139-147 `slugify`, 370-373 id mint), `tests/`
**Scope:** Stop `build_source_manifest` from emitting duplicate ids. Follow the
disambiguation precedent already proven in `walled.py`
(`tests/test_walled_build.py::test_build_disambiguates_duplicate_concept_ids`).
A collision must not survive as a note on a duplicate row.
**Acceptance:** A test builds a manifest from a fixture containing `x.jsonl` and
`x.md` in the same routed directory and asserts the emitted ids are distinct and
deterministic across two runs. Existing `tests/test_indexing.py` stays green.

### [ ] T2 — Make curated manifest fields survive regeneration
**Requirements:** R3, R4
**Files:** `vuorse_vortex/indexing.py`, `tests/`
**Scope:** Regeneration must not revert `canon_status` to the route default or
blank curated `notes` for sources that still exist. New sources still appear;
removed sources still drop. Curation must be explicit and inspectable, not
implicit.
**Acceptance:** A round-trip test — write a manifest with a curated
`canon_status: "locked"` and a non-empty `notes`, regenerate, assert both
survive; assert a brand-new file is added; assert a deleted file is dropped.

### [ ] T3 — Resolve the 4 dangling entity references
**Requirements:** R5
**Files:** `manifests/corpus/`, `canon/`
**Scope:** For each of the 4 dangling targets, determine from repository
evidence whether an entity exists under another name, exists only in prose, or
is genuinely absent. Resolve or record the finding explicitly. Do not invent lore.
**Acceptance:** Every one of the 4 has a written, evidence-cited disposition.

### [ ] T4 — Repair the charter citation paths
**Requirements:** R6
**Files:** `canon/organizations/organizations.md`, `canon/creative_works/creative_works.md`
**Scope:** Both cite `data/golden_wingers_charter.md`, which does not exist.
Point them at the real locked charter. Minimal edit — path only, no prose changes.
**Acceptance:** No `data/golden_wingers_charter.md` reference remains in a
markdown canon source; every replacement path resolves on disk.

### [ ] T5 — Cortex reindex package
**Requirements:** R7 (chunk-id collision clearance)
**Files:** `scripts/`
**Scope:** The 8 colliding chunk ids persist in the sqlite until rebuild, which
cannot run here. Deliver (a) the exact command for the Weaver, and (b) a
stdlib-only verification script that reads the sqlite read-only and reports
duplicate chunk ids and any chunk id spanning two visibility classes.
**Acceptance:** The verification script runs on the device VM against the current
index and correctly reports the 8 known collisions. Dry-run/read-only only.

### [ ] T6 — Full invariant suite green
**Requirements:** R7
**Scope:** All 11 invariants in `tests/test_manifest_integrity.py` pass, plus
every new test from T1 and T2, verified by stdlib-only execution on the device VM.
**Acceptance:** Verified run output, not a claim.
