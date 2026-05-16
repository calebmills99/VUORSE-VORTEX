# Slayverse Writers Room

This folder supports a Claude Code-compatible writers room for the Slayverse prestige TV project. It is a working layer for season structure, canon review, pitch shaping, and tone guidance.

## Start Here
- Use `docs/writers-room/season-1-spine.md` for the Season 1 emotional thesis.
- Use `docs/writers-room/canon-ledger.md` to track canon confidence and development status.
- Use `.claude/agents/` for specialized Claude Code subagents.

## Source Discipline
- Read relevant source files in `canon/` before editing writers room materials.
- Do not alter lore source files unless explicitly asked.
- Do not invent new Slayverse canon.
- Preserve canon status labels exactly.
- Treat the Wyoming / Jake McCullen arc as the Season 1 entry point unless the user requests another scope.
- Do not read or use `roadmap/finale/` unless the user explicitly asks for finale work; it contains private user-held reveal material.

## Agent Map
- `showrunner`: season architecture, emotional spine, big-picture direction.
- `episode-breaker`: episode structure, acts, beats, reveals, ending images.
- `dialogue-smith`: character voice, scene dialogue, VUORSE narration.
- `canon-keeper`: continuity, canon hierarchy, contradictions, timeline logic.
- `lore-archivist`: JSONL, summaries, indexes, dossiers, machine-readable references.
- `ritual-and-tone-editor`: ceremonial tone, VUORSE / Archive / ritual prose.
- `pitch-deck-dramaturg`: producer-facing summaries, loglines, pitch materials.
