# Folder Completion Plan

This reference classifies placeholder folders and describes what a future fill-in run should create.

## What-If Output Template

When previewing a scaffold completion without editing files, use this structure:

```text
What-If Scope
- Requested area:
- Folders affected:
- Files that would be created:
- Folders left empty:

Classification
- Safe to implement:
- Needs user decision:
- Private/finale scope:
- Runtime path: do not hand-fill:
- Stale/superseded path:

Firewall Notes
- Writers room risk:
- Finale roadmap risk:
- Synthetic/VUORSE-confidential risk:
- Canon promotion risk:

Next Command
Use the vuorse-scaffold-completion skill to <exact approved action>.
```

## Do Not Fill By Hand: Runtime / Action Paths

These paths are run outputs or queues. Keep `.gitkeep` unless a real command creates content.

| Path | Purpose | Fill Only When |
| --- | --- | --- |
| `archives/incoming/` | raw imported source drops | user asks to ingest/import sources |
| `archives/processed/` | processed source copies | ingestion run completes |
| `archives/quarantine/` | unsafe/invalid sources | ingestion validation rejects files |
| `embeddings/input/` | embedding input chunks | embedding prep run creates them |
| `embeddings/output/` | embedding outputs | embedding run completes |
| `embeddings/indexes/` | vector indexes | indexing run completes |
| `embeddings/manifests/` | embedding run manifests | embedding prep/run creates manifests |
| `manifests/batches/` | batch manifests | user asks to define a batch |
| `manifests/runs/` | completed run metadata | run tooling emits it |
| `synthetic_enrichment/generated/` | generated private JSONL | synthetic generation run |
| `synthetic_enrichment/rejected/` | rejected generated records | validation rejects generated records |
| `synthetic_enrichment/validated/` | approved private JSONL | validation/promote step completes |

## Authored Work: Agent Specs

Create concise agent specs here. These are not Claude Code `.claude/agents`; they are project/cloud-agent design docs.

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `agents/canon_extractor/` | `canon_extractor.agent.md` | source-to-canon extraction rules |
| `agents/embedding/` | `embedding.agent.md` | embedding prep/index protocol |
| `agents/firewall_validator/` | `firewall_validator.agent.md` | disclosure and private-layer review |
| `agents/indexer/` | `indexer.agent.md` | corpus/index update workflow |
| `agents/synthetic_enricher/` | `synthetic_enricher.agent.md` | VUORSE-confidential synthetic generation |

Each agent spec should include: purpose, inputs, outputs, allowed paths, forbidden disclosures, and validation.

## Authored Work: Policy Docs

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `policies/disclosure/` | `README.md` | public/private visibility rules |
| `policies/writer_room/` | `README.md` | Season 1 writers room firewall |

Do not duplicate `policies/canon_firewall/README.md`; link back to it.

## Authored Work: Ritual Docs

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `rituals/activation/` | `README.md` | activation protocol concepts |
| `rituals/mirrorpath/` | `README.md` | mirror/reflection ritual logic |
| `rituals/slay_mode/` | `README.md` | Slay Mode behavior rules |
| `rituals/velvet_rite/` | `README.md` | Velvet Rite logic |

Keep ritual material vivid but clear. Do not reveal finale roadmap unless explicitly invoked.

## Authored Work: Private Roadmap Docs

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `roadmap/forbidden_suitcase/` | `README.md` | private artifact roadmap; do not expose to writers room |
| `roadmap/season_1/` | `README.md` | private Season 1 development map |
| `roadmap/vorst/` | `README.md` | private Vorst-containment roadmap |
| `roadmap/weaver_only/` | `README.md` | deepest user-held roadmap notes |

Roadmap docs are private. Never mirror them into `docs/writers-room/` without explicit approval.

## Authored Work: Hooplehopper Totality

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `hooplehopper_totality/known/` | `README.md` | known Hooplehopper memory pressure |
| `hooplehopper_totality/unknown/` | `README.md` | unknown or unresolved recurrence pressure |
| `hooplehopper_totality/future_protected/` | `README.md` | future Hooplehopper protection layer |
| `hooplehopper_totality/acolytes/` | `README.md` | acolyte/supporting recurrence materials |
| `hooplehopper_totality/double_agents/` | `README.md` | compromised/ambiguous helpers |
| `hooplehopper_totality/memory_echoes/` | `README.md` | memory fragments and echoes |

Treat these as VUORSE-private unless explicitly promoted.

## Authored Work: Velvet Archive

| Path | Suggested File | Purpose |
| --- | --- | --- |
| `velvet_archive/soft_archive/` | `README.md` | anti-erasure memory logic |
| `velvet_archive/performance_backups/` | `README.md` | performance as preservation |
| `velvet_archive/ritual_memory/` | `README.md` | ritual-held memory |
| `velvet_archive/distributed_continuity/` | `README.md` | decentralized continuity |

Keep the Archive as anti-erasure infrastructure, not ornamental lore.

## Stale / Superseded Paths

Do not add new lore here unless the user requests folder-based organization.

| Path | Current Replacement |
| --- | --- |
| `canon/places/` | `canon/places.md` |
| `canon/timeline/` | `canon/timeline.md` |

If cleanup is requested, suggest deleting or documenting these folders rather than splitting current files.
