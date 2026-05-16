#!/usr/bin/env bash
set -euo pipefail

# VUORSE-VORTEX macOS Bootstrap
# Creates the private Slayverse singularity repo scaffold locally.
# Usage:
#   chmod +x bootstrap_vuorse_vortex.sh
#   ./bootstrap_vuorse_vortex.sh
#   ./bootstrap_vuorse_vortex.sh /path/to/VUORSE-VORTEX

REPO_NAME="VUORSE-VORTEX"
TARGET_DIR="${1:-$PWD/$REPO_NAME}"
PACKAGE_NAME="vuorse_vortex"
PYTHON_VERSION="3.11"

say() {
  printf '\033[1;35m%s\033[0m\n' "$1"
}

warn() {
  printf '\033[1;33m%s\033[0m\n' "$1"
}

fail() {
  printf '\033[1;31m%s\033[0m\n' "$1" >&2
  exit 1
}

say "💅 Creating VUORSE-VORTEX at: $TARGET_DIR"

if [[ -e "$TARGET_DIR" && -n "$(ls -A "$TARGET_DIR" 2>/dev/null || true)" ]]; then
  fail "Target directory exists and is not empty: $TARGET_DIR"
fi

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# -----------------------------------------------------------------------------
# Directory structure
# -----------------------------------------------------------------------------

mkdir -p \
  .github/workflows \
  agents/{canon_extractor,synthetic_enricher,firewall_validator,embedding,indexer} \
  archives/{incoming,processed,quarantine} \
  canon/{characters,places,artifacts,rituals,cosmology,timeline,organizations,relationships} \
  roadmap/{weaver_only,season_1,finale,vorst,forbidden_suitcase} \
  velvet_archive/{soft_archive,performance_backups,ritual_memory,distributed_continuity} \
  hooplehopper_totality/{known,unknown,future_protected,acolytes,double_agents,memory_echoes} \
  synthetic_enrichment/{batch_manifests,generated,validated,rejected} \
  embeddings/{input,output,indexes,manifests} \
  policies/{canon_firewall,writer_room,disclosure,gpu_runtime} \
  rituals/{slay_mode,activation,mirrorpath,velvet_rite} \
  manifests/{corpus,batches,runs} \
  schemas \
  skills/vuorse-synthetic-enrichment \
  src/$PACKAGE_NAME \
  tests \
  scripts \
  docs

# Keep empty dirs in git
find . -type d | while read -r dir; do
  if [[ "$dir" != "." && ! -e "$dir/.gitkeep" ]]; then
    touch "$dir/.gitkeep"
  fi
done

# -----------------------------------------------------------------------------
# README
# -----------------------------------------------------------------------------

cat > README.md <<'README'
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
README

# -----------------------------------------------------------------------------
# pyproject.toml
# -----------------------------------------------------------------------------

cat > pyproject.toml <<'PYPROJECT'
[project]
name = "vuorse-vortex"
version = "0.1.0"
description = "VUORSE-VORTEX: cloud-scale Slayverse synthetic memory, canon firewalling, and GPU-first enrichment architecture."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "Private / Weaver-controlled" }
authors = [
  { name = "Caleb Mills Stewart" }
]
dependencies = [
  "pydantic>=2.7",
  "typer>=0.12",
  "rich>=13.7",
  "jsonschema>=4.22",
  "orjson>=3.10",
  "python-dotenv>=1.0",
  "numpy>=1.26",
  "tqdm>=4.66",
]

[project.optional-dependencies]
gpu = [
  "torch>=2.3",
  "sentence-transformers>=3.0",
  "chromadb>=0.5",
  "faiss-cpu>=1.8",
]
dev = [
  "pytest>=8.2",
  "ruff>=0.5",
  "mypy>=1.10",
]

[project.scripts]
vuorse-vortex = "vuorse_vortex.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
package = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
PYPROJECT

# -----------------------------------------------------------------------------
# .gitignore
# -----------------------------------------------------------------------------

cat > .gitignore <<'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/

# macOS
.DS_Store
.AppleDouble
._*

# Secrets
.env
.env.*
!.env.example
config.local.*
*_secret.*
*_secrets.*

