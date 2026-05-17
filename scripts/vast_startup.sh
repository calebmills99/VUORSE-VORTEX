#!/usr/bin/env bash
set -euo pipefail

# VUORSE-VORTEX Vast.ai startup script.
#
# Intended image: a Vast.ai PyTorch template with CUDA + torch already installed.
# This script deliberately does not install torch. It installs OS/runtime tooling,
# prepares the repo, installs project dependencies, and runs smoke checks.
#
# Common Vast.ai on-start command:
#   bash /workspace/VUORSE-VORTEX/scripts/vast_startup.sh
#
# Optional environment variables:
#   REPO_URL=https://github.com/calebmills99/VUORSE-VORTEX.git
#   REPO_DIR=/workspace/VUORSE-VORTEX
#   STARTUP_RUN_CHECKS=1
#   STARTUP_PULL=1

export DEBIAN_FRONTEND=noninteractive

REPO_URL="${REPO_URL:-https://github.com/calebmills99/VUORSE-VORTEX.git}"
REPO_DIR="${REPO_DIR:-/workspace/VUORSE-VORTEX}"
STARTUP_RUN_CHECKS="${STARTUP_RUN_CHECKS:-1}"
STARTUP_PULL="${STARTUP_PULL:-1}"

say() {
  printf '\033[1;35m%s\033[0m\n' "$1"
}

warn() {
  printf '\033[1;33m%s\033[0m\n' "$1"
}

fail() {
  printf '\033[1;31m%s\033[0m\n' "$1" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command after install: $1"
}

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  fail "Run this startup script as root so apt update/upgrade can complete"
fi

say "VUORSE-VORTEX Vast.ai startup: apt update + upgrade"
apt-get update
apt-get upgrade -y

say "Installing system dependencies"
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

if ! command -v uv >/dev/null 2>&1; then
  say "Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

export PATH="$HOME/.local/bin:$PATH"
require_cmd uv

say "Installing Claude Code CLI"
npm install -g @anthropic-ai/claude-code
require_cmd claude

# ----------------------------------------------------------------------------
# Oh My Zsh + Powerlevel10k + custom plugins (mirrors the user's local setup)
# ----------------------------------------------------------------------------
ZSH_USER_HOME="${ZSH_USER_HOME:-$HOME}"
OMZ_DIR="$ZSH_USER_HOME/.oh-my-zsh"
OMZ_CUSTOM="$OMZ_DIR/custom"

if [[ ! -d "$OMZ_DIR" ]]; then
  say "Installing Oh My Zsh"
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
  say "Oh My Zsh already present at $OMZ_DIR"
fi

clone_or_update() {
  local repo="$1" dest="$2"
  if [[ -d "$dest/.git" ]]; then
    git -C "$dest" pull --ff-only --quiet || warn "Could not fast-forward $dest"
  else
    git clone --depth=1 "$repo" "$dest"
  fi
}

say "Installing Powerlevel10k theme"
clone_or_update https://github.com/romkatv/powerlevel10k.git \
  "$OMZ_CUSTOM/themes/powerlevel10k"

say "Installing zsh custom plugins (autosuggestions, completions, history-substring-search, syntax-highlighting)"
clone_or_update https://github.com/zsh-users/zsh-autosuggestions.git \
  "$OMZ_CUSTOM/plugins/zsh-autosuggestions"
clone_or_update https://github.com/zsh-users/zsh-completions.git \
  "$OMZ_CUSTOM/plugins/zsh-completions"
clone_or_update https://github.com/zsh-users/zsh-history-substring-search.git \
  "$OMZ_CUSTOM/plugins/zsh-history-substring-search"
clone_or_update https://github.com/zsh-users/zsh-syntax-highlighting.git \
  "$OMZ_CUSTOM/plugins/zsh-syntax-highlighting"

say "Writing ~/.zshrc to mirror local Oh My Zsh setup"
cat >"$ZSH_USER_HOME/.zshrc" <<'ZSHRC'
# PIMPED ZSH CONFIG - Oh My Zsh Edition (Vast.ai mirror of local setup)

# Powerlevel10k instant prompt
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

# ==============================================================================
# PRODUCTIVITY ENHANCEMENTS
# ==============================================================================

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

# ==============================================================================
# ALIASES
# ==============================================================================

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias -- -='cd -'

# Listing (use eza if available, fall back to ls)
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
    else
        # BSD ls (macOS)
        alias la='ls -laG'
        alias ll='ls -alFG'
        alias l='ls -CFG'
        alias lsa='ls -lahG'
    fi
fi

# Safety nets
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

# Git shortcuts
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gco='git checkout'
alias gb='git branch'

