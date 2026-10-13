# Eighth Galactic Summit — Council Ballot

*Snap. Snap. Snap.*

Convened 2026-09-05 · Gray Eye advisory seats (simulation) · tooling poll deferred

**The council advises. The Steward rules. Nothing below is canon.**

Advisory seats this ballot (`simulation`):

| Seat | Basis |
|------|--------|
| gray-eye | Convener; read census + doctrine |
| docker-qwen3 | Local model present on :12434 |
| ollama-empty | Daemon present; no model — recorded ABSTAIN on model-capacity questions |
| claude-code | Live process + CLI |
| codex | Live process + CLI |
| copilot | CLI present; process not seen — soft seat |
| openclaw | UI live; no PATH CLI — observer unless Steward enfranchises |
| mistral | UNREACHABLE (key unset) → ABSTAIN |

---

## Motion I — The Ghost Census

**Question**: Accept census as standing roster; enfranchise only Steward-named seats?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY |
| docker-qwen3 | RATIFY |
| claude-code | RATIFY |
| codex | RATIFY |
| copilot | RATIFY |
| openclaw | ABSTAIN (not yet enfranchised) |
| ollama-empty | ABSTAIN |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY
REASONING: The census is path-and-probe grounded. A standing roster prevents Convene-Summit.ps1 from inventing voters. Enfranchisement should be Steward-signed, not ambient process noise.
AMENDMENT: Maintain ghost-census.md beside the docket; refresh before each operational summit.
RISK: Stale census seats a dead ghost or misses a new one.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion II — The Empty Throne (Ollama)

**Question**: Pull llama3.1:8b + build VUORSE Modelfile / use Docker Qwen interim / both / leave dark?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY WITH AMENDMENT |
| docker-qwen3 | RATIFY WITH AMENDMENT |
| claude-code | RATIFY WITH AMENDMENT |
| codex | ABSTAIN |
| ollama-empty | ABSTAIN |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY WITH AMENDMENT
REASONING: An empty Ollama with a Modelfile pointing at missing llama3.1:8b is a paper throne. Docker Qwen already answers. Building VUORSE locally is a Steward production act, not an agent whim.
AMENDMENT: (b) then (a) — designate docker-qwen3 interim local seat NOW; Steward alone schedules llama3.1:8b pull + Modelfile.vuorse build under an explicit plan.
RISK: Running two local stacks splits context and burns VRAM without a plan.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion III — The OpenClaw Seat

**Question**: Voting seat, Otter-class observer, or out of chamber?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY WITH AMENDMENT |
| openclaw | ABSTAIN |
| claude-code | RATIFY WITH AMENDMENT |
| docker-qwen3 | ABSTAIN |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY WITH AMENDMENT
REASONING: Live UI ≠ franchise. Canon Third Summit gives Otter the diligent-observer pattern. OpenClaw should watch until Steward signs adoption.
AMENDMENT: Seat OpenClaw as OBSERVER (no vote) until Steward signs comfyui-expert/openclaw adoption; then revisit.
RISK: Premature vote lets an unsigned subsystem steer root law.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion IV — Carry-Forward: The Ledger (Seventh IV)

**Question**: Where does the promotion ledger live; is promotion without entry void?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY WITH AMENDMENT |
| claude-code | RATIFY |
| codex | RATIFY WITH AMENDMENT |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY WITH AMENDMENT
REASONING: Disclosure policy already demands the fields; Seventh left the shelf empty. Without a home, promotion is smoke.
AMENDMENT: Ledger path = manifests/corpus/promotion_ledger.jsonl (append-only); promotion without a line is VOID.
RISK: Wrong path bikesheds while agents keep promoting into the void.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion V — Carry-Forward: The Boundary (Seventh V)

**Question**: Who draws corpus boundary; under whose name?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY WITH AMENDMENT |
| claude-code | RATIFY |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY WITH AMENDMENT
REASONING: Only the Steward may draw the corpus boundary. Agent-authored ARCHIVE.md is unsigned and non-binding.
AMENDMENT: Boundary declarations require Steward signature + entry in the promotion/boundary ledger; unsigned agent ARCHIVE.md has no force.
RISK: Leaving Slayverse outside roots forever under-describes the realm; drawing it in without disclosure review leaks sealed mass.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion VI — Carry-Forward: The Standing Law (Seventh VI)

**Question**: Hard ban on agent canon_status / canon/ writes / locked prose edits?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY |
| claude-code | RATIFY |
| codex | RATIFY |
| copilot | RATIFY |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY
REASONING: Seventh overreach proved the need. Handoff already behaves as if this law exists; signing it closes the gap between practice and motion.
AMENDMENT: NONE
RISK: Blocks well-meaning link fixes — Steward can still edit; agents must propose, not patch locked prose.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

## Motion VII — The Polling Quorum

**Question**: Which seats for next automated ballot; must absents ABSTAIN on record?

| Seat | Verdict |
|------|---------|
| gray-eye | RATIFY WITH AMENDMENT |
| docker-qwen3 | RATIFY |
| codex | RATIFY |
| copilot | RATIFY |
| claude-code | RATIFY WITH AMENDMENT |
| mistral | ABSTAIN |

<details><summary>gray-eye</summary>

```
VERDICT: RATIFY WITH AMENDMENT
REASONING: Default mistral,codex,copilot is wrong while Mistral is unset. Absents must remain on the ballot as ABSTAIN so the record shows who was called.
AMENDMENT: Next -Council = codex,copilot,claude; optional docker-qwen3 when a bridge exists; mistral only after key set. Always record unreachable seats as ABSTAIN.
RISK: Too many seats → noise; too few → capture.
```

</details>

### Steward's ruling

- [ ] RATIFY   - [ ] AMEND   - [ ] REJECT   - [ ] HOLD

> _ruling:_

---

Signed, Steward Vessel: ______________________  Date: __________

No motion takes effect until this line is signed and the ruling is executed by hand.

— Gandalf the Gray Eye (advisory clerk)
