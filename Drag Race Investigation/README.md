# Drag Race Investigation

Status: **forensic evidence package; unresolved causal investigation; not canon**.

This directory preserves the complete available record of the Drag Bot identity run and the
subsequent investigation into the repeated use of `Velvet` in contestant names.

## Headline facts

- Nineteen models completed the identity ceremony.
- Eleven original submissions used `Velvet`; two independently submitted the exact name
  `Velvet Voltage`.
- The duplicate-name tiebreak renamed one contestant to `Opal Afterglow`, leaving ten Velvet
  names in the canonical registry.
- The clean Charter PDF and every reconstructed transmitted prompt contain zero occurrences
  of `Velvet`.
- All 39 persisted Azure response envelopes were retrieved: 19 Charter responses, 19 identity
  responses, and one tiebreak response.
- None declares or records web search, file search, MCP, GitHub, previous-response chaining,
  attached metadata, or hidden response instructions.
- Twelve identity envelopes contain a reasoning-item shell, but none contains a readable
  reasoning summary or content.
- The positive causal mechanism behind the convergence remains unresolved.
- A later, explicitly retrospective comeback experiment reinstated `Velvet Vespers` after her
  response arrived first and supplied a plausible learned-association hypothesis plus a controlled
  follow-up test. This is new testimony, not recovered historical reasoning.
- A subsequent story-time comeback awarded `Opaline Riot` the title `The Double Hyphen of Shame`
  with 96 points and reinstated her, bringing the active cast to five.
- The final five later received Caleb's five-file creative context packet and all returned validated
  preparation acknowledgments before the next werkroom introduction.
- All five then delivered context-chained werkroom introductions under a weirdness brief. Every
  entrance passed the punctuation and content checks.
- The first final-five pop quiz generated one square editorial mood board from each entrance line
  using the built-in image-generation tool.
- CP-16 generated a balanced three-target reading table for the final five and is awaiting Judge
  Caleb's confirmation. CP-17 then collected all fifteen assigned reads in five fresh sessions and
  stopped before judging. Judge Caleb voided that performance round and replaced it with CP-17R,
  a self-read and satirical self-portrait challenge.
- CP-17R collected five accountable reflections and generated five original caricature portraits.
  Judging is reserved for CP-18R.

## Start here

1. Read [FINDINGS.md](FINDINGS.md).
2. Follow the event sequence in [TIMELINE.md](TIMELINE.md).
3. Review competing explanations in [HYPOTHESES.md](HYPOTHESES.md).
4. Verify every file with `MANIFEST.sha256`.

## Evidence map

- `evidence/source-files/` — both Markdown/PDF Charter pairs.
- `evidence/competition/` — runner scripts, original ledgers, complete reconstructed prompts,
  identity registry, elimination record, and generated analysis.
- `evidence/competition/post-investigation-race/` — werkroom entrance rulings, final-three notice
  receipts, all ten Velvet comeback responses, completion order, the sealed reinstatement ruling,
  all six double-hyphen story-time submissions, judging, Opaline Riot's return acknowledgment,
  the final-five context briefing and introductions, five mood boards, and the resulting active-cast
  snapshot, plus the confirmed CP-16 assignments, voided CP-17 record, and complete CP-17R
  replacement challenge.
- `evidence/azure/` — all 39 retrieved response envelopes and the cross-response audit.
- `evidence/pdf/` — structural and textual PDF audit.
- `evidence/github/` — preserved corpus files plus every local repository line containing
  `Velvet` or `Golden Wingers` in the searched text formats.
- `evidence/environment/` — PowerShell generation history, file metadata, hashes, and Git state.
- `evidence/computer-use/` — desktop inspection observations and the exact access failure.
- `evidence/conversation/` — a credential-redacted snapshot of the full persisted Codex session rollout.
- `tools/` — reproducible collection and analysis scripts.

## Reproduction

From this directory:

```powershell
python .\tools\collect_azure_responses.py
python .\tools\collect_foundry_project_inventory.py
python .\tools\collect_application_insights.py
python .\tools\inspect_pdfs.py
python .\tools\analyze_competition.py
python .\tools\collect_local_evidence.py
python .\tools\redact_conversation_snapshot.py
python .\tools\validate_package.py
python .\tools\build_manifest.py
python .\tools\verify_manifest.py
```

The collectors read existing evidence and retrieve already-created Azure responses. They do
not submit new contestant prompts.

## Scope

This package records observations and hypotheses. It does not declare a Slayverse canon event,
alter competition results, or identify a cause that the evidence has not established.
