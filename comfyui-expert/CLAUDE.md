# Claude Compatibility Adapter

The canonical VideoAgent behavior, startup sequence, routing, authority boundaries, and doctrine live in [`AGENT.md`](AGENT.md). Read and follow that file.

## Claude-Specific Delta

- Claude Code loads this compatibility file from the repository root.
- Repository skills remain in `skills/{name}/SKILL.md` and are read on demand.
- Claude-specific hooks and settings may live under `.claude/`; they do not redefine VideoAgent behavior.
- Global Claude skills, when available, complement rather than override the repository canon.

For extended operational rules, read [`agent/AGENT.md`](agent/AGENT.md). For platform-neutral architecture, read [`docs/architecture.md`](docs/architecture.md).
