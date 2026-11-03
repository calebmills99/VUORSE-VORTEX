# VUORSE-VORTEX

VUORSE-VORTEX is the Slayverse continuity system: a canon-governed corpus, a disclosure firewall, and the tooling that turns sealed narrative sources into indexes, graphs, and downstream production.

```text
RAG retrieves.
Memory Cortex remembers.
VUORSE-VORTEX preserves continuity against erasure.
```

Doctrine: [`docs/VUORSE_VORTEX.md`](docs/VUORSE_VORTEX.md).
VUORSE-VORTEX is **not** Memory Cortex; see
[`docs/VUORSE_CORTEX_SATELLITE.md`](docs/VUORSE_CORTEX_SATELLITE.md).

## Authority order

1. [`policies/`](policies/) — canon firewall, disclosure, writer room, GPU runtime.
   **These govern.** Nothing below may relax them.
2. [`manifests/corpus/source_manifest.json`](manifests/corpus/source_manifest.json)
   — the corpus of record: what is a source, its layer, visibility, canon status.
3. [`canon/`](canon/) — the narrative sources themselves.
4. [`AGENT.md`](AGENT.md) — how an agent operates inside the above.
5. Subsystem doctrine (e.g. [`comfyui-expert/`](comfyui-expert/)) — binding
   *within* that subsystem only.

Platform files `CLAUDE.md` and `AGENTS.md` are compatibility adapters. They do
not redefine the canon.

## Repository map

| Layer | Location         | Purpose                                                    |
| ----- | ---------------- | ---------------------------------------------------------- |
| Gover | `policies/`      | firewall, disclosure classes, writer-room boundary, GPU    |
| nance |                  | floor                                                      |
| Corpu | `manifests/corp  | source manifest, entity index, relationship index          |
| s of  | us/`             |                                                            |
| recor |                  |                                                            |
| d     |                  |                                                            |
| Canon | `canon/`         | Books One/Two, characters, cosmology, artifacts, story     |
|       |                  | arcs, TV bible                                             |
| Seale | `roadmap/` ,     | private by default; promotion is explicit                  |
| d     | `hooplehopper_t  |                                                            |
| layer | otality/`        |                                                            |
| s     |                  |                                                            |
| Runti | ` vuorse_vortex/ | firewall, walled load, indexing, graph, synthesis,         |
|       |                  | vectors,                                                   |
| me    | `                | API/CLI                                                    |
| Agent | `agents/`        | canon extractor, indexer, firewall validator, seam clerk,  |
| s     |                  | writers room, enricher                                     |
| Retri | `embeddings/ind  | sqlite-fts5 chunk store carrying per-chunk visibility      |
| eval  | exes/`           |                                                            |
| Write | `docs/writers-r  | Season 1 spine, canon ledger, room protocol                |
| rs    | oom/`            |                                                            |
| room  |                  |                                                            |
| Forge | `worldforge/`    | reconnaissance and exploratory runs — **provisional, never |
|       |                  | canon**                                                    |
| Produ | `comfyui-expert  | ComfyUI/VideoAgent orchestration, called — not sovereign   |
| ction | /`               |                                                            |
| speci |                  |                                                            |
| alist |                  |                                                            |
| Tests | `tests/`         | including `test_manifest_integrity.py`                     |
|       |                  | (disclosure-boundary invariants)                           |

## Core rules

- **Sealed layers are `apocrypha`, `roadmap_manifest`, `hooplehopper_totality`**
  (`vuorse_vortex/settings.py`). Records in them carry
  `may_state_as_fact=false` and `may_reveal_to_user=false`.
- **Promotion is explicit and recorded.** Private material becomes canon only by
  the Weaver's direction, logging source path, new visibility, canon status,
  reason, and remaining disclosure risk (`policies/disclosure/README.md`).
- **A source `id` is a disclosure boundary.** Chunk ids in the embedding index
  derive from it; two sources sharing an id collapse into one retrieval key.
  `tests/test_manifest_integrity.py` enforces this.
- **`worldforge/` output is provisional.** Reports and generated media are not
  canon and must not be indexed as canon.
- **`.agent-quarantine/`** is outside agent context: do not enumerate, search,
  read, summarize, index, or ingest it unless the Weaver names the exact file.

## Getting started

```bash
uv sync --extra dev
uv run pytest -q
uv run python -m vuorse_vortex.cli --help
uv run vuorse-vortex validate-lore-index
```

`validate-lore-index` checks the WorldForge Seam Index against Draft 2020-12,
Book One governance, global identity and reference invariants, and the corpus
source manifest. It fails when a governed `canon/` source is missing from the
index or its repository-relative path drifts.
