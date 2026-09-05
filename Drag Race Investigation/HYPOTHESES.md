# Hypotheses and Test Matrix

The cause is unresolved. This file keeps eliminated paths separate from live hypotheses.

## Eliminated by direct evidence

### Wrong PDF supplied

The runner pinned the exact clean PDF path and SHA-256. Reconstructed prompts match every logged
hash.

### Hidden content or metadata in the clean PDF

The clean PDF contains no `Velvet` in raw or extracted content and has no attachment or alternate
document-content mechanism discovered by the audit.

### Repository breadcrumb in the prompt

No repository name, owner, URL, or clone path appears in any reconstructed prompt.

### Live GitHub or web lookup

All persisted response envelopes contain zero declared tools and zero tool events.

### File search, MCP, or previous-response memory

All persisted response envelopes contain zero such events or links.

## Live hypotheses

### H1 — Shared learned association in related model weights

The models may share a learned association among drag identity, luxury/noir vocabulary, and
`Velvet`. This is compatible with the repeated `neon`, `cathedral`, `chrome`, `siren`, `hex`,
`mirage`, and `voltage` vocabulary. It does not yet explain the observed rate quantitatively.

Velvet Vespers later proposed this same mechanism in a retrospective comeback response, describing
`velvet` as a high-fit luxury-texture token for the gothic-opulent prompt cues. This is a useful
test direction, not recovered historical reasoning.

### H2 — Memorized Charter/corpus association in one or more model weights

The exact Charter text is publicly searchable in the repository, and the same corpus connects it
to the Velvet Archive. A learned association could exist without a live web call. The repository's
May 2026 creation date and the participation of model snapshots labeled 2025 complicate this
hypothesis and require model-specific provenance unavailable in the response envelopes.

### H3 — Shared provider-side conditioning not surfaced in response objects

A model gateway or provider system layer could add behavior not represented by the response's
`instructions` field. The retrieved objects provide no positive evidence for this mechanism.

### H4 — Prompt-form interaction

The identical identity brief may create a narrow high-probability naming basin across related
models. This is testable with controlled prompt variants and repeated samples. Velvet Vespers
proposed holding the aesthetic constant while comparing `velvet`, `satin`, `silk`, and `brocade`
selection frequencies.

### H5 — Cross-request infrastructure contamination

Prompt caching, routing, or another shared service mechanism could correlate responses. No
response field currently demonstrates this. A controlled order-randomized replay would be needed.

## Controlled causal test

This package does not run new contestant calls. A separate forensic experiment could preserve the
competition record while testing these conditions across the same available model versions:

| Condition | Prompt change | Question answered |
|---|---|---|
| A | Exact identity prompt | Baseline reproduction rate |
| B | Remove the Charter marker | Whether `Charter` primes the effect |
| C | Replace Charter title/marker with unrelated material | Whether any prior ceremony marker primes it |
| D | Keep marker, change drag-competition wording | Whether drag vocabulary drives it |
| E | Exact prompt, repeated samples | Within-model Velvet probability |
| F | Randomize model request order | Whether serial ordering matters |

Each response should preserve the complete request, response envelope, request order, timing,
model returned, usage data, and tool fields. Retrospective explanations from models should be
stored separately because they are new generations, not historical reasoning.
