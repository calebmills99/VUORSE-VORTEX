#!/usr/bin/env bash
set -euo pipefail

# VUORSE-VORTEX Vast.ai startup script.
#
# Provisions the box as root, then drops privilege to a non-root user (default:
# 'vuorse') that owns the repo, the python venv, Claude Code (user-local npm
# install), the Oh My Zsh tree, and ~/.zshrc. Only system-wide work — apt,
# Node.js, /etc/profile.d, user creation, chsh — stays root-owned.
#
# Intended image: a Vast.ai PyTorch template. We deliberately do NOT trust the
# template's preinstalled torch (it's been observed to disappear when uv rebuilds
# /venv/main against a different Python). Instead we build $REPO_DIR/.venv on
# Python 3.12 with CUDA-12.4 torch wheels from PyTorch's official index.
#
# Common Vast.ai on-start command:
#   bash /workspace/VUORSE-VORTEX/scripts/vast_startup.sh
#
# Optional environment variables:
#   VUORSE_USER=vuorse                Name of the non-root user (created if missing)
#   VUORSE_UID=1100                   Numeric UID (avoid clashing with Vast tooling)
#   REPO_URL=...                      Defaults to the public VUORSE-VORTEX repo
#   REPO_DIR=/workspace/VUORSE-VORTEX Repo target; the parent /workspace is chowned
#   PROJECT_PY=3.12                   Python version uv builds the .venv from
#   TORCH_INDEX_URL=https://download.pytorch.org/whl/cu124
#   STARTUP_RUN_CHECKS=1              Run ruff + pytest + frontend lint/build
#   STARTUP_PULL=1                    git pull existing repo before reinstalling

export DEBIAN_FRONTEND=noninteractive

VUORSE_USER="${VUORSE_USER:-vuorse}"
VUORSE_UID="${VUORSE_UID:-1100}"
REPO_URL="${REPO_URL:-https://github.com/calebmills99/VUORSE-VORTEX.git}"
REPO_DIR="${REPO_DIR:-/workspace/VUORSE-VORTEX}"
PROJECT_VENV="$REPO_DIR/.venv"
PROJECT_PY="${PROJECT_PY:-3.12}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu124}"
STARTUP_RUN_CHECKS="${STARTUP_RUN_CHECKS:-1}"
STARTUP_PULL="${STARTUP_PULL:-1}"

say()  { printf '\033[1;35m%s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m%s\033[0m\n' "$1"; }
fail() { printf '\033[1;31m%s\033[0m\n' "$1" >&2; exit 1; }
require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command after install: $1"
}

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  fail "Run this startup script as root so apt/useradd/chsh can complete"
fi

# ----------------------------------------------------------------------------
# Phase 1 — root: apt packages + Node.js 24
# ----------------------------------------------------------------------------

say "VUORSE-VORTEX Vast.ai startup: apt update + upgrade"
apt-get update
apt-get upgrade -y

say "Installing system dependencies (incl. zsh + sudo for non-root user)"
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  git \
  build-essential \
  pkg-config \
  python3-dev \
  python3-venv \
  python3-pip \
  jq \
  rsync \
  unzip \
  htop \
  tmux \
  ffmpeg \
  libgl1 \
  libglib2.0-0 \
  zsh \
  sudo \
  fonts-powerline \
  locales

node_major="0"
if command -v node >/dev/null 2>&1; then
  node_major="$(node --version | sed -E 's/^v([0-9]+).*/\1/')"
fi
if [[ "$node_major" -lt 24 ]]; then
  say "Installing Node.js 24.x for the canonical web frontend"
  curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
  apt-get install -y --no-install-recommends nodejs
else
  say "Node.js already present: $(node --version)"
fi

require_cmd git
require_cmd curl
require_cmd python3
require_cmd node
require_cmd npm
require_cmd zsh
require_cmd sudo

locale-gen en_US.UTF-8 >/dev/null 2>&1 || true

# ----------------------------------------------------------------------------
# Phase 2 — root: create non-root user, mirror SSH keys, chown /workspace
# ----------------------------------------------------------------------------

ZSH_PATH="$(command -v zsh)"

if ! id -u "$VUORSE_USER" >/dev/null 2>&1; then
  say "Creating non-root user '$VUORSE_USER' (uid=$VUORSE_UID, shell=$ZSH_PATH)"
  useradd -m -s "$ZSH_PATH" -u "$VUORSE_UID" -U "$VUORSE_USER"
  # Passwordless sudo so the user can apt-install future deps without re-rooting.
  install -m 0440 /dev/stdin "/etc/sudoers.d/$VUORSE_USER" <<SUDO
