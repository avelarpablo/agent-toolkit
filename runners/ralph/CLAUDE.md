# AFK Agent (ralph-core)

> Extracted from root CLAUDE.md. This is the detailed reference for running
> ralph-core, issue conventions, blocker chains, and prerequisites.

`ralph-core` is a workspace-specific AFK agent runner that adapts the global
`ralph` system for this multi-repo workspace. Issues are tracked on
`discount-genie-core` (this repo) but code lives in the nested sub-repos.
`ralph-core` bridges this gap.

## How it works

1. Fetches `ready-for-agent` issues from `shopstackio/discount-genie-core`
2. Routes each issue to a sub-repo based on its title prefix (`BE:` → backend, `FE:` → frontend)
3. Runs the shared eligibility engine — checks labels, blocker chain, sub-repo presence
4. Ensures the target sub-repo is on a feature branch (creates one from `develop` if needed)
5. Acquires a workspace lock (prevents concurrent runs)
6. Runs Claude inside the sub-repo (Claude reads that repo's CLAUDE.md/AGENTS.md)
7. Detects usage exhaustion — writes resume hints if Claude hits limits
8. After Claude finishes: verifies HEAD moved, runs a blocking Codex review gate
9. Closes the issue on the core repo; unlocks any downstream issues whose blockers are now all closed

## Architecture

`ralph-core` is pure bash orchestration. All Python operations go through a
single helper: `ralph/lib/core.py` with ~25 subcommands. Usage from bash:
`python3 "$LIB" <subcommand> [args]`. This replaces inline python3 -c calls
and the previous separate Python files (journal.py, preflight.py, sched_meta.py).

## Commands

```bash
./ralph/ralph-core once                           # one iteration (next eligible issue)
./ralph/ralph-core once --issue 42                # target a specific issue
./ralph/ralph-core once --prd 20                  # pick next child of PRD #20
./ralph/ralph-core once --prd 20 --allow-risky    # same, allow risky issues
./ralph/ralph-core once --schedule "2026-06-04 09:00"  # defer to a future time
./ralph/ralph-core loop                           # loop until done (default max 10)
./ralph/ralph-core loop --max 5 --prd 20          # loop over PRD children (max 5)
./ralph/ralph-core resume list                    # list resumable interrupted runs
./ralph/ralph-core resume 20260528T091500-a3f7c2d1  # retry an interrupted run
./ralph/ralph-core schedule list                  # list scheduled runs
./ralph/ralph-core schedule show JOB_ID           # inspect a scheduled run
./ralph/ralph-core schedule logs JOB_ID [--follow]  # view scheduled run logs
./ralph/ralph-core schedule cancel JOB_ID         # cancel a scheduled run
./ralph/ralph-core check                          # verify auth, sub-repos, lock, issues
./ralph/ralph-core init                           # first-time setup
RALPH_MODEL=claude-sonnet-4-6 ./ralph/ralph-core once  # override model
RALPH_FEATURE_BRANCH=feature/my-feature ./ralph/ralph-core once
RALPH_DIFF_LINES=1200 ./ralph/ralph-core once     # more diff context for Codex review
```

## Issue convention

**All implementation issues (vertical slices, bugs, features) that target the
backend or frontend are filed on `shopstackio/discount-genie-core` — never on
the sub-repos directly.** The centralized queue on this repo is what allows
ralph-core to manage cross-repo work, respect blocker chains, and unlock
downstream issues. Filing issues on the sub-repos splits the queue and breaks
this.

Issues **must** have a `BE:` or `FE:` title prefix for routing:

| Prefix | Target sub-repo            | Example                                        |
| ------ | -------------------------- | ---------------------------------------------- |
| `BE:`  | `discount-genie-backend/`  | `BE: KlaviyoIntegration table + config + CRUD` |
| `FE:`  | `discount-genie/`          | `FE: Settings page + nav link`                 |
| `PRD:` | Skipped (not implementable) | `PRD: Klaviyo OAuth Integration`              |

Issues without a recognized prefix are skipped with a warning.

PRDs get `PRD:` prefix and should **not** have the `ready-for-agent` label —
they are parent tracking issues, not implementable work units.

## PRD parent convention

Issues that belong to a PRD should declare their parent in a `## Parent`
section. This enables `--prd N` filtering:

```markdown
## Parent
- #20 (PRD: Klaviyo OAuth Integration)
```

## Blocker chain

Issues can declare dependencies via a `## Blocked by` section in their body:

```markdown
## Blocked by
- #2 (BE: KlaviyoIntegration table + config + CRUD) — needs the model and config
```

`ralph-core` parses these, checks if each blocker is closed, and skips blocked
issues. After closing an issue, it scans all open issues for newly-unblocked
ones and adds the `ready-for-agent` label.

## Labels

| Label              | Meaning                                          |
| ------------------ | ------------------------------------------------ |
| `ready-for-agent`  | Fully specified, unblocked, ready for ralph-core |
| `needs-triage`     | Needs human review before agent pickup           |
| `needs-info`       | Waiting for more information                     |
| `ready-for-human`  | Requires human action, not agent                 |

Issues with `needs-triage`, `needs-info`, `ready-for-human`, or `wontfix` are
hard-blocked and will not be picked even if they also have `ready-for-agent`.

## Workspace lock

`ralph-core` uses a file lock (`ralph/.run.lock`) to prevent concurrent runs
from corrupting sub-repo state. The lock records PID and hostname:

- If a process dies, the stale lock is automatically cleaned on the next run
- Cross-host locks are never automatically removed
- `./ralph/ralph-core check` shows lock status

## Usage exhaustion & resume

When Claude hits a usage/session limit mid-run, ralph-core:
1. Detects the exhaustion from the JSONL log
2. Records resume hints (issue, branch, HEAD) in the run journal
3. Reopens the issue if Claude closed it before the review gate ran

To resume: `./ralph/ralph-core resume list` shows resumable runs, then
`./ralph/ralph-core resume RUN_ID` retries. Resume pre-checks verify the
branch, HEAD, worktree, and issue eligibility before proceeding.

## Scheduling

Defer execution to a future time with `--schedule "YYYY-MM-DD HH:MM"`.
Supported on macOS (launchd), Linux (systemd-run or at). The schedule stores
metadata in `ralph/schedules/`, including preflight results at creation time and
runtime. Use `schedule list|show|logs|cancel` to manage.

## Codex review gate

After each commit, `ralph-core` runs a blocking Codex review using
`ralph/review-schema.json`. **Do not loosen this schema** — read the file for
details. If blockers are found, the issue is reopened with findings. On
multi-commit runs (including resume), the review covers the full commit range.

Set `RALPH_GATE_STRICT=1` to fail-closed on inconclusive reviews (default:
fail-open with a warning).

## Prerequisites

Before running `ralph-core`, ensure:

1. Sub-repos exist (`scripts/clone-repos.sh`)
2. Sub-repos are on feature branches (not `main`/`develop`/`staging`), or set
   `RALPH_FEATURE_BRANCH` to auto-create them
3. Auth is configured: `claude`, `gh`, and `codex` for the account matching this
   repo path in `~/.ralph/accounts.toml`
4. Issues are filed on this repo with `BE:`/`FE:` prefixes and `ready-for-agent` label
5. Global ralph prompt exists at `~/.ralph/prompt.md`

Run `./ralph/ralph-core check` to verify all of the above.

## Creating new feature work for ralph-core

To set up a new feature for AFK agent implementation:

1. Write a PRD and file it on this repo (label it `enhancement`, **not** `ready-for-agent`)
2. Break the PRD into vertical slices using `/to-vertical-issues` or manually
3. Each slice gets `BE:` or `FE:` prefix, `## Parent`, `## Blocked by`, `## Demo command`, and `## Acceptance criteria`
4. Label unblocked slices `ready-for-agent`; blocked ones get labeled automatically as their blockers close
5. Set up and run:
   ```bash
   RALPH_FEATURE_BRANCH=feature/<name> ./ralph/ralph-core init   # creates branches + dirs
   RALPH_FEATURE_BRANCH=feature/<name> ./ralph/ralph-core loop   # runs the queue
   # or for a specific PRD:
   RALPH_FEATURE_BRANCH=feature/<name> ./ralph/ralph-core loop --prd 20
   ```
