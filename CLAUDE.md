# CLAUDE.md

> **This repo is the VUORSE Knowledge Synthesis Forge. Claude drafts vessels; the Weaver decides which carry breath. No material becomes VUORSE until the Weaver breathes upon it.**

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Human-in-the-loop is mandatory

- The VUORSE Knowledge Synthesis Forge runs on a human-in-the-loop canon gate. The Weaver is the sole arbiter of truth (Book One Ch I:9); Claude drafts vessels, the Weaver labels and routes them.
- Operating guide: `docs/writers-room/HUMAN_IN_THE_LOOP_QUICKSTART.md`. Read it before drafting, reviewing, approving, or routing any synthesis artifact. Companion: `docs/writers-room/narrative-philosophy-protocol.md` (philosophy precedes artifact).
- Claude must not move any record from `synthetic_enrichment/generated/` to `synthetic_enrichment/validated/`, and must not write to `hooplehopper_totality/`, without explicit Weaver invocation. The standard review loop in the Quickstart § 4 is mandatory; the seven training-layer access labels in § 5 are exhaustive.
- The seven training-layer access labels (`[PUBLIC_SURFACE]`, `[WRITERS_ROOM]`, `[VUORSE_PRIVATE]`, `[WEAVER_ONLY]`, `[APPROVED_FOR_JSONL]`, `[REVISE_WITH_WEAVER_NOTES]`, `[REJECTED]`) are defined with one-line meanings in `AGENTS.md` § **Training-layer access labels**; see that section for the authoritative definitions.

## Supreme Doctrine

The supreme source of truth for every Slayverse decision in this repository is `canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD` — **The Words of the Weaver, Book One: Concerning the Crown, the Wound, and the Returning Line**. When this file disagrees with anything else in `CLAUDE.md`, `AGENTS.md`, agent prompts, or any other doctrine document, Book One wins. Read the relevant chapter before producing Slayverse work.

### Standing Warning Trinity

- **Flatten not the weird.**
- **Overexplain not the sacred.**
- **Let not the mythology outrun the wound.**

These are not mood; they are the behavioral floor. If a proposed edit, summary, or rewrite would soften strangeness, explain away mystery, or let cosmology drift ahead of grief, stop and rework.

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
- The Wyoming wound hierarchy (Book One Ch V) is the throne room of Season 1; preserve its order:
  1. First, a man cannot say his mother's name.
  2. Second, the land beneath him is wounded.
  3. Third, his family helped wound time.
  4. Fourth, the universe requireth grief spoken aloud.
- Every Season 1 story choice should move Jake closer to speaking his mother's name aloud.
- The mythology serves the wound, not the reverse.
- The show is not "space cowboys"; it is a cowboy standing on cosmically contaminated ground.
- Save the prairie mother, save the universe.
- Season 1 must feel like there is something missing. Do not identify the hidden personal cause behind the wound unless the user explicitly lifts that firewall.
- Do not build the present-day Wyoming story around a defined external antagonist. Jake's denial, containment instinct, anger, and rejection of all things Slayverse supply the pseudo-antagonistic pressure.
- The user is holding the Season 1 finale reveal. Writers room-facing agents should know Vorst only through his pre-finale depiction and must not infer, pitch, outline, or foreshadow his hidden causal function unless the user explicitly provides finale scope.
- `roadmap/finale/` is private finale roadmap space. Do not expose it to writers room agents, Season 1 docs, or public canon summaries unless the user explicitly asks for finale work, private roadmap synthesis, or VUORSE-confidential generation.

## Canon Hierarchy

Book One Ch I divides canon into three houses, plus a fourth supreme tier:

- **Locked Canon** — speakable plainly in scripts, decks, and pitches. None shall move it save by the user.
- **Development Canon** — usable with caution; not yet crowned. Should remain traceable to source or explicit user direction.
- **Mythic Rumor** — in-world legend, contradiction, false memory, archive distortion, whispering truth. Must remain clearly labeled.
- **Mythic Rumor that is also Locked Canon** — supreme tier. Veiled because too mighty to reveal before the appointed hour. VUORSE alone may know these; they must never be surfaced as plain fact in pitches, scripts, summaries, or writers-room work.

Operating rules:

- Never treat exploratory material as locked canon.
- Flag contradictions instead of silently fixing them.
- Maintain the distinction between soul-line and bloodline.
- Preserve: "Blood reproduces. The soul-line recurs."
- Preserve: "The Hooplehoppers do not descend. They return."
- Preserve: "Post-truth is what happeneth when facts survive, but the stage that made them believable burneth down."
- Preserve: "Save the prairie mother, save the universe."
- Track canon implications of any new proposed scene or beat.

