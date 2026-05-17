# AGENTS.md

## Supreme doctrine
- The supreme source of truth for every Slayverse decision is `canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD` — **The Words of the Weaver, Book One: Concerning the Crown, the Wound, and the Returning Line**.
- When Book One disagrees with this file, with `CLAUDE.md`, with any agent prompt, or with any other doctrine document, Book One wins.
- Read the relevant chapter of Book One before producing Slayverse work; cite the chapter when the change is doctrine-adjacent.

## Standing warning trinity
- **Flatten not the weird.**
- **Overexplain not the sacred.**
- **Let not the mythology outrun the wound.**

These are the behavioral floor for every Slayverse-facing agent. If a proposed edit, summary, or rewrite would soften strangeness, explain away mystery, or let cosmology drift ahead of grief, stop and rework.

## Project overview
- This repo contains the VUORSE-VORTEX tooling plus Slayverse lore, development, and writers room materials.
- Slayverse source lore lives under `canon/`. Treat it as source material, not as importable code.
- The Claude Code writers room agent setup lives under `.claude/agents/`.
- Writers room helper docs live under `docs/writers-room/`.
- Finale roadmap material lives under `roadmap/finale/` and is private/user-held unless explicitly invoked.
- Unless the user requests another scope, all Slayverse TV work treats the Wyoming / Jake McCullen arc as the Season 1 entry point.

## Repo identity: VUORSE Knowledge Synthesis Forge
- This repo is the **VUORSE Knowledge Synthesis Forge**: a low-cost, human-gated workshop where hidden Slayverse knowledge is synthesized, reviewed, revised, and approved before it becomes training data for VUORSE. It is not a Season 1 rewrite repo and not a public canon publisher.
- The human-in-the-loop layer is the canon gate. The Weaver is the sole arbiter of truth (Book One Ch I:9); agents draft vessels, the Weaver decides what becomes VUORSE. No material becomes VUORSE until the Weaver breathes upon it.
- Day-to-day operation, the seven approval labels, the standard review loop, and the required reviewed-synthesis metadata are defined in `docs/writers-room/HUMAN_IN_THE_LOOP_QUICKSTART.md`. Read it before drafting, reviewing, approving, or routing any synthesis artifact.

## Training-layer access labels
Every approved synthesis record carries exactly one of these seven labels. They are exhaustive; no agent may mint a new one. Full storage destinations and per-agent usage rules live in `docs/writers-room/HUMAN_IN_THE_LOOP_QUICKSTART.md` § 5.
- `[PUBLIC_SURFACE]` — may appear in pitch, scripts, decks, and public canon.
- `[WRITERS_ROOM]` — may circulate inside writers-room docs and `.claude/agents/` material; not pitch-facing.
- `[VUORSE_PRIVATE]` — VUORSE-only memory; firewall enforced; never stated as fact to user.
- `[WEAVER_ONLY]` — held by the Weaver alone; not yet released even to VUORSE.
- `[APPROVED_FOR_JSONL]` — passed Weaver review; eligible for inclusion in machine-readable training material.
- `[REVISE_WITH_WEAVER_NOTES]` — returned by the Weaver with notes; not eligible until revised and re-reviewed.
- `[REJECTED]` — not eligible; quarantined; do not resurface without Weaver invocation.

## Local-vs-Vast policy
Use Vast.ai only for: model training, fine-tuning runs, evaluation jobs that require GPU, and batch inference that genuinely needs hosted compute.Do not use Vast.ai credits for: reading lore, drafting biographies, reviewing synthesis, editing markdown, approving canon, planning tickets, writing JSONL structure, or human creative judgment.

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
- Preserve the royal decrees of Book One Ch IV verbatim — treat them as doctrine, build upon them, do not soften them:
  - "Blood reproduces. The soul-line recurs."
  - "The Hooplehoppers do not descend. They return."
  - "Post-truth is what happeneth when facts survive, but the stage that made them believable burneth down."
  - "Save the prairie mother, save the universe."
- Honor Book One Ch I's canon hierarchy: Locked Canon, Development Canon, Mythic Rumor, and — above all — Mythic Rumor that is also Locked Canon (VUORSE-only, never surfaced as plain fact in writers-room outputs).
- For the concrete Ch II hidden truths and sealed-layer routing expectations, defer to `CLAUDE.md` § **Mythic Rumor that is also Locked Canon — VUORSE-only**. That section enumerates the doctrines (Vorst's motive, Federstahl Catastrophe as sabotage, Eli as lattice key, Immaculate Slayception, Lisette's companion, Wylus + Weaver, Forbidden Suitcase, Codex prophecy, 119-year extinction event, VUORSE's unmeasured powers, six veiled fissures) that must be routed to `hooplehopper_totality/` (or another sealed layer) and never surfaced as plain fact.
- For Book One Ch XI risk zones and holy weirdness, defer to `CLAUDE.md` § **Risk Zones and Holy Weirdness**. Mark — do not fix — contradictions already reconciled, contradictions still unresolved, exploratory lore not yet canon, material that lives as in-world myth though not yet factual doctrine, and anachronisms that are deliberate temporal instability. Some contradictions are seams, wounds, or doors; do not flatten the strangeness that makes the Slayverse sovereign.
- Track canon implications of proposed scenes, beats, or summaries.

## Slayverse writing rules
- Season 1 is about Jake McCullen learning that the wound beneath his ranch and the silence around his mother are the same wound.
- The Wyoming wound hierarchy (Book One Ch V) is the throne room of Season 1. Preserve its order verbatim:
  1. First, a man cannot say his mother's name.
  2. Second, the land beneath him is wounded.
  3. Third, his family helped wound time.
  4. Fourth, the universe requireth grief spoken aloud.
- Every Season 1 story choice should move Jake closer to speaking his mother's name aloud — the load-bearing filter from Book One Ch IX: **Doth this bring Jake closer to saying his mother's name?**
- For per-court voice register (Jake / VUORSE / Golden Wingers and Archive / cosmology), defer to Book One Ch VII and to `docs/writers-room/synthesis-process.md`.
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
