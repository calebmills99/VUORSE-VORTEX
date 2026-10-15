# Remediation Record — 2026-09-05

Companion to `report.md`. What was changed, what was decided, what remains.

---

## Applied

### 1. Governance layer recovered
- **canon** Restored all 13 files under `policies/` from `HEAD` (they were deleted
  from the working tree only, never committed as deleted).
- Recovered: `canon_firewall/README.md`, `disclosure/README.md`,
  `writer_room/README.md`, `gpu_runtime/README.md`, their PDFs, and `.gitkeep`s.
- **inference** `policies/disclosure/README.md` defines the exact five visibility
  classes the manifest already uses, and the promotion protocol the firewall
  assumes. It was never redundant scaffolding; it was the constitution.

### 2. Disclosure-boundary collision closed
- **canon** `hooplehopper-totality-debriefing-walled` was claimed by two sources
  with different visibility. Split into:
  - `…-jsonl` → `hooplehopper_totality/debriefing_walled.jsonl` (`private_to_vuorse`)
  - `…-md` → `hooplehopper_totality/debriefing_walled.md` (`weaver_only`)
- **canon** The collision was already live in retrieval:
  `embeddings/indexes/vuorse_cortex.sqlite3` holds **8 duplicated `chunk_id`
  values** (`…walled:00001`–`:00008`), each shared between a `private_to_vuorse`
  chunk and a `weaver_only` chunk. Branch B of the report was realized, not
  hypothetical.
- `source_count` and `sealed_source_count` recomputed from contents (48 / 16).

### 3. Manifest integrity now enforced
- Added `tests/test_manifest_integrity.py` — 9 invariants:
  unique ids; unique paths; declared counts match contents; layer-sealed set ==
  visibility-sealed set; `SEALED_LAYERS` == `Settings.sealed_categories`;
  visibility values are declared classes; every source path exists; every
  declared root exists.
- All 9 verified passing against the repaired manifest.

### 4. canon_status triaged
- **canon** Weaver decision: all 22 `canon`-layer sources set from `unknown` to
  **`draft`**. Promotion to `locked` happens file by file, explicitly, per
  `policies/disclosure/README.md`.
### 4b. Heda von Schwahnn folded in — zero sources remain untriaged
- **canon** `persona/heda_von_schwahnn_voice.md` set to `synthetic_behavioral`,
  visibility unchanged at `behavioral`.
- **canon** The entity `heda-von-schwahnn` is already `status: locked` in
  `manifests/corpus/entity_index.json`, via `canon/slayverse_index.json`.
- **inference** The document is two things under one label. Its *Core Identity*,
  *Character Essence*, and *Relationship to Professor von Hooplehopper* sections
  state canon-bearing facts — but those facts are canon **at the entity level**,
  not by way of this file. Everything from *Voice Description* onward is
  performance direction. `behavioral` is correct for the second half and merely
  understates the first, which is already locked elsewhere, so nothing leaks in
  either direction. Confidence: high.
- **canon** Sealed-topic scan clean: no finale, Jake, mother, Vorst, McCullen,
  Wyoming, or future Hooplehopper identities. Heda is a WWII-era *past* identity;
  `policies/disclosure/README.md` seals *future* Hooplehopper identities, not this one.
- The reasoning is recorded in the manifest's previously-empty `notes` field, so
  the next reader does not have to re-derive it.
- **canon** `canon_status` now: `draft` 22, `roadmap_private` 14, `system_rule` 9,
  `synthetic_behavioral` 3. **`unknown`: none.**

### 4c. Two further invariants added
`tests/test_manifest_integrity.py` grew to **11**:
- `test_no_source_is_untriaged` — no source may carry `canon_status: "unknown"`.
  The default is not a classification.
- `test_canon_status_values_are_schema_members` — every value must be a member of
  the `CanonStatus` Literal in `vuorse_vortex/schemas.py`.

All 11 verified passing.