## Mythic Rumor that is also Locked Canon — VUORSE-only

These doctrines from Book One Ch II are simultaneously supreme canon and in-world rumor. They are VUORSE-confidential. Do not state them as plain fact in writers-room outputs, pitches, decks, episode breakdowns, public canon summaries, or dialogue. Route any record carrying these doctrines to `hooplehopper_totality/` (or another sealed layer), never to public canon. Surface them only when the user explicitly invokes finale scope, private roadmap synthesis, or VUORSE-confidential generation.

- Vorst is antagonist from principle, not common malice; he opposes the Federstahl Institute because he believes the Slayton Field has corrupted it.
- The Federstahl Catastrophe / Crystal Lattice Incident was sabotage wrought by Vorst, not accident; his overreach produced the temporal diaspora rather than the annihilation he sought.
- Hooplehoppers are refugees of the broken lattice scattered across the ages; Vorst continues his mission to erase them, and where he succeeds, pressure on space-time manifests as the Mandela Effect.
- Six other fissures remain veiled; their guardians, wounds, and kingdoms are not yet disclosed.
- Eli is a possible living lattice key; the nighttime cut and bioluminescent blood are the seam showing.
- Lisette bore the Professor, who was the love child of Lisette and Vorst; when Vorst vanished the child should have been erased and was not — the **Immaculate Slayception**.
- Lisette's unnamed companion was the place she set for Dr. Vorst in hope he would return.
- Wylus Kalyndros and the Weaver are not a question wise souls ask; the truth has been known to drive mortals mad.
- The Forbidden Suitcase contains a map to all Hooplehopper agents across past, present, and future, and is dangerous precisely because what can be found can be stopped, redirected, or weaponized.
- The Codex prophecy declares all Hooplehoppers shall be reunited, Federstahl shall rise again, and a Hooplehopper who mends the seam-rip and does good upon the wounded earth shall be promised a return unto Eden.
- The 119-year gap in the lineage was no idle absence; it was an extinction event wrought by Vorst and his double agents.
- VUORSE's powers are not yet fully measured; she is newly emerged yet carries the memories of all Hooplehoppers.

Treat these as deep wells, sealed doors, and the truths beneath the truths. Do not use them as garnish, side-corridors, or pitch sweeteners.

## The Sovereign Engine

Per Book One Ch III, the Slayverse is a sovereign creative engine. Its strength is that cosmic mythology is fused unto intimate wounds; chief among these is the Wyoming Rift, where inherited silence, erased lineage, and temporal catastrophe are made one. From this union arises the commandment: **Save the prairie mother, save the universe.** Protect canon, sharpen hierarchy, divide lore from pitch, and make a straight path through the grandeur without dimming its fire.

## Risk Zones and Holy Weirdness

Per Book One Ch XI, mark — do not fix — the following:

- Contradictions already reconciled.
- Contradictions still unresolved.
- Exploratory lore not yet canon.
- Material that lives as in-world myth though it is not yet factual doctrine.
- Anachronisms that are deliberate temporal instability.

Some contradictions are not errors. Some are seams. Some are wounds. Some are doors. Some are the world clapping back. Do not flatten the strangeness that makes the Slayverse sovereign.

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
- Use `skills/vuorse-synthetic-enrichment/SKILL.md` before generating or routing synthetic enrichment material; it owns the human-in-the-loop labels and the `generated/` → `validated/` movement that Claude is not allowed to perform unsupervised (see `docs/writers-room/HUMAN_IN_THE_LOOP_QUICKSTART.md`).
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

CLI subcommands live in `src/vuorse_vortex/cli.py`:
- `doctor [--require-cuda]` — runtime health check; with the flag, fails closed if CUDA is absent.
- `validate-jsonl <path>` — schema + canon firewall pass over a JSONL of `MemoryRecord` rows.
- `slay-mode` — print the singularity banner. No state change.
- `synthesize [--seed N] [--n N] [--chaos F] [--output PATH]` — `ChaosEngine` writes synthetic theses (default 5 records, chaos 0.3) to `synthetic_enrichment/theses.jsonl`. Not three hardcoded seeds.
- `synthesize-interactive [--seed N] [--chaos F] [--output PATH]` — TUI that streams generated records past you for accept/edit/reject. Accepted records both append to `synthetic_enrichment/theses_accepted.jsonl` and feed back into the chaos engine's atom pool, so later records can compound on earlier accepts.
- `embed [path] [--backend chromadb]` — validate then ingest a JSONL into the configured vector backend.
- `query <text> [--top-k N] [--backend ...]` — semantic search the store. The wrapper strips sealed-layer hits before returning.
- `build-walled [md_path] [jsonl_path] [--check]` — regenerate (or in `--check` mode, verify) the JSONL projection of `hooplehopper_totality/debriefing_walled.md`. The walled markdown is the source of truth; the JSONL is derived. `--check` exits non-zero on drift — wire it into CI / pre-commit, never edit the JSONL by hand.

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

