# AFK Agent (ralph)

`ralph` is a generic AFK agent runner that picks GitHub issues labeled
`ready-for-agent`, implements them with Claude, commits, closes the issue,
and runs a blocking Codex review gate.

## How it works

1. Auto-detects repo root and GitHub slug from `git remote`
2. Fetches `ready-for-agent` issues from the repo
3. Runs the eligibility engine — checks labels, blocker chains
4. Optionally routes to sub-repos via `RALPH_HOOKS` (for multi-repo workspaces)
5. Ensures the repo is on a feature branch (creates one if `RALPH_FEATURE_BRANCH` is set)
6. Acquires a workspace lock (prevents concurrent runs)
7. Runs Claude in the target repo
8. Detects usage exhaustion — writes resume hints if Claude hits limits
9. After Claude finishes: verifies HEAD moved, runs a blocking Codex review gate
10. Closes the issue; unlocks any downstream issues whose blockers are now all closed

## Architecture

`ralph` is pure bash orchestration. All Python operations go through a single
helper: `lib/core.py` with ~25 subcommands. Usage from bash:
`python3 "$LIB" <subcommand> [args]`.

Multi-repo workspaces extend ralph via `RALPH_HOOKS` — a shell file that
overrides routing functions (`_route_issue`, `_repo_dir`, `_repo_name`) and
init/check hooks (`_ralph_init_extra`, `_ralph_check_extra`).

## Commands

```bash
ralph once                                # one iteration (next eligible issue)
ralph once --issue 42                     # target a specific issue
ralph once --prd 20                       # pick next child of PRD #20
ralph once --allow-risky                  # allow risky issues
ralph once --schedule "2026-06-04 09:00"  # defer to a future time
ralph loop                                # loop until done (default max 10)
ralph loop --max 5 --prd 20              # loop over PRD children (max 5)
ralph resume list                         # list resumable interrupted runs
ralph resume RUN_ID                       # retry an interrupted run
ralph review <sha> -- <issue>             # manual post-commit Codex review
ralph schedule list                       # list scheduled runs
ralph schedule show JOB_ID                # inspect a scheduled run
ralph schedule logs JOB_ID [--follow]     # view scheduled run logs
ralph schedule cancel JOB_ID              # cancel a scheduled run
ralph check                               # verify auth, config, issues
ralph init                                # first-time setup
ralph ping                                # minimal Claude session (keeps usage alive)
ralph schedule-pings                      # schedule pings for a full day
ralph clean-pings                         # cancel pending ping schedules
```

## Environment variables

```bash
RALPH_REPO=org/repo              # GitHub owner/repo (auto-detected from git remote)
RALPH_HOOKS=/path/to/hooks.sh    # shell file with routing overrides
RALPH_PROTECTED_BRANCHES="main"  # space-separated (default: main)
RALPH_BASE_BRANCH=main           # branch to create feature branches from
RALPH_FEATURE_BRANCH=feature/x   # target feature branch
RALPH_MODEL=claude-opus-4-6      # Claude model (default: claude-opus-4-6)
RALPH_EFFORT=medium              # Claude effort (default: medium)
RALPH_CODEX_MODEL=gpt-5.5        # Codex review model (default: gpt-5.5)
RALPH_CODEX_REVIEW_EXTRA="..."   # additional review focus lines
RALPH_DIFF_LINES=800             # max diff lines for Codex review (default: 800)
RALPH_SKIP_CODEX=1               # skip Codex review gate
RALPH_GATE_STRICT=1              # fail-closed on inconclusive reviews
RALPH_RETENTION_DAYS=30          # prune journals/schedules older than N days
RALPH_CROSS_REPO_KEYWORDS='{}'   # JSON: cross-repo keyword detection for core.py
RALPH_VERBOSE=1                  # shell trace
```

## Issue convention

Issues need the `ready-for-agent` label to be picked up. In single-repo mode,
any issue with this label is eligible (no title prefix required).

Multi-repo workspaces define custom routing via `RALPH_HOOKS` — the hooks file
overrides `_route_issue()` to parse title prefixes and map to sub-repos.

## PRD parent convention

Issues that belong to a PRD should declare their parent in a `## Parent`
section. This enables `--prd N` filtering:

```markdown
## Parent
- #20 (PRD: Feature Name)
```

## Blocker chain

Issues can declare dependencies via a `## Blocked by` section:

```markdown
## Blocked by
- #2 (Some prerequisite issue) — needs the model and config
```

ralph parses these, checks if each blocker is closed, and skips blocked issues.
After closing an issue, it scans all open issues for newly-unblocked ones and
adds the `ready-for-agent` label.

## Labels

| Label              | Meaning                                  |
| ------------------ | ---------------------------------------- |
| `ready-for-agent`  | Fully specified, unblocked, ready        |
| `needs-triage`     | Needs human review before agent pickup   |
| `needs-info`       | Waiting for more information             |
| `ready-for-human`  | Requires human action, not agent         |

Issues with `needs-triage`, `needs-info`, `ready-for-human`, or `wontfix` are
hard-blocked and will not be picked even if they also have `ready-for-agent`.

## Workspace lock

ralph uses a file lock (`ralph/.run.lock`) to prevent concurrent runs.
The lock records PID and hostname:

- If a process dies, the stale lock is automatically cleaned on the next run
- Cross-host locks are never automatically removed
- `ralph check` shows lock status

## Usage exhaustion & resume

When Claude hits a usage/session limit mid-run, ralph:
1. Detects the exhaustion from the JSONL log
2. Records resume hints (issue, branch, HEAD) in the run journal
3. Reopens the issue if Claude closed it before the review gate ran

To resume: `ralph resume list` shows resumable runs, then
`ralph resume RUN_ID` retries.

## Codex review gate

After each commit, ralph runs a blocking Codex review using
`ralph/review-schema.json`. If blockers are found, the issue is reopened with
findings. Set `RALPH_GATE_STRICT=1` to fail-closed on inconclusive reviews.

## Extending ralph (RALPH_HOOKS)

Create a shell file that overrides these functions:

```bash
_route_issue()         # parse title -> route name (default: always "default")
_repo_dir()            # route name -> directory path
_repo_name()           # route name -> display name
_ralph_init_extra()    # additional init steps (called by `ralph init`)
_ralph_check_extra()   # additional check output (called by `ralph check`)
```

Set `RALPH_HOOKS=/path/to/hooks.sh` before running ralph. See
`runners/ralph-dg/hooks.sh` for a working example.

## Prerequisites

1. `claude` CLI installed and authenticated
2. `gh` CLI installed and authenticated
3. `codex` CLI installed (for review gate)
4. Issues filed on the repo with `ready-for-agent` label

Run `ralph check` to verify.
