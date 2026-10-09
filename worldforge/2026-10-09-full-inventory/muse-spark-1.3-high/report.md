# Full inventory report - 2026-10-09 (`muse-spark-1.3-high`)

Source data: `inventory.jsonl` in this directory. Scope: `.json/.jsonl/.md/.txt` (case-insensitive). `.agent-quarantine/`, virtualenvs, caches, build outputs, and `node_modules/` pruned and not inspected.

## Totals

Files: 459 | Total bytes: 39509228 | Total lines: 115065

By ext:
- .json: 77
- .jsonl: 36
- .md: 278
- .txt: 68

By zone:
- Slayverse: 84
- canon: 23
- comfyui-expert: 71
- docs: 16
- hooplehopper_totality: 9
- manifests: 4
- other: 55
- persona: 4
- policies: 4
- roadmap: 8
- root: 10
- scripts: 1
- skills: 14
- synthetic_enrichment: 61
- web: 7
- worldforge: 88

By git_status:
- tracked: 405
- untracked: 54

## Twenty largest files (path, bytes, lines)

- canon/projects/projects.json | 6206350 bytes | 1 lines
- synthetic_enrichment/generated/canon_corpus_semantic_sift_v2.jsonl | 5279660 bytes | 2251 lines
- synthetic_enrichment/generated/canon_corpus_semantic_sift.jsonl | 5180475 bytes | 2251 lines
- synthetic_enrichment/generated/canon_corpus_raw.jsonl | 4624590 bytes | 2251 lines
- Slayverse/json/jsonl/slayverse_md_batch_messages_fixedgguf.json | 3255704 bytes | 1406 lines
- canon/slayverse_md_records_clean/slayverse_md_records_clean.jsonl | 2253221 bytes | 1406 lines
- Slayverse/json/jsonl/slayverse_md_records_clean.jsonl | 2253221 bytes | 1406 lines
- synthetic_enrichment/generated/canon_corpus_raw_audit.md | 595887 bytes | 2151 lines
- synthetic_enrichment/generated/canon_corpus_entity_sift_scripted.jsonl | 586035 bytes | 486 lines
- synthetic_enrichment/generated/vuorse_secret_training_knowledge_candidates.jsonl | 545453 bytes | 262 lines
- synthetic_enrichment/batches/batch_002a_hh_discovery_augment/training_examples.jsonl | 543714 bytes | 272 lines
- synthetic_enrichment/generated/vuorse_sft_batch_001_002_plus_hh_discovery_draft.jsonl | 543714 bytes | 272 lines
- worldforge/2026-10-09-full-inventory/muse-spark-1.3-high/inventory.jsonl | 538582 bytes | 785 lines
- synthetic_enrichment/batches/batch_001_vuorse_synthesis/training_examples.jsonl | 527284 bytes | 262 lines
- synthetic_enrichment/generated/vuorse_sft_batch_001_002_combined_draft.jsonl | 527284 bytes | 262 lines
- synthetic_enrichment/generated/vuorse_sft_training_examples_style_approved.jsonl | 527284 bytes | 262 lines
- synthetic_enrichment/generated/vuorse_sft_training_examples_draft.jsonl | 467024 bytes | 262 lines
- worldforge/worldforge/lore-index-2.0/slayverse_lore_index_2.0.json | 326815 bytes | 10560 lines
- synthetic_enrichment/generated/weaver_review_packet_001_mythic_and_hooplehopper.md | 234786 bytes | 6592 lines
- synthetic_enrichment/generated/batch_002_person_training_candidates.jsonl | 165273 bytes | 76 lines

## Duplicate content (non-empty files sharing sha256)

- sha256 0fc78a60e322a8e2.. (4 files):
  - comfyui-expert/references/workflows.md
  - comfyui-expert/skills/comfyui-character-gen/references/workflows.md
  - comfyui-expert/skills/comfyui-video-production/references/workflows.md
  - comfyui-expert/skills/comfyui-workflow-builder/references/workflows.md
- sha256 0a483948e25a0056.. (3 files):
  - comfyui-expert/references/models.md
  - comfyui-expert/skills/comfyui-character-gen/references/models.md
  - comfyui-expert/skills/comfyui-workflow-builder/references/models.md
- sha256 5d78a362313202df.. (3 files):
  - synthetic_enrichment/batches/batch_001_vuorse_synthesis/training_examples.jsonl
  - synthetic_enrichment/generated/vuorse_sft_batch_001_002_combined_draft.jsonl
  - synthetic_enrichment/generated/vuorse_sft_training_examples_style_approved.jsonl
- sha256 835fc830012be7ad.. (2 files):
  - Slayverse/assets/lora_training/sassy_frames/clip04/clip04_001 - Copy.txt
  - Slayverse/assets/lora_training/sassy_frames/clip04/clip04_001.txt
- sha256 b914d955a51f8921.. (2 files):
  - Slayverse/json/slayverse_index.json
  - Slayverse/json/slayverse_index_orginal.json
- sha256 e3946af5e5a1a382.. (2 files):
  - _to_delete/claude-promoted/Continutity_Audit.md
  - Slayverse/json/jsonl/Continutity_Audit.md
- sha256 4d780e5f0617a815.. (2 files):
  - _to_delete/claude-promoted/Theory_of_Everything_Confirmed_.md
  - Slayverse/md/Theory_of_Everything_Confirmed_.md
- sha256 19b983a57e263757.. (2 files):
  - _to_delete/claude-promoted/golden_wings_intergaltactic_league_charter.json
  - Slayverse/json/golden_wings_intergaltactic_league_charter.json
