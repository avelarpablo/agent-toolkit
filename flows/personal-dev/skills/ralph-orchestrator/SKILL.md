---
name: ralph-orchestrator
description: Drive ralph (the AFK agent runner) from inside a Claude Code session — launch ralph loops as background subprocesses so their verbose output never fills the driving session's context, chain loops until the agent queue drains, and dodge the epic-label / allow-risky / account-isolation gotchas. Use when the user says "orchestrate ralph", "run ralph loops", "drive ralph in the background", "batch-implement issues with ralph", or wants a Claude session to shepherd a batch of GitHub issues through ralph.
---

# ralph-orchestrator

Operator guidance for a Claude Code session that is **driving** ralph (not being
run by it). Goal: implement a batch of `ready-for-agent` issues via chained ralph
loops, keeping the driver's context tiny across an arbitrarily long run.

This is the orchestration layer on top of ralph itself. For how ralph works
internally, read [`../../primitives/runners/ralph/CLAUDE.md`](../../../../primitives/runners/ralph/CLAUDE.md).
For multi-account isolation, read
[`../../primitives/runners/ralph/MULTI_ACCOUNT_SETUP.md`](../../../../primitives/runners/ralph/MULTI_ACCOUNT_SETUP.md).

## The core idea: ralph loops as background subprocesses

A `ralph loop` emits a huge stream (`--output-format stream-json --verbose`). If
you run it foreground, that stream lands in your context and drowns you. Instead:

1. Redirect stdout+stderr to a log file in your scratchpad.
2. Run it as a **background** subprocess. The harness re-invokes you when the
   process **exits** — you do not poll and do not read the full log.
3. On startup, `tail` only a few lines for a sanity check. On completion,
   `tail` a small slice to learn why the loop stopped. Never `cat` the log.

```bash
LOG=/path/to/scratchpad/ralph-loop-1.log
RALPH_BASE_BRANCH=main RALPH_FEATURE_BRANCH=feature/integration \
  ralph loop --max 10 --allow-risky > "$LOG" 2>&1
```

Run that as a background command (the harness backgrounding mechanism), **not**
with a trailing `&` — see the pitfall below.

### PITFALL — never append a shell `&` inside the backgrounded command

A trailing `&` detaches ralph from the wrapper the harness is watching. The
wrapper exits immediately, so the task-completion notification fires **now**
(wrapper exit) instead of when ralph actually finishes — you lose the real
completion signal and think the loop is done when it just started.

If detachment is genuinely unavoidable, arm a separate watcher that completes
only when the loop truly exits:

```bash
while pgrep -f "primitives/runners/ralph/ralph loop" >/dev/null; do sleep 30; done; echo "loop exited"
```

## Chaining loops until the queue drains

A loop can stop early: it hits `--max`, a review-gate reopen pauses progress, or
Claude usage is exhausted. So one loop rarely finishes the batch. On each
completion:

1. `tail` the log to see why it stopped.
2. Count remaining eligible work: open issues labeled `ready-for-agent` that are
   NOT hard-blocked (`needs-triage`, `needs-info`, `ready-for-human`, `wontfix`).
   `ralph check` prints the eligible list under `── Issues ──`.
3. If any remain, launch the next loop (same background pattern, same feature
   branch, new log file).
4. Stop when only `ready-for-human` residue is left — the agent queue is drained.

This keeps the driver's context flat no matter how long the batch runs.

## Preflight checklist (before the first loop)

- [ ] **Slice the work first.** Break big epics/ports into dependency-chained
      vertical slices with `## Parent` and `## Blocked by #N`. See
      [reference.md](reference.md#slice-before-you-run).
- [ ] **Give every epic/parent tracker a human label.** Otherwise ralph
      hijacks it and tries to implement the whole epic in one iteration. This is
      the biggest gotcha — see [reference.md](reference.md#epic-label-hijack).
- [ ] **Set the integration branch.** `main` is protected; ralph refuses to
      commit there. Export `RALPH_BASE_BRANCH` + `RALPH_FEATURE_BRANCH` so all
      work lands on one branch for a single review PR.
- [ ] **Run `ralph check`.** Confirm resolved account, claude/gh config dirs,
      lock status, and the eligible-issue list before launching.
- [ ] **Decide on `--allow-risky`.** Preflight NO_GOs on any issue body
      mentioning `alembic`, `generate-client`, or `migration` — including false
      positives like a filename. See [reference.md](reference.md#allow-risky).
- [ ] **Guard the driver's own `gh`.** ralph is account-isolated; your direct
      `gh` calls are not. See [reference.md](reference.md#account-isolation).

## Deeper mechanics and gotchas

All the sharp edges — the epic-label hijack, allow-risky false positives,
account isolation vs. the driver's gh, one-branch-per-batch, slicing, safe
parallel testing with worktrees, and recovery mechanics — are in
[reference.md](reference.md).
