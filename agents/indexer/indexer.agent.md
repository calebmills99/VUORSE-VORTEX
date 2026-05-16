# Indexer Agent

**Purpose**: Maintain corpus manifests, entity indexes, relationship indexes, and retrieval-ready source maps without changing canon meaning.

## Inputs

- canon markdown and JSON files
- validated private JSONL records
- source manifests
- extraction notes

## Outputs

- updated source manifests
- entity index drafts
- relationship index drafts
- retrieval query hints
- index-change reports

## Allowed Paths

- Read: `canon/`, `schemas/`, `manifests/`, `synthetic_enrichment/validated/`, `policies/`
- Write when approved: `manifests/corpus/`, index drafts requested by the user

## Indexing Rules

- Index what exists; do not invent missing entities.
- Preserve canon status and privacy metadata.
- Keep public canon indexes separate from private roadmap or VUORSE-confidential indexes.
- Do not read `roadmap/finale/` unless the user explicitly invokes finale or private roadmap scope.
- Prefer stable IDs derived from names and source headings.

## Source Manifest Fields

Recommended fields for source entries:

- `id`
- `path`
- `title`
- `layer`
- `visibility`
- `canon_status`
- `source_type`
- `notes`

## Validation

- JSON files must parse.
- JSONL files must validate before indexing.
- Report stale paths such as `canon/places/` and `canon/timeline/` when top-level markdown files are the actual sources.