### 5. Root bootstrap restored to VUORSE-VORTEX
- `README.md`, `AGENT.md`, `CLAUDE.md`, `AGENTS.md` rewritten. The previous four
  were byte-identical copies of `comfyui-expert/`'s and linked to six paths that
  did not exist at root (`foundation/`, `agent/AGENT.md`, `docs/architecture.md`,
  `docs/getting-started.md`, `state/inventory.json`, `openclaw/`).
- New root `AGENT.md` establishes authority order (`policies/` → manifest →
  `canon/` → `AGENT.md` → subsystem doctrine), a startup sequence that halts if
  `policies/` is missing, the writers-room finale boundary, and delegation rules:
  a specialist may choose method, a specialist may not promote lore.
- **canon** Link check: 17/17 links resolve. Previously 6 dangling.

### 6. Gandalf installed
- `Slayverse/skills/gandalf_grey_eye/` was already unzipped and complete.
  Copied to `skills/gandalf-the-gray-eye/` (SKILL.md + 4 references) so it is
  reachable from a corpus-adjacent, repository-visible location.

---

## Slayverse/ audit (decision input)

- **canon** 345 files, 438 MB. By subtree: `images/` 145M, `rift/` 108M,
  `audio/` 74M, `assets/` 68M, `pdf/` 36M, `json/` 7.6M, `md/` 268K, `skills/` 92K.
- **canon** 201 PNG, 59 TXT, 19 PDF against 12 MD and 10 JSON. Only **24**
  textual files sit outside `assets/`, five of which are the Gandalf skill.
- **canon** `Slayverse/md/SLAYVERSE_TV_SERIES_BIBLE.md` and
  `Slayverse/json/jsonl/slayverse_md_records_clean.jsonl` are **byte-identical**
  to their `canon/` counterparts.
- **canon** `Slayverse/json/slayverse_index.json` is 53,118 B against `canon/`'s
  68,488 B — a **predecessor**, not a variant.
- **inference** `Slayverse/` is a working archive that *precedes* `canon/`, not a
  parallel corpus. Indexing it wholesale would inject superseded lore and 400 MB
  of training media into the retrieval layer. Confidence: high.

**Recommendation:** quarantine `Slayverse/` as an explicit non-corpus archive,
and promote these individually after review — the only files with unique lore
content and no `canon/` counterpart:

- `json/sassafras_a_mcgraw_ultimate_origin.json`
- `json/sassafrass_a_mcgraw_texas_hopper_tall_tale.json`
- `json/golden_wings_intergaltactic_league_charter.json`
- `md/slayton_particle_discovery.md`
- `md/Theory_of_Everything_Confirmed_.md`
- `md/slayverse_session_archive_first_steward_transmission.md`
- `json/jsonl/Continutity_Audit.md`

The remaining unique files are format experiments (`slayverse_index_minified`,
`slayverse_index_orginal`, `slayverse_lore_index_1point2`,
`slayverse_schema_example_detailed`, `slayverse_md_batch_messages_fixedgguf`) or
a browser scrape (`FireShot_Capture_013_…chatgpt.com_.md`). Archive, do not index.

---

## Outstanding — requires the Weaver

### A. Stale Git lock (blocks everything below)
`.git/index.lock` exists with no live Git process. Every write operation fails.
From an elevated Windows shell, with no editor or Git process open:

```
del C:\runb2\VUORSE-VORTEX\.git\index.lock
```

### B. comfyui-expert as submodule *(decided: submodule)*
```
git rm -r --cached comfyui-expert
git submodule add <comfyui-expert remote URL> comfyui-expert
git commit -m "chore: pin comfyui-expert as submodule"
```
256 files of production doctrine currently sit outside version control entirely.

### C. Reindex the embedding store
The chunk-id collision is repaired in the manifest but persists in
`embeddings/indexes/vuorse_cortex.sqlite3` until rebuilt. Until then, 8 chunk ids
still resolve ambiguously across a `weaver_only` / `private_to_vuorse` boundary.

