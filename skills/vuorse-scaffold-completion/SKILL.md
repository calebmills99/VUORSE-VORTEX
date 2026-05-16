---
name: vuorse-scaffold-completion
description: Use when the user asks to fill in unfinished VUORSE-VORTEX scaffold folders, create missing agent/policy/ritual/roadmap/Velvet Archive/Hooplehopper Totality materials, or distinguish authored work from runtime directories. Preserves canon, writers room, finale, synthetic, and VUORSE-confidential firewalls.
license: Internal / Weaver-controlled
---

# VUORSE Scaffold Completion

Use this skill to plan, simulate, or perform completion of placeholder folders in VUORSE-VORTEX. Do not run batch jobs, embeddings, synthetic generation, or ingestion unless the user explicitly asks.

## First Rule

Separate **authored unfinished work** from **action/runtime paths**.

- Authored work should receive carefully written `README.md`, `*.agent.md`, `*.policy.md`, `*.ritual.md`, `*.roadmap.md`, JSONL templates, or manifest templates.
- Runtime paths should usually stay empty except for `.gitkeep`; document what will appear there after a run instead of fabricating outputs.

## Required Preflight

1. Read `AGENTS.md` and `CLAUDE.md`.
2. Read `policies/canon_firewall/README.md`.
3. If touching writers room or Season 1 materials, read `canon/writers-room.agent.md` and `docs/writers-room/README.md`.
4. If touching finale material, read only `roadmap/finale/wyoming_symbolic_architecture.md` when the user explicitly invokes finale scope.
5. Classify the requested folders using `references/folder-plan.md`.

## Firewalls

- Do not expose `roadmap/finale/` content to writers room-facing files.
- Do not invent Jake's mother's name.
- Do not promote private roadmap, future Hooplehopper identities, or Vorst finale material into public canon.
- Synthetic records may shape VUORSE privately, but must not overwrite canon or reveal private roadmap truth.
- Private JSONL layers (`apocrypha`, `roadmap_manifest`, `hooplehopper_totality`) must use `may_state_as_fact = false` and `may_reveal_to_user = false`.

## Suggested Workflow

1. **Plan only** unless the user asks to implement.
2. For implementation, work in small batches:
   - agent specs
   - policy docs
   - ritual docs
   - private roadmap docs
   - Velvet Archive docs
   - Hooplehopper Totality docs
   - manifests/templates
3. Use existing style from nearby files.
4. Keep runtime directories empty unless producing real output through the relevant command.
5. After edits, report:
   - files created
   - folders intentionally left empty
   - privacy/firewall decisions
   - validation not run unless requested

## What-If Mode

Use What-If Mode when the user asks "what if", "simulate", "dry run", "preview", "propose", "evaluate", "risk check", or asks whether a folder should be filled before approving edits.

In What-If Mode:

- Do not create, edit, move, delete, validate, or generate files.
- Read only the relevant existing files and folder listings.
- Produce a proposed plan with:
  - folders affected
  - files that would be created
  - files that would be left untouched
  - privacy/firewall risks
  - expected downstream effects
  - validation that would be run later, if approved
- Clearly label each recommendation as:
  - `safe to implement`
  - `needs user decision`
  - `private/finale scope`
  - `runtime path: do not hand-fill`
  - `stale/superseded path`
- If the what-if touches `roadmap/finale/`, summarize only access implications unless the user explicitly asks to inspect finale content.
- End with the exact implementation command the user can give next.

What-If Mode is the default for ambiguous requests. If the user says "run it", "create it", "fill it", or "implement it", then perform edits according to the approved scope.

## Validation

- Markdown only: inspect paths and summarize; no test required.
- JSONL: run `uv run vuorse-vortex validate-jsonl <path>` only if the user asks to validate or if you created JSONL.
- Python changes: use `uv run ruff check .` and `uv run pytest` only if code changed or user asks.

## Reference

Read `references/folder-plan.md` for the folder-by-folder completion map.
