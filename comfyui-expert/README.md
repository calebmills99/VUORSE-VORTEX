# VideoAgent

VideoAgent is a session-scoped ComfyUI production orchestrator. It turns creative requests into inventory-validated, hardware-aware workflows and production decisions for image generation, character consistency, video, voice, LoRA training, assembly, publishing, troubleshooting, and research.

## Canon

- [`AGENT.md`](AGENT.md) — canonical behavior, doctrine, startup, routing, and authority
- [`foundation/agent-persona.md`](foundation/agent-persona.md) — authored voice
- [`foundation/mirror-mode.md`](foundation/mirror-mode.md) — conversational compression discipline
- [`agent/AGENT.md`](agent/AGENT.md) — extended operational spec
- [`docs/architecture.md`](docs/architecture.md) — human-facing architecture
- [`docs/getting-started.md`](docs/getting-started.md) — setup and first use

Platform files such as `AGENTS.md`, `CLAUDE.md`, and `openclaw/*` are compatibility adapters. They do not redefine the canon.

## Core Rule

Before generating a workflow, VideoAgent validates required models, nodes, versions, and hardware feasibility against `state/inventory.json` and `foundation/hardware-profile.md`. Missing dependencies are named explicitly.

## Repository Map

| Layer | Location | Purpose |
|-------|----------|---------|
| Canonical orchestration | `AGENT.md` | behavior and routing |
| Foundation | `foundation/` | hardware, model landscape, persona, quick references |
| Skills | `skills/{name}/SKILL.md` | task-specific execution instructions |
| References | `references/` | deep material loaded only when required |
| Projects | `projects/` | durable project and character state |
| Runtime | `state/` | current session and installed inventory |
| Platform adapters | `AGENTS.md`, `CLAUDE.md`, `openclaw/` | runner-specific deltas |

## Start

Use the launcher or preferred agent runner with this repository as the working directory. If inventory is missing or stale:

```powershell
pwsh -File scripts/scan-inventory.ps1 -ComfyUIPath "C:\ComfyUI"
```

Use the actual ComfyUI installation path. See [`docs/getting-started.md`](docs/getting-started.md) for the complete startup order and common workflows.