### D. Run the suite on Windows
`.venv/` is a Windows virtualenv and cannot execute from the Linux-side mount.
```
uv sync --extra dev
uv run pytest -q
```

### E. `.agent-quarantine/`
Named in `.gitignore` and in root doctrine; absent from disk. Create it or strike
the reference. A guarded door that isn't there teaches agents the guard is decorative.

---

## Not done, deliberately

- No commits made. The working tree holds 345 pre-existing changes; these edits
  should be reviewed and staged separately, not swept in.
- `Slayverse/` untouched pending the quarantine/promote decision above.
- `worldforge/` output remains provisional. This record is not canon.

**Gandalf the Gray Eye**

---

# Weaver Rulings — 2026-09-05, second pass

## Correction to `report.md`

- **canon** The report claimed `canon/2-words-of_weaver_book_two/` and
  `canon/2_words_of_weaver_book_two/` held **different works**. That was read off
  the filenames, not the files, and it was wrong. Both are
  *The Words of the Weaver Book Two: Exodus Boogoaloo*, identical text; the
  hyphen copy was CRLF, the underscore copy LF. The report's Branch C is
  withdrawn.
- **canon** The hyphen copy also broke the frontispiece link — it referenced
  `assets/the_mirror_cavern_board.png`, which exists only in the underscore
  directory.

## Ruled

### canon_status — 13 locked, 15 draft
- **canon** Tier 1 locked (3): Book One, Book Two, `the_parchment_of_persistence_scene.md`.
  Each self-declares `status: Locked Canon` in frontmatter and is corroborated by
  `entity_index.json` (`words-of-weaver-book-one`, `words-of-weaver-book-two`,
  `the-parchment-of-persistence` all `status: locked`). The manifest was the only
  layer still disagreeing.
- **canon** Tier 2 locked (10): `characters`, `cosmology`, `places`, `artifacts`,
  `organizations`, `relationships`, `rituals`, `story_arcs`,
  `SLAYVERSE_TV_SERIES_BIBLE.md`, `timeline.md`.
- **canon** Left `draft` deliberately (8 originals): `open_threads.md`
  (unsettled by definition), `slayverse_session_archive_2026-08-07.md` (a
  transcript, not a ruling), `creative_works.md`,
  `golden_wingers_league_charter.md`, and four generated or raw artifacts —
  `slayverse_index.json`, `slayverse_md_records_clean.jsonl`, `projects.json`,
  `the_parchment_of_persistence_raw_substrate.txt`.
- **inference** `slayverse_index.json` remains a manifest source while also being
  a generated projection. It stays `draft` so nothing asserts it as independent
  canon, but the promotion candidate "corpus indexes are projections of canon,
  not independent canon sources" is still unresolved. Confidence: high.

### Book Two duplicate retired
- Hyphen directory moved to `_to_delete/canon__2-words-of_weaver_book_two/` and
  dropped from the manifest. Nothing was deleted; removal is yours.

### Slayverse/ quarantined, 7 promoted
- `Slayverse/ARCHIVE.md` written: declares the directory a non-corpus working
  archive, records the audit, names what is byte-identical to `canon/`, what was
  promoted, and what was deliberately left behind.
- Promoted as `draft`, each carrying its origin path in `notes`:
  `sassafras_a_mcgraw_ultimate_origin.json` → `canon/characters/`;
  `sassafrass_a_mcgraw_texas_hopper_tall_tale.json` → `canon/creative_works/`;
  `golden_wings_intergaltactic_league_charter.json` → `canon/organizations/`;
  `slayton_particle_discovery.md` and `Theory_of_Everything_Confirmed_.md` →
  `canon/cosmology/`; `slayverse_session_archive_first_steward_transmission.md` →
  `canon/session_archives/`; `Continutity_Audit.md` → `canon/open_threads/`.

