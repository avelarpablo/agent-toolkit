#!/bin/bash
# ~/.claude/hooks/stop.sh — Fires at end of every Claude Code session.
# Runs a structured Codex review (blocker/concern/nit JSON verdict) on
# any commit made during the session, then summarises findings to stdout.
#
# Two paths:
#   1. Ralph session: once.sh writes /tmp/.ralph_pre_session_head before
#      calling claude. Hook detects it, diffs HEADs, reviews, cleans up.
#   2. General session: if HEAD moved in the last 60 minutes, review it.

set -euo pipefail

MARKER="/tmp/.ralph_pre_session_head"
REVIEWS_DIR="/tmp/claude-session-reviews"
SCHEMA="$HOME/.claude/review-schema.json"

log() { echo "[stop-hook] $(date '+%H:%M:%S') $*"; }

mkdir -p "$REVIEWS_DIR"

# ── Read session context ──────────────────────────────────────────────────────
input=$(cat)
cwd=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || true)

if [[ -z "$cwd" || ! -d "$cwd" ]]; then
  log "No valid cwd — skipping review."
  exit 0
fi

repo_root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$repo_root" ]]; then
  log "Not a git repo — skipping review."
  exit 0
fi

current_head=$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || true)
if [[ -z "$current_head" ]]; then
  log "Could not read HEAD — skipping review."
  exit 0
fi

commit_title=$(git -C "$repo_root" log -1 --format="%s" 2>/dev/null || true)
repo_name=$(basename "$repo_root")
timestamp=$(date +%Y%m%dT%H%M%S)
result_file="${REVIEWS_DIR}/review-${timestamp}-${current_head:0:8}.json"

run_review() {
  local sha="$1"
  log "Running structured Codex review on ${sha:0:12} — \"${commit_title}\"..."

  set +e
  codex exec review \
    --commit "$sha" \
    --title "$commit_title" \
    --json \
    --output-schema "$SCHEMA" \
    -o "$result_file" \
    -c model_reasoning_effort=xhigh \
    "You are reviewing a commit produced by an AI coding agent (Claude Code).

Commit: ${sha}
Title: ${commit_title}
Repo: ${repo_name}

Review focus:
1. Correctness — logic bugs, off-by-ones, wrong error handling, security issues
2. AGENTS.md invariants — if AGENTS.md exists at the repo root, flag any rule violations by rule ID
3. Tests — are tests added/updated? Do they exercise the new behaviour?

Classify each finding as blocker / concern / nit.
Return verdict 'clean' only if there are no blockers and no concerns." \
    2>&1 | sed 's/^/[codex-session] /'
  local codex_exit=$?
  set -e

  if [[ $codex_exit -ne 0 ]]; then
    log "Codex exited non-zero ($codex_exit) — review may be incomplete."
    return
  fi

  if [[ ! -s "$result_file" ]]; then
    log "No result file written — skipping summary."
    return
  fi

  local verdict blockers concerns nits
  verdict=$(python3 -c "import json; d=json.load(open('$result_file')); print(d.get('verdict','unknown'))" 2>/dev/null || echo "unknown")
  blockers=$(python3 -c "import json; d=json.load(open('$result_file')); print(sum(1 for i in d.get('issues',[]) if i.get('severity')=='blocker'))" 2>/dev/null || echo 0)
  concerns=$(python3 -c "import json; d=json.load(open('$result_file')); print(sum(1 for i in d.get('issues',[]) if i.get('severity')=='concern'))" 2>/dev/null || echo 0)
  nits=$(python3 -c "import json; d=json.load(open('$result_file')); print(sum(1 for i in d.get('issues',[]) if i.get('severity')=='nit'))" 2>/dev/null || echo 0)

  log "────────────────────────────────────────────"
  log "Verdict: ${verdict} | blockers=${blockers} concerns=${concerns} nits=${nits}"
  log "Saved to: ${result_file}"
  log "────────────────────────────────────────────"

  if [[ "$blockers" -gt 0 ]]; then
    log "ACTION REQUIRED: ${blockers} blocker(s) found — review ${result_file} before pushing."
  fi
}

# ── Path 1: Ralph marker ──────────────────────────────────────────────────────
if [[ -f "$MARKER" ]]; then
  pre_head=$(cat "$MARKER")
  rm -f "$MARKER"

  if [[ "$pre_head" == "$current_head" ]]; then
    log "Ralph session: HEAD unchanged — no review needed."
    exit 0
  fi

  log "Ralph session: HEAD moved ${pre_head:0:12} → ${current_head:0:12}"
  run_review "$current_head"
  exit 0
fi

# ── Path 2: General session — 60-minute heuristic ────────────────────────────
commit_ts=$(git -C "$repo_root" log -1 --format="%ct" 2>/dev/null || echo 0)
now_ts=$(date +%s)
age=$(( now_ts - commit_ts ))

if [[ "$age" -le 3600 ]]; then
  log "General session: recent commit (${age}s ago) — running review..."
  run_review "$current_head"
else
  log "General session: last commit ${age}s ago — no review needed."
fi
