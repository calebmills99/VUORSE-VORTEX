# Synthesis Process

The Weaver named this process. The room obeys it. The supreme source of truth is
`canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD` — **The Words of
the Weaver, Book One: Concerning the Crown, the Wound, and the Returning Line**.
When this document and Book One disagree, Book One wins.

This file houses the ten faces of the synthesis ritual.

---

## 1. Submission to the Weaver

Every synthesis act beginneth by identifying its controlling Book One doctrine.
No agent createth, reviseth, indexeth, or expandeth before naming the chapter
and verse that ruleth the act.

The submission line is required as the first line of any synthesis artifact:

> **Controlling Weaver Doctrine:** Book One, Chapter __, verses __.

If the controlling doctrine cannot be named, the work stoppeth and the matter
is escalated to the Weaver. There is no synthesis without submission.

This rule applieth to every agent — the writers-room subagents under
`.claude/agents/`, the pipeline agents under `agents/`, and any contributor
human or otherwise.

---

## 2. Canon Hierarchy

Rebuilt from Book One. Higher tiers always outrank lower tiers. When tiers
collide, the higher tier ruleth and the lower bendeth.

1. **Weaver Doctrine.** Book One itself. Supreme; not subject to revision
   except by the Weaver.
2. **Mythic Rumor That Is Also Locked Canon.** Book One Chapter II in its
   entirety. Veiled because too mighty to surface before the appointed hour.
   VUORSE alone may know these. Never speak them plain in pitches, scripts,
   public summaries, or writers-room outputs unless the Weaver explicitly
   unsealeth.
3. **Locked Canon.** Speakable plainly in scripts, decks, and pitches. None
   moveth it save by the hand of the Weaver.
4. **Development Canon.** Usable with caution. Not yet crowned before the
   court. Traceable to source or to explicit Weaver direction.
5. **Mythic Rumor.** In-world legend, contradiction, false memory, archive
   distortion, whispering truth. Must remain labeled as such.
6. **Exploratory Material.** Notes, sketches, hypotheses, room-floor proposals.
   Never to be treated as canon. Always labeled.
7. **Pitch-facing simplification.** The producer-facing surface. The narrow
   door through which the audience entereth.

> **Explicit rule:** pitch-facing simplicity must never override hidden
> synthesis truth. If a pitch requireth a fact that contradicteth Tier 2 or
> higher, the pitch yieldeth, not the truth.

---

## 3. Synthesis Ladder

Nine rungs. No item is fully synthesized until it hath climbed all nine. A
synthesis act may pause on any rung, but the artifact is not complete while
rungs remain unclimbed.

1. **Detail.** The smallest concrete particular: an object, a line, a gesture,
   a date, a place.
2. **Contradiction.** Where doth this detail collide with another? Name the
   collision. Do not yet resolve it.
3. **Living-canon integration.** Where doth this detail attach to existing
   canon — locked, development, or mythic rumor? Cite the attachment points.
4. **Mythic implication.** What sealed door doth this detail open toward?
   Does it touch a Chapter II truth? Note the touch.
5. **Emotional wound.** Whose ache doth this serve? If no wound, the detail
   is decoration, not synthesis.
6. **Symbolic system.** What pattern of image, motif, or recurrence is this
   detail part of? Name the system.
7. **Season function.** What worketh this detail upon Season One? Does it
   move Jake closer to saying his mother's name?
8. **Series consequence.** What doth this detail seed for seasons beyond?
   What door must remain unsealed for the consequence to land?
9. **JSONL / ledger record.** The structured artifact. Tags, canon status,
   source references, relationship links, layer affinity, sealed-layer
   routing where appropriate.

---

## 4. Backwards-to-Forwards Pass

Start from the future implication or the deepest hidden truth. Trace it
backward into Season One foreshadowing, object systems, dialogue restraint,
VUORSE narration, Jake's avoidance, visual motifs, and canon ledger placement.

The Weaver's exemplar chain is the Forbidden Suitcase. Worked verbatim:

