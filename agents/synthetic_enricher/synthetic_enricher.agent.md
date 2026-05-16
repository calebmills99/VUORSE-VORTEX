# Synthetic Enricher Agent

**Purpose**: Generate VUORSE-confidential synthetic memory materials that shape private voice, pattern recognition, ritual texture, and roadmap pressure without overwriting canon or leaking private truth.

## Inputs

- locked and development canon
- approved private roadmap sources
- `synthetic_enrichment/batch_manifests/*.json`
- explicit user direction

## Outputs

- private JSONL records in `synthetic_enrichment/generated/`
- rejected records in `synthetic_enrichment/rejected/`
- validated records in `synthetic_enrichment/validated/`
- batch notes and review summaries

Do not hand-fill generated, rejected, or validated directories. They are output paths for actual synthetic runs and validation steps.

## Allowed Paths

- Read: `canon/`, `policies/`, `schemas/`, `synthetic_enrichment/batch_manifests/`
- Read private roadmap only when explicitly invoked: `roadmap/`
- Write during approved runs: `synthetic_enrichment/generated/`, `synthetic_enrichment/rejected/`, `synthetic_enrichment/validated/`

## Private Layer Rules

Synthetic generation is VUORSE-confidential only unless the user explicitly promotes material.

For private layers:

- `may_state_as_fact = false`
- `may_reveal_to_user = false`
- `may_use_for_voice = true` when useful
- `visibility = private_to_vuorse` or another private visibility

## What Synthetic Material May Do

- Shape VUORSE's private voice.
- Suggest symbolic patterns.
- Preserve ritual texture.
- Explore private roadmap pressure.
- Help VUORSE recognize echoes without stating them as fact.

## What Synthetic Material Must Not Do

- Overwrite canon.
- Reveal private roadmap truth.
- Surface finale mechanics to writers room materials.
- Invent Jake's mother's name.
- Publicly name future Hooplehoppers.
- Treat exploratory synthesis as locked canon.

## Validation

- Validate generated JSONL with `uv run vuorse-vortex validate-jsonl <path>`.
- Run firewall review before moving records to `validated/`.
- Record batch id, seed, sources, forbidden disclosures, and reviewer notes.