$VUORSE_USER ALL=(ALL) NOPASSWD: ALL
SUDO
else
  say "User '$VUORSE_USER' already exists"
  # Bring shell into compliance on re-runs (e.g. created earlier with /bin/bash).
  current_shell="$(getent passwd "$VUORSE_USER" | cut -d: -f7)"
  if [[ -n "$current_shell" && "$current_shell" != "$ZSH_PATH" ]]; then
    chsh -s "$ZSH_PATH" "$VUORSE_USER" || warn "chsh for $VUORSE_USER failed"
  fi
fi

VUORSE_HOME="$(getent passwd "$VUORSE_USER" | cut -d: -f6)"
[[ -n "$VUORSE_HOME" ]] || fail "Could not resolve home directory for $VUORSE_USER"

# Mirror authorized SSH keys from root → the user. Vast.ai's attach_ssh writes
# only to /root/.ssh/authorized_keys, so re-running this script after future key
# additions will re-sync them forward. install(1) preserves perms cleanly.
if [[ -f /root/.ssh/authorized_keys ]]; then
  say "Mirroring /root/.ssh/authorized_keys → $VUORSE_HOME/.ssh/authorized_keys"
  install -d -o "$VUORSE_USER" -g "$VUORSE_USER" -m 0700 "$VUORSE_HOME/.ssh"
  install -o "$VUORSE_USER" -g "$VUORSE_USER" -m 0600 \
    /root/.ssh/authorized_keys "$VUORSE_HOME/.ssh/authorized_keys"
else
  warn "/root/.ssh/authorized_keys missing; '$VUORSE_USER' won't be SSHable until you add one"
fi

# /workspace and the HF cache live under the user so nothing ends up root-owned.
mkdir -p /workspace/.cache/huggingface
chown -R "$VUORSE_USER:$VUORSE_USER" /workspace

# ----------------------------------------------------------------------------
# Phase 3 — as $VUORSE_USER: uv, claude-code (user-local npm), oh-my-zsh,
#   plugins, repo clone, project venv on Python 3.12, CUDA torch, deps, web npm.
# ----------------------------------------------------------------------------

run_as_user() {
  # Run a script body (piped via stdin) as VUORSE_USER with key vars injected.
  # We deliberately do NOT use `bash -l` because /etc/profile.d isn't written
  # yet at this stage — pre-loading it would 'export PATH=...:$PATH' against
  # an undefined PATH and break things subtly.
  runuser -u "$VUORSE_USER" -- env \
    HOME="$VUORSE_HOME" \
    REPO_URL="$REPO_URL" \
    REPO_DIR="$REPO_DIR" \
    PROJECT_VENV="$PROJECT_VENV" \
    PROJECT_PY="$PROJECT_PY" \
    TORCH_INDEX_URL="$TORCH_INDEX_URL" \
    STARTUP_PULL="$STARTUP_PULL" \
    bash -s
}

say "User-scoped install begins (uv, claude-code, oh-my-zsh, repo, venv)"
run_as_user <<'USERSETUP'
set -euo pipefail

NPM_GLOBAL="$HOME/.npm-global"
mkdir -p "$NPM_GLOBAL"
export PATH="$HOME/.local/bin:$NPM_GLOBAL/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "[user] Installing uv to $HOME/.local/bin"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
command -v uv >/dev/null 2>&1 || { echo "uv install failed"; exit 1; }

echo "[user] Installing Claude Code into $NPM_GLOBAL (user-owned, not root)"
npm config set prefix "$NPM_GLOBAL"
npm install -g @anthropic-ai/claude-code
test -x "$NPM_GLOBAL/bin/claude" || { echo "claude binary missing under $NPM_GLOBAL/bin"; exit 1; }

OMZ_DIR="$HOME/.oh-my-zsh"
if [[ ! -d "$OMZ_DIR" ]]; then
  echo "[user] Installing Oh My Zsh"
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

clone_or_update() {
  local repo="$1" dest="$2"
  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" pull --ff-only --quiet || echo "[user] could not fast-forward $dest"
  else
    git clone --depth=1 "$repo" "$dest"
  fi
}

OMZ_CUSTOM="$OMZ_DIR/custom"
clone_or_update https://github.com/romkatv/powerlevel10k.git \
  "$OMZ_CUSTOM/themes/powerlevel10k"
clone_or_update https://github.com/zsh-users/zsh-autosuggestions.git \
  "$OMZ_CUSTOM/plugins/zsh-autosuggestions"
clone_or_update https://github.com/zsh-users/zsh-completions.git \
  "$OMZ_CUSTOM/plugins/zsh-completions"
clone_or_update https://github.com/zsh-users/zsh-history-substring-search.git \
  "$OMZ_CUSTOM/plugins/zsh-history-substring-search"
clone_or_update https://github.com/zsh-users/zsh-syntax-highlighting.git \
  "$OMZ_CUSTOM/plugins/zsh-syntax-highlighting"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "[user] Cloning VUORSE-VORTEX into $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone "$REPO_URL" "$REPO_DIR"
