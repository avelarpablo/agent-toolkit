#!/usr/bin/env bash
# ralph state management — per-iteration JSON state for the footer
# Sourced by ralph; not executable standalone.
#
# State dir: /tmp/ralph-loop-PID/
#   loop.json       — {max, start_ts, pid}
#   iter-N.json     — {iter, phase, start_ts, issue_number, issue_title, ...}
#
# The loop parent creates state. The `once` child updates it (via exported
# RALPH_STATE_DIR). The footer reads it. This is the single source of truth.
# Stale dirs from crashed runs are cleaned at next _state_init.
RALPH_STATE_DIR="${RALPH_STATE_DIR:-}"

_state_init() {
  local max="$1"

  # Clean stale state dirs from crashed prior runs
  for d in /tmp/ralph-loop-*; do
    [[ -d "$d" ]] || continue
    local old_pid="${d##*-}"
    kill -0 "$old_pid" 2>/dev/null || rm -rf "$d"
  done

  RALPH_STATE_DIR="/tmp/ralph-loop-$$"
  mkdir -p "$RALPH_STATE_DIR"
  export RALPH_STATE_DIR

  local tmp="$RALPH_STATE_DIR/.loop.json.tmp"
  python3 -c "
import json, time, sys
json.dump({
    'max': int(sys.argv[1]),
    'start_ts': time.time(),
    'pid': $$
}, open(sys.argv[2], 'w'))
" "$max" "$tmp"
  mv -f "$tmp" "$RALPH_STATE_DIR/loop.json"
}

_state_update_iter() {
  [[ -z "$RALPH_STATE_DIR" ]] && return 0
  local iter="$1" phase="$2"
  shift 2

  local file="$RALPH_STATE_DIR/iter-${iter}.json"
  local tmp="$RALPH_STATE_DIR/.iter-${iter}.json.tmp"

  python3 -c "
import json, time, sys, os

iter_n = int(sys.argv[1])
phase = sys.argv[2]
file = sys.argv[3]
tmp = sys.argv[4]
kv_pairs = sys.argv[5:]

# Load existing or start fresh
data = {}
if os.path.exists(file):
    try:
        data = json.load(open(file))
    except (json.JSONDecodeError, OSError):
        pass

data['iter'] = iter_n
data['phase'] = phase
data.setdefault('start_ts', time.time())

if phase in ('blocked', 'done'):
    data['end_ts'] = time.time()
    data['elapsed'] = int(data['end_ts'] - data['start_ts'])

# If retried (was blocked, now done), mark the transition
if phase == 'done' and data.get('was_blocked'):
    data['retried'] = True
if phase == 'blocked':
    data['was_blocked'] = True

for kv in kv_pairs:
    if '=' in kv:
        k, v = kv.split('=', 1)
        # Try to parse as int
        try:
            v = int(v)
        except ValueError:
            pass
        data[k] = v

json.dump(data, open(tmp, 'w'))
" "$iter" "$phase" "$file" "$tmp" "$@"
  mv -f "$tmp" "$file"
}

_state_read_iter() {
  [[ -z "$RALPH_STATE_DIR" ]] && return 0
  local iter="$1"
  local file="$RALPH_STATE_DIR/iter-${iter}.json"
  [[ -f "$file" ]] && cat "$file" || echo "{}"
}

_state_read_loop() {
  [[ -z "$RALPH_STATE_DIR" ]] && return 0
  local file="$RALPH_STATE_DIR/loop.json"
  [[ -f "$file" ]] && cat "$file" || echo "{}"
}

_state_cleanup() {
  [[ -n "$RALPH_STATE_DIR" && -d "$RALPH_STATE_DIR" ]] && rm -rf "$RALPH_STATE_DIR"
}
