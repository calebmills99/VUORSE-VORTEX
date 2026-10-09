# Cleanup Notes - 2026-10-09

## Removed

- `Drag Race Investigation/` - forensic/evidence package marked "not canon"; outside governed roots, absent from `source_manifest.json`, and not cited by the Seam Index.
- `FrameCode-VibeWork-V0.14.0-en-US/` - untracked portable Markdown governance framework; outside governed roots and unrelated to VUORSE/Slayverse canon.
- `canon/1_words_of_weaver_book_one/Jenna Maroney.md` - untracked scratch file containing only `6+9` and `15`; not legitimate canon.

## JSON Updates

- `manifests/corpus/source_manifest.json`
  - Added `canon-characters-characters-first-folio` for `canon/characters/characters_first_folio.md`.
  - Added `canon-characters-characters-second-folio` for `canon/characters/characters_second_folio.md`.
  - Updated `source_count` to match the current 49 records.
- `worldforge/worldforge/lore-index-2.0/slayverse_lore_index_2.0.json`
  - Added `src:repo:canon-characters-characters-first-folio`.
  - Added `src:repo:canon-characters-characters-second-folio`.
  - Both records use `type: repository-document`, `availability: repository`, `repository_path`, and matching `manifest_source_id`.

## Validation

- `uv run vuorse-vortex validate-lore-index`
  - Passed: valid repository-synchronized lore index.
- `uv sync --extra dev`
  - Installed missing test dependency `iniconfig` and related dev packages needed by the local pytest environment.
- `uv run python -m pytest tests/test_lore_index.py -q`
  - Passed: `3 passed, 1 warning in 0.23s`.
  - Warning: pytest could not create `.pytest_cache\v\cache\nodeids` due to Windows access denied.

## Ambiguous Items Left Untouched

- `_to_delete/` - ignored archival/deletion staging area; left untouched.
- `HOME_BASE.md` - VUORSE root note; left untouched.
- `project-specs/` and `project-tasks/` - VUORSE remediation docs; left untouched.
- Existing dirty canon, manifest, web, and worldforge edits predated this cleanup pass and were not reverted.
