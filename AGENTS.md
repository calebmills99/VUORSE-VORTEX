# AGENTS.md

## Project overview
- This repo contains the VUORSE-VORTEX tooling plus Slayverse lore, development, and writers room materials.
- Slayverse source lore lives under `canon/`. Treat it as source material, not as importable code.
- The Claude Code writers room agent setup lives under `.claude/agents/`.
- Writers room helper docs live under `docs/writers-room/`.
- Finale roadmap material lives under `roadmap/finale/` and is private/user-held unless explicitly invoked.
- Unless the user requests another scope, all Slayverse TV work treats the Wyoming / Jake McCullen arc as the Season 1 entry point.

## Slayverse source file map
- `canon/SLAYVERSE_TV_SERIES_BIBLE.md` — primary TV series bible when present.
- `canon/creative_works.md` — creative works and project-adjacent source material.
- `canon/story_arcs.md` — narrative arcs, season movements, mythic events, and development levels.
- `canon/timeline.md` — chronological sequence of known Slayverse events.
- `canon/open_threads.md` — undeveloped hooks, contradictions, gaps, and opportunities.
- `canon/places.md` — locations, realms, fissures, archives, and recurring sites.
- `canon/writers-room.agent.md` — writers room operating prompt/source instructions.
- `canon/projects.json` — project metadata.
- `canon/ett555.rtf` — raw scratch/source material; exclude `.rtf` files from normal search and discovery unless the user explicitly asks to inspect scratch files.
- `canon/characters/characters.md` — character source material.
- `canon/cosmology/cosmology.md` — cosmology source material.
- `canon/artifacts/artifacts.md` — artifact source material.
- `canon/rituals/rituals.md` — ritual source material.
- `canon/relationships/relationship_map.md` — relationship source material.
- `canon/organizations/organizations.md` — organization source material.
- `canon/slayverse_index.json` — Slayverse index.
- `canon/slayverse_md_records_clean.jsonl` — machine-readable lore records.
- Some expected development files may be absent, top-level, nested, or generated later; use `rg --files canon -g '!*.rtf'` before assuming a path.
- Treat all `.rtf` files as scratch/raw material. Do not include them in ordinary `rg`, `Grep`, or corpus-discovery passes unless the user explicitly requests `.rtf` scratch material.

## Slayverse canon rules
- Read the relevant `canon/` files before editing writers room docs, JSONL, indexes, scripts, or summaries.
- Do not invent new Slayverse canon.
- Do not alter lore source files unless the user explicitly asks.
- Preserve canon status labels exactly, including `[LOCKED]`, `[PENDING REVIEW]`, `[EXPLORATORY]`, `[FULL]`, `[MODERATE]`, `[SKETCHED]`, and `[HOOK ONLY]`.
- Never treat exploratory material as locked canon.
- Flag contradictions instead of silently fixing them.
- Maintain the distinction between soul-line and bloodline.
- Preserve: "Blood reproduces. The soul-line recurs."
- Preserve: "The Hooplehoppers do not descend. They return."
- Track canon implications of proposed scenes, beats, or summaries.

## Slayverse writing rules
- Season 1 is about Jake McCullen learning that the wound beneath his ranch and the silence around his mother are the same wound.
- Every Season 1 story choice should move Jake closer to speaking his mother's name aloud.
- The mythology serves the wound, not the reverse.
- The show is not "space cowboys"; it is a cowboy standing on cosmically contaminated ground.
- Save the prairie mother, save the universe.
- Season 1 must feel like there is something missing. Do not identify the hidden personal cause behind the wound unless the user explicitly lifts that firewall.
- Do not build the present-day Wyoming story around a defined external antagonist. Jake's denial, containment instinct, anger, and rejection of all things Slayverse supply the pseudo-antagonistic pressure.
- The user is holding the Season 1 finale reveal. Writers room-facing agents should know Vorst only through his pre-finale depiction and must not infer, pitch, outline, or foreshadow his hidden causal function unless the user explicitly provides finale scope.
- Do not expose `roadmap/finale/` material to writers room agents or Season 1 docs unless the user explicitly asks for finale work, private roadmap synthesis, or VUORSE-confidential generation.
- Reveal cosmic scale through human consequence, objects, land, behavior, weather, sound, and withheld memory.
- Keep Wyoming and Jake material restrained and grounded; reserve heightened ceremonial force for VUORSE, Archive, and ritual material where supported by source.

