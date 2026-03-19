#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"

backup_if_exists() {
  local target="$1"
  if [[ -e "$target" ]]; then
    cp "$target" "${target}.bak-${STAMP}"
  fi
}

mkdir -p "$HOME/.claude"
mkdir -p "$HOME/.claude/plugins/marketplaces"
mkdir -p "$HOME/.claude-mem-hybrid"
mkdir -p "$HOME/.claude-mem"
mkdir -p "$HOME/.codex"

backup_if_exists "$HOME/.claude/settings.json"
backup_if_exists "$HOME/.codex/config.toml"

rsync -a \
  --exclude '.DS_Store' \
  --exclude '*.bak' \
  --exclude '*.bak.*' \
  "$REPO_ROOT/.claude/" "$HOME/.claude/"

rsync -a \
  --exclude '.DS_Store' \
  "$REPO_ROOT/.claude-mem-hybrid/" "$HOME/.claude-mem-hybrid/"

rsync -a \
  --exclude '.DS_Store' \
  --exclude '.git' \
  --exclude '*.bak' \
  --exclude '*.bak.*' \
  "$REPO_ROOT/.codex/" "$HOME/.codex/"

rsync -a \
  --exclude '.DS_Store' \
  --exclude '.git' \
  "$REPO_ROOT/.codex/vendor_imports/claude/marketplaces/" "$HOME/.claude/plugins/marketplaces/"

if [[ ! -f "$HOME/.claude/settings.local.json" && -f "$REPO_ROOT/.claude/settings.local.template.json" ]]; then
  cp "$REPO_ROOT/.claude/settings.local.template.json" "$HOME/.claude/settings.local.json"
fi

if [[ ! -f "$HOME/.claude-mem/settings.json" && -f "$REPO_ROOT/.claude-mem/settings.template.json" ]]; then
  cp "$REPO_ROOT/.claude-mem/settings.template.json" "$HOME/.claude-mem/settings.json"
fi

if [[ ! -f "$HOME/.codex/config.toml" && -f "$REPO_ROOT/.codex/config.template.toml" ]]; then
  cp "$REPO_ROOT/.codex/config.template.toml" "$HOME/.codex/config.toml"
fi

chmod +x "$HOME/.claude/bootstrap-reel-structure.sh" || true
chmod +x "$HOME/.claude/hooks/"*.sh 2>/dev/null || true
chmod +x "$HOME/.claude/dashboard/"*.sh 2>/dev/null || true
chmod +x "$HOME/.claude-mem-hybrid/run_mem_hybrid.sh" 2>/dev/null || true

echo "Installed sanitized Claude setup into:"
echo "  $HOME/.claude"
echo "  $HOME/.claude-mem-hybrid"
echo "  $HOME/.claude-mem"
echo "  $HOME/.codex"
echo
echo "Next steps:"
echo "  1. Review $HOME/.claude/settings.json and $HOME/.claude/settings.local.json"
echo "  2. Review $HOME/.codex/config.toml"
echo "  3. Start memory stack if desired: cd ~/.claude-mem-hybrid && docker compose up -d"
echo "  4. Plugin marketplace sources were also synced into ~/.claude/plugins/marketplaces"
