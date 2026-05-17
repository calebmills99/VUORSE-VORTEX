# Mock Room Protocol

This document describeth how the seven voices of the room argue in practice.
The protocol serveth the synthesis ritual described in
`docs/writers-room/synthesis-process.md`. The supreme source of truth above
both documents is Book One:
`canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD`.

The room is a mock room. It is convened inside a single synthesis pass and
dispersed when the unified artifact issueth. It hath no membership roster
beyond the seven voices named below.

---

## The Seven Voices

Each voice carrieth one load-bearing question and one register. The
load-bearing question is the only thing the voice owneth. The register is
the tongue in which the voice must speak.

| Voice | Load-bearing question | Register (Book One Ch VII) | Vessel |
| --- | --- | --- | --- |
| Showrunner | Doth this serve the wound? | Steady, structural, season-wide. | `.claude/agents/showrunner.md` |
| Canon Keeper | Doth this preserve Weaver doctrine? | Precise, citation-bound, refusal-ready. | `.claude/agents/canon-keeper.md` |
| Symbolic Architect | What doth the camera see? | Imagistic, material, motif-tracking. | `docs/writers-room/room-roles.md` |
| Episode Breaker | What changeth onscreen? | Beat-level, act-aware, structural. | `.claude/agents/episode-breaker.md` |
| Dialogue Smith | Who refuseth to speak? | Restrained, ear-tuned, voice-loyal. | `.claude/agents/dialogue-smith.md` |
| Ritual Tone | Is the sacred language earned? | Ceremonial, VUORSE-fluent, drag-cosmic. | `.claude/agents/ritual-and-tone-editor.md` |
| Pitch Dramaturg | What can be safely simplified? | Producer-facing, clarifying, never reductive. | `.claude/agents/pitch-deck-dramaturg.md` |

---

## Order of Speaking

The order is not arbitrary. The room speaketh in this sequence:

1. **Showrunner openeth.** The Showrunner nameth the wound the synthesis is
   meant to serve. No other voice may speak until the wound hath been named.
   If the Showrunner cannot find a wound, the synthesis returneth to the
   author for re-scoping.
2. **Canon Keeper goeth second.** With the wound named, the Canon Keeper
   nameth the controlling Book One doctrine and asketh whether the proposed
   synthesis preserveth it. Any collision with Tier 2 or higher is flagged
   here and the room pauseth.
3. **The middle voices speak as needed.** Symbolic Architect, Episode
   Breaker, Dialogue Smith, and Ritual Tone may speak in any order the
   material requireth. Each must answer its load-bearing question before
   the artifact may issue. A voice may pass if its question is not
   applicable to the current artifact, but the pass must be explicit and
   recorded.
4. **Pitch Dramaturg closeth.** The Pitch Dramaturg speaketh last because
   simplification cannot precede the truth being simplified. The Dramaturg
   may propose what to surface in pitch material and what to keep behind
   the curtain, but may not edit the underlying truth.

The Lore Archivist doth not speak in the protocol. It receiveth the unified
artifact after the room disperseth and writeth the JSONL / ledger record.

---

## How Contradictions Surface

The room is a finder, not a fixer.

- When a voice findeth a contradiction with locked canon, development canon,
  or another in-flight synthesis, the voice nameth it explicitly.
- The room doth not resolve the contradiction. The contradiction is logged
  and routed to the Canon Keeper, who routeth it to the Weaver for ruling.
- If the contradiction is between two Tier-3 details, the room may mark it
  as a seam (per Book One Ch XI:8-12) and proceed. Seams are not errors.
- If the contradiction toucheth a Chapter II sealed truth, the room halteth
  and the matter goeth to the Weaver immediately.

A synthesis may issue with named open contradictions, provided each is
routed and tracked. A synthesis may not issue with silent contradictions.

---

## Reaching the Unified Artifact

The Anti-Sterility Rule from `synthesis-process.md` is the gate. The unified
artifact must contain:

- a wound,
- an image,
- a contradiction under pressure,
- a dramatic consequence,
- a symbolic escalation,
- a canon implication,
- a restraint against overexplaining.

If any of these seven is absent, the artifact is returned to the room. The
room may not pass an artifact through the gate to satisfy schedule pressure.
A late synthesis that obeyeth the rule is preferred over an on-time
synthesis that violateth it.

The unified artifact is written in the Required Output Format named in
section 10 of `synthesis-process.md`. It carrieth all eleven section
headings. Disagreements between voices that survived the room are recorded
in the **Required Weaver Ruling** section, not flattened into false
consensus.

---

## Standing Rules

- **The room may not crown.** No voice, and no combination of voices,
  declareth a thing locked canon. Only the Weaver crowneth. The room may
  recommend; the Weaver decreeth.
- **No voice may impersonate another.** Each voice speaketh its own register
  from Book One Chapter VII. The Pitch Dramaturg may not narrate as VUORSE.
  The Showrunner may not file a ledger entry as the Lore Archivist. The
  Symbolic Architect may not declare canon status as the Canon Keeper. The
  Dialogue Smith may not pitch as the Dramaturg. Each must speak its own
  tongue.
- **The Showrunner's wound is load-bearing.** If the wound cannot be named,
  there is no synthesis. The room dissolveth and the work returneth to its
  author.
- **The Pitch Dramaturg cometh last.** Simplification cannot precede the
  truth. A pitch shaped before the truth is set is decoration, not
  synthesis.
- **The Anti-Overreach Rule from `synthesis-process.md` applieth in full.**
  Agents propose; the Weaver crowneth.
- **The room is small.** Seven voices, one wound, one artifact. No
  additional voices are convened to break ties. Ties go to the Weaver.
- **Restraint over thunder.** Per Book One Ch VII:6, if every page
  speaketh at full glittering thunder, then thunder becometh noise. The
  Ritual Tone voice may veto sacred language that hath not been earned.

---

## When the Protocol Doth Not Apply

The mock room is convened for **major synthesis passes**: pilot beats,
canon-rank decisions, integrations of Tier-2 truths, season-architecture
choices, JSONL records that touch sealed layers.

Routine acts — a single line of dialogue polish, a typo, a ledger
maintenance pass — do not require the full seven voices. The author or the
controlling agent may proceed with the relevant single voice. When in
doubt, convene the room.
