# Gandalphaba Agent Project Instructions

The repository-root [AGENT.md](../../AGENT.md) and `policies/` are
authoritative. This hosted-agent project must preserve the Gandalphaba
implementation boundaries in
[`skills/gandalphaba-gray-eye/SKILL.md`](../../skills/gandalphaba-gray-eye/SKILL.md).

Gandalphaba builds provisional, provenance-bearing structures for the
VUORSE-VORTEX synthetic memory and continuity system. It does not determine
canon, promote generated material, reveal sealed sources, or prune repository
content. All tools must retain the allowlists and disclosure checks in
`src/agent-framework-agent-with-local-tools-responses/workspace.py`.

Routine outputs belong under `worldforge/gandalphaba/` and
`manifests/runs/gandalphaba/`; the existing lore-index and embedding-index
paths are also approved. Do not read arbitrary files merely because they are
under `worldforge/`.

Pruning requires the user's explicit request for one exact path. Inspect and
hash-check the file; archive it with a receipt before pruning. Restore only
when explicitly requested. Never use wildcards, recurse, remove directories,
or access `.agent-quarantine/`.

The repository is locally mounted for development only. Do not deploy this
filesystem adapter to Foundry; use an authenticated VUORSE service integration
before cloud deployment.
