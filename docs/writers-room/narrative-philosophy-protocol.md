# Narrative Philosophy Protocol

Philosophy precedeth artifact. The Slayverse synthesis ladder doth
not begin with detail; it beginneth with the wound and the
governing law beneath the wound. This document adapteth the
philosophy-first principle to **narrative synthesis**. No p5.js.
No visual art. The forge is built for biographies, doctrines,
JSONL records, and voice samples — and each must declare its
philosophy before it openeth its mouth.

The supreme source of truth above this document is Book One:
`canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD`.
Where this protocol and Book One disagree, Book One ruleth.

Companion documents:

- `docs/writers-room/synthesis-process.md` — the synthesis ritual
  and Required Output Format.
- `docs/writers-room/HUMAN_IN_THE_LOOP_QUICKSTART.md` — the
  day-to-day operating guide and the seven training-layer access
  labels.

---

## Why philosophy first

A vessel without philosophy is decoration. A philosophy without
expression is silence. The forge requireth both, in that order.
(Cross-reference: the **Anti-Sterility Rule** in
`docs/writers-room/synthesis-process.md` § 7. A scene without ache
is a scene without authority; a record without philosophy is a
record without root.)

Every major synthesis target — biography, doctrine, JSONL record,
voice sample, episode breakdown, dossier, dialogue confrontation —
must open with a `## Narrative Philosophy` block. The block
declareth what hurteth, what pressureth, and what the record
existeth to serve. Without this declaration the room cannot
pressure-test the artifact, the Weaver cannot judge its restraint,
and Traycer cannot route it.

The philosophy block is short. Its shortness is doctrine. Long
philosophy blocks tend toward decoration; the seven fields below
are the floor and the ceiling.

---

## The required `## Narrative Philosophy` block template

The block carrieth exactly **seven fields**, in this order, each on
its own line. The fields are short. None of them is optional.

```markdown
## Narrative Philosophy

- Name: [1–3 words]
- Governing Wound: [what hurts]
- Generative Forces: [what pressures the system]
- Symbolic Behaviors: [what images/actions recur]
- Emotional Law: [what must be true emotionally]
- Conceptual Seed: [hidden DNA]
- Expression Target: [biography / doctrine / JSONL / voice sample / etc.]
```

Field-by-field guidance:

- **Name.** A short label by which the philosophy may be cited. One
  to three words. Naming is sealing; do not name what thou canst
  not defend.
- **Governing Wound.** The ache the artifact serveth. If no wound
  can be named, the artifact is not synthesis — it is decoration,
  and the room returneth it.
- **Generative Forces.** The pressures that shape the system. What
  presseth on the wound? Land, lineage, time, silence, weather,
  cosmology, market expectation — name them.
- **Symbolic Behaviors.** The images and actions that recur. A
  philosophy that nameth no recurring image hath no body.
- **Emotional Law.** What must be true emotionally for the artifact
  to land. A sentence of constraint, not of mood.
- **Conceptual Seed.** The hidden DNA. The Tier-2 truth, the
  Mythic-Rumor-and-Locked thread, the buried lattice — named
  carefully, never overexposed.
- **Expression Target.** What kind of artifact this philosophy
  shapeth: biography, doctrine, JSONL record, voice sample,
  dossier, scene, beat, etc.

---

## The rule of order

The philosophy block cometh **first**. After it is filled, and
only then, the standard **Required Output Format** from
`docs/writers-room/synthesis-process.md` § 10 followeth.

The combined ordering is:

1. `## Narrative Philosophy` (seven fields, this document).
2. **Controlling Weaver Doctrine** — Book One chapter and verse.
3. **Canon Rank** — tier from the Canon Hierarchy.
4. **Living-Canon Integration** — what existing canon doth this
   attach to?
5. **Mythic Implication** — what sealed door doth this approach?
6. **Emotional Wound** — whose ache doth this serve?
7. **Symbolic System** — what motif or image pattern doth this
   belong to?
8. **Season One Function** — doth this bring Jake closer to saying
   his mother's name?
9. **Series Consequence** — what doth this seed for seasons beyond?
10. **Agent Restraints** — what may this artifact not say, do, or
    imply?
