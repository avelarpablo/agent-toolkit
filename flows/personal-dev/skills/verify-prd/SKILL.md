---
name: verify-prd
description: The verification stage (stage:verify) — the human gate. Verify an assembled feature on the worktree of the branch that will promote, against the PRD's success criteria, one test case at a time with mandatory human confirmation. Posts a verification report to the tracker, loops findings back (fixes re-run the build loop; out-of-scope findings spawn linked task issues), and holds stage:verify until the feature passes clean or a re-verify cap flips needs:human. Use to verify a feature before it promotes to main.
argument-hint: "<feature-issue#> — the PRD/feature to verify"
---

# verify-prd — the human verification gate

Feature-level and **serial**: once all a feature's slices have merged into `feat/…`, you verify the
**assembled feature** in the `feat/…` worktree (the unit's own branch for single-unit work), one at a
time. This is a **human** gate on purpose — reading the assembled feature is how you keep contact with
what the loops built (comprehension debt). The PRD is the contract; verify **its success criteria**,
not each slice in isolation.

## Core principle

**Every test case requires explicit human confirmation.** You prepare evidence (grep, code reads, run
the app on the `feat/…` worktree, run unit/integration tests), present it, and wait. The human says
"pass", "fail", or "concerns". Only then does the status update. No exceptions — this is the one gate
whose reality anchor is *a human looked*.

## FIC discipline

The working state is a **VERIFY file** under `.verify/VERIFY-<n>/`, following the
[FIC protocol](../../../../primitives/skills/fic/PROTOCOL.md): a live resume header, checkpoint each
case verdict the moment the human gives it. Add `.verify/` to `.gitignore`. Never write a verdict
before the human confirms it in that turn.

## Flow

1. **Derive the plan.** From the PRD's **success criteria** (+ the Design Doc and child slices),
   generate one test case per criterion — each with what to run and what "pass" looks like. A
   criterion that isn't exercised by any case is a gap; add one.
2. **Run on the promote worktree.** `dev-flow`-created `feat/…` worktree for a multi-slice feature; the
   unit's own branch otherwise. Assemble and run the real feature; for UI, compare against the
   prototype's frozen screenshots.
3. **Walk the cases, one at a time**, human-confirmed. Prepare evidence, present, wait, record.
4. **Route findings** (don't just log them):
   - **In scope** → a fix re-runs the relevant build loop on the slice → re-merge → re-verify.
   - **Out of scope** → spawn a **linked `kind:` task issue**; don't block this feature on it.
5. **The re-verify cap** (principle 12): findings loop back until the feature passes clean **or** the
   cap is hit — then hold `needs:human` and report, rather than cycling forever.
6. **Close-out.** When every criterion passes clean, post the **verification report** to the feature
   issue (what was tested, pass/fail, findings, links to spawned tasks) and tell the user verification
   passed — the orchestrator then advances `stage:verify → stage:docs`. Never sign off while any
   case is ❌.

## Hard rules — the agent must NOT

1. Update a case's status without explicit human confirmation in that turn.
2. Batch-confirm multiple cases — one at a time.
3. Write evidence to the VERIFY file before the human confirms — hold it in conversation.
4. Sign off (advance the stage) while any case is failing.
5. Promote to `main` — that's the orchestrator's, out of `stage:docs`, after this passes.

See [REFERENCE.md](REFERENCE.md) for workflow detail and [FORMATS.md](FORMATS.md) for the VERIFY-file
and report templates. (Progress lives in the GitHub Project — the old Trello mirror is removed.)
