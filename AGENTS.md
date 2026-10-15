# Codex Compatibility Adapter

The canonical VUORSE-VORTEX behavior, authority order, startup sequence, and
doctrine live in [`AGENT.md`](AGENT.md). Read and follow that file.

Governance itself lives in [`policies/`](policies/) and outranks `AGENT.md`.

## Codex-specific delta

- Codex loads this compatibility file from the repository root.
- Repository skills live in [`skills/`](skills/) and are read on demand.
- Codex-specific configuration may live under `.codex/`; it does not redefine
  VUORSE-VORTEX behavior.
- Global Codex skills complement rather than override the repository canon.
- `comfyui-expert/` carries its own `AGENTS.md` and `AGENT.md`. Those are
  binding **inside that subsystem only** and do not govern this repository.
- `.agent-quarantine/` is outside agent context. Do not enumerate, search, read,
  summarize, index, or ingest anything inside it unless the user explicitly
  requests the exact file.

For doctrine, read [`docs/VUORSE_VORTEX.md`](docs/VUORSE_VORTEX.md).
For the disclosure classes and promotion protocol, read
[`policies/disclosure/README.md`](policies/disclosure/README.md).
