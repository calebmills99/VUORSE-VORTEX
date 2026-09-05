# Claude Compatibility Adapter

The canonical VUORSE-VORTEX behavior, authority order, startup sequence, and
doctrine live in [`AGENT.md`](AGENT.md). Read and follow that file.

Governance itself lives in [`policies/`](policies/) and outranks `AGENT.md`.

## Claude-specific delta

- Claude Code loads this compatibility file from the repository root.
- Repository skills live in [`skills/`](skills/) and are read on demand.
- Claude-specific hooks and settings may live under `.claude/`; they do not
  redefine VUORSE-VORTEX behavior.
- Global Claude skills complement rather than override the repository canon.
- `comfyui-expert/` carries its own `CLAUDE.md` and `AGENT.md`. Those are
  binding **inside that subsystem only** and do not govern this repository.

For doctrine, read [`docs/VUORSE_VORTEX.md`](docs/VUORSE_VORTEX.md).
For the disclosure classes and promotion protocol, read
[`policies/disclosure/README.md`](policies/disclosure/README.md).