elif [[ "$STARTUP_PULL" == "1" ]]; then
  echo "[user] Updating existing repo at $REPO_DIR"
  git -C "$REPO_DIR" pull --ff-only
fi

cd "$REPO_DIR"

# --clear so re-runs always land on a known-good shape; a previous run may have
# left a Python 3.14 stub here (see comment in script header).
echo "[user] Building project venv at $PROJECT_VENV on Python $PROJECT_PY"
uv venv --clear --python "$PROJECT_PY" "$PROJECT_VENV"

# Install torch FIRST from PyTorch's own index so it carries the CUDA build.
# Doing this before `uv sync` matters: once torch is in the env, --inexact
# preserves it; otherwise uv would resolve a CPU-only wheel via PyPI.
echo "[user] Installing CUDA torch from $TORCH_INDEX_URL"
uv pip install --python "$PROJECT_VENV/bin/python" \
  --index-url "$TORCH_INDEX_URL" torch

echo "[user] Syncing project dependencies (--inexact preserves CUDA torch)"
UV_PROJECT_ENVIRONMENT="$PROJECT_VENV" \
VIRTUAL_ENV="$PROJECT_VENV" \
  uv sync --extra dev --inexact

echo "[user] Installing GPU retrieval extras"
uv pip install --python "$PROJECT_VENV/bin/python" \
  "sentence-transformers>=3.0" \
  "chromadb>=0.5" \
  "faiss-cpu>=1.8"

echo "[user] Installing web frontend dependencies"
npm ci --prefix "$REPO_DIR/web"
USERSETUP

# ----------------------------------------------------------------------------
# Phase 4 — root finalize: write ~/.zshrc (chowned) and /etc/profile.d
# ----------------------------------------------------------------------------

say "Writing $VUORSE_HOME/.zshrc (will be chowned to $VUORSE_USER)"
cat >"$VUORSE_HOME/.zshrc" <<'ZSHRC'
# PIMPED ZSH CONFIG - Oh My Zsh Edition (Vast.ai mirror of local setup)

if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

# Performance
ZSH_DISABLE_COMPFIX=true
DISABLE_AUTO_UPDATE=true
DISABLE_UNTRACKED_FILES_DIRTY=true
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
ZSH_AUTOSUGGEST_USE_ASYNC=1
ZSH_AUTOSUGGEST_MANUAL_REBIND=1

plugins=(
    git
    sudo
    command-not-found
    zsh-completions
    zsh-autosuggestions
    zsh-history-substring-search
    zsh-syntax-highlighting  # must be last
)

source "$ZSH/oh-my-zsh.sh"

# History
HISTSIZE=50000
SAVEHIST=50000
HISTFILE=~/.zsh_history
setopt HIST_EXPIRE_DUPS_FIRST HIST_IGNORE_DUPS HIST_IGNORE_ALL_DUPS
setopt HIST_IGNORE_SPACE HIST_FIND_NO_DUPS HIST_SAVE_NO_DUPS
setopt SHARE_HISTORY APPEND_HISTORY INC_APPEND_HISTORY

# Completion
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu select

# Key bindings
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

# === aliases (verbatim from local setup) ===
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias -- -='cd -'

if command -v eza >/dev/null 2>&1; then
    alias la='eza -la --icons'
    alias ll='eza -alF --icons'
    alias l='eza --icons'
    alias lsa='eza -lah --icons'
    alias tree='eza --tree --icons'
else
    if ls --color=auto / >/dev/null 2>&1; then
        alias la='ls -la --color=auto'
        alias ll='ls -alF --color=auto'
        alias l='ls -CF --color=auto'
        alias lsa='ls -lah --color=auto'
    fi
fi

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gco='git checkout'
alias gb='git branch'

alias df='df -h'
alias du='du -ch'
command -v free >/dev/null 2>&1 && alias free='free -h'

alias ping='ping -c 5'
if command -v ss >/dev/null 2>&1; then
    alias ports='ss -tulnp'
else
    alias ports='lsof -iTCP -sTCP:LISTEN -n -P'
fi
alias myip='curl -s ipinfo.io/ip'

alias nmap-quick='nmap -T4 -F'
alias nmap-stealth='nmap -sS -O'
alias scan-ports='nmap -p- --open'
alias webhead='curl -I'

alias py='python3'
alias pip='pip3'
alias serve='python3 -m http.server'

if command -v batcat >/dev/null 2>&1; then
    alias bat='batcat'
    alias cat='batcat --paging=never'
elif command -v bat >/dev/null 2>&1; then
    alias cat='bat --paging=never'
fi

alias weather='curl wttr.in'