## Slayverse JSONL rules
- Each JSONL line must be valid JSON.
- Preserve source meaning and nuance.
- Do not add facts not present in source material.
- Include metadata fields when available: `id`, `title/name`, `type`, `status`, `summary`, `tags`, `related`, `source_pages`, `references`, `canon_status`.
- Prefer machine-readable clarity over ornamental prose.
- Validate project memory records with `uv run vuorse-vortex validate-jsonl <path>` when working on schema-governed JSONL.
- Keep `src/vuorse_vortex/schemas.py` and `schemas/vuorse_cloud_memory_record.schema.json` in sync when the record contract changes.

## Python tooling (uv)
- Install: `uv sync --extra dev` (add GPU stack with `--extra gpu`)
- Lint: `uv run ruff check .`
- Tests: `uv run pytest` (single: `uv run pytest tests/test_import.py::test_import -q`)
- Typecheck (strict): `uv run mypy src`
- CLI: `uv run vuorse-vortex --help`
- API: `uv run uvicorn vuorse_vortex.api:app --reload`

## Entry points
- `src/vuorse_vortex/cli.py` is the Typer CLI (`vuorse-vortex` console script).
- `src/vuorse_vortex/api.py` is the FastAPI app (`app`); HTTP endpoints are separate from CLI commands.

## Memory record contract
- Keep `src/vuorse_vortex/schemas.py` and `schemas/vuorse_cloud_memory_record.schema.json` in sync.
- `vuorse_vortex/jsonl.py` enforces: `apocrypha`, `roadmap_manifest`, `hooplehopper_totality` must set `behavior.may_state_as_fact = False` and `behavior.may_reveal_to_user = False`.

## GPU strict mode
- `src/vuorse_vortex/gpu.py` gates with `CORTEX_REQUIRE_GPU` and `CORTEX_ALLOW_CPU_DIAGNOSTIC`.
- Call `require_gpu("<workload>")` before embeddings/inference/reranking or other deep-learning work.

## Frontend layout
- The integrated canonical Vite React app now lives in `web/`.
- Legacy comparison apps remain in `frontend/` and `vuorse-vortex/`; do not treat either as canonical unless the user explicitly asks for legacy comparison work.
- Repo root only has Tailwind deps (`package.json`) + `vite.config.ts` and no canonical Vite app sources; do not run `npm` at root expecting the production frontend.
- Use `cd web && npm run dev|lint|build|preview` for frontend work.

## Repo data vs code
- Python package lives in `src/vuorse_vortex/`; top-level lore dirs (`canon/`, `roadmap/`, `velvet_archive/`, `hooplehopper_totality/`, `synthetic_enrichment/`, etc.) are content, not importable modules.
- `bootstrap_vuorse_vortex.sh` defines intended `.gitignore` patterns (e.g., `embeddings/output/`, `embeddings/indexes/`, `*.parquet`, `*.faiss`, `*.safetensors`, `*.pt`, `*.ckpt`, `chromadb/`); treat these as generated artifacts.

## Testing + style
- Pytest uses `pythonpath = ["src"]` (run from repo root; no editable install needed).
- Ruff line length 100; rules `E`, `F`, `I`, `UP`, `B`; mypy is strict (`ignore_missing_imports = true`).

## File safety
- Do not run destructive commands.
- Do not commit generated embedding artifacts, local databases, model weights, or other generated data.
- Before modifying lore-adjacent files, list the source files reviewed and whether the change is canon, development canon, or exploratory.
- Keep finale roadmap reveals in `roadmap/finale/`; do not mirror them into `docs/writers-room/` or `canon/writers-room.agent.md`.
- Use `skills/vuorse-scaffold-completion/SKILL.md` when filling placeholder folders; do not populate runtime output directories by hand.
- For uncertain scaffold work, use the skill's What-If Mode first and report the proposed files, risks, and exact follow-up command before editing.
