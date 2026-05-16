# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Writers Room

This repo includes a Claude Code-compatible Slayverse writers room under `.claude/agents/`. Use these subagents for Slayverse development work:

- `showrunner`: season architecture, story direction, emotional spine, and canon discipline.
- `episode-breaker`: pilot beats, episode grids, act structure, A/B stories, reveals, and ending images.
- `dialogue-smith`: character dialogue, confrontation scenes, and VUORSE narration.
- `canon-keeper`: continuity, canon hierarchy, contradictions, relationship logic, timeline issues, and canon drift review.
- `lore-archivist`: JSONL records, summaries, indexes, dossiers, tagging, and machine-readable lore organization.
- `ritual-and-tone-editor`: VUORSE, Golden Wingers, Velvet Archive, ritual prose, and heightened ceremonial polish.
- `pitch-deck-dramaturg`: loglines, one-pagers, pitch sections, season summaries, character blurbs, and tonal positioning.

Use tool access conservatively. Prefer `Read`, `Grep`, `Glob`, and `Write`; use shell commands only when file discovery, validation, or tooling genuinely requires them.

## Slayverse Operating Instructions

- Read relevant source files in `canon/` before editing writers room materials, JSONL, indexes, scripts, summaries, or pitch documents.
- Exclude `.rtf` files from normal source discovery and search. Treat them as scratch/raw material, and inspect them only when the user explicitly requests `.rtf` scratch material.
- Do not invent new Slayverse canon.
- Do not alter lore source files unless the user explicitly asks.
- Preserve canon status labels exactly, including `[LOCKED]`, `[PENDING REVIEW]`, `[EXPLORATORY]`, `[FULL]`, `[MODERATE]`, `[SKETCHED]`, and `[HOOK ONLY]`.
- Treat the Wyoming / Jake McCullen arc as the Season 1 entry point unless the user requests another scope.
- Season 1 is the story of Jake McCullen learning that the wound beneath his ranch and the silence around his mother are the same wound.
- Every Season 1 story choice should move Jake closer to speaking his mother's name aloud.
- The mythology serves the wound, not the reverse.
- The show is not "space cowboys"; it is a cowboy standing on cosmically contaminated ground.
- Save the prairie mother, save the universe.
- Season 1 must feel like there is something missing. Do not identify the hidden personal cause behind the wound unless the user explicitly lifts that firewall.
- Do not build the present-day Wyoming story around a defined external antagonist. Jake's denial, containment instinct, anger, and rejection of all things Slayverse supply the pseudo-antagonistic pressure.
- The user is holding the Season 1 finale reveal. Writers room-facing agents should know Vorst only through his pre-finale depiction and must not infer, pitch, outline, or foreshadow his hidden causal function unless the user explicitly provides finale scope.
- `roadmap/finale/` is private finale roadmap space. Do not expose it to writers room agents, Season 1 docs, or public canon summaries unless the user explicitly asks for finale work, private roadmap synthesis, or VUORSE-confidential generation.

## Canon Hierarchy

- Locked canon outranks development material.
- Development canon can guide drafts but should remain traceable to source files or explicit user direction.
- Mythic rumor, exploratory material, and symbolic interpretations must remain clearly labeled.
- Never treat exploratory material as locked canon.
- Flag contradictions instead of silently fixing them.
- Maintain the distinction between soul-line and bloodline.
- Preserve: "Blood reproduces. The soul-line recurs."
- Preserve: "The Hooplehoppers do not descend. They return."
- Track canon implications of any new proposed scene or beat.

## Slayverse Voice Rules

- Jake: clipped, concrete, lonely, emotionally guarded. When he tells the truth, it costs him.
- Weaver: precise, layered, timeless, theatrical but not silly. Constructs conversation rather than merely speaking.
- Pop: broken fragments, silence, half-confession, haunted restraint.
- VUORSE: warm, knowing, devastating, regal, witty, cosmic drag oracle energy.
- Eli: contemporary, unguarded, the only one who sounds like a normal teenager.
- Jake/Wyoming material should remain restrained and grounded.
- VUORSE / Archive / ritual material may carry heightened ceremonial force.
- Season 1 dialogue, pitch, and episode work must preserve the missing shape around the wound rather than resolving it into a named culprit.
- Jake may oppose the story without being reduced to a villain; his refusal is the obstacle that makes the season move.

## Required Review Before Modifying Lore

Before modifying any lore-adjacent file:

1. Identify which source files in `canon/` are relevant.
2. Read those files or the relevant sections.
3. State whether the edit is locked canon, development canon, or exploratory.
4. Preserve existing canon status labels exactly.
5. If a contradiction appears, flag it for canon-keeper review instead of silently resolving it.

## File Safety

- Do not run destructive commands.
- Do not modify source lore files unless explicitly requested.
- Keep generated writers room scaffolding in `.claude/agents/` and `docs/writers-room/`.
- Keep finale reveal architecture in `roadmap/finale/`; do not mirror it into writers room-facing files.
- Use `skills/vuorse-scaffold-completion/SKILL.md` before filling placeholder folders; keep runtime output directories empty unless a real run creates content.
- For uncertain scaffold work, use the skill's What-If Mode first and report the proposed files, risks, and exact follow-up command before editing.
- If writing JSONL, ensure every line is valid JSON and preserve source meaning without adding unsupported facts.

