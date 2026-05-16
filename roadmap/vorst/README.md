# Vorst Roadmap

## Purpose

This is a private containment lane for Vorst-related roadmap material.

It exists because Vorst information is structurally dangerous to Season 1 mystery if handled too early or too plainly.

## Use This Folder For

- Private Vorst continuity questions.
- Reveal-order constraints.
- Notes separating pre-finale depiction from sealed causal material.
- VUORSE-confidential analysis that should not be available to writers room agents.
- Guardrails for when and how Vorst material may be promoted.

## Do Not Use This Folder For

- Writers room-facing antagonist framing.
- Present-day Season 1 external antagonist construction.
- Public canon summaries.
- Automatic synthetic enrichment visible to users.
- Casual foreshadowing instructions.

## Core Boundary

Writers room-facing agents may know Vorst only through approved pre-finale depiction unless the user explicitly invokes finale or private roadmap scope.

Do not infer, pitch, outline, or foreshadow sealed causal function from this folder.

## Handling Rules

1. Keep Vorst material private by default.
2. Preserve moral complexity; do not flatten him into a cartoon villain.
3. Separate principle, intent, action, consequence, and reveal timing.
4. Do not mirror this folder into `.claude/agents/` or `docs/writers-room/`.
5. Treat any promotion as a deliberate user decision.

## JSONL Boundary

Records derived from this folder belong in a private layer such as `roadmap_manifest` and must preserve:

- `behavior.may_state_as_fact = false`
- `behavior.may_reveal_to_user = false`

Containment is the point.

