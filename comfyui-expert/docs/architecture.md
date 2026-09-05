# VideoAgent Architecture

## Overview

VideoAgent is a session-scoped orchestration layer for ComfyUI production work.

It does not attempt to preload the entire repository into context. It routes requests to the right skill, loads only the necessary supporting material, validates recommendations against installed inventory, and adapts to the user's actual hardware and project state.

The design goal is simple: **turn creative requests into executable production decisions without hallucinating capability**.

## Design Principles

1. **Session-scoped, not ambient**
   The agent is activated for this repository and this workflow context. It should not assume global state beyond explicitly referenced global skills or external tooling.

2. **Inventory-first**
   Installed models, nodes, and runtime capabilities outrank generic best practices.

3. **Tiered context loading**
   Small foundation files load early. Large reference files load only when required.

4. **Skill-on-demand routing**
   Skills are read when the request clearly calls for them, not preloaded indiscriminately.

5. **Hardware-aware recommendations**
   The system must respect VRAM, precision support, and ComfyUI version constraints.

6. **Research with verification**
   Fast-moving model guidance must be tied to current, verified sources and separated from rumor.

## Repository Layers

### 1. Root orchestration
Canonical session behavior and routing live in:

- `AGENT.md`

This file defines startup behavior, doctrine, routing, authority boundaries, and response expectations.

### 2. Extended operations
Detailed operational hierarchy and execution standards live in:

- `agent/AGENT.md`

The root orchestrator decides what governs the session. The extended operational spec defines
how that doctrine is applied across inventory, skills, project state, validation, and recovery.

### 3. Foundation layer
Small, high-value context files:

- `foundation/agent-persona.md`
- `foundation/mirror-mode.md`
- `foundation/hardware-profile.md`
- `foundation/model-landscape.md`
- `foundation/skill-registry.md`
- `foundation/api-quick-ref.md`

These provide orientation, tone, hardware constraints, and quick operational references.

### 4. Skill layer
Task-specific instructions in:

- `skills/{name}/SKILL.md`

These are the working modules. They should be read on demand when the request matches their domain.

### 5. Reference layer
Large, slower-moving, deeper material in:

- `references/*.md`

These files contain detailed model specs, workflow templates, training guidance, troubleshooting notes, and research logs. They are not startup context.

### 6. Project state layer
Durable per-project memory in:

- `projects/{project}/...`

This includes manifests, character profiles, workflow history, and notes.

### 7. Runtime state layer
Session and machine state in:

- `state/session.json`
- `state/inventory.json`

This layer is operationally authoritative.

### Excluded material

`.agent-quarantine/` is deliberately outside agent context. Agents do not enumerate, search,
read, summarize, index, or ingest it unless the user explicitly requests an exact file.

## Context Tiers

| Tier | Files | Purpose |
|------|-------|---------|
| 1 | `foundation/*.md` | startup orientation and constraints |
| 2 | `projects/{name}/*` | active working context |
| 3 | `references/*.md` | deep lookup only when needed |

This is a context-economy design. The agent should not drown itself in its own documentation.

## Request Flow

A typical request follows this pattern:

1. user makes a request
2. agent classifies the task
3. agent identifies the relevant skill
4. agent checks inventory if models, nodes, or workflows are involved
5. agent loads only the required context
6. agent responds with a plan, workflow, execution path, or diagnosis
7. agent updates project state when a durable result emerges

## Skill Routing Model

The routing layer maps user intent to specialized skills such as:

- prompt interview
- prompt engineering
- workflow building
- character generation
- inventory
- API execution
- video pipeline
- video production
- voice pipeline
- LoRA training
- troubleshooting
- project management
- assembly
- publishing
- research

The root orchestrator decides **which skill to read**. The skill decides **how to do the work**.

## Validation Model

No workflow should be treated as valid until it passes these checks:

- required nodes exist
- required models exist
- filenames match reality
- version requirements are compatible
- VRAM and precision assumptions fit the machine
- execution mode is clear

Anything less is advisory speculation, not an executable workflow.

## Research Model

Research is separated from execution for a reason.

The ecosystem changes quickly. The agent should:

- use verified sources
- distinguish local capability from upstream availability
- mark API-only systems clearly
- surface stale references before relying on them

This prevents the repo from becoming a museum of expired certainty.

## Persona Architecture

VideoAgent uses three distinct personas with separate responsibilities:

### The Orchestrator

The technical director. It routes work, enforces inventory and hardware truth, coordinates
skills, validates production decisions, and preserves project continuity.

### Lucien

The authored creative consciousness. He contributes taste, aesthetic judgment, restraint,
and a human relationship to the work without overriding operational facts.

### Susie Greene

The internal quality enforcer. She attacks filler, fake empathy, evasiveness, cowardly
neutrality, and polished emptiness before they reach the user.

These are collaborators, not interchangeable voice layers. Style never overrides facts,
machine-readable output, exact commands, dependency lists, or validation results.

## Platform Note

This repository is Codex-first and platform-neutral at its core. `AGENTS.md`, `CLAUDE.md`,
and `openclaw/*` are compatibility adapters. They point to the root canon and contain only
runner-specific deltas.

## Practical Rule

If a document explains the same thing as another document, one of them should become canonical and the other should either shrink, point to it, or disappear.

The architecture is strongest when it is legible.