- sha256 9ef1582ca199f81a.. (2 files):
  - _to_delete/claude-promoted/sassafras_a_mcgraw_ultimate_origin.json
  - Slayverse/json/sassafras_a_mcgraw_ultimate_origin.json
- sha256 e9a3119e52b4c64b.. (2 files):
  - _to_delete/claude-promoted/sassafrass_a_mcgraw_texas_hopper_tall_tale.json
  - Slayverse/json/sassafrass_a_mcgraw_texas_hopper_tall_tale.json
- sha256 cbb8bcf939f17e79.. (2 files):
  - _to_delete/claude-promoted/slayton_particle_discovery.md
  - Slayverse/md/slayton_particle_discovery.md
- sha256 dfbf5514069434bb.. (2 files):
  - _to_delete/claude-promoted/slayverse_session_archive_first_steward_transmission.md
  - Slayverse/md/slayverse_session_archive_first_steward_transmission.md
- sha256 9e615e0dfeaa5c30.. (2 files):
  - canon/slayverse_md_records_clean/slayverse_md_records_clean.jsonl
  - Slayverse/json/jsonl/slayverse_md_records_clean.jsonl
- sha256 93586c5dadff9ca6.. (2 files):
  - comfyui-expert/references/evolution.md
  - comfyui-expert/skills/comfyui-character-gen/references/evolution.md
- sha256 4663973c19e1b3af.. (2 files):
  - comfyui-expert/references/lora-training.md
  - comfyui-expert/skills/comfyui-character-gen/references/lora-training.md
- sha256 71bc5b0a535a41b7.. (2 files):
  - comfyui-expert/references/prompt-templates.md
  - comfyui-expert/skills/comfyui-workflow-builder/references/prompt-templates.md
- sha256 82739e9dd2f47315.. (2 files):
  - comfyui-expert/references/troubleshooting.md
  - comfyui-expert/skills/comfyui-video-production/references/troubleshooting.md
- sha256 9016cf9af1d32cb5.. (2 files):
  - comfyui-expert/references/voice-synthesis.md
  - comfyui-expert/skills/comfyui-character-gen/references/voice-synthesis.md
- sha256 44afd78438ae3516.. (2 files):
  - skills/gandalf-the-gray-eye/references/artifacts.md
  - Slayverse/skills/gandalf_grey_eye/references/artifacts.md
- sha256 98f274a2fdc8eb02.. (2 files):
  - skills/gandalf-the-gray-eye/references/human-nodes.md
  - Slayverse/skills/gandalf_grey_eye/references/human-nodes.md
- sha256 3bbb750c1c786ac0.. (2 files):
  - skills/gandalf-the-gray-eye/references/labels.md
  - Slayverse/skills/gandalf_grey_eye/references/labels.md
- sha256 a71ffd29aea0747d.. (2 files):
  - skills/gandalf-the-gray-eye/references/report-template.md
  - Slayverse/skills/gandalf_grey_eye/references/report-template.md
- sha256 bdc54c3c5d36e430.. (2 files):
  - synthetic_enrichment/batches/batch_001_vuorse_synthesis/candidate_report.md
  - synthetic_enrichment/generated/vuorse_secret_training_knowledge_candidates_report.md
- sha256 0ef5ab2f721ed972.. (2 files):
  - synthetic_enrichment/batches/batch_001_vuorse_synthesis/report.md
  - synthetic_enrichment/generated/vuorse_sft_training_examples_style_approved_report.md
- sha256 0862b7aacf757ad6.. (2 files):
  - synthetic_enrichment/batches/batch_001_vuorse_synthesis/weaver_review_decisions.jsonl
  - synthetic_enrichment/generated/weaver_review_decisions.jsonl
- sha256 5f4575a8e55ef600.. (2 files):
  - synthetic_enrichment/batches/batch_002_person_confirmation/combined_duplicate_report.md
  - synthetic_enrichment/generated/vuorse_sft_batch_001_002_combined_draft_report.md
- sha256 f76e1ffe38126b46.. (2 files):
  - synthetic_enrichment/batches/batch_002_person_confirmation/person_examples_confirmed_duplicate.jsonl
  - synthetic_enrichment/generated/batch_002_person_sft_examples_draft.jsonl
- sha256 ec3f65fb206f165f.. (2 files):
  - synthetic_enrichment/batches/batch_002_person_confirmation/weaver_review_decisions_batch_002_person.jsonl
  - synthetic_enrichment/generated/weaver_review_decisions_batch_002_person.jsonl
- sha256 21d7e473c5dbad84.. (2 files):
  - synthetic_enrichment/batches/batch_002a_hh_discovery_augment/hh_discovery_extraction_report.md
  - synthetic_enrichment/generated/hooplehopper_agent_discovery_extraction_report.md
- sha256 4cec43af6c231f81.. (2 files):
  - synthetic_enrichment/batches/batch_002a_hh_discovery_augment/hh_discovery_sft_draft.jsonl
  - synthetic_enrichment/generated/hooplehopper_agent_discovery_sft_draft.jsonl

## Hygiene

- zero-byte files: 3
  - Slayverse/assets/lora_training/sassy_frames/clip01/clip01_001.txt
  - Slayverse/assets/lora_training/sassy_frames/clip01/clip01_002.txt
  - Slayverse/assets/lora_training/sassy_frames/clip01/clip01_005.txt
- non-UTF-8 files: 0

## Coverage Notes

- This is a disk inventory, not canon promotion. Corpus authority remains `manifests/corpus/source_manifest.json`.
- Removed straight-documentary scratch paths and removed non-canon investigation dumps are not represented in this regenerated inventory.