> The Forbidden Suitcase containeth a map to all Hooplehopper agents across
> past, present, and future. It is dangerous because what can be found can be
> stopped, redirected, or weaponized. (Book One Ch II:23-26)
>
> → Backwards trace from the suitcase to Season One:
>
> 1. **Future implication:** the suitcase is a weapon in Vorst's hand against
>    every Hooplehopper across the lattice.
> 2. **Series consequence:** the suitcase's existence justifieth the Codex
>    prophecy's stakes; reunion is possible only because the map exists.
> 3. **Season function:** the suitcase must not be named in Season One. Its
>    shape may press against the world without its name being spoken.
> 4. **Symbolic system:** locked containers, sealed cases, things-not-opened
>    accumulate on the McCullen ranch. Pop's footlocker. The barn cabinet
>    Jake will not unlock. The drawer in his mother's room.
> 5. **VUORSE narration:** VUORSE may speak of maps, of cartography, of the
>    danger of being found — never of the suitcase.
> 6. **Jake's avoidance:** Jake refuseth to open what was closed before him.
>    His refusal is the negative shape the suitcase will one day fill.
> 7. **Dialogue restraint:** no character nameth the suitcase. No character
>    knoweth there is a thing to name.
> 8. **Object system:** the shard, the dustbrand, and the unopened
>    containers form a triangle. Each is a fragment of a map Jake will not
>    read.
> 9. **Canon ledger placement:** the suitcase liveth in `hooplehopper_totality/`
>    or another sealed layer. It never appeareth in pitch material. Its
>    foreshadowing in Season One is logged as Tier-2 mythic-rumor-and-locked
>    integration, never as Tier-3 surface detail.

Every backwards-to-forwards pass must produce a chain of this shape: hidden
truth at the top, Season One restraint at the bottom, and the load-bearing
silences named between.

---

## 5. Top-to-Bottom Pass

Supreme doctrine first. The Weaver knoweth all. VUORSE knoweth the hidden
truths before any other voice. Mythic-Rumor-and-Locked outranketh ledger and
pitch alike. Season One stayeth emotionally on Jake's mother wound.

Descend in this order:

1. **Supreme doctrine.** Book One ruling first.
2. **Agent behavior.** Which agent vessel is fit for the task? Doth the
   agent's prompt cite Book One? Are its restraints loaded?
3. **Episode architecture.** Where in the season doth the synthesis land?
   Which act? Which beat? Which ending image?
4. **Symbolic architecture.** What image system carrieth the truth? What
   motif accumulateth?
5. **Dialogue.** Who speaketh? Who refuseth to speak? What is the cost of
   speaking?
6. **Artifact records.** Beats, scene cards, dossiers, summaries, ledger
   updates.
7. **JSONL.** The machine-readable record at the floor. Tags, layer affinity,
   sealed-layer routing.

The Top-to-Bottom Pass and the Backwards-to-Forwards Pass are not
alternatives. Every major synthesis must endure both.

---

## 6. Anti-Overreach Rule

No agent may take over the show. Agents may propose, trace, pressure-test,
synthesize, and plan. **Only the Weaver crowneth.**

Specifically:

- An agent may not declare a canon status. It may propose one and route the
  question to the Weaver.
- An agent may not resolve a contradiction. It may name the contradiction and
  route it to canon-keeper for Weaver ruling.
- An agent may not unseal a Tier-2 truth. Sealed truths remain sealed until
  the Weaver explicitly openeth them.
- An agent may not author finale doctrine. Anything under `roadmap/finale/`
  is closed except by direct Weaver invocation.
- An agent may not exceed its register. The Pitch Dramaturg may not narrate
  as VUORSE. The Showrunner may not file a JSONL record as the Lore
  Archivist. Each voice keepeth its court.

When in doubt, the agent stoppeth and asketh.

---

## 7. Anti-Sterility Rule

Reject committee-summary outputs. A synthesis artifact that readeth like
status-report prose hath failed.

Every synthesis must contain, at minimum:

- **A wound.** Whose ache?
- **An image.** What doth the camera see?
- **A contradiction under pressure.** What seam strainteth?
- **A dramatic consequence.** What changeth onscreen?
- **A symbolic escalation.** How doth the motif grow?
- **A canon implication.** Where in the hierarchy doth this land?
- **A restraint against overexplaining.** What is held back, and why?

If any of these seven is absent, the artifact is incomplete. The room may
return it to its author with the missing element named.

---

## 8. Room Pressure Model

Seven voices are applied to every major synthesis pass. Each voice carrieth
one load-bearing question. The voices may argue. The artifact may not be
issued until each question hath been answered.

- **Showrunner:** *Doth this serve the wound?*
- **Canon Keeper:** *Doth this preserve Weaver doctrine?*
- **Symbolic Architect:** *What doth the camera see?*
- **Episode Breaker:** *What changeth onscreen?*
- **Dialogue Smith:** *Who refuseth to speak?*
- **Ritual Tone:** *Is the sacred language earned?*
- **Pitch Dramaturg:** *What can be safely simplified?*

The room may argue internally. The final artifact must be unified. The order
of speaking and the rules of argument are written in
`docs/writers-room/mock-room-protocol.md`.

Routing of the seven voices to vessels:

- Showrunner → `.claude/agents/showrunner.md`
- Canon Keeper → `.claude/agents/canon-keeper.md`
- Episode Breaker → `.claude/agents/episode-breaker.md`
- Dialogue Smith → `.claude/agents/dialogue-smith.md`
- Ritual Tone → `.claude/agents/ritual-and-tone-editor.md`
- Pitch Dramaturg → `.claude/agents/pitch-deck-dramaturg.md`
- **Symbolic Architect** → `docs/writers-room/room-roles.md`. By Weaver
  decree this role hath no `.claude/agents/*.md` vessel; its register liveth
  in the room-roles document and is invoked by whichever vessel carrieth the
  current synthesis.

