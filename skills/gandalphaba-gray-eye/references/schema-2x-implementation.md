# Seam Schema 2.x Implementation Field Guide

This guide is for controlled implementation passes against the governed
Slayverse Lore Index currently stored at
`worldforge/worldforge/lore-index-2.0/slayverse_lore_index_2.0.json` with its
schema at `worldforge/worldforge/lore-index-2.0/slayverse_lore_index_2.0.schema.json`.
The path says 2.0; the file currently declares version 2.1.1.

## Operating Rule

Implement structure; do not promote canon. A patch can add `candidate` or
`proposed` records, repair repository-sync metadata, or surface questions for
the Steward. It cannot seal material unless the Steward has explicitly ruled and
the source trail records that ruling.

## Current Vocabulary Snapshot

Use the schema vocabulary, not improvised synonyms:

- `seal`: `sealed`, `candidate`, `proposed`, `deprecated`
- `canon_tier`: `primary-pdf`, `creator-supplement`, `oral-canon`,
  `meta-canon`, `session-archive`, `production-record`, `gray-eye`
- `epistemic`: `canon`, `declared`, `inference`, `assumption`, `simulation`,
  `counterfactual`, `record`
- `rank`: `preferred`, `normal`, `deprecated`
- `availability`: `repository`, `external`, `unavailable`

## ID Conventions

### General ids

- Keep ids lowercase and slug-like.
- Use schema-safe characters: lowercase letters, numbers, colon, dot,
  underscore, and hyphen.
- Do not reuse ids across collections when the schema or validator expects
  global uniqueness.
- Use collection prefixes where the index already does:
  - `src:` for sources
  - `agent:` for agents
  - `act:` for activities
  - `st:` for statements
  - `rel:` for relationships
  - `question:` for open questions

### Entity ids

Entity ids are collection-local and usually unprefixed:

```json
"id": "the-thumper"
```

Use stable lore slugs, not display names. Preserve deprecated names in
`names.deprecated` instead of renaming records casually.

### Statement ids

Use the local entity/event slug plus an ordinal:

```json
"id": "st:the-thumper:1"
```

When inserting in the middle would renumber existing statements, append a new
ordinal instead. Stable ids matter more than tidy order.

### Source ids

For manifest-backed files, prefer:

```text
src:repo:<manifest_source_id>
```

Example:

```json
{
  "id": "src:repo:canon-artifacts-artifacts",
  "type": "repository-document",
  "title": "Slayverse Artifacts",
  "repository_path": "canon/artifacts/artifacts.md",
  "manifest_source_id": "canon-artifacts-artifacts",
  "availability": "repository"
}
```

For Steward sessions or forge runs that are not in the manifest, use a
descriptive `src:<slug>` and provide `path`, `availability`, `date`, and a note.

## Manifest / Source Workflow

1. Read `manifests/corpus/source_manifest.json`.
2. Record `source_count`, `sealed_source_count`, roots, and any unknown canon
   status.
3. For every governed repository file being indexed, check whether a manifest
   source already exists.
4. If it exists, link the Seam `Source` with `manifest_source_id` and
   repository-relative `repository_path`.
5. If it does not exist, do not invent a manifest id. Either:
   - add a manifest source record in a focused manifest patch, or
   - create a Seam `Source` for a non-manifest session/workshop path and note
     why it is not manifest-backed.
6. Confirm paths are repository-relative: no Windows drive letters, no leading
   slash, no backslashes.
7. Record coverage gaps in a report even when not fixing them.

Known inventory pressure points from the 2026-10-09 full inventory:

- `canon/characters/characters_first_folio.md` is a canon file not represented
  in the source manifest.
- `canon/characters/characters_second_folio.md` is a canon file not represented
  in the source manifest.
- `canon/1_words_of_weaver_book_one/Jenna Maroney.md` is a canon file not
  represented in the source manifest.
- The Seam Index has repository-path coverage for its repository sources but
  also contains non-file sources such as `src:gray-eye` and external standards.

## Statement Construction

A statement is one claim. Do not bundle mixed epistemic status into one value.

Use this pattern:

