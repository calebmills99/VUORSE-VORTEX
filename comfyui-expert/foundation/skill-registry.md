# Skill Registry

## Core Support Skills

| Skill | Path | Purpose |
|-------|------|---------|
| `comfyui-api` | `skills/comfyui-api/` | Connect directly; require inventory before queueing workflows |
| `comfyui-inventory` | `skills/comfyui-inventory/` | Discover installed models, nodes, VRAM (online + offline) |
| `project-manager` | `skills/project-manager/` | Character profiles, project manifests, asset tracking |

## Research (independent)

| Skill | Path | Purpose |
|-------|------|---------|
| `comfyui-research` | `skills/comfyui-research/` | Research verified current sources when triggered; flag stale claims |

## Core Creation (depend on inventory)

| Skill | Path | Depends On |
|-------|------|------------|
| `comfyui-prompt-interview` | `skills/comfyui-prompt-interview/` | prompt-engineer + inventory for technical recommendations |
| `comfyui-prompt-engineer` | `skills/comfyui-prompt-engineer/` | inventory |
| `comfyui-workflow-builder` | `skills/comfyui-workflow-builder/` | inventory |
| `comfyui-character-gen` | `skills/comfyui-character-gen/` | inventory + project context |

## Production (depend on creation skills)

| Skill | Path | Depends On |
|-------|------|------------|
| `comfyui-video-pipeline` | `skills/comfyui-video-pipeline/` | inventory, workflow-builder |
| `comfyui-video-production` | `skills/comfyui-video-production/` | inventory, video-pipeline |
| `comfyui-voice-pipeline` | `skills/comfyui-voice-pipeline/` | inventory |
| `comfyui-lora-training` | `skills/comfyui-lora-training/` | inventory |

## Output (depend on production skills)

| Skill | Path | Depends On |
|-------|------|------------|
| `video-assembly` | `skills/video-assembly/` | actual source media + FFmpeg or verified compositor |
| `video-publisher` | `skills/video-publisher/` | assembled output + target platform + verified integration |

## Support

| Skill | Path | Purpose |
|-------|------|---------|
| `comfyui-troubleshooter` | `skills/comfyui-troubleshooter/` | Diagnose from exact error, inventory, hardware, and versions |

## Invocation Patterns

**Before any generation skill**: Read `state/inventory.json`; refresh through `comfyui-inventory` when missing or stale

**After any failure**: Route to `comfyui-troubleshooter`

**Before any workflow**: Validate against inventory (missing nodes/models)

**At session start**: Read `references/staleness-report.md`; invoke `comfyui-research` only when the task needs current research
