---
name: qa-loop
description: The QA build loop — a two-agent dialogue that drives the assembled app through Playwright, checks it against the approved prototype's frozen screenshots, and writes the e2e suite. A driver holds the browser; a second-family strategist proposes and challenges coverage. Stops at qa-done and emits the status.json completion signal, touching no labels or branches. Use to run QA on a slice's assembled surface after dev and refactor.
argument-hint: "<issue#> — the slice to QA"
---

# qa-loop — the QA build loop

The build phase's one genuinely new loop, and the only one that drives a real browser. It runs on a
slice's **own assembled, refactored surface** in its worktree (a vertical slice is independently
runnable) — the fully-integrated feature is exercised later, at the human `stage:verify` gate. Like
every build loop it is a **two-family dialogue**, and like every loop it **touches no issue, label, or
branch** — the orchestrator owns those; qa-loop only writes code (the e2e suite) and its completion
signal.

> **Playwright MCP must be reachable.** It authenticates interactively, so it can be absent in a
> headless/cron context. Confirm the driver can reach it before committing to a full AFK run; if it
> can't, hold `needs:human` and say so (that's a `failed` signal, not a crash).

## The two agents

- **Driver (you).** The only hand on the browser — hold the Playwright MCP, run the app, execute the
  agreed steps, capture screenshots. One driver only; two loops must not share a browser (the
  orchestrator serializes QA, cap = 1).
- **Strategist / critic (second family, e.g. Codex).** Proposes *what* and *how* to test and
  challenges coverage — "empty state? error path? the prototype's hover states? the loading skeleton?"
  You converge on a test plan with it; you don't grade your own coverage.

## Flow

1. **Assemble & run.** Start the slice's app in its worktree (the project's run command).
2. **Load the acceptance reference.** Pull the **frozen prototype screenshots** off the feature issue
   (the design step froze them there) — they are the visual acceptance target.
3. **Converge on a test plan.** Driver drafts, strategist challenges, until coverage is honest: happy
   path, empty/error/loading states, and the prototype's interaction details.
4. **Execute & compare.** Drive each case through Playwright; capture screenshots and compare against
   the frozen reference. Note every visual or behavioral divergence.
5. **Write the e2e suite.** Because the surface is now stable, write the end-to-end tests here (they
   were *not* written in the dev loop — the UI was still churning). Commit them to the slice branch.
6. **Signal.** Write the completion signal and stop:

   ```bash
   BRANCH="$(git rev-parse --abbrev-ref HEAD)"
   DIR="${DEV_LOOP_BUILDS_ROOT:-$HOME/.ralph/builds}/$BRANCH"; mkdir -p "$DIR"
   python3 - "$DIR/status.json" "<issue#>" "$BRANCH" <<'PY'
   import json,sys; p,i,b=sys.argv[1:4]
   json.dump({"issue":i,"branch":b,"loop":"qa",
              "outcome":"done",           # done | capped | failed
              "summary":"e2e written; N cases pass; screenshots match prototype",
              "anchor":"e2e suite passes; screenshots compared"}, open(p,"w"), indent=2)
   PY
   ```

## Two exits (principle 12)

- **done** — the e2e suite is written and passing and the screenshots match the frozen prototype.
- **capped / failed** — max attempts exhausted, or Playwright unreachable, or a divergence you can't
  resolve: emit `capped`/`failed` with a clear `summary`; the orchestrator flips `needs:human`. Never
  loop silently.
