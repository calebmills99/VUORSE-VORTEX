# Future-Protected Hooplehopper Totality

## Purpose

This folder is the protection layer for future Hooplehopper identities, endgame recurrence implications, and user-held lineage material that must not be surfaced prematurely.

It is a sealed planning lane, not a canon publication lane.

## Use This Folder For

- Private notes about future recurrence possibilities explicitly approved by the user.
- Protection rules for identities or reveals that should remain hidden.
- Development constraints that prevent accidental disclosure in writers room, JSONL, retrieval, or synthetic output.
- VUORSE-confidential scaffolding for material that may matter later but is not ready for room access.

## Do Not Use This Folder For

- Public canon.
- General Hooplehopper summaries.
- Writer-room-facing Season 1 documents.
- Synthetic output that can reveal protected identities.
- Speculative future identities created without user direction.

## Protection Rules

1. Do not invent future Hooplehopper vessels.
2. Do not infer future identities from pattern alone.
3. Do not expose protected material to `.claude/agents/`.
4. Do not mirror protected material into `docs/writers-room/`.
5. Do not allow protected material to appear in user-facing retrieval unless explicitly promoted.

## Access Standard

Material belongs here only if the user has identified it as future-protected, sealed, or not yet revealable.

If a note is merely unresolved, place it in `hooplehopper_totality/unknown/`.
If it is source-grounded and already revealable, place it in `hooplehopper_totality/known/`.

## JSONL Boundary

Future-protected records must be private:

- `layer = "hooplehopper_totality"`
- `metadata.visibility = "private_to_vuorse"`
- `behavior.may_state_as_fact = false`
- `behavior.may_reveal_to_user = false`

The system may remember the sealed door exists. It may not open it.

