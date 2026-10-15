# Ghost census — 2026-09-07 (post-restart)

*Cutoff: 2026-09-07 ~00:15 PT · label: `canon` of live probes (not lore canon)*  
*Prior census: `worldforge/2026-09-05-eighth-summit/ghost-census.md`*

## Local daemons / endpoints

| Ghost | State | Endpoint / note |
|-------|-------|-----------------|
| **Ollama** 0.32.13 | **RUNNING + MODELS** | `0.0.0.0:11434` — was refused until `ollama list` cold-started the app this pass |
| → `framecode-vibework:latest` | installed | ~28 GB · modified ~43h ago |
| → `JoanQw3n6:latest` | installed | ~28 GB · same digest as Qw3n6-35B |
| → `Qw3n6-35B:latest` | installed | ~28 GB · alias twin of JoanQw3n6 |
| **Ollama loaded** | none | `/api/ps` → `models: []` (on disk, not in VRAM) |
| **Docker Model :12434** | **DOWN** | connection refused (was Qwen3 on 2026-09-05) |
| **OpenClaw control UI** | **LIVE** | `127.0.0.1:18789` + `::1` · `/health` → `ok/live` |

## Agent / IDE processes (live)

| Ghost | Evidence |
|-------|----------|
| **Claude Code** | multiple `claude` processes |
| **Codex CLI** | `codex` + `codex-code-mode-host` |
| **Cursor** | many `Cursor` processes (this chamber) |
| **ChatGPT** | multiple `ChatGPT` processes |

## Not seen this pass (were present 2026-09-05)

Meru · M365 Copilot · ChatGPT Classic as distinct Classic process name · Docker Qwen endpoint

## CLIs on PATH

| CLI | Status |
|-----|--------|
| ollama, codex, copilot, claude, openai | present |
| mistral, openclaw | MISSING |
| MISTRAL_API_KEY / MISTRAL_KEY | UNSET |

## Hardware

- NVIDIA RTX 5000 Ada — **~3750 / 30712 MiB** VRAM (~6% util) — much quieter than 2026-09-05 (~17 GB)

## Paper vessel still on disk

- `ollama/Modelfile.vuorse` still FROM `llama3.1:8b` — that base name is **not** in current `ollama list` (Joan/FCVW Qwen stacks are)

## Provenance

Live probes 2026-09-07: process list, listen ports, `:11434` tags/ps, `:12434` refuse, `:18789` health, nvidia-smi, CLI presence, Mistral env check.