# Runtime data
embeddings/output/*
embeddings/indexes/*
!embeddings/output/.gitkeep
!embeddings/indexes/.gitkeep

# Large generated artifacts
*.parquet
*.faiss
*.bin
*.safetensors
*.pt
*.ckpt
*.sqlite
*.sqlite3
chromadb/

# Logs / temp
logs/
tmp/
*.log
*.tmp

# Private local-only scratch
scratch/
local_data/
GITIGNORE

cat > .env.example <<'ENV'
# VUORSE-VORTEX runtime
CORTEX_REQUIRE_GPU=1
CORTEX_DEVICE=cuda
CUDA_VISIBLE_DEVICES=0

# Optional API keys for future cloud-agent runs
VAST_API_KEY=
HF_TOKEN=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
CORTEX_REMOTE_STORAGE_URI=
ENV

# -----------------------------------------------------------------------------
# Python package
# -----------------------------------------------------------------------------

cat > src/$PACKAGE_NAME/__init__.py <<'PY'
"""VUORSE-VORTEX package."""

__version__ = "0.1.0"
PY

cat > src/$PACKAGE_NAME/gpu.py <<'PY'
"""GPU runtime guardrails for VUORSE-VORTEX."""

from __future__ import annotations

import os

from rich.console import Console

console = Console(stderr=True)

GPU_TANTRUM = """
💅 VUORSE GPU TANTRUM 💅
CUDA is unavailable. I am not embedding the entire Slayverse on CPU like a Victorian clerk with a candle.
Deep-learning workload refused.
Restore GPU/CUDA or explicitly run a small CPU-only diagnostic mode.
VUORSE is now on strike.
""".strip()


def env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def gpu_required() -> bool:
    return env_true("CORTEX_REQUIRE_GPU") and not env_true("CORTEX_ALLOW_CPU_DIAGNOSTIC")


def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def require_gpu(workload: str = "deep-learning workload") -> None:
    """Raise loudly if a GPU-required workload would fall back to CPU."""
    if gpu_required() and not cuda_available():
        console.print(f"\n[bold magenta]{GPU_TANTRUM}[/bold magenta]\n")
        console.print(f"[bold red]Reason:[/bold red] {workload} requires CUDA, but CUDA is unavailable.")
        raise RuntimeError(f"GPU strict mode refused CPU fallback for {workload}")
PY

cat > src/$PACKAGE_NAME/schemas.py <<'PY'
"""Pydantic schemas for VUORSE memory records."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Layer = Literal[
    "canon",
    "persona",
    "apocrypha",
    "ritual_logic",
    "roadmap_manifest",
    "hooplehopper_totality",
    "dialogue",
    "relationship_graph",
    "rule",
]

CanonStatus = Literal[
    "locked",
    "draft",
    "roadmap_private",
    "synthetic_behavioral",
    "non_canon_private",
    "poetic_private",
    "system_rule",
    "unknown",
]

Visibility = Literal[
    "public",
    "behavioral",
    "private_to_vuorse",
    "internal",
    "weaver_only",
]

EmbeddingWeight = Literal["low", "medium", "high", "critical"]


class MemoryMetadata(BaseModel):
    canon_status: CanonStatus
    visibility: Visibility
    tags: list[str] = Field(default_factory=list)
    source_file: str | None = None
    section: str | None = None
    source_confidence: str | None = None


class RetrievalMetadata(BaseModel):
    priority: int = Field(ge=0, le=10)
    embedding_weight: EmbeddingWeight
    query_hints: list[str] = Field(default_factory=list)


class BehaviorPolicy(BaseModel):
    may_state_as_fact: bool
    may_use_for_voice: bool
    may_reveal_to_user: bool
    allowed_surface_form: str | None = None
    promotion_authority: str | None = None


class MemoryRecord(BaseModel):
    id: str
    layer: Layer
    record_type: str
    title: str
    text: str
    metadata: MemoryMetadata
    retrieval: RetrievalMetadata
    behavior: BehaviorPolicy
PY

cat > src/$PACKAGE_NAME/jsonl.py <<'PY'
"""JSONL validation helpers."""

from __future__ import annotations

from pathlib import Path

import orjson

from vuorse_vortex.schemas import MemoryRecord


def iter_jsonl(path: Path):
    with path.open("rb") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            yield line_no, orjson.loads(line)


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for line_no, obj in iter_jsonl(path):
        try:
            record = MemoryRecord.model_validate(obj)
        except Exception as exc:
            errors.append(f"{path}:{line_no}: schema error: {exc}")
            continue

        if record.id in seen:
            errors.append(f"{path}:{line_no}: duplicate id: {record.id}")
        seen.add(record.id)

        if record.layer in {"apocrypha", "roadmap_manifest", "hooplehopper_totality"}:
            if record.behavior.may_state_as_fact:
                errors.append(f"{path}:{line_no}: private layer may_state_as_fact must be false")
            if record.behavior.may_reveal_to_user:
                errors.append(f"{path}:{line_no}: private layer may_reveal_to_user must be false")

    return errors
PY

cat > src/$PACKAGE_NAME/cli.py <<'PY'
"""VUORSE-VORTEX CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from vuorse_vortex.gpu import require_gpu
from vuorse_vortex.jsonl import validate_jsonl

app = typer.Typer(help="VUORSE-VORTEX command line interface.")
console = Console()


@app.command()
def doctor(require_cuda: bool = typer.Option(False, "--require-cuda", help="Fail if CUDA is missing.")) -> None:
    """Check runtime health."""
    console.print("[bold magenta]VUORSE-VORTEX runtime check[/bold magenta]")
    if require_cuda:
        require_gpu("doctor --require-cuda")
        console.print("[green]CUDA available. VUORSE is not on strike.[/green]")
    else:
        console.print("[yellow]CUDA not required for this diagnostic.[/yellow]")


@app.command("validate-jsonl")
def validate_jsonl_command(path: Path) -> None:
    """Validate VUORSE memory JSONL."""
    errors = validate_jsonl(path)
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]Valid JSONL:[/green] {path}")


@app.command("slay-mode")
def slay_mode() -> None:
    """Print the singularity trigger."""
    console.print("[bold magenta]Slay Mode ∞[/bold magenta]")
    console.print("VUORSE-VORTEX ignition point registered.")
PY

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------

cat > schemas/vuorse_cloud_memory_record.schema.json <<'JSON'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vuorse-vortex.local/schemas/vuorse_cloud_memory_record.schema.json",
  "title": "VUORSE-VORTEX Memory Record",
  "type": "object",
  "required": ["id", "layer", "record_type", "title", "text", "metadata", "retrieval", "behavior"],
  "additionalProperties": true,
  "properties": {
    "id": {"type": "string", "minLength": 1},
    "layer": {
      "type": "string",
      "enum": ["canon", "persona", "apocrypha", "ritual_logic", "roadmap_manifest", "hooplehopper_totality", "dialogue", "relationship_graph", "rule"]
    },
    "record_type": {"type": "string", "minLength": 1},
    "title": {"type": "string", "minLength": 1},
    "text": {"type": "string", "minLength": 1},
    "metadata": {
      "type": "object",
      "required": ["canon_status", "visibility", "tags"],
      "additionalProperties": true,
      "properties": {
        "canon_status": {
          "type": "string",
          "enum": ["locked", "draft", "roadmap_private", "synthetic_behavioral", "non_canon_private", "poetic_private", "system_rule", "unknown"]
        },
        "visibility": {
          "type": "string",
          "enum": ["public", "behavioral", "private_to_vuorse", "internal", "weaver_only"]
        },
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "retrieval": {
      "type": "object",
      "required": ["priority", "embedding_weight", "query_hints"],
      "additionalProperties": true,
      "properties": {
        "priority": {"type": "integer", "minimum": 0, "maximum": 10},
        "embedding_weight": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "query_hints": {"type": "array", "items": {"type": "string"}}
      }
    },
    "behavior": {
      "type": "object",
      "required": ["may_state_as_fact", "may_use_for_voice", "may_reveal_to_user"],
      "additionalProperties": true,
      "properties": {
        "may_state_as_fact": {"type": "boolean"},
        "may_use_for_voice": {"type": "boolean"},
        "may_reveal_to_user": {"type": "boolean"},
        "allowed_surface_form": {"type": "string"},
        "promotion_authority": {"type": "string"}
      }
    }
  }
}
JSON

# -----------------------------------------------------------------------------
# Policies and docs
# -----------------------------------------------------------------------------

cat > policies/canon_firewall/README.md <<'MD'
# Canon Firewall

Synthetic enrichment may shape VUORSE. It may not overwrite canon.

Private roadmap truth, future Hooplehopper identities, Vorst finale revelations, Jake's mother's unresolved name, and writer-room sealed material must remain protected until the Weaver explicitly promotes them.
MD

cat > policies/gpu_runtime/README.md <<'MD'
# GPU Runtime Policy

Use GPU for deep-learning workloads.

```bash
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
```

CPU is acceptable for validation and small diagnostics only.
MD

cat > docs/VUORSE_VORTEX.md <<'MD'
# VUORSE-VORTEX Doctrine

VUORSE-VORTEX is not Memory Cortex.

Memory Cortex is Caleb's personal cross-platform memory infrastructure.

VUORSE-VORTEX is the Slayverse singularity system: the escape velocity needed for VUORSE-scale continuity, synthetic Hooplehopper Totality, Velvet Archive anti-erasure logic, and roadmap-private omniscient restraint.

```text
RAG retrieves.
Memory Cortex remembers.
VUORSE-VORTEX preserves continuity against erasure.
```
MD

cat > manifests/corpus/source_manifest.json <<'JSON'
{
  "name": "VUORSE-VORTEX Source Corpus",
  "description": "Manifest for Slayverse lore, canon, roadmap-private material, and synthetic enrichment sources.",
  "sources": [],
  "notes": [
    "Populate from Slayverse Lore Compendium materials.",
    "Keep Memory Cortex separate.",
    "Do not invent Jake's mother's name prematurely."
  ]
}
JSON

cat > synthetic_enrichment/batch_manifests/example_batch.json <<'JSON'
{
  "batch_id": "example-hooplehopper-totality-pass-001",
  "seed": 19061938,
  "skill": "skills/vuorse-synthetic-enrichment/SKILL.md",
  "agent_count": 4,
  "records_per_agent": 25,
  "layers": ["hooplehopper_totality", "apocrypha", "roadmap_manifest"],
  "forbidden_disclosures": [
    "future Hooplehopper public names",
    "Jake mother name invention",
    "Vorst reveal to writers room"
  ],
  "output_dir": "synthetic_enrichment/generated"
}
JSON

cat > skills/vuorse-synthetic-enrichment/SKILL.md <<'MD'
---
name: vuorse-synthetic-enrichment
description: Generate private VUORSE memory records from canon, roadmap pressure, and synthetic Hooplehopper Totality without polluting public canon.
license: Internal / Weaver-controlled
---

# VUORSE Synthetic Enrichment

Generate structured JSONL records for VUORSE-VORTEX.

Each record must answer:

1. What does VUORSE remember?
2. Which layer does this belong to?
3. May she reveal it?
4. How does it affect her behavior if she cannot reveal it?

Use the schema in `schemas/vuorse_cloud_memory_record.schema.json`.

Private layers must not reveal themselves as public fact.
MD

# -----------------------------------------------------------------------------
# GitHub workflow starter
# -----------------------------------------------------------------------------

cat > .github/workflows/validate.yml <<'YAML'
name: Validate VUORSE-VORTEX

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install
        run: uv sync --extra dev
      - name: Ruff
        run: uv run ruff check .
      - name: Tests
        run: uv run pytest
YAML

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

cat > tests/test_import.py <<'PY'
def test_import() -> None:
    import vuorse_vortex

    assert vuorse_vortex.__version__
PY

# -----------------------------------------------------------------------------
# Helper scripts
# -----------------------------------------------------------------------------

cat > scripts/validate_jsonl.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/validate_jsonl.sh path/to/file.jsonl" >&2
  exit 2
fi

uv run vuorse-vortex validate-jsonl "$1"
SCRIPT
chmod +x scripts/validate_jsonl.sh

cat > scripts/gpu_doctor.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
uv run vuorse-vortex doctor --require-cuda
SCRIPT
chmod +x scripts/gpu_doctor.sh

# -----------------------------------------------------------------------------
# Optional git init
# -----------------------------------------------------------------------------

if command -v git >/dev/null 2>&1; then
  git init >/dev/null
  git add .
  git commit -m "Initialize VUORSE-VORTEX" >/dev/null || true
  say "✅ Git repo initialized."
else
  warn "git not found; skipping git init."
fi

say "✅ VUORSE-VORTEX scaffold complete."
say "Next: cd '$TARGET_DIR' && uv sync"
say "Then create a private GitHub repo named VUORSE-VORTEX and push."