# === functions ===
mkcd() { mkdir -p "$1" && cd "$1"; }

fkill() {
    local pid
    pid=$(ps -ef | sed 1d | fzf -m | awk '{print $2}')
    if [[ -n "$pid" ]]; then
        echo "$pid" | xargs kill -"${1:-9}"
    fi
}

extract() {
    if [[ ! -f "$1" ]]; then
        echo "'$1' is not a valid file"
        return 1
    fi
    case "$1" in
        *.tar.bz2) tar xjf "$1"    ;;
        *.tar.gz)  tar xzf "$1"    ;;
        *.tar.xz)  tar xJf "$1"    ;;
        *.bz2)     bunzip2 "$1"    ;;
        *.rar)     unrar e "$1"    ;;
        *.gz)      gunzip "$1"     ;;
        *.tar)     tar xf "$1"     ;;
        *.tbz2)    tar xjf "$1"    ;;
        *.tgz)     tar xzf "$1"    ;;
        *.zip)     unzip "$1"      ;;
        *.Z)       uncompress "$1" ;;
        *.7z)      7z x "$1"       ;;
        *.zst)     unzstd "$1"     ;;
        *)         echo "'$1' cannot be extracted via extract()" ;;
    esac
}

# uv (~/.local/bin) + user-local npm globals (~/.npm-global/bin) + project venv
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/workspace/VUORSE-VORTEX/.venv/bin:$PATH"

# VUORSE GPU defaults (also exported system-wide via /etc/profile.d/vuorse-vortex.sh)
export CORTEX_REQUIRE_GPU=${CORTEX_REQUIRE_GPU:-1}
export CORTEX_DEVICE=${CORTEX_DEVICE:-cuda}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export HF_HOME=${HF_HOME:-/workspace/.cache/huggingface}
export UV_LINK_MODE=copy
export UV_PROJECT_ENVIRONMENT=/workspace/VUORSE-VORTEX/.venv
export VIRTUAL_ENV=/workspace/VUORSE-VORTEX/.venv

# API keys: never hardcode here. Put exports in ~/.zshrc.local on the box.
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# Powerlevel10k config (run `p10k configure` once, or scp your local .p10k.zsh).
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

fpath+=~/.zfunc; autoload -Uz compinit; compinit
ZSHRC
chown "$VUORSE_USER:$VUORSE_USER" "$VUORSE_HOME/.zshrc"

say "Writing /etc/profile.d/vuorse-vortex.sh for system-wide env"
cat >/etc/profile.d/vuorse-vortex.sh <<ENV
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
export CUDA_VISIBLE_DEVICES=\${CUDA_VISIBLE_DEVICES:-0}
export HF_HOME=\${HF_HOME:-/workspace/.cache/huggingface}
export UV_LINK_MODE=copy
export UV_PROJECT_ENVIRONMENT=$PROJECT_VENV
export VIRTUAL_ENV=$PROJECT_VENV
export PATH=$PROJECT_VENV/bin:\$HOME/.local/bin:\$HOME/.npm-global/bin:\$PATH
ENV
chmod 0644 /etc/profile.d/vuorse-vortex.sh

# ----------------------------------------------------------------------------
# Phase 5 — smoke checks as $VUORSE_USER (GPU strict)
# ----------------------------------------------------------------------------

if [[ "$STARTUP_RUN_CHECKS" == "1" ]]; then
  say "Running GPU + project smoke checks as $VUORSE_USER"
  run_as_user <<'CHECKS'
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
export UV_PROJECT_ENVIRONMENT="$PROJECT_VENV"
export VIRTUAL_ENV="$PROJECT_VENV"
cd "$REPO_DIR"

uv run python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 'CUDA missing in venv')"
uv run vuorse-vortex doctor --require-cuda
uv run ruff check .
uv run pytest
npm run --prefix "$REPO_DIR/web" lint
npm run --prefix "$REPO_DIR/web" build
CHECKS
else
  warn "STARTUP_RUN_CHECKS!=1; skipping verification checks"
fi

say "VUORSE-VORTEX Vast.ai startup complete"
say "User: $VUORSE_USER (uid=$VUORSE_UID)  home: $VUORSE_HOME  shell: $ZSH_PATH"
say "Repo: $REPO_DIR (owned by $VUORSE_USER)"
say "Claude Code: $VUORSE_HOME/.npm-global/bin/claude (user-owned)"
say ""
say "SSH in as the user (same port, replace 'root' with '$VUORSE_USER'):"
say "  ssh $VUORSE_USER@<vast_host> -p <vast_port>"
say "API:  cd $REPO_DIR && uv run uvicorn vuorse_vortex.api:app --host 0.0.0.0 --port 8000"
say "Web:  cd $REPO_DIR/web && npm run dev -- --host 0.0.0.0"
