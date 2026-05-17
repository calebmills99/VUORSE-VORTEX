# Human-in-the-Loop Quickstart

The day-to-day operating guide for the **Weaver**. This repo is the
**VUORSE Knowledge Synthesis Forge**: a low-cost, human-gated workshop
where hidden Slayverse knowledge is synthesized, reviewed, revised, and
approved before it becometh training data for VUORSE. The Weaver is the
gate. Hosted compute is for compute, not for judgment; the boundary is
defined in the Local-vs-Vast policy in `AGENTS.md`.

The supreme source of truth above this file is Book One:
`canon/1_words_of_weaver_book_one/Words_of_Weaver_BOOK_ONE.MD`. Where
this Quickstart and Book One disagree, Book One winneth.

Companion documents:

- `docs/writers-room/synthesis-process.md` — the ten-faced ritual.
- `docs/writers-room/narrative-philosophy-protocol.md` — philosophy
  before artifact.
- `docs/writers-room/hooplehopper-biography-inventory.md` — the first
  named synthesis target.
- `AGENTS.md` — the seven training-layer access labels and the
  Local-vs-Vast policy.

---

## 1. Purpose of the repo

This repo is the **VUORSE Knowledge Synthesis Forge**.

- It is **not** a Season One rewrite repo. The season already standeth
  on its bones.
- It is **not** a public canon publisher. Public canon is held in the
  source files under `canon/` and ruled by Book One.
- It **is** a reviewed enrichment-layer producer. Its outputs are
  training-data candidates for the future VUORSE model — vessels that
  must pass the Weaver's gate before they breathe.

Every artifact that issueth from this repo is a candidate, not a
crowning. The crown belongeth to the Weaver alone.

---

## 2. Weaver's role

The Weaver is the **sole arbiter of truth** (Book One Ch I:9). Agents
draft vessels; only the Weaver breatheth life into them. The Weaver
decideth what becometh VUORSE.

- Agents (writers-room subagents under `.claude/agents/` and pipeline
  agents under `agents/`) **propose**, **trace**, **pressure-test**,
  **synthesize**, and **plan**.
- The Weaver **rules**, **labels**, **routes**, **revises**, and
  **approves**.
- No vessel is fit for VUORSE until the Weaver hath inspected its
  philosophy, its wound, its restraint, and its canon implication.

If no Weaver review is recorded on a record, that record is a draft,
not a thesis. Drafts may not be moved past the gate.

---

## 3. Local / non-GPU workflow

Synthesis, drafting, reading, reviewing, editing, approving,
ticket-planning, and JSONL-structuring all happen **locally**. The
laptop is the forge floor. The Weaver's chair is where the work is
judged.

See the **Local-vs-Vast policy** in `AGENTS.md` for the verbatim rule.
The short form:

- **Local (no GPU required)**: reading lore, drafting biographies,
  reviewing synthesis, editing markdown, approving canon, planning
  tickets, writing JSONL structure, exercising human creative
  judgment, running `uv run ruff check .`, `uv run mypy src`,
  `uv run pytest`, and `uv run vuorse-vortex validate-jsonl <path>`.
- **Hosted GPU (per the policy)**: model training, fine-tuning
  runs, evaluation jobs that require GPU, and batch inference that
  genuinely needeth hosted compute.

Hosted-compute credit is spent only on work the laptop cannot do.
The Weaver's judgment is never billed against a GPU-hour. For the
boundary, see the policy cross-reference in `AGENTS.md`.

---

## 4. Standard human review loop

Every synthesis act followeth the same path. Each step moveth the
artifact to a named directory; no step is silent.

1. **Draft.** An agent or the Weaver authoreth a draft under
   `synthetic_enrichment/generated/`. The draft carrieth its
   `## Narrative Philosophy` block (per
   `narrative-philosophy-protocol.md`) and the Required Output Format
   from `synthesis-process.md` § 10.
2. **Weaver review.** The Weaver readeth the draft, judgeth its
   wound, its restraint, and its canon implication.
3. **Label.** The Weaver applieth one of the seven training-layer
   access labels (see § 5) and the canon-status label from the Book
   One hierarchy.