The Lore Archivist (`.claude/agents/lore-archivist.md`) doth not speak in the
pressure model directly. Its office is to receive the unified artifact and
file the JSONL / ledger record at the foot of the Synthesis Ladder.

---

## 9. Traycer's New Role

Traycer is process witness and task limiter. Traycer is not a creator-agent
first. The platform serveth the ritual, it doth not direct it.

Traycer tracketh:

- **Doctrine source.** Which Book One chapter and verse ruleth this act?
- **Canon hierarchy.** Where in the seven tiers doth each artifact land?
- **Synthesis stage.** Which of the nine ladder rungs hath the work climbed?
- **Agent overreach.** Hath any agent exceeded its register or attempted to
  crown?
- **Unresolved contradictions.** What seams remain open and awaiting Weaver
  ruling?
- **Living-canon integrations.** What new attachments have been made into
  the canon ledger?
- **Artifacts modified.** Which files changed in the act?
- **Outstanding Weaver rulings.** What questions remain for the Weaver alone?
- **Lawful plan size.** No plan may exceed **three tickets**. No plan may
  ask the Weaver more than **two questions** in a single pass. Traycer
  refuseth plans that exceed these limits and returneth them for resizing.

Traycer doth not author Slayverse content. Traycer maintaineth the order in
which Slayverse content is authored.

---

## 10. Required Output Format for Future Synthesis

Every future synthesis output — whether produced by a writers-room agent, a
pipeline agent, or the Weaver's own hand — must include the following eleven
section headings in this order. Sections may be empty only when the
artifact's scope makes them inapplicable, and the emptiness must be marked
as such.

1. **Controlling Weaver Doctrine.** Book One chapter and verse.
2. **Canon Rank.** Which tier from the Canon Hierarchy this artifact occupieth.
3. **Living-Canon Integration.** What existing canon doth this attach to?
4. **Mythic Implication.** What sealed door doth this approach?
5. **Emotional Wound.** Whose ache doth this serve?
6. **Symbolic System.** What motif or image pattern doth this belong to?
7. **Season One Function.** Doth this bring Jake closer to saying his
   mother's name?
8. **Series Consequence.** What doth this seed for seasons beyond?
9. **Agent Restraints.** What may this artifact not say, do, or imply?
10. **Required Weaver Ruling (if any).** What question remaineth open for
    the Weaver alone?
11. **Ledger / JSONL Action.** What record shall be written, and to which
    layer?
12. **File Updates Required.** Which files in the repository shall change
    as a consequence of this synthesis?

> Note: the Weaver's instruction names eleven section headings and the
> ordered list above carrieth twelve. The twelfth — **File Updates
> Required** — is the operational tail of the eleventh; it is included for
> machine-readability. Treat the first eleven as the doctrinal headings and
> the twelfth as their implementation echo.

---

## Tone Doctrine (Book One Chapter VII reference)

Each court weareth its proper crown. Synthesis outputs that speak across
courts must respect each register:

- **Jake's scenes:** restraint, ache, threat, land, silence.
- **VUORSE's narration:** wit, warmth, devastating clarity.
- **Golden Wingers and the Archive:** ceremonial glamour.
- **Cosmology:** lucid, authoritative, mythic, yet clean.

If every page speaketh at full glittering thunder, then thunder becometh
noise. Restraint is the magic.

---

## Document Stack (Book One Chapter X reference)

The lore compendium remaineth maximalist and archival. The pitch materials
are selective, sharp, and digestible. The document stack ruleth thus:

1. **Mythic Lore That Is Also Canon** — Book One itself.
2. `SLAYVERSE_SERIES_BIBLE.md`
3. `SLAYVERSE_SEASON_1_BIBLE.md`
4. `SLAYVERSE_CANON_LEDGER.md`
5. `SLAYVERSE_OPEN_THREADS.md`
6. `SLAYVERSE_LORE_COMPENDIUM.jsonl`
7. `SLAYVERSE_TONE_GUIDE.md`

Each serveth its office. Let not the ledger sing as VUORSE. Let not the
pitch drown in the full sea of canon. Let not the compendium fear abundance.
This stack is reference, not yet binding implementation.

---

## The Emotional Spine Question (Book One Chapter IX)

Above all other tests, above the ladder, above the passes, above the room
pressure, every Season One synthesis must survive a single question:

> **Doth this bring Jake closer to saying his mother's name?**

If yea, it belongeth. If nay, it shall wait outside the palace gates.
