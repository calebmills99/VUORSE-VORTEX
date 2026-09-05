# Declared assumptions — 2026-09-05-governance-repair

- `assumption` `manifests/corpus/source_manifest.json` is authoritative for layer, visibility and canon_status. Nothing else was treated as the corpus of record.
- `assumption` Caleb is the sole authority for canon promotion; no simulation output was promoted without an explicit ruling.
- `assumption` `Slayverse/` is a working archive that predates `canon/`, not a parallel corpus. Basis: its TV Bible and md_records are byte-identical to canon's, and its index is a 53KB predecessor of canon's 68KB.
- `assumption` Sealed-layer content may be cited by path but never quoted. Applied to `roadmap/`, `hooplehopper_totality/`, `.agent-quarantine/`.
- `assumption` The hand-patched ids `-jsonl` / `-md` were a workaround, not curation, and were surrendered to the generator.

## Unverified at seal time
- pytest was run by the Steward on Windows; the Gray Eye did not observe its output.
- Whether any retrieval prior to 2026-09-05 already crossed the duplicated chunk-id boundary. Unknowable from the index alone.
