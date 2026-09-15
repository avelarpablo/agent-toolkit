# Standards criteria — for the refactor loop (structure & patterns)

Grade whether working code is **clean**: well-structured, using the right patterns, maintainable to
this repo's standard. The code already passes its tests (the dev loop saw to that); this gate is
about *structure*, not correctness. Every finding must name a **concrete, checkable** violation — the
refactor loop can only act on blockers it can verify, not on "could be nicer".

This is a **tier-3 template** — projects tune it. Keep it falsifiable: a rule no one can point at a
line for is not a rule.

**Out of scope — do not report:** correctness bugs (the dev loop's Codex gate owns those); behavior
changes; personal style preferences with no maintainability cost; missing features.

---

## R-1 — Shallow module / leaky abstraction (blocker)

A module whose interface is nearly as complex as its implementation, or that exposes its internals so
callers must know how it works. Deep modules (simple interface over real functionality) are the goal.

> Report as: the module, its interface surface, and what leaks.

## R-2 — Wrong or missing pattern where one is warranted (blocker)

Logic that hand-rolls what an established pattern handles cleanly (a chain of conditionals that is a
strategy/state machine; duplicated branching that is a polymorphic dispatch; manual resource juggling
that is RAII/context management). Name the pattern and the lines.

> Report as: the code shape, and the specific pattern it should be.

## R-3 — Duplication that should be factored (blocker)

The same non-trivial logic in three or more places, where a single well-named unit would do. (Two
occurrences is often fine; three is a pattern begging for extraction.)

## R-4 — Poor naming / unclear intent (concern)

A name that misleads or hides intent, forcing the reader to trace the implementation to understand
the call site. Names are the cheapest documentation.

## R-5 — Function/module doing too much (concern)

A unit with several unrelated responsibilities — the reason it changes for more than one kind of
reason. Flag the distinct responsibilities.

## R-6 — Repo-convention violation (concern)

Code that ignores an established convention in this repo (error handling, logging, file layout, the
patterns the surrounding code already uses). Cite the convention and a place it's followed correctly.

---

## Reporting

- **`file`** / **`line`** — the offending code.
- **`criteria_rule`** — the rule ID (`R-2`).
- **Severity**: `blocker` for R-1 to R-3 (structural debt the refactor loop must fix before the slice
  merges); `concern` for R-4 to R-6. **Do not pad** — a clean diff should return zero findings, which
  is how the loop terminates.
