# Gray Eye forge — 2026-09-05-governance-repair

*Counsel of Gandalf the Gray Eye*

## Setup
- Change point: repair VUORSE-VORTEX governance and disclosure integrity before further production work.
- Cutoff: 2026-09-05, live filesystem and Git state.
- Interval: one working night — first reconnaissance to verified clean audit.
- Mode: hybrid
- Domains / geographies: governance doctrine, corpus manifest, disclosure firewall, retrieval index, version control. Windows checkout at `C:\runb2\VUORSE-VORTEX`; Linux-side mount for tooling.
- Declared assumptions: (1) `manifests/corpus/source_manifest.json` is authoritative for layer/visibility/canon_status; (2) Caleb is sole authority for canon promotion; (3) `Slayverse/` is a working archive predating `canon/`, not a parallel corpus.

## Baseline (canon anchors)
- `canon` `policies/` absent from working tree — 13 files, deleted but never committed as deleted. Provenance: `git status --porcelain`.
- `canon` `vuorse_vortex/indexing.py:370` minted ids via `slugify(rel.rsplit(".",1)[0])` — extension stripped.
- `canon` `indexing.py:371-373` detected the collision, appended it to `notes`, emitted the duplicate row anyway.
- `canon` `vuorse_vortex/cortex.py:194` — `chunk_id = f"{source['id']}:{chunk_index:05d}"`.
- `canon` 8 duplicate chunk ids in `embeddings/indexes/vuorse_cortex.sqlite3`, each pairing `private_to_vuorse` with `weaver_only`.
- `canon` All 22 canon-layer sources at `canon_status: "unknown"`. Provenance: `source_manifest.json`.
- `canon` `indexing.py:178` — `Route("canon","public","unknown")`; regeneration read no prior curated state.
- `canon` `Settings.sealed_categories = [apocrypha, roadmap_manifest, hooplehopper_totality]`; layer-sealed set and visibility-sealed set were identical.

## Causal map
### Nodes
- `canon` Governance doctrine — `policies/{canon_firewall,disclosure,writer_room,gpu_runtime}`
- `canon` Corpus of record — `manifests/corpus/source_manifest.json`
- `canon` Id minter — `indexing.py::build_source_manifest`
- `canon` Retrieval index — `embeddings/indexes/vuorse_cortex.sqlite3`
- `canon` Curation overlay — `manifests/corpus/source_curation.json` (new)
- `canon` Sealed layers — `roadmap/`, `hooplehopper_totality/`
- `assumption` Steward — Caleb, sole promotion authority

### Edges
- `deleted policies/ → no root doctrine → subsystem files fill the vacuum` | vacated authority | − | already realized | high
- `slugify(path minus extension) → duplicate source id` | extension discarded before slug | − | build-time | high
- `duplicate source id → duplicate chunk_id → disclosure tiers share one key` | chunk id derives from source id | − | one index build | high
- `collision written to notes, not raised → defect ships silently` | detected failure swallowed into prose | − | immediate | high
- `regeneration ignores curated file → canon_status reverts to route default` | no read of prior state | − | next rebuild | high
- `curation keyed by path (not id) → survives id renames` | path is identity, id is derived | + | every rebuild | high

## Propagation
Primary chain:
- Reconnaissance found `policies/` gone → root doctrine was VideoAgent's, byte-identical, six dangling links.
- Manifest audit found 16 sealed rows / 15 unique ids → one id claimed by two files at two disclosure levels.
- Traced id → chunk id → sqlite: 8 live collisions, each spanning `private_to_vuorse` / `weaver_only`.
- Traced upstream to `indexing.py` → the generator was the author; the manifest was only the symptom.
- Found regeneration would revert all curated state → any manifest-only repair would erase itself.
- Fixed at the generator (ordinal disambiguation + `DuplicateSourceIdError` guard) and added a path-keyed curation overlay.
- Restored `policies/`; rewrote root bootstrap (17/17 links resolve); triaged all sources; rebuilt index.
- Final: 54 sources / 54 unique ids; 6,910 chunks / 6,910 unique ids; audit exit 0.

## Branches
| Branch | Weight | One-line outcome |
|--------|--------|------------------|
| B1 Repair holds through rebuild | likely | Realized — curation survived `cortex build`; 15 locked, 17 notes intact. |
| B2 Manifest-only fix, generator untouched | plausible | Averted — the next reindex would have silently restored all 8 collisions. |
| B3 Disclosure inversion reaches an artifact | stretch | Averted at the index; unquantifiable whether any prior retrieval already crossed the boundary. |
| B4 Sealed-layer content quoted into a deliverable | stretch | Did not occur; sealed paths cited by name only. |

## Human decisions (if any)
- Caleb / 2026-09-05 / all 22 canon sources → `draft`, not bulk-`locked` / rejected: lock all, lock the settled spine only.
- Caleb / 2026-09-05 / charter → `locked`, both editions / rejected: leave as Tier-3 draft — Gray Eye's misclassification, caught by the Steward.
- Caleb / 2026-09-05 / `comfyui-expert/` → submodule / rejected: vendor in, gitignore.
- Caleb / 2026-09-05 / `Slayverse/` → quarantine + promote 7 named files / rejected: index whole, quarantine only.
- Caleb / 2026-09-05 / declined blanket delete permission on the repo root / accepted: manual removal of the stale lock.

## Continuity flags
- Contradictions with existing lore: **none introduced.** No canon prose was edited; two broken citation paths repaired.
- Corrections to prior Gray Eye output: the 2026-09-05 reconnaissance claimed the two Book Two directories were different works. They were the same text, CRLF vs LF. Branch C of that report is withdrawn.
- Soft spots needing bible language: `slayverse_index.json` is indexed as a canon source while also being a generated projection of canon.
- Promotion candidates (assumptions → canon?):
  - A source id is a disclosure boundary; collisions are security defects, not tidiness defects.
  - Curation is keyed by path — an id is derived and may change; a path is identity.
  - Doctrine deleted from the working tree is doctrine repealed.
  - A detected failure written into a note is a swallowed failure.
  - **An audit reports what breaks. Everything else is noise wearing a badge.** (Stated by the Steward, repeatedly, before it was heard.)

## Labels audit
Unlabeled claims: **0**. Baseline 8/8 `canon`; edges 6/6 labeled with sign, lag, confidence; branches 4/4 weighted; assumptions 3 declared in Setup; promotion candidates held as candidates, not canon.

— Gandalf the Gray Eye
