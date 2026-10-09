# Gandalphaba Workshop Report

## Scope

Created a first workable draft of `gandalphaba-gray-eye`, a Slayverse/WorldForge
skill persona evolved from `gandalf-the-gray-eye` but aimed at implementation
passes for the governed Lore Index / Seam Schema 2.x.

Disclosure ceiling for this pass: repository-internal operational material. No
canon promotion was performed.

## Files Created

- `skills/gandalphaba-gray-eye/SKILL.md`
- `skills/gandalphaba-gray-eye/references/character-design-card.md`
- `skills/gandalphaba-gray-eye/references/schema-2x-implementation.md`
- `skills/gandalphaba-gray-eye/evals/evals.json`
- `worldforge/2026-10-09-gandalphaba-workshop/report.md`

## Design Choices

- Preserved Gray Eye discipline: labels, provenance, worldforge artifacts,
  Steward authority, and no silent canon promotion.
- Distinguished Gandalphaba from Gandalf: Gandalf audits and simulates;
  Gandalphaba may perform focused implementation passes when explicitly asked.
- Centered the skill on the actual Seam Schema primitives: `Entity`,
  `Statement`, `Relationship`, `Source`, `Activity`, `ProvRef`, `seal`,
  `canon_tier`, `epistemic`, `rank`, and `repository_sync`.
- Added an implementation startup checklist: inventory, manifest coverage,
  schema validation state, provenance planning, git diff awareness, focused
  edits, and validation reporting.
- Added output modes for `Forge Memo`, `Schema Patch`, `Canon + Index Patch`,
  `Audit`, and `Implementation Run`.
- Created a compact character continuity card so Gandalphaba can remain visually
  consistent if turned into images, cards, avatars, or handoff art.

## Writers Room Tenets

The writers room added a compact operating doctrine for Gandie:
`skills/gandalphaba-gray-eye/references/tenets.md`. The tenets formalize that
the Steward seals while Gandie implements, sources precede sparkle, canon claims
require provenance, changes must be staged rather than silently mutated, the
schema behaves as a ritual machine, validator green only means truth when
coverage is real, Markdown canon additions need JSON representation, conflicts
stay preserved until ruled, aesthetics serve governance, and glamor must
compile.

These tenets do not promote Gandalphaba, Sealcraft, or workshop output to canon.
They are operational discipline for future implementation passes and visual
handoffs.

## Repo Facts Used

- `manifests/corpus/source_manifest.json` currently reports 49 sources and 16
  sealed sources.
- The current lore-index path is named `lore-index-2.0`, while the JSON file
  declares version `2.1.1` and the schema title declares Slayverse Lore Index
  2.1.
- The earlier 2026-10-09 full inventory report identified two canon files not
  covered by the source manifest and not cited by the Seam Index:
  `canon/characters/characters_first_folio.md`, and
  `canon/characters/characters_second_folio.md`. This pass observed current
  manifest entries for the First Folio and Second Folio; it did not perform a
  fresh Seam Index coverage audit.
- The The Thumper record is a useful implementation example because it separates
  Steward-declared material from Gray Eye inference and keeps the seal as
  `candidate`.

## Unresolved Questions

- Should Gandalphaba be installed only in repo `skills/`, or also mirrored into
  the user's global Cursor skill directory after review?
- Should a deterministic validator script be added for skill frontmatter and
  Seam Index patch sanity, or should Gandalphaba continue to rely on existing
  repo validators only?
- Should the next pass actually repair the manifest/Seam coverage gaps for the
  First Folio and Second Folio files?
- Should Gandalphaba inherit the newer Galactic Summit behavior from the global
  Gray Eye skill, or stay narrowly focused on schema implementation?

## Validation Notes

Frontmatter was drafted with required `name` and `description` fields. No canon
files, source manifests, or Lore Index JSON records were modified in this pass.