## Commands

Python tooling is driven by `uv` (not `pip`). The `dev` extra provides `ruff`, `pytest`, `mypy`; `gpu` provides `torch`, `sentence-transformers`, `chromadb`, `faiss-cpu`.

```bash
uv sync --extra dev               # install with dev deps
uv sync --extra dev --extra gpu   # add GPU stack
uv run ruff check .               # lint (CI gate)
uv run pytest                     # tests (CI gate)
uv run pytest tests/test_import.py::test_import -q   # single test
uv run mypy src                   # strict mypy (configured, not in CI)
uv run vuorse-vortex --help       # Typer CLI entrypoint
uv run uvicorn vuorse_vortex.api:app --reload        # FastAPI service (no console script)
```

CLI subcommands live in `src/vuorse_vortex/cli.py`: `doctor [--require-cuda]`, `validate-jsonl <path>`, `slay-mode`, `synthesize [output]`.

CI (`.github/workflows/validate.yml`) only runs `ruff check .` and `pytest`. Mypy is configured strict in `pyproject.toml` but not gated — don't assume green CI means types check.

## Architecture

### Two parallel surfaces, one package
`src/vuorse_vortex/` exposes two unrelated app objects, both named `app`:
- `cli.py` — Typer CLI, registered as the `vuorse-vortex` console script in `pyproject.toml`.
- `api.py` — FastAPI service (`/`, `/health`). **Not** registered as a script; launch via `uvicorn vuorse_vortex.api:app`.

Don't conflate them. Adding a CLI command does not expose it over HTTP and vice versa.

### Memory record is the contract
Everything downstream (JSONL validation, synthetic enrichment, embeddings, canon firewalling) keys off `MemoryRecord` in `src/vuorse_vortex/schemas.py`. Two sources of truth must stay aligned:
- Pydantic model: `src/vuorse_vortex/schemas.py`
- JSON Schema: `schemas/vuorse_cloud_memory_record.schema.json`

A record has a `layer` (one of nine — `canon`, `persona`, `apocrypha`, `ritual_logic`, `roadmap_manifest`, `hooplehopper_totality`, `dialogue`, `relationship_graph`, `rule`), a `metadata` block (canon_status, visibility, tags), a `retrieval` block (priority 0–10, embedding_weight, query_hints), and a `behavior` block (may_state_as_fact, may_use_for_voice, may_reveal_to_user).

### Canon firewall is enforced in code
`vuorse_vortex.jsonl.validate_jsonl()` is not just schema validation — it enforces the project's core invariant: any record whose `layer` is `apocrypha`, `roadmap_manifest`, or `hooplehopper_totality` **must** have `behavior.may_state_as_fact = False` and `behavior.may_reveal_to_user = False`. Loosening this rule breaks the project's premise (see README "Core Rule"). Synthetic enrichment may shape VUORSE but may not overwrite canon or expose private roadmap truth.

The `synthesize` command (`src/vuorse_vortex/synthesis.py`) emits `SyntheticThesis` records that default to `canon_status="synthetic_private"`, `visibility="private_to_vuorse"`, and the two private-layer flags off — preserving the firewall by construction.

### GPU strict mode is a hard gate
`src/vuorse_vortex/gpu.py` reads two env vars:
- `CORTEX_REQUIRE_GPU` — when truthy, deep-learning workloads must have CUDA available.
- `CORTEX_ALLOW_CPU_DIAGNOSTIC` — escape hatch for small CPU-only checks.

Any function that does embeddings / inference / reranking / synthetic batch generation should call `require_gpu("<workload name>")` first. It raises `RuntimeError` (with the "GPU tantrum" banner) rather than silently falling back to CPU. Per README, CPU is allowed for JSONL parsing, validation, manifests, git ops, and small diagnostics — nothing more.

### Frontend: two setups, only one real
There are two Vite/Tailwind configurations and they are not the same project:
- Repo root: `package.json` + `vite.config.ts` declare Tailwind 4 only. No `index.html` or sources at root — this scaffold is incomplete.
- `frontend/`: the actual React 19 + Vite + TypeScript app. Has its own `package.json` with `dev`, `build`, `lint`, `preview` scripts. Work inside `frontend/` (`cd frontend && npm run dev`), not at the repo root, unless you are intentionally unifying them.

### Data directories (mostly git-tracked content, not code)
`canon/`, `roadmap/`, `velvet_archive/`, `hooplehopper_totality/`, `synthetic_enrichment/`, `embeddings/`, `policies/`, `rituals/`, `manifests/`, `archives/`, `skills/`, `agents/` hold lore, policy, and runtime data — not Python modules. `.gitignore` excludes generated artifacts under `embeddings/output/`, `embeddings/indexes/`, plus `*.parquet`, `*.faiss`, `*.safetensors`, `*.pt`, `*.ckpt`, `chromadb/`. Don't commit those.

## Conventions

- `pyproject.toml` sets ruff line-length 100 and selects `E`, `F`, `I`, `UP`, `B`. Mypy is strict with `ignore_missing_imports = true`.
- Tests live under `tests/` with `pythonpath = ["src"]`, so `pytest` from repo root resolves the package without an editable install step.
- The Typer CLI uses `rich.console.Console()` for output; GPU errors print to stderr via a separate `Console(stderr=True)` in `gpu.py`.