```json
{
  "id": "st:the-thumper:2",
  "property": "mass",
  "value": "Five hundred pounds.",
  "rank": "preferred",
  "epistemic": "declared",
  "provenance": [
    {
      "source": "src:first-folio-2026-10-07",
      "activity": "act:gray-eye-first-folio-2026-10-07",
      "agent": "agent:steward-vessel"
    }
  ]
}
```

Checklist:

- `id` is unique.
- `property` is specific enough to query.
- `value` carries only one claim or a tightly bound claim cluster.
- `rank` reflects display preference, not confidence.
- `epistemic` reflects source status.
- `provenance` has at least one source or activity reference.

## Entity Construction

Minimal practical shape:

```json
{
  "id": "the-thumper",
  "type": "artifact",
  "names": {
    "preferred": "The Thumper",
    "alternates": ["The Portable Mechanized Wardrobe"],
    "deprecated": []
  },
  "status": "moderate",
  "seal": "candidate",
  "canon_tier": "oral-canon",
  "time": {
    "mode": "span",
    "edtf": "1147/..",
    "display": "after 1147, borne through the Conrad lane"
  },
  "summary": "Short, source-grounded description.",
  "provenance": [
    {
      "source": "src:first-folio-2026-10-07",
      "activity": "act:gray-eye-first-folio-2026-10-07",
      "agent": "agent:steward-vessel"
    }
  ],
  "statements": []
}
```

The Thumper is the useful model: declared Steward-session facts are `declared`
and `candidate`, while Gray Eye mechanism inference stays inference and never
becomes a seal by proximity.

## Relationship Construction

Use relationships for graph edges, not decorative prose:

```json
{
  "id": "rel:conrad-von-hooplehopper:inhabits:the-thumper",
  "from": "conrad-von-hooplehopper",
  "to": "the-thumper",
  "type": "inhabits",
  "rank": "preferred",
  "epistemic": "declared",
  "seal": "candidate",
  "provenance": [
    {
      "source": "src:first-folio-2026-10-07",
      "activity": "act:gray-eye-first-folio-2026-10-07",
      "agent": "agent:steward-vessel"
    }
  ]
}
```

Checklist:

- `from` and `to` ids already exist or are created in the same patch.
- `type` is stable enough to reuse.
- `epistemic` and `seal` do not exceed the source.
- Provenance points to the source of the edge, not merely the source of each
  endpoint.

## Activity Construction

Every implementation pass should add or reuse an activity when records are
generated or modified by a named process.

Use:

- `act:<short-run-slug>`
- `type`: `indexing`, `migration`, `steward-session`, `gray-eye-analysis`,
  `gandalphaba-implementation`, or another concrete process label.
- `agents`: include existing `agent:` ids when present.
- `used`: source ids read.
- `generated`: ids created or updated.
- `summary`: one sentence.

Do not create an activity that claims validation passed unless validation
actually ran.

## Validation Workflow

1. Confirm the file still parses as JSON.
2. Validate against the schema if a repo validator or JSON Schema runner exists.
3. Run repository-aware checks when available:
   - unique ids;
   - dangling typed references;
   - source manifest coverage;
   - repository path resolution;
   - sealed-layer behavior;
   - timeline entries pointing at real events.
4. If no validator exists, write a validation TODO and report "not run".
5. Never manually edit `validation.status`, `validation.valid`, or
   `validation.errors` to manufacture success.

The existing validation block may record prior checks. Treat it as history until
rerun.

## First Folio Example

When integrating `characters_first_folio.md`:

1. Add or request a manifest source record for
   `canon/characters/characters_first_folio.md`.
2. Add a matching Seam `Source`:
   `src:repo:<new-manifest-id>` with `repository_path` and
   `manifest_source_id`.
3. Add an `Activity` for the integration pass.
4. Add `Entity`, `Statement`, and `Relationship` records only for claims
   supported by that file or by a Steward session source.
5. Put unresolved identity or contradiction issues in `open_for_the_steward`.

## Patch Report Template

Use this after an implementation pass:

```markdown
## Gandalphaba Implementation Report

- Scope:
- Files edited:
- Sources used:
- Records added:
- Records updated:
- Canon status:
- Validation run:
- Validation result:
- Remaining TODOs:
- Steward questions:
```