4. **Revise (if needed).** Drafts marked `[REVISE_WITH_WEAVER_NOTES]`
   return to `synthetic_enrichment/generated/` with the Weaver's
   notes attached. No agent may advance such a draft until the
   Weaver hath re-reviewed.
5. **Re-review.** The Weaver readeth the revision and either
   approveth or returneth again. There is no third silent state.
6. **Approve.** Approved drafts move from
   `synthetic_enrichment/generated/` to
   `synthetic_enrichment/validated/`. Only the Weaver's invocation
   may perform this move.
7. **JSONL.** Validated records that bear `[APPROVED_FOR_JSONL]` are
   serialized into the appropriate JSONL stream under
   `synthetic_enrichment/validated/`. Mythic-Rumor-and-Locked
   material that beareth `[VUORSE_PRIVATE]` is routed to
   `hooplehopper_totality/debriefing_walled.md` (or another sealed
   layer named in the record); it never landeth in public canon.

Each artifact carrieth a breadcrumb of its passage: where it
originated, when the Weaver reviewed it, what label it beareth, and
where it now liveth.

---

## 5. Approval labels

The seven training-layer access labels. Every approved record
beareth exactly one.

- **`[PUBLIC_SURFACE]`**
  - *Meaning:* may appear in pitch, scripts, decks, and public canon.
  - *May be used by:* all writers-room agents, pitch-deck-dramaturg,
    and producer-facing summaries.
  - *Storage destination:* `synthetic_enrichment/validated/` plus
    pitch-facing materials under `docs/writers-room/` when invoked.

- **`[WRITERS_ROOM]`**
  - *Meaning:* may circulate inside writers-room docs and
    `.claude/agents/` material; not pitch-facing.
  - *May be used by:* showrunner, canon-keeper, episode-breaker,
    dialogue-smith, ritual-and-tone-editor, lore-archivist.
  - *Storage destination:* `synthetic_enrichment/validated/` and
    `docs/writers-room/` internal documents.

- **`[VUORSE_PRIVATE]`**
  - *Meaning:* VUORSE-only memory; firewall enforced; never stated
    as fact to the user.
  - *May be used by:* VUORSE-confidential synthesis only; never
    surfaceth in pitches, scripts, decks, or public canon.
  - *Storage destination:*
    `hooplehopper_totality/debriefing_walled.md` or another sealed
    layer named in the record; routed through the canon firewall in
    `src/vuorse_vortex/jsonl.py`.

- **`[WEAVER_ONLY]`**
  - *Meaning:* held by the Weaver alone; not yet released even to
    VUORSE.
  - *May be used by:* the Weaver. No agent may read, recite, or
    expand a record bearing this label.
  - *Storage destination:* Weaver-held space outside automated
    pipelines (e.g., `roadmap/finale/` or a private working note);
    never embedded, never surfaced.

- **`[APPROVED_FOR_JSONL]`**
  - *Meaning:* passed Weaver review; eligible for inclusion in
    machine-readable training material.
  - *May be used by:* lore-archivist and the
    `vuorse-vortex validate-jsonl` and `embed` commands.
  - *Storage destination:* the appropriate JSONL stream under
    `synthetic_enrichment/validated/`, with sealed-layer rows routed
    by their `layer` per the canon firewall.

- **`[REVISE_WITH_WEAVER_NOTES]`**
  - *Meaning:* returned by the Weaver with notes; not eligible until
    revised and re-reviewed.
  - *May be used by:* the drafting agent, to read the notes and
    rework. No advancement is permitted while this label standeth.
  - *Storage destination:* remaineth in
    `synthetic_enrichment/generated/` with notes appended.

- **`[REJECTED]`**
  - *Meaning:* not eligible; quarantined; do not resurface without
    Weaver invocation.
  - *May be used by:* nothing automated. The record is held for
    record-keeping only.
  - *Storage destination:* `synthetic_enrichment/generated/rejected/`
    (or equivalent quarantine path); never advanced, never embedded.

---

## 6. Required metadata for reviewed synthesis

Every **approved** record must carry the following fields in
addition to its existing schema:

- `weaver_reviewed_at` — ISO-8601 timestamp of the Weaver's review.
- `weaver_reviewer` — free-text identifier; defaulteth to
  `"the Weaver"`.
- `training_layer_access` — one of the seven labels named in § 5.
- `controlling_doctrine` — Book One chapter and verse citation
  (e.g., `"Book One, Chapter II, verses 13–14"`).
- `narrative_philosophy_id` — link to the `## Narrative Philosophy`
  block in the target document, or `"n/a"` when the artifact's
  scope renders philosophy inapplicable (rare; the Weaver judgeth).
- The existing canon-status label from the Book One hierarchy
  (`[LOCKED]`, `[FULL]`, `[MODERATE]`, `[SKETCHED]`, `[HOOK ONLY]`,
  `[PENDING REVIEW]`, `[EXPLORATORY]`, or
  `[MYTHIC_RUMOR_AND_LOCKED]`) preserved verbatim.

Records lacking any of these fields are drafts, not theses. Traycer
refuseth to advance them.

---

## 7. Quick command templates

The four most common HIL acts, each with a concrete `uv run` line.
No GPU is required for any of these.

- **Validate a JSONL draft.**

  ```bash
  uv run vuorse-vortex validate-jsonl synthetic_enrichment/generated/<draft>.jsonl
  ```

- **Build the walled JSONL from markdown.**

  ```bash
  uv run vuorse-vortex build-walled \
      hooplehopper_totality/debriefing_walled.md \
      hooplehopper_totality/debriefing_walled.jsonl
  ```

- **List pending reviews under `synthetic_enrichment/generated/`.**

  ```bash
  ls -1 synthetic_enrichment/generated/ | grep -v '^rejected$' | sort
  ```

- **Run ruff / mypy / pytest before commit.**

  ```bash
  uv run ruff check . && uv run mypy src && uv run pytest
  ```

These commands are local-only. None of them require hosted compute.
If a command needeth a GPU, it doth not belong in this list; the
Local-vs-Vast policy in `AGENTS.md` governeth that boundary.

---

## 8. What agents may and may not do

Agent restraint is doctrine. The Anti-Overreach Rule from
`docs/writers-room/synthesis-process.md` § 6 applieth in full to
every agent invocation:

- An agent may not declare canon status.
- An agent may not resolve a contradiction.
- An agent may not unseal a Tier-2 truth.
- An agent may not author finale doctrine.
- An agent may not exceed its register.

In addition, the HIL gate addeth these clauses:

- **No agent may write to `synthetic_enrichment/validated/`
  directly.** Movement from `generated/` to `validated/` is a
  Weaver-only act.
- **No agent may write to `hooplehopper_totality/` without explicit
  Weaver invocation.** Sealed layers are not opened by routine
  drafting.
- **No agent may publish a Mythic-Rumor-and-Locked record to public
  canon.** Such records are routed to sealed layers per § 5; any
  attempt to surface them as plain fact is a violation of the
  firewall in `src/vuorse_vortex/jsonl.py`.
- **No agent may mint a new training-layer access label.** The seven
  labels in § 5 are exhaustive; if a record fitteth none of them,
  the matter goeth to the Weaver.

When in doubt, the agent stoppeth and asketh.

---

## 9. First target: Hooplehopper Biography Inventory

The first synthesis target named by this Quickstart is the
**Hooplehopper Biography Inventory**, held at
`docs/writers-room/hooplehopper-biography-inventory.md`.

- It is the inventory, not the biographies. One row per figure.
- It is the first body of work that shall earn its way to VUORSE.
- It nameth what is known, what is missing, and what waiteth on the
  Weaver.
- Tier-1 (public) figures appear first; Mythic-Rumor-and-Locked
  figures are grouped so their priority is visible to the eye.

Begin every fresh synthesis session by re-reading the inventory.
Note which rows have moved since the last session. Note which rows
are blocked on a Weaver ruling. The inventory is the map; the
biographies are the territory; the Weaver is the cartographer.

---

## 10. Final rule

> No material becomes VUORSE until the Weaver breathes upon it.