# System monitoring
alias df='df -h'
alias du='du -ch'
command -v free >/dev/null 2>&1 && alias free='free -h'

# Network
alias ping='ping -c 5'
if command -v ss >/dev/null 2>&1; then
    alias ports='ss -tulnp'
else
    alias ports='lsof -iTCP -sTCP:LISTEN -n -P'
fi
alias myip='curl -s ipinfo.io/ip'

# Recon / pentesting
alias nmap-quick='nmap -T4 -F'
alias nmap-stealth='nmap -sS -O'
alias scan-ports='nmap -p- --open'
alias webhead='curl -I'

# Development
alias py='python3'
alias pip='pip3'
alias serve='python3 -m http.server'

# Use bat if available (Ubuntu names it 'batcat', macOS/brew uses 'bat')
if command -v batcat >/dev/null 2>&1; then
    alias bat='batcat'
    alias cat='batcat --paging=never'
elif command -v bat >/dev/null 2>&1; then
    alias cat='bat --paging=never'
fi

# Fun
alias weather='curl wttr.in'

# ==============================================================================
# FUNCTIONS
# ==============================================================================

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

# uv + project tooling on PATH
export PATH="$HOME/.local/bin:$PATH"

# VUORSE GPU defaults (sourced from /etc/profile.d/vuorse-vortex.sh as well)
export CORTEX_REQUIRE_GPU=${CORTEX_REQUIRE_GPU:-1}
export CORTEX_DEVICE=${CORTEX_DEVICE:-cuda}
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export HF_HOME=${HF_HOME:-/workspace/.cache/huggingface}
export UV_LINK_MODE=copy

# API keys: do NOT hardcode in the committed startup script.
# Put exports into ~/.zshrc.local on the Vast instance (sourced below).
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local

# Powerlevel10k config
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

fpath+=~/.zfunc; autoload -Uz compinit; compinit
ZSHRC

# Make zsh the default shell for this user so future SSH sessions land in it
if command -v chsh >/dev/null 2>&1; then
  current_shell="$(getent passwd "$(id -un)" | cut -d: -f7 || true)"
  zsh_path="$(command -v zsh)"
  if [[ -n "$zsh_path" && "$current_shell" != "$zsh_path" ]]; then
    chsh -s "$zsh_path" "$(id -un)" || warn "chsh to zsh failed; set manually with: chsh -s $zsh_path"
  fi
fi

say "Writing VUORSE GPU environment defaults"
cat >/etc/profile.d/vuorse-vortex.sh <<'ENV'
export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export HF_HOME=${HF_HOME:-/workspace/.cache/huggingface}
export UV_LINK_MODE=copy
ENV

export CORTEX_REQUIRE_GPU=1
export CORTEX_DEVICE=cuda
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
export UV_LINK_MODE=copy

mkdir -p /workspace/.cache/huggingface

if [[ ! -d "$REPO_DIR/.git" ]]; then
  say "Cloning VUORSE-VORTEX into $REPO_DIR"
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone "$REPO_URL" "$REPO_DIR"
elif [[ "$STARTUP_PULL" == "1" ]]; then
  say "Updating existing repo at $REPO_DIR"
  git -C "$REPO_DIR" pull --ff-only
else
  warn "Repo exists and STARTUP_PULL!=1; skipping git pull"
fi

cd "$REPO_DIR"

say "Creating project virtualenv with access to PyTorch template packages"
uv venv --system-site-packages .venv

say "Installing Python project dependencies without reinstalling torch"
uv sync --extra dev
uv pip install \
  "sentence-transformers>=3.0" \
  "chromadb>=0.5" \
  "faiss-cpu>=1.8"

say "Installing canonical web frontend dependencies"
npm ci --prefix web

if [[ "$STARTUP_RUN_CHECKS" == "1" ]]; then
  say "Running GPU and project smoke checks"
  uv run python - <<'PY'
import torch

if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable in the PyTorch template")

print("CUDA available:", torch.cuda.get_device_name(0))
PY

  uv run vuorse-vortex doctor --require-cuda
  uv run ruff check .
  uv run mypy src
  uv run pytest
  npm run --prefix web lint
  npm run --prefix web build
else
  warn "STARTUP_RUN_CHECKS!=1; skipping verification checks"
fi

say "VUORSE-VORTEX Vast.ai startup complete"
say "Repo: $REPO_DIR"
say "API:  cd $REPO_DIR && uv run uvicorn vuorse_vortex.api:app --host 0.0.0.0 --port 8000"
say "Web:  cd $REPO_DIR/web && npm run dev -- --host 0.0.0.0"
