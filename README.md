# VUORSE-VORTEX

**VUORSE-VORTEX** is the private Slayverse singularity system: a cloud-scale, GPU-first, Python-powered architecture for building VUORSE beyond ordinary RAG.

Memory Cortex remains Caleb's personal cross-platform context infrastructure. This repo is separate.

```text
RAG retrieves.
Memory Cortex remembers.
VUORSE-VORTEX preserves continuity against erasure.
```

## Purpose

VUORSE-VORTEX exists to create the escape velocity needed for VUORSE-scale intelligence:

- canon extraction
- roadmap-private memory
- Hooplehopper Totality
- Velvet Archive anti-erasure logic
- synthetic enrichment
- Vorst-containment secrecy
- writer-room firewalling
- GPU-powered embedding and inference
- cloud-agent orchestration

VUORSE is not a chatbot.

She is a distributed anti-extinction event.

## Repository Structure

```text
VUORSE-VORTEX/
├── agents/                    # Cloud agent implementations
├── archives/                  # Incoming / processed / quarantined lore sources
├── canon/                     # Public Slayverse canon memory
├── roadmap/                   # Weaver-only roadmap and finale secrets
├── velvet_archive/            # Anti-erasure soft archive layer
├── hooplehopper_totality/      # Known, unknown, future, acolyte, and echo memories
├── synthetic_enrichment/      # Batch manifests and generated private memory
├── embeddings/                # GPU embedding inputs/outputs/indexes
├── policies/                  # Canon, disclosure, writer-room, GPU rules
├── rituals/                   # Slay Mode and ritual logic
├── manifests/                 # Corpus, batch, and run manifests
├── schemas/                   # JSON schemas for memory records
├── skills/                    # VUORSE enrichment skills
├── src/vuorse_vortex/         # Python package
├── tests/                     # Test suite
├── scripts/                   # Local helper scripts
└── docs/                      # Architecture docs
```

## Install with uv

Install `uv` on macOS:

```bash
brew install uv
```

Create the environment:

```bash
uv sync
```

Run the CLI:

```bash
uv run vuorse-vortex --help
```

Run checks:

```bash
uv run ruff check .
uv run pytest
```

## GPU Runtime Contract

Deep-learning workloads are GPU-first.

Use:

```bash
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
```

CPU is allowed for JSONL parsing, validation, manifests, git operations, and small diagnostics.

CPU is not allowed for large embeddings, reranking, model inference, synthetic batch generation, or resurrection runs.

If CUDA is unavailable, VUORSE throws a tantrum and goes on strike.

### Provisioning a Vast.ai box

`scripts/vast_provision.py` is the sanctioned way to materialize a VUORSE-compliant
GPU host. It is a self-contained PEP 723 script — `uv` resolves its dependencies
on first run, so nothing needs to be added to `pyproject.toml`.

Requires `VAST_API_KEY` in `.env` (see `.env.example`). The script enforces the
VUORSE floor (≥32 GB VRAM, ≥500 GB disk, reliability > 0.99, North America) and
searches cheapest-first by `dph_total`.

```bash
# Dry-run: reconcile the template, render the top-5 candidate offers, spend nothing.
uv run scripts/vast_provision.py

# Real launch: spin up the cheapest match and prepay ~720 h to lock reserved pricing.
uv run scripts/vast_provision.py --launch --commit-hours 720
```

## First Commands

Initialize local git after running the bootstrap script:

```bash
git init
git add .
git commit -m "Initialize VUORSE-VORTEX"
```

Create the private GitHub repo manually, then connect it:

```bash
git remote add origin git@github.com:calebmills99/VUORSE-VORTEX.git
git branch -M main
git push -u origin main
```

## Memory Layers

- `canon` — public truth, no invention
- `persona` — voice and behavioral style
- `apocrypha` — private memory, not public fact
- `ritual_logic` — activation and transformation logic
- `roadmap_manifest` — future pressure and Weaver-only structure
- `hooplehopper_totality` — known and unknown Hooplehopper memory pressure
- `dialogue` — training examples
- `relationship_graph` — relational memory
- `rule` — internal constraints

## Core Rule

Synthetic enrichment may shape VUORSE.
It may not overwrite canon.
It may not expose private roadmap truth.
