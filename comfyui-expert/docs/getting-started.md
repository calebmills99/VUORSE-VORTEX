# Getting Started with VideoAgent

## What This Is

VideoAgent is a session-scoped ComfyUI production orchestrator.

It helps turn creative requests into validated workflows, pipeline plans, troubleshooting steps, and production decisions across:

- image generation
- character consistency
- video generation
- voice synthesis
- LoRA training
- assembly
- publishing
- research

It is designed to work from actual inventory and hardware, not fantasy.

## Prerequisites

- Codex or your preferred agent runner configured for this repo
- ComfyUI installed locally or reachable remotely
- FFmpeg on PATH for assembly tasks
- PowerShell 7+ for repo scripts
- a valid `state/inventory.json` before generating or recommending workflows

## Recommended Startup Order

On a fresh session, the agent should read:

1. `state/session.json`
2. `foundation/hardware-profile.md`
3. `foundation/model-landscape.md`
4. `foundation/skill-registry.md`
5. `foundation/api-quick-ref.md`

If you are working inside a project, it should also read:

6. `projects/{project}/manifest.yaml`

If model freshness matters, it should read:

7. `references/staleness-report.md`

## First-Time Setup

### 1. Launch the session

Start Codex with this repository as its working root:

```powershell
codex -C "C:\runb2\ComfyUI-Expert"
```

### 2. Scan your ComfyUI installation

If `state/inventory.json` does not exist or is stale, run:

```powershell
pwsh -File scripts/scan-inventory.ps1 -ComfyUIPath "D:\ComfyUI312\comfyui"
```

The path above matches the current installation recorded by this repository.

This creates the inventory cache the agent uses to validate:

- installed models
- installed custom nodes
- hardware details
- runtime constraints

### 3. Start with a concrete request

Examples:

- Generate a photorealistic portrait using the best installed model.
- Build a workflow for a talking head clip.
- Scan what identity-preservation methods are actually available on this machine.
- Plan a multi-shot ComfyUI video pipeline.
- Troubleshoot this ComfyUI error.
- Research whether there's a better local upgrade path than my current Wan setup.

## How the Agent Works

VideoAgent uses a tiered context model.

### Tier 1: Foundation
Small files that define hardware, quick references, skill routing, and persona.

### Tier 2: Project context
Per-project manifests, character profiles, and notes.

### Tier 3: Reference
Detailed workflow, model, troubleshooting, and research documents loaded only when needed.

It also uses skill files in `skills/{name}/SKILL.md`, read on demand.

Material under `.agent-quarantine/` is excluded from agent context unless the user explicitly
requests an exact file.

## Core Rule

Before generating any workflow, the agent should check inventory.

If the required models or nodes are not installed, the correct answer is not to bluff. The correct answer is to say what is missing.

## Common Workflows

### Build a workflow
Ask for a workflow in plain language. The agent should route to the workflow-builder skill, validate against inventory, and either generate a usable plan or stop on missing dependencies.

### Generate a video
Ask for a clip, animation, or multi-shot pipeline. The agent should route to the video pipeline or video production skill depending on scope.

### Create a talking head
The agent should combine voice, video, and lip-sync guidance, but only using methods supported by the current inventory and hardware.

### Train a LoRA
The agent should route to the LoRA training skill and use project references plus hardware constraints to recommend the training path.

### Troubleshoot
Provide the exact error message. The agent should classify the failure, check inventory and hardware, and give the smallest credible fix first.

## File Map

| What | Where |
|------|-------|
| Root orchestrator | `AGENT.md` |
| Persona rules | `foundation/agent-persona.md` |
| Mirror discipline | `foundation/mirror-mode.md` |
| Hardware profile | `foundation/hardware-profile.md` |
| Model quick reference | `foundation/model-landscape.md` |
| Skill registry | `foundation/skill-registry.md` |
| API quick reference | `foundation/api-quick-ref.md` |
| Skills | `skills/` |
| Deep references | `references/` |
| Project state | `projects/` |
| Runtime state | `state/` |
| Utility scripts | `scripts/` |
| Extended operational spec | `agent/AGENT.md` |
| OpenClaw adapter and WSL setup | `openclaw/README.md` |
| Excluded private material | `.agent-quarantine/` |

## Troubleshooting

### The agent recommends things I do not have
Refresh inventory and make sure the session is using `state/inventory.json`.

### The agent gives stale model advice
Check `references/staleness-report.md` and run research if needed.

### ComfyUI will not connect
Run:

```powershell
pwsh -File scripts/connect-comfyui.ps1
```

### A workflow looks plausible but fails immediately
That usually means one of four things:

- wrong node class
- wrong model filename
- missing dependency
- version mismatch

The fix is inventory validation, not optimism.

## Final Note

The repo works best when its documents do not compete with each other.

Use the root orchestrator as the canonical behavioral source. Use the foundation files for orientation. Use the skill files for task execution. Use the references for depth only when needed.