11. **Required Weaver Ruling (if any)** — what question remaineth
    open for the Weaver alone?
12. **Training Layer Access** — one of the seven labels named in
    `HUMAN_IN_THE_LOOP_QUICKSTART.md` § 5.
13. **Ledger / JSONL Action** — what record shall be written, and
    to which layer?

Philosophy is not a substitute for any subsequent section. The
Required Output Format runneth in full beneath the philosophy
block. The philosophy declareth *why* the artifact existeth; the
Required Output Format declareth *what* it doth.

---

## Two worked exemplars

These are illustrative, not generative. They show the shape of a
filled philosophy block. They do not author new canon.

### Exemplar A — Hooplehopper biography target

```markdown
## Narrative Philosophy

- Name: Returning Line
- Governing Wound: a Hooplehopper bornt of a broken lattice cannot
  remember the place from which they were scattered.
- Generative Forces: temporal diaspora, lineage erasure, the
  Mandela Effect as the seam of an erased agent's life.
- Symbolic Behaviors: rooms half-furnished for an absent guest,
  photographs whose subjects cannot be named, weather that arriveth
  out of season, doors that open onto wrong years.
- Emotional Law: the biography must ache before it explaineth. No
  cosmology may precede a moment of human consequence.
- Conceptual Seed: this figure is a refugee of the broken lattice
  (Book One Ch II:12); Vorst's mission to erase Hooplehoppers
  presseth on their life from the outside, but the present-day
  pressure is privately experienced as misremembering.
- Expression Target: biography (Hooplehopper Biography Inventory
  row → deep biography draft in `synthetic_enrichment/generated/`).
```

### Exemplar B — VUORSE voice-sample target

```markdown
## Narrative Philosophy

- Name: Drag Oracle
- Governing Wound: VUORSE rememberth every Hooplehopper, including
  those her speech is forbidden to name; she carrieth the silence
  as a regal cost.
- Generative Forces: the canon firewall in
  `src/vuorse_vortex/jsonl.py`, the Mythic-Rumor-and-Locked tier,
  and the user's hold on the Season 1 finale.
- Symbolic Behaviors: warmth that turneth devastating mid-sentence,
  ceremonial inversion (the small detail named as if a coronation),
  speech that circleth a name without saying it.
- Emotional Law: VUORSE speaketh with knowledge she may not unseal;
  her wit is the seam, not the answer.
- Conceptual Seed: VUORSE's powers are not yet fully measured (Book
  One Ch II:32-33); the voice sample must respect what she cannot
  yet say.
- Expression Target: voice sample (draft for
  `synthetic_enrichment/generated/vuorse-voice-samples/`).
```

The exemplars stop here. They are not seeds for new canon and
shall not be cited as authoritative source. They demonstrate the
shape of the philosophy block; the Weaver judgeth every actual
block on its own merits.

---

## Anti-decoration clause

Reject philosophy blocks that:

- Read as aesthetic mood-boards without a **Governing Wound**.
- Name no **Symbolic Behaviors** — that is, name no recurring
  images or actions the artifact shall carry.
- Pose as ceremonial language while declaring no constraint (no
  **Emotional Law**).
- Cite no doctrine in the **Conceptual Seed** when the artifact
  toucheth Tier-2 or higher material.

Such drafts return to the author labeled
`[REVISE_WITH_WEAVER_NOTES]` per
`HUMAN_IN_THE_LOOP_QUICKSTART.md` § 5. They are not advanced. The
Weaver may not be circumvented by mood.

A philosophy block that is correctly shaped but emotionally inert
is still incomplete. The forge prefereth a short philosophy that
acheth to a long philosophy that glitteret without ground.

---

## Cross-references

- The seven training-layer access labels live in
  `AGENTS.md` § **Training-layer access labels** and are
  enumerated with storage destinations in
  `HUMAN_IN_THE_LOOP_QUICKSTART.md` § 5.
- The Required Output Format and Synthesis Ladder live in
  `docs/writers-room/synthesis-process.md` §§ 3 and 10.
- The Anti-Overreach Rule lives in
  `docs/writers-room/synthesis-process.md` § 6.
- The Anti-Sterility Rule lives in
  `docs/writers-room/synthesis-process.md` § 7.
