# Ghost census — Eighth Galactic Summit

*Cutoff: 2026-09-05 · label: `canon` of live probes (not lore canon)*

## Local daemons / endpoints

| Ghost | State | Endpoint / note |
|-------|-------|-----------------|
| **Ollama** 0.32.13 | RUNNING (empty) | `0.0.0.0:11434` — `/api/tags` → `models: []`; `ollama ps` empty |
| **Docker Model Runner** (ollama-compat) | RUNNING | `127.0.0.1:12434` — `docker.io/ai/qwen3:latest` (8.19B, IQ2/Q4) |
| **OpenClaw control UI** | LIVE | `127.0.0.1:18789` (+ `::1`) via `wslrelay`; `/health` → `{"ok":true,"status":"live"}` |
| **Docker Desktop backend** | RUNNING | owns :12434 path; Docker service StartType Manual but backend process up |
| **VUORSE Modelfile** | ON DISK ONLY | `ollama/Modelfile.vuorse` FROM `llama3.1:8b` — base not in Ollama |

## Agent / IDE processes (live)

| Ghost | Evidence |
|-------|----------|
| **Claude Code** | process `claude` → `~\.local\bin\claude.exe` (v 2.1.261 CLI) |
| **Codex CLI** | process `codex` + `codex-code-mode-host`; CLI 0.146.1 |
| **Cursor** | many `Cursor.exe` processes (this chamber) |
| **ChatGPT Classic** | WindowsApp desktop process |
| **ChatGPT / Codex app** | `OpenAI.Codex_…\ChatGPT.exe` |
| **M365 Copilot** | `M365Copilot.exe` |
| **Meru** | `C:\Program Files\Meru\Meru.exe` |

## CLIs on PATH (may be dark)

| CLI | Path status |
|-----|-------------|
| ollama | present |
| codex | present |
| copilot | present (1.0.82) — no dedicated process caught this scan |
| claude | present |
| openai | present (1.9.0) |
| mistral | MISSING |
| lmstudio | MISSING |
| openclaw | MISSING from PATH (repo subtree exists) |

## Cloud key *names* present in env (values not logged)

OPENAI_API_KEY, CLAUDE_API_KEY / CLAUDIA_API_KEY, GEMINI_API_KEY, VERTEX_API_KEY, AZFOUNDRY_API_KEY + endpoint, HUGGINGFACEHUB_API_TOKEN, FAL_API_KEY, CURSOR_API_KEY, plus others non-LLM. **MISTRAL_API_KEY / MISTRAL_KEY: unset.**

## Hardware

- NVIDIA RTX 5000 Ada — ~17171 / 30712 MiB VRAM in use at probe (utilization low %)

## Not found running this pass

LM Studio, standalone vLLM/textgen/Kobold, ComfyUI listen on 8188, populated native Ollama model library.

## Provenance

Live `Get-Process`, `Get-NetTCPConnection`, `Invoke-RestMethod`/`Invoke-WebRequest` to :11434/:12434/:18789, `nvidia-smi`, CLI `--version`, env name scan (lengths only), read of `ollama/Modelfile.vuorse`.
