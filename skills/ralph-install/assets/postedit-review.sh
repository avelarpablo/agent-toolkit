#!/bin/bash
# ~/.claude/hooks/postedit-review.sh — Async inline Codex review after every edit.
# Fired by the global PostToolUse hook on Edit|Write|MultiEdit.
# Runs in the background so Claude Code is never blocked.

set -euo pipefail

log() { echo "[postedit-review] $(date '+%H:%M:%S') $*"; }

input=$(cat)
cwd=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || true)
tool=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || true)
file=$(echo "$input" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('file_path', '') or ti.get('path', ''))
" 2>/dev/null || true)

if [[ -z "$cwd" || ! -d "$cwd" ]]; then
  exit 0
fi

repo_root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$repo_root" ]]; then
  exit 0
fi

file_label="${file:-uncommitted changes}"
log "Running Codex review on ${file_label} (${tool})..."

codex review \
  --uncommitted \
  -c model_reasoning_effort=medium \
  "You are doing a rapid inline review of a single file edit made by an AI coding agent.

File changed: ${file_label}
Repo: $(basename "$repo_root")

Focus only on:
1. Correctness — obvious logic bugs, off-by-ones, wrong error handling, security issues in the changed lines
2. AGENTS.md invariants — if an AGENTS.md exists at the repo root, flag any rule violations by rule ID
3. Tests — if a non-test file changed, is there an obvious missing test case?

Skip style nits. Keep findings brief (one sentence each). If nothing is wrong, say 'LGTM'." \
  2>&1 | sed "s/^/[codex-inline] /" || log "Codex review exited non-zero (non-fatal)."