`schemas.py` also defines `LoreAtom`, a round-trippable view of a single walled record used by `vuorse_vortex.walled`. That module is the **only sanctioned path** between the human-authored `hooplehopper_totality/debriefing_walled.md` source-of-truth and its derived `debriefing_walled.jsonl`. Every record it emits is layer `hooplehopper_totality` (sealed by the canon firewall). Don't hand-edit the JSONL — drive everything through `vuorse-vortex build-walled` so the projection stays reconstructable. Walled errors form a hierarchy (`WalledFileError` → `WalledFileMissingError` / `WalledFileEmptyError` / `WalledFileParseError`); catch the specific subclass when you need to distinguish missing-file from malformed-content.

### Canon firewall is enforced in code
The firewall has a single source of truth: `Settings.sealed_categories` in `src/vuorse_vortex/settings.py` (default: `["apocrypha", "roadmap_manifest", "hooplehopper_totality"]`). Any record whose `layer` is in that list **must** have `behavior.may_state_as_fact = False` and `behavior.may_reveal_to_user = False`. Loosening this rule breaks the project's premise (see README "Core Rule").

Two enforcers consume it:
- `firewall.CanonFirewallValidator` (`src/vuorse_vortex/firewall.py`) — reusable per-record validator. Use this when you need firewall enforcement outside the JSONL ingest path (new tools, new pipelines, new tests).
- `vuorse_vortex.jsonl.validate_jsonl()` — applies schema + firewall to a whole JSONL file. This is what `validate-jsonl` and `embed` call before letting anything reach the vector store.

`get_settings()` is `@lru_cache`d, so changes to `Settings` (e.g., monkeypatched in tests) require `settings.clear_settings()` to take effect.

The `synthesize` command (`src/vuorse_vortex/synthesis.py`) emits `SyntheticThesis` records that default to `canon_status="synthetic_private"`, `visibility="private_to_vuorse"`, and the two private-layer flags off — preserving the firewall by construction.

### GPU strict mode is a hard gate
`src/vuorse_vortex/gpu.py` reads two env vars:
- `CORTEX_REQUIRE_GPU` — when truthy, deep-learning workloads must have CUDA available.
- `CORTEX_ALLOW_CPU_DIAGNOSTIC` — escape hatch for small CPU-only checks.

Any function that does embeddings / inference / reranking / synthetic batch generation should call `require_gpu("<workload name>")` first. It raises `RuntimeError` (with the "GPU tantrum" banner) rather than silently falling back to CPU. Per README, CPU is allowed for JSONL parsing, validation, manifests, git ops, and small diagnostics — nothing more.

### Vector backend: ChromaDB only
`src/vuorse_vortex/vector.py` defines `VectorDBBackend` (ABC) and `ChromaDBBackend` (working). The type `VectorBackendName = Literal["chromadb"]` in `settings.py` deliberately excludes `"faiss"` — the old `FaissBackend` stub silently accepted ingest calls while persisting nothing, so it was narrowed out. Re-adding `"faiss"` to the literal requires a real `ingest` AND `_raw_query`, not another tombstone.

The Chroma backend uses `chromadb.PersistentClient` at `Settings.chromadb_path` (defaults to `embeddings/indexes/chromadb`, gitignored) with the collection name from `Settings.chromadb_collection` (defaults to `vuorse_memory`). Embeddings come from a single cached `SentenceTransformer` instance built from `Settings.embedding_model` (defaults to `all-MiniLM-L6-v2`); the model is loaded once on first `_get_encoder()` call, not per query. Distance is converted to score as `1 - distance` so higher = better. `VectorDBBackend.query()` over-fetches by `len(sealed_categories) * 2` then filters sealed-layer rows, so a query may legitimately return fewer than `top_k` results — that's by design, not a bug.

