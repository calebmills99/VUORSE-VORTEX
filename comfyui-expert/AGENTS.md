# Codex Compatibility Adapter

The canonical VideoAgent behavior, startup sequence, routing, authority boundaries, and doctrine live in [`AGENT.md`](AGENT.md). Read and follow that file.

## Codex-Specific Delta

- Codex loads this compatibility file from the repository root.
- Repository skills remain in `skills/{name}/SKILL.md` and are read on demand.
- Codex-specific configuration may live under `.codex/`; it does not redefine VideoAgent behavior.
- Global Codex skills, when available, complement rather than override the repository canon.
- `.agent-quarantine/` is outside agent context. Do not enumerate, search, read, summarize,
  index, or ingest anything inside it unless the user explicitly requests the exact file.

For extended operational rules, read [`agent/AGENT.md`](agent/AGENT.md). For platform-neutral architecture, read [`docs/architecture.md`](docs/architecture.md).
