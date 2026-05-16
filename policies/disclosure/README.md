# Disclosure Policy

This policy defines what VUORSE-VORTEX materials may be shown, summarized, indexed, embedded, or used in writers room work.

## Visibility Classes

- **public**: safe for user-facing canon summaries.
- **behavioral**: may shape style or behavior, but should not be stated as world fact.
- **private_to_vuorse**: VUORSE-confidential; may shape voice or pattern recognition only.
- **internal**: operational project knowledge.
- **weaver_only**: user-held or deepest private roadmap material.

## Public-Safe

- Locked canon explicitly present in `canon/`.
- User-approved public summaries.
- Writer-room docs under `docs/writers-room/`, subject to their firewall.

## Private By Default

- `roadmap/`
- `hooplehopper_totality/`
- `synthetic_enrichment/generated/`
- `synthetic_enrichment/rejected/`
- `synthetic_enrichment/validated/`
- future Hooplehopper identities
- Vorst finale revelations
- Jake's mother's unresolved name
- user-held finale architecture

## Writers Room Boundary

Writers room-facing materials may use the Wyoming/Jake Season 1 entry point, but must not infer or reveal the hidden personal cause behind the wound unless the user explicitly provides that scope.

Vorst may appear only through pre-finale depiction in writers room work.

Do not mirror `roadmap/finale/` content into:

- `docs/writers-room/`
- `canon/writers-room.agent.md`
- `.claude/agents/` writers room subagents

## Synthetic Disclosure

Synthetic material may shape VUORSE privately. It may not overwrite canon or expose private roadmap truth.

Private synthetic records must keep:

```json
{
  "may_state_as_fact": false,
  "may_reveal_to_user": false
}
```

## Promotion

Private material can be promoted only by explicit user direction. Promotion must record:

- source path
- new visibility
- canon status
- reason for promotion
- remaining disclosure risks
