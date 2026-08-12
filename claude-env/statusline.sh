#!/bin/sh
# Claude Code status line — inspired by Powerlevel10k (dir + vcs segments).
#
# Shared by every Claude account (personal + shopstack) so both render exactly
# the same information. Installed by setup-claude-env.sh, which points each
# account's settings.json at this file. See CLAUDE_ENV_SETUP.md.
#
# Segments: cwd + git · model │ effort │ context bar + tokens · account │ bg tasks
input=$(cat)

# Payload capture, for working out what Claude Code actually exposes. Keyed off
# a sentinel file rather than an env var, because a status line script inherits
# neither CLAUDE_CONFIG_DIR nor anything else — only COLUMNS and LINES.
#   touch ~/.claude-statusline-capture   then read $TMPDIR/cl-payload-<session>.json
if [ -f "$HOME/.claude-statusline-capture" ]; then
  printf '%s' "$input" > "${TMPDIR:-/tmp}/cl-payload-$(printf '%s' "$input" | jq -r '.session_id // "unknown"').json"
fi

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.id // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
effort=$(echo "$input" | jq -r '.effort.level // ""')
tok_used=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
tok_max=$(echo "$input" | jq -r '.context_window.context_window_size // empty')
transcript=$(echo "$input" | jq -r '.transcript_path // ""')

# Shorten home directory to ~
home="$HOME"
short_cwd=$(echo "$cwd" | sed "s|^$home|~|")

# Git branch and status (skip optional locks for safety)
git_info=""
if git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.fsmonitor=false symbolic-ref --short HEAD 2>/dev/null \
           || git -C "$cwd" -c core.fsmonitor=false rev-parse --short HEAD 2>/dev/null)
  dirty=""
  if ! git -C "$cwd" -c core.fsmonitor=false diff --quiet 2>/dev/null \
     || ! git -C "$cwd" -c core.fsmonitor=false diff --cached --quiet 2>/dev/null; then
    dirty="*"
  fi
  git_info=" \033[33m($branch$dirty)\033[0m"
fi

# Context progress bar
ctx_info=""
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  bar_width=15
  filled=$((used_int * bar_width / 100))
  if [ "$filled" -gt "$bar_width" ]; then filled=$bar_width; fi
  empty=$((bar_width - filled))
  bar=""
  i=0; while [ "$i" -lt "$filled" ]; do bar="${bar}█"; i=$((i + 1)); done
  i=0; while [ "$i" -lt "$empty" ]; do bar="${bar}░"; i=$((i + 1)); done
  if [ "$used_int" -ge 80 ]; then
    color="31"
  elif [ "$used_int" -ge 50 ]; then
    color="33"
  else
    color="36"
  fi
  # Absolute token counts alongside the percentage — 200k and 1M models both
  # render as e.g. "67.1k/1M", so the ceiling is always explicit.
  tokens=""
  if [ -n "$tok_used" ] && [ -n "$tok_max" ]; then
    tokens=$(awk -v u="$tok_used" -v m="$tok_max" '
      function h(n) {
        if (n >= 1000000) return (n % 1000000 == 0) ? sprintf("%dM", n / 1000000) : sprintf("%.1fM", n / 1000000)
        if (n >= 1000)    return (n % 1000 == 0)    ? sprintf("%dk", n / 1000)    : sprintf("%.1fk", n / 1000)
        return sprintf("%d", n)
      }
      BEGIN { printf "%s/%s", h(u), h(m) }')
  fi
  ctx_info="\033[${color}m${bar} ${used_int}%\033[0m"
  [ -n "$tokens" ] && ctx_info="${ctx_info} \033[90m${tokens}\033[0m"
fi

# Which account this session belongs to. Not in the payload, and the script does
# not inherit CLAUDE_CONFIG_DIR, but transcript_path sits inside the config dir —
# so the dir name identifies the account exactly. Derived generically, so a third
# account (~/.claude-foo) labels itself without touching this script.
acct_info=""
case "$transcript" in
  *"/.claude-"*)
    acct=$(echo "$transcript" | sed -n 's|.*/\.claude-\([^/]*\)/.*|\1|p')
    [ -n "$acct" ] && acct_info="\033[36m⬢ ${acct}\033[0m"
    ;;
  *"/.claude/"*) acct_info="\033[35m⬢ personal\033[0m" ;;
esac

# Model display name
model_info=""
if [ -n "$model" ]; then
  display=$(echo "$model" | sed \
    -e 's/claude-/Claude /' \
    -e 's/sonnet/Sonnet/' \
    -e 's/opus/Opus/' \
    -e 's/haiku/Haiku/' \
    -e 's/fable/Fable/' \
    -e 's/-\([0-9]\)-\([0-9]\).*/\ \1.\2/' \
    -e 's/-\([0-9]\).*/\ \1/')
  model_info="\033[35m${display}\033[0m"
fi

# Effort display name
effort_info=""
if [ -n "$effort" ]; then
  case "$effort" in
    low)    eff_display="Low" ;;
    medium) eff_display="Medium" ;;
    high)   eff_display="High" ;;
    xhigh)  eff_display="Extra High" ;;
    max)    eff_display="Max" ;;
    *)      eff_display="$effort" ;;
  esac
  effort_info="\033[33m${eff_display}\033[0m"
fi

# Background tasks started by any agent, in any terminal, on either account.
# Cached briefly so the status line does not shell out to ps/lsof on every
# render. Detail view (ports, logs, owning session): `claude-bg`.
bg_info=""
cache="${TMPDIR:-/tmp}/claude-bg-$(id -u).cache"
now=$(date +%s)
mtime=$(stat -f %m "$cache" 2>/dev/null || echo 0)
bg_bin="$(cd "$(dirname "$0")" && pwd)/bin/claude-bg"
if [ $((now - mtime)) -ge 5 ] && [ -x "$bg_bin" ]; then
  "$bg_bin" --short >"$cache.tmp" 2>/dev/null && mv "$cache.tmp" "$cache"
fi
bg=$(cat "$cache" 2>/dev/null)
[ -n "$bg" ] && bg_info="\033[32m▶ ${bg}\033[0m"

printf "\033[34m%s\033[0m%b\n" "$short_cwd" "$git_info"
parts=""
[ -n "$model_info" ] && parts="${model_info}"
[ -n "$effort_info" ] && parts="${parts} \033[90m│\033[0m ${effort_info}"
[ -n "$ctx_info" ] && parts="${parts} \033[90m│\033[0m ${ctx_info}"
printf "%b" "$parts"

line3=""
[ -n "$acct_info" ] && line3="${acct_info}"
[ -n "$bg_info" ] && { [ -n "$line3" ] && line3="${line3} \033[90m│\033[0m ${bg_info}" || line3="${bg_info}"; }
[ -n "$line3" ] && printf "\n%b" "$line3"
