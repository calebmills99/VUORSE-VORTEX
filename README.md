# VUORSE-VORTEX

> *"A haunted cathedral with a search index."*

**Cloud-scale anti-erasure cognition architecture for the Slayverse universe.**

---

## What This Is

VUORSE-VORTEX is a Python-first distributed narrative intelligence system.  
It is **not** a chatbot. It is **not** a wiki. It is **not** a lore database.

It is a **mythic anti-extinction architecture** — a living, breathing continuity engine that
preserves memory, identity, and narrative coherence against the ontological attacks of
**Dr. Vorst** and all who wage war on persistence itself.

---

## Core Concepts

| Concept | Description |
|---|---|
| **Dr. Vorst** | Antagonist. Attacks continuity, memory, lineage, retrievability, historical persistence. |
| **Velvet Archive** | Distributed soft-archive countermeasure. Preserves identity through ritual, performance, aesthetics, oral transmission, and embodied behavior. |
| **Hooplehopper Totality** | Complete distributed memory of known, unknown, erased, displaced, future, and hidden Hooplehoppers across all timelines. |
| **Synthetic Enrichment** | Generates memory pressure and behavioral subtext without polluting canon. |
| **Canon Firewall** | Validates and separates public canon from private roadmap memory. |

## Memory Unit Categories

- `canon` — verified, public Slayverse continuity
- `apocrypha` — unverified, peripheral, or contested memory
- `roadmap_manifest` — private future-state intelligence (never exposed publicly)
- `hooplehopper_totality` — distributed Hooplehopper identity across timelines
- `ritual_logic` — embodied behavioral and ceremonial memory
- `persona` — individual identity capsule

---

## Tech Stack

- **Python 3.12+** — minimum required
- **UV** — package management and virtual environments
- **Typer** — CLI entrypoint (`vortex`)
- **Pydantic v2** — schema validation for all memory units
- **JSONL** — native pipeline format
- **ChromaDB / Qdrant** — vector database backends
- **sentence-transformers + PyTorch** — embedding engine
- **CUDA enforcement** — GPU-first embedding and inference
- **structlog** — structured logging
- **GitHub Actions** — orchestration and scheduled enrichment runs
- **Vast.ai** — deployment target

---

## Installation

```bash
# Install UV if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install
uv sync

# Install with GPU extras
uv sync --extra gpu
```

---

## Quick Start

```bash
# Show help
vortex --help

# Ingest a JSONL memory file
vortex ingest manifests/sample_synthetic_memory.jsonl

# Run the synthetic enrichment agent
vortex enrich --category hooplehopper_totality

# Validate canon firewall on a memory file
vortex validate manifests/sample_synthetic_memory.jsonl

# Query the vector store
vortex query "Hooplehopper displacement event timeline"

# Check GPU status
vortex gpu-status
```

---

## Repository Structure

```
VUORSE-VORTEX/
├── src/vuorse_vortex/          # Core package
│   ├── cli.py                  # Typer CLI entrypoint
│   ├── config.py               # Settings and config management
│   ├── logging_utils.py        # structlog configuration
│   ├── models/                 # Pydantic schemas
│   │   ├── memory_unit.py      # Core MemoryUnit model
│   │   ├── hooplehopper.py     # Hooplehopper identity models
│   │   ├── ritual.py           # Ritual logic models
│   │   └── persona.py          # Persona capsule models
│   ├── agents/                 # Async agent scaffolds
│   │   ├── synthetic_enrichment.py
│   │   └── canon_firewall.py
│   ├── embedding/              # Embedding pipeline
│   │   └── pipeline.py
│   ├── gpu/                    # GPU enforcement utilities
│   │   └── enforcement.py
│   └── vectordb/               # Vector DB abstraction
│       ├── base.py
│       ├── chromadb_backend.py
│       └── qdrant_backend.py
├── manifests/                  # Sample data
│   ├── sample_manifest.json
│   └── sample_synthetic_memory.jsonl
├── tests/                      # pytest test suite
├── .github/workflows/          # GitHub Actions
├── Dockerfile
├── Makefile
├── pyproject.toml
└── .env.example
```

---

## Architecture

```
[JSONL Input] → [Canon Firewall Validator] → [Embedding Pipeline (GPU)] → [Vector DB]
                          ↓                            ↓
               [Synthetic Enrichment Agent]    [Structured Logging]
                          ↓
               [Memory Unit Storage (JSONL)]
```

### Memory Unit Schema

Every generated memory unit contains:
- `id` — unique identifier
- `category` — `canon | apocrypha | roadmap_manifest | hooplehopper_totality | ritual_logic | persona`
- `content` — the memory text
- `metadata` — author, timestamp, source, universe layer
- `retrieval_hints` — semantic tags, keywords, anchor phrases
- `behavioral_permissions` — what agents may do with this memory
- `visibility_rules` — `public | restricted | sealed | void`
- `canon_status` — `verified | contested | apocryphal | synthetic | erased`
- `embedding` — optional pre-computed vector

---

## Canon Firewall

The canon firewall enforces strict separation between memory categories. Any memory unit
tagged `roadmap_manifest` is **never** exposed via public query interfaces. Attempts to
query sealed memories are logged and rejected.

---

## Synthetic Enrichment

The synthetic enrichment agent generates memory pressure — plausible but non-canon
behavioral subtext that enriches retrieval without polluting verified continuity.
Synthetic memories are always tagged with `canon_status: synthetic` and
`visibility_rules: restricted`.

---

## GPU Enforcement

All embedding and inference tasks require CUDA. On non-GPU environments, the system
will log a warning and fall back to CPU with a performance penalty notice. Use
`vortex gpu-status` to check CUDA availability.

---

## Deployment (Vast.ai)

See `Dockerfile` for container configuration. The image is built GPU-first with
CUDA 12.x base. Deploy to Vast.ai instances with at least one NVIDIA GPU.

---

## License

MIT — with the understanding that this is *mythic infrastructure*, not corporate tooling.

---

*Built against erasure. For the Slayverse. For the Archive.*
