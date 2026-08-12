#!/usr/bin/env bash
# setup-claude-env.sh — give every Claude Code account the same environment.
#
# Idempotent. Applies settings.base.json to each account's settings.json
# (pointing hooks + status line at this repo), and writes the managed ~/.zshrc
# block with the helper aliases. Per-account keys not present in the base are
# preserved, so a UI preference set on one account survives.
#
# See CLAUDE_ENV_SETUP.md for the why. Edit the ACCOUNTS array below, then run.
#
#   ./setup-claude-env.sh              apply
#   ./setup-claude-env.sh --dry-run    show what would change
set -euo pipefail

# ── CONFIG ────────────────────────────────────────────────────────────────────
# One line per account:  label | claude-config-dir
# Must mirror the ACCOUNTS array in runners/ralph/setup-multi-account.sh —
# that script routes accounts per project, this one makes them look alike.
ACCOUNTS=(
  "personal|~/.claude"
  "shopstack|~/.claude-shopstack"
)
ZSHRC="${ZSHRC:-$HOME/.zshrc}"
# ──────────────────────────────────────────────────────────────────────────────

HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="$HERE/settings.base.json"
SENTINEL_BEGIN="# >>> agent-toolkit claude-env >>>"
SENTINEL_END="# <<< agent-toolkit claude-env <<<"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

expand() { echo "${1/#\~/$HOME}"; }
say() { printf '\033[1;34m[claude-env]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[claude-env]\033[0m %s\n' "$*"; }

[[ -f "$BASE" ]] || { warn "missing $BASE"; exit 1; }

# ── Preflight ─────────────────────────────────────────────────────────────────
# Everything installed here shells out to something. Check up front, so a fresh
# machine fails with a name to install rather than a status line that silently
# renders half its segments.
missing=0
for dep in python3 jq lsof; do
  command -v "$dep" >/dev/null 2>&1 && continue
  case "$dep" in
    python3) why="settings merge + hooks" ;;
    jq)      why="status line payload parsing" ;;
    lsof)    why="port and log-file lookup in claude-bg/devports" ;;
  esac
  warn "missing required: $dep — $why"
  missing=1
done
[[ "$missing" -eq 1 ]] && exit 1
# Optional: the setup is valid without these, only some features go quiet.
command -v codex >/dev/null 2>&1 || warn "codex not on PATH — the review hooks will no-op until it is installed"
command -v open  >/dev/null 2>&1 || warn "no \`open\` command — \`cbg open\` will not launch a browser"

chmod +x "$HERE"/statusline.sh "$HERE"/bin/* "$HERE"/hooks/*.sh 2>/dev/null || true

# 1. Settings for each account -------------------------------------------------
for row in "${ACCOUNTS[@]}"; do
  IFS='|' read -r label cdir <<<"$row"
  dir="$(expand "$cdir")"
  if [[ ! -d "$dir" ]]; then
    warn "$label: $dir does not exist — run \`claude\` once with CLAUDE_CONFIG_DIR=$dir first, then re-run"
    continue
  fi

  target="$dir/settings.json"
  merged="$(HERE="$HERE" BASE="$BASE" TARGET="$target" python3 <<'PY'
import json, os

base = json.load(open(os.environ["BASE"]))
# Placeholder keeps the base file portable — the repo can live anywhere.
base = json.loads(json.dumps(base).replace("__CLAUDE_ENV__", os.environ["HERE"]))

target = os.environ["TARGET"]
try:
    with open(target) as fh:
        current = json.load(fh)
except (FileNotFoundError, json.JSONDecodeError):
    current = {}

# Base is the source of truth for shared keys; anything else the account set
# for itself (UI prefs, per-account permissions) is left alone.
merged = {**current, **base}
print(json.dumps(merged, indent=2) + "\n")
PY
)"

  if [[ -f "$target" ]] && diff -q <(printf '%s\n' "$merged") "$target" >/dev/null 2>&1; then
    say "$label: settings already in sync"
    continue
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    say "$label: would update $target"
    [[ -f "$target" ]] && diff <(printf '%s\n' "$merged") "$target" | sed 's/^/    /' || true
    continue
  fi

  [[ -f "$target" ]] && cp "$target" "$target.bak"
  printf '%s\n' "$merged" > "$target"
  say "$label: wrote $target (backup: settings.json.bak)"
done

# 2. Managed ~/.zshrc block ----------------------------------------------------
new_block="$(cat <<EOF
$SENTINEL_BEGIN
# Detail views behind the Claude Code status line segments.
alias cbg="$HERE/bin/claude-bg"       # agent-started background tasks + logs
alias devports="$HERE/bin/devports"   # every local dev server, agent or not
$SENTINEL_END
EOF
)"

if [[ ! -f "$ZSHRC" ]]; then
  warn "$ZSHRC not found — skipping aliases"
elif grep -qF "$SENTINEL_BEGIN" "$ZSHRC"; then
  current_block="$(sed -n "/$SENTINEL_BEGIN/,/$SENTINEL_END/p" "$ZSHRC")"
  if [[ "$current_block" == "$new_block" ]]; then
    say "zshrc: no changes"
  elif [[ "$DRY_RUN" == "true" ]]; then
    say "zshrc: would update managed block"
    echo "$new_block" | sed 's/^/    /'
  else
    tmp="$(mktemp)"; new_tmp="$(mktemp)"
    echo "$new_block" > "$new_tmp"
    awk -v begin="$SENTINEL_BEGIN" -v end="$SENTINEL_END" -v newfile="$new_tmp" '
      $0 == begin { while ((getline line < newfile) > 0) print line; close(newfile); skip=1; next }
      $0 == end { skip=0; next }
      !skip { print }
    ' "$ZSHRC" > "$tmp"
    mv "$tmp" "$ZSHRC"; rm -f "$new_tmp"
    say "zshrc: updated managed block"
  fi
elif [[ "$DRY_RUN" == "true" ]]; then
  say "zshrc: would append managed block"
  echo "$new_block" | sed 's/^/    /'
else
  printf '\n%s\n' "$new_block" >> "$ZSHRC"
  say "zshrc: appended managed block"
fi

say "done — open a new session for settings to apply, and \`source $ZSHRC\` for aliases"
