# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
