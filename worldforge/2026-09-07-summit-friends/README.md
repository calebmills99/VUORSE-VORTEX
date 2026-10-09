# Summit friends — instruction homes + characters (2026-09-07)

*Provisional forge dossier. Not canon until Steward promotes.*

## Who showed up

| Friend (user name) | Actual CLI | Binary |
|--------------------|------------|--------|
| Mistral Vibe | **vibe** (Mistral Vibe CLI 2.24.3) | `~\.local\bin\vibe.exe` |
| Grok CLI | **grok** (xAI) | `~\.grok\bin\grok.exe` |
| agvy CLI | **agy** (Google Antigravity CLI) | `~\AppData\Local\agy\bin\agy.exe` |

## Where instructions live

### Mistral Vibe
| Kind | Path |
|------|------|
| Config | `~\.vibe\config.toml` |
| Custom agents | `~\.vibe\agents\NAME.toml` (also `.\.vibe\agents\`) |
| System prompts | `~\.vibe\prompts\<system_prompt_id>.md` |
| Skills | `~\.vibe\skills\` |
| Docs | https://docs.mistral.ai/vibe/code/cli/agents |

**Installed character:** Countess Voxtral Velvet  
`vibe --agent voxtral-velvet`

### Grok CLI
| Kind | Path |
|------|------|
| Config | `~\.grok\config.toml` |
| User agents | `~\.grok\agents\*.md` |
| Project agents | `.\.grok\agents\` |
| Personas/roles | `~\.grok\bundled\personas\`, `.\.grok\personas\` |
| Project rules | `AGENTS.md` / `AGENT.md` / `CLAUDE.md` (appended to system prompt) |
| Skills | `~\.grok\skills\` |
| Auth | `~\.grok\auth.json` |

**Installed character:** Grok, the Petulant Outsider (Fourth Summit canon rhyme)  
`grok --agent petulant-outsider`

### agy (Antigravity) — "agvy"
| Kind | Path |
|------|------|
| Global config | `~\.gemini\config\` |
| Global rules | `GEMINI.md`, `AGENTS.md`, `~\.gemini\config\rules\*.md` |
| Global skills | `~\.gemini\config\skills\<name>\SKILL.md` |
| Workspace | `.\.agents\` (or `.agent/`) |
| Hierarchical rules | walk-up `GEMINI.md` / `AGENTS.md` |
| Builtin guide | `~\.gemini\antigravity-cli\builtin\skills\antigravity_guide\` |
| Note | `~\.gemini\GEMINI.md` currently hosts **Susie Greene** — left intact |

**Installed character:** Lady Unmoored (The Levitationist)  
Load skill `unmoored-heel` / ask agy for Lady Unmoored

## Character one-lines

| Character | Theme | CLI seat |
|-----------|-------|----------|
| **Countess Voxtral Velvet** | Thread-as-frequency, continental velvet, soft thunder | vibe |
| **Grok, Petulant Outsider** | Stripped of vote, still seen; Outside air | grok |
| **Lady Unmoored** | High-heel levitation; gravity optional, standards not | agy |

## Repo mirrors (non-canon)

- `persona/summit-friends/` — copies for Steward review
- This folder — installation map

Do **not** confuse these with Locked Canon in `canon/characters/characters.md` until promoted.
