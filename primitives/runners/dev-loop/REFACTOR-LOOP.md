# The refactor loop — orchestrator policy, not a new runner

The refactor loop is **not** its own runner; it is the orchestrator chaining two existing ones. This
file is the recipe the orchestrator (build item 3.1) implements. `review-loop` stays a pure critic;
`dev-loop` stays the only thing that writes code.

```
review-loop (find)  →  dev-loop (fix, refactor prompt)  →  review-loop (re-check)  →  … 
      │                                                                                │
      └────────────────────────── until zero blockers ────────────────────────────────┘
                                        or the round cap
```

Each round:

1. **Find** — `review-loop --base <branch-base> --criteria <repo standards>` against
   [`criteria/standards.md`](../review-loop/criteria/standards.md) (R-1…R-6; pattern/maintainability
   violations encoded as blockers, so "apply the best pattern" is *testable*, not a vibe).
2. **Fix** — if there are blockers, run this loop as the fix actor with the refactor prompt:
   `dev-loop --issue <N> --prompt <this dir>/refactor-prompt.md --test-cmd "<repo tests>"`. It fixes
   exactly the flagged issues, preserves behavior (tests still pass — the anchor), and emits its
   `status.json`.
3. **Re-check** — run `review-loop` again on the new diff.

**Two exits** (principle 12): zero blockers → the slice advances; the **round cap** is hit → the
orchestrator stops, flips `needs:human`, and reports what could not be fixed. Silent looping is the
failure a cap prevents.

The number of rounds scales with stakes; the standards criteria are the work (a vague criterion trains
you to ignore the gate).
