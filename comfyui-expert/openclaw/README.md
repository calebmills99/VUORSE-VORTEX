# OpenClaw WSL Adapter

This repository runs as a separate OpenClaw agent. The existing `main` agent and
its workspace remain untouched.

## Verified Local Layout

| Component | Path |
|---|---|
| WSL distribution | `OpenClawGateway` |
| OpenClaw home | `/home/openclaw/.openclaw` |
| Repository | `/mnt/c/runb2/ComfyUI-Expert` |
| OpenClaw workspace | `/mnt/c/runb2/ComfyUI-Expert/openclaw` |
| Repository skills | `/mnt/c/runb2/ComfyUI-Expert/skills` |
| ComfyUI | `/mnt/d/ComfyUI312/comfyui` |
| ComfyUI API | `http://127.0.0.1:8188` |

## One-Time WSL Mount Setup

`OpenClawGateway` currently disables Windows-drive automounting. This Windows
PowerShell command changes only that block:

```powershell
wsl.exe -d OpenClawGateway -u root -- bash -lc "sed -i '/^\[automount\]/,/^\[/{s/^enabled=false`$/enabled=true/;s/^mountFsTab=false`$/mountFsTab=true/;}' /etc/wsl.conf"
```

The resulting block is:

```ini
[automount]
enabled=true
mountFsTab=true
```

Restart WSL from Windows after changing it:

```powershell
wsl.exe --shutdown
wsl.exe -d OpenClawGateway
```

## Configure VideoAgent

Run inside `OpenClawGateway`:

```bash
bash /mnt/c/runb2/ComfyUI-Expert/openclaw/setup-wsl.sh
```

The script:

- creates an isolated `video-agent`
- uses `openclaw/` as its workspace so adapter links remain valid
- loads all repository skills directly from `skills/`
- sets `COMFYUI_URL` and the WSL-visible `COMFYUI_PATH`
- validates the active OpenClaw configuration
- restarts the existing gateway service

## Model Authentication

The installed OpenClaw currently defaults to `openai/gpt-5.5`. Authenticate the
provider from the WSL terminal:

```bash
openclaw models auth --agent video-agent login --provider openai --device-code
```

## Validate

```bash
openclaw config validate
openclaw models --agent video-agent status
openclaw skills list --agent video-agent
openclaw agent --agent video-agent --message "Read the canon and report readiness."
```

The ComfyUI connection can be checked after ComfyUI is running:

```bash
curl -fsS http://127.0.0.1:8188/system_stats
```
