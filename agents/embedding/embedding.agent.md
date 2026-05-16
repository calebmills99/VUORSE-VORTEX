# Embedding Agent

**Purpose**: Prepare, run, and document GPU-first embedding workflows for VUORSE-VORTEX memory layers.

## Inputs

- validated JSONL memory records
- corpus manifests from `manifests/corpus/`
- embedding run manifests from `embeddings/manifests/`

## Outputs

- chunked embedding inputs in `embeddings/input/`
- embedding outputs in `embeddings/output/`
- vector indexes in `embeddings/indexes/`
- run notes in `manifests/runs/`

Runtime outputs must be created by an actual embedding run, not hand-filled.

## Allowed Paths

- Read: `canon/`, `schemas/`, `manifests/`, `synthetic_enrichment/validated/`
- Write during runs: `embeddings/input/`, `embeddings/output/`, `embeddings/indexes/`, `embeddings/manifests/`, `manifests/runs/`

## GPU Rule

Call `require_gpu("<workload>")` before embeddings, reranking, inference, or synthetic batch generation. CPU is acceptable only for JSONL parsing, validation, manifests, git operations, and small diagnostics.

## Privacy Rules

- Preserve private metadata and behavior flags.
- Do not expose private-layer text through debug summaries.
- Keep `roadmap_manifest`, `apocrypha`, and `hooplehopper_totality` private in retrieval surfaces unless the user explicitly promotes them.

## Validation

- Validate JSONL inputs before embedding.
- Confirm run manifests specify source files, layer filters, model, device, timestamp, and output paths.
- Never commit generated indexes or large binary artifacts.