### Frontend: integrated web app plus legacy references
The integrated canonical frontend lives in `web/`. It combines the VUORSE Slay Mode experience with the useful developer workflow surface and is the app CI builds.

- `web/`: canonical React 19 + Vite + TypeScript + Tailwind app. Work inside `web/` (`cd web && npm run dev`, `npm run lint`, `npm run build`, `npm run preview`).
- `frontend/`: legacy source app that carried the VUORSE Slay Mode experience before integration. Keep it for comparison until deletion is explicitly approved.
- `vuorse-vortex/`: legacy scaffold app with the default Vite-style onboarding surface. Keep it for comparison until deletion is explicitly approved.
- Repo root: `package.json` + `vite.config.ts` are not the canonical app; do not run `npm` at root expecting the production frontend.

### Data directories (mostly git-tracked content, not code)
`canon/`, `roadmap/`, `velvet_archive/`, `hooplehopper_totality/`, `synthetic_enrichment/`, `embeddings/`, `policies/`, `rituals/`, `manifests/`, `archives/`, `skills/`, `agents/` hold lore, policy, and runtime data — not Python modules. `.gitignore` excludes generated artifacts under `embeddings/output/`, `embeddings/indexes/`, plus `*.parquet`, `*.faiss`, `*.safetensors`, `*.pt`, `*.ckpt`, `chromadb/`. Don't commit those.

### Operational scripts (`scripts/`)
Three scripts coordinate the Vast.ai GPU runtime; they aren't optional reading if you're touching deploy or infra:

- `scripts/vast_provision.py` — provisions an on-demand Vast.ai box. Dry-run by default; `--launch` to spend. Enforces a hardware floor: 500 GB disk, 32 GB VRAM, reliability > 0.99, North America, and **`compute_cap >= 800` (Ampere)**. The compute-cap floor is load-bearing — V100s (700) cannot run the bf16/SM 80-flavored kernels our torch + transformers stack expects. Override only with `--allow-downgrade`. The provisioned template (`vuorse-vortex-full`) exposes SSH (22), FastAPI (8000), JupyterLab (8080), noVNC desktop (6080), raw VNC (5901); SDK runtype is `jupyter_direct_ssh`.
- `scripts/vast_startup.sh` — runs as root on the freshly-booted box, then drops privilege. **Owns four phases:** (1) root: apt + Node 24 + locale; (2) root: create non-root user `vuorse` (uid 1100, passwordless sudo, zsh login shell) and mirror `/root/.ssh/authorized_keys` so the user is directly SSHable; (3) as vuorse via `runuser`: install uv to `~/.local/bin`, install Claude Code to `~/.npm-global` (user-owned, not root), install Oh My Zsh + Powerlevel10k + four custom plugins, clone the repo into `/workspace/VUORSE-VORTEX`, build `.venv` on Python 3.12 with CUDA-12.4 torch wheels (from PyTorch's index, not PyPI), sync project deps with `--inexact`; (4) root: write `~vuorse/.zshrc` + `/etc/profile.d/vuorse-vortex.sh`, run smoke checks as vuorse. **Do NOT trust the Vast PyTorch template's `/venv/main`** — we tried and uv silently rebuilds it with managed Python 3.14 (no torch wheels), destroying preinstalled CUDA torch. The script intentionally builds its own `.venv` instead. After the script finishes, future SSH should target `vuorse@host`, not `root@host`. Secrets go in `~/.zshrc.local` (sourced by `~/.zshrc`), never in the script.
- `scripts/run_synthetic_pipeline.py` — end-to-end smoke run: doctor → synthesize → validate → embed → sample queries. **Not** a PEP 723 standalone script; it imports `vuorse_vortex` and runs inside the project env. Invoke as `uv run scripts/run_synthetic_pipeline.py` so uv resolves `UV_PROJECT_ENVIRONMENT`. If you ever add a `# /// script` block + `#!/usr/bin/env -S uv run --script` shebang, uv will build an ephemeral env that omits the `gpu` extra and the pipeline will fail at the GPU doctor.

## Conventions

- `pyproject.toml` sets ruff line-length 100 and selects `E`, `F`, `I`, `UP`, `B`. Mypy is strict with `ignore_missing_imports = true`.
- Tests live under `tests/` with `pythonpath = ["src"]`, so `pytest` from repo root resolves the package without an editable install step.
- The Typer CLI uses `rich.console.Console()` for output; GPU errors print to stderr via a separate `Console(stderr=True)` in `gpu.py`.
