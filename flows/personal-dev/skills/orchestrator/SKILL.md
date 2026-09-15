---
name: orchestrator
description: The pipeline orchestrator pass — read the board, and for every issue it can legally advance (respecting dependencies, shared-file conflicts, concurrency caps, QA=1, and skipping needs:human) create/tear down worktrees, launch the right build loop in the background, read each finished loop's status.json, flip the stage: label, close merged slices and roll a finished feature up to stage:verify, and open the promote PR out of stage:docs. Idempotent and resumable — driven entirely by durable labels + status files. Use to advance the build board a step, or run it on a cron as the standing loop.
argument-hint: "[--once] — one pass (default), or the repo/project to drive"
---

# orchestrator — the stage-machine pass

You invoke it; it reads the board and, for every issue it can **legally** advance, launches the next
background loop and flips the `stage:` label, then reports and exits. Driven entirely by durable
labels + `status.json` files, so it is **idempotent and resumable** — a crashed loop just leaves its
issue at the old label, and re-running picks up from there. (The standing autonomous version is this
same pass on a cron; later.)

It owns **policy** (which loop, when, respecting conflicts); the [`dev-flow`](../../runners/dev-flow/runner.json)
runner owns the deterministic mechanics (worktrees, label flips, cleanup) and the build loops own the
work. The orchestrator writes `stage:` labels and nothing else — **not** Project `Status` (that write
is added in build item 4.4).

## One pass

1. **Read the board.** `gh issue list` for every `stage:*` issue, grouped by stage; note the
   parent/child (feature→slices) graph, each slice's `blocked` state and its files-to-modify.
2. **Skip what you may not touch.** Anything carrying `needs:human` — a human owes it a step. Anything
   `blocked` whose blocker isn't closed. Anything already running (its worktree/loop is live).
3. **Advance each legally-advanceable issue** per the [dispatch table](#dispatch) — respecting the
   [conflict rules](#conflicts). Launch loops as **background subprocesses**, logging to your
   scratchpad; never run a loop foreground (its stream would drown your context) and never append a
   shell `&` (it detaches from the wrapper the harness watches — you'd lose the real completion
   signal). The harness re-invokes you when a loop exits.
4. **On each loop completion, read its signal** — `~/.ralph/builds/<branch>/status.json`:
   `done` → do the stage's exit action (below); `capped`/`failed` → flip `needs:human` and surface the
   `summary`. Never advance an issue whose loop didn't emit `done`.
5. **Report and exit.** A short board summary: what advanced, what's running, what holds `needs:human`.

## Dispatch

| Issue at | Launch | On `done` (exit action) |
|---|---|---|
| `stage:ready` (slice) | `dev-flow create slice <n> <slug> --base <feat>` → `dev-loop --issue <n> --work-dir <wt> --test-cmd …` | flip `stage:refactor` |
| `stage:refactor` (slice) | the [refactor chain](../../../../primitives/runners/dev-loop/REFACTOR-LOOP.md): `review-loop` → `dev-loop --prompt refactor-prompt.md` → re-check, to zero blockers or the cap | flip `stage:qa` |
| `stage:qa` (slice) | dispatch an agent running [`qa-loop`](../../../../primitives/skills/qa-loop/SKILL.md) (**cap = 1**) | **merge** slice into `feat/…`, `dev-flow cleanup`, **close the slice issue** |
| `stage:design` (feature) | dispatch [`design-step`](../design-step/SKILL.md) AFK to generate variations | hold `needs:human` for the pick (board-visible) |
| `stage:docs` (feature) | run `sync-docs` feature-level on `feat/…` | open the `feat → main` promote PR (from the 1.1 template) |

**The two joins** (see [PROCESS → State machine](../../../../docs/PROCESS.md#state-machine--labels)):

- When a slice's QA merges into `feat/…`, **close the slice issue** (a merged slice is done; closing
  keeps a stage-less slice out of the inbox).
- When the **last** open slice child of a feature closes, flip the **feature (PRD)** issue to
  `stage:verify` — the rollup that reassembles the parallel slices. (`stage:verify` is the human gate;
  the orchestrator does not run it.)

## Conflicts (respect all four)

| Dimension | Rule |
|---|---|
| **Dependency** | never start a slice whose `blocked`-by isn't closed |
| **Shared-file** | two parallel slices editing overlapping lines → serialize their merges (order by the slice plan) |
| **Concurrency** | a global cap on simultaneous loops (machine/API limits) |
| **QA runtime** | **QA is serial, cap = 1** — two QA loops would clash on ports/test DB; dev/refactor may parallelize |

## Notes

- **Verification and design-pick stay human** — the orchestrator dispatches `stage:design` AFK then
  holds `needs:human`; it never runs `stage:verify`.
- **Resumability rests on the signal**, not memory: if you crash mid-pass, the labels + `status.json`
  files are the whole state. Re-invoke and continue.