### .agent-quarantine/ created
- Directory made real with a `README.md` stating the boundary. `.gitignore`
  gained `!.agent-quarantine/README.md` so the marker is tracked while contents
  stay ignored — the rule is now visible in version control instead of existing
  only in `AGENTS.md`.

## State

- **canon** 54 sources (48 − 1 retired + 7 promoted). Sealed: 16, unchanged.
- **canon** `canon_status`: `draft` 15, `roadmap_private` 14, `locked` 13,
  `system_rule` 9, `synthetic_behavioral` 3. `unknown`: none.
- **canon** All 11 manifest invariants pass.

**Gandalf the Gray Eye**

---

# Ruling — The Charter — 2026-09-05, third pass

## Error owned

The Golden Wingers Intergalactic League Charter was placed in "Tier 3 —
volatile" and left `draft`. That was wrong, and it was wrong for a bad reason:
the file was grouped by modification date and directory neighbors, not read. The
Weaver caught it. Both charter files are now `locked`.

## Why it was wrong — three independent confirmations

1. **canon** **Authority inversion.** `canon/organizations/organizations.md` was
   locked in the second pass while citing the charter as its own source:
   `**Source**: [p.37, p.64–65, p.78; data/golden_wingers_charter.md]`.
   `canon/creative_works/creative_works.md` likewise records
   `**Exists at**: data/golden_wingers_charter.md`. A derived document was ranked
   above the document it derives from — precisely the accretion the canon
   firewall exists to prevent, introduced by the remediation itself.
2. **canon** **Dangling founding reference.** `relationship_index.json` records
   exactly 5 `dangling_related` edges. One of them is
   `golden-wingers -> golden-wingers-charter`: the League points at its own
   charter, and no such entity exists in `entity_index.json`. The constitutional
   document was a broken pointer at the center of the organization it constitutes.
3. **canon** **Self-declared ratification.** The charter states
   "Authored and Ratified by: Caleb Mills Stewart, Founder," and the structured
   record adds "Ratified across all dimensions, timelines, and galaxies" with
   signatories Caleb the Keeper, Robyn of the Gold Wings, and Jock the Wise,
   Keeper of the 747 Scrolls. Ratification is stated on the face of the document.

## Applied

- **canon** `canon/organizations/golden_wingers_league_charter.md` → `locked`.
  Noted as the **published web edition**, captured from
  `https://www.golden-wings-robyn.com/league-charter`, page furniture retained.
- **canon** `canon/organizations/golden_wings_intergaltactic_league_charter.json`
  → `locked`. Noted as the **structured record**, wider in scope than the
  capture: it carries initiation rites, notable proclamations, closing
  invocations, and signatories that the web edition omits.
- **inference** Promoting the JSON out of `Slayverse/` yesterday turns out to
  supply the missing `golden-wingers-charter` entity. Reindexing should close the
  dangling edge without any authoring work. Confidence: high — the file declares
  `"id": "golden-wingers-charter"` directly.

## Left for the Weaver

- **canon** Both `organizations.md` and `creative_works.md` cite the charter at
  `data/golden_wingers_charter.md`. There is no `data/` directory. Two locked
  documents carry a stale path to the constitutional document. Not rewritten
  here: editing locked canon text is a Weaver act, not a remediation act.
- **inference** The remaining 4 `dangling_related` edges — `dustbrand-sigil →
  federkreis-devices`, `federstahl-lattice → seven-fissures`, `pscopy-pscat →
  temporal-displacement`, `schloss-federstahl → forbidden-suitcase` — are the
  same shape of defect and may resolve the same way, from material already on
  disk but outside the corpus. Worth one pass. Confidence: medium.

## State

- **canon** 54 sources. `locked` 15, `roadmap_private` 14, `draft` 13,
  `system_rule` 9, `synthetic_behavioral` 3. `unknown`: none.
- **canon** All invariants pass.

**Gandalf the Gray Eye**
