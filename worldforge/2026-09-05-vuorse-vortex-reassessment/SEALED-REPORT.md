# Gray Eye Sealed Report — The Night the Boundary Held

*A kingdom is not usually lost to the army at the gate. It is lost to a clerk
who files two different things under one name, and to the policy that would
have caught him being quietly deleted from the shelf.*

---

## Run frame

- **canon** Change point: repair VUORSE-VORTEX's governance and disclosure integrity. Provenance: this session, 2026-09-05.
- **canon** Observation cutoff: 2026-09-05, live filesystem and Git state.
- **canon** Interval: one working night, from the first reconnaissance to a verified clean audit.
- **canon** Domains: governance, corpus integrity, disclosure firewall, retrieval, version control.
- **canon** Temporal mode: `hybrid` — a defect already set in the past, propagated forward until it was cut.

---

## What was actually wrong

- **canon** `policies/` — canon firewall, disclosure classes, writer-room finale boundary, GPU floor — had been deleted from the working tree. Thirteen files. Never committed as deleted, so recoverable, but absent from disk. The code enforcing the rules was live; the document explaining them was gone.
- **canon** `vuorse_vortex/indexing.py` minted every source id by slugifying the path **with the extension stripped**, so `debriefing_walled.jsonl` and `debriefing_walled.md` claimed the same id. It **detected** the collision, appended a note to the duplicate row, and shipped it anyway.
- **canon** `cortex.py` derives `chunk_id` from that source id. The collision therefore reached the retrieval index: 8 chunk ids, each naming one `private_to_vuorse` row and one `weaver_only` row. **A source id is a disclosure boundary, and it was being minted unsafely.**
- **canon** All 22 canon-layer sources carried `canon_status: "unknown"`. The firewall could say what must not be spoken; it could not say what was true.
- **canon** Regeneration read no curated state. Any rebuild reverted every classification to the route-table default and blanked every provenance note. The repair, had it stopped at the manifest, would have erased itself on the next index.

---

## What holds now

- **canon** `policies/` restored — 13 files, 4 governing documents.
- **canon** Id minting is collision-proof: deterministic ordinal disambiguation matching the precedent already proven in `walled.py`, with `DuplicateSourceIdError` as a last-line guard.
- **canon** Curation lives in `manifests/corpus/source_curation.json`, **keyed by path, not id** — 29 entries. That choice is why the repair survived the rename that fixed the collision.
- **canon** 54 sources, 54 unique ids, 16 sealed by both layer and visibility, 17 notes intact, `unknown`: none. `locked` 15, `draft` 13, `roadmap_private` 14, `system_rule` 9, `synthetic_behavioral` 3.
- **canon** Index rebuilt: 6,910 chunks, 6,910 unique chunk ids, 64 sealed. Verified exit 0.
- **canon** `scripts/gandalf.py` — deterministic, stdlib-only, read-only, free. Watches only what can break: duplicate ids, sealing coherence, chunk collisions, curation survival, governance presence, git lock.

---

## The lesson, promoted at the Steward's instruction

- **canon** *The only question that matters is whether it breaks something.*
  Imperfection is not a finding. A broken link in a file nobody opens costs nothing
  and is not worth a man's attention. This governs what the Gray Eye reports, not
  merely what it checks. Provenance: Caleb, 2026-09-05, stated plainly and more
  than once before it was heard.

---

## Canon-promotion candidates

Not canon until the Weaver promotes them.

- **simulation** A source id is a disclosure boundary. Collisions are security defects, not tidiness defects.
- **simulation** Curation is keyed by path. An id is derived and may change; a path is identity.
- **simulation** Doctrine deleted from the working tree is doctrine repealed. Restore it or rewrite it; do not run without it.
- **simulation** A detected failure written into a note is a swallowed failure.
- **simulation** An audit reports what breaks. Everything else is noise wearing a badge.

---

## Verification

- **canon** Every claim above carries a repository path, a command, or a stated provenance.
- **canon** `roadmap/`, `hooplehopper_totality/` and `.agent-quarantine/` were cited by path only; no sealed content was quoted.
- **canon** No canon prose was edited. Two broken citation paths were repaired; nothing else was touched.
- **canon** Final audit: FAIL 0, WARN 0. Exit 0.

**Gandalf the Gray Eye**
