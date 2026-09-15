# PRD criteria — for a product requirements document

Grade whether this PRD is a sound **scope lock**: the right altitude (what & why, not how), bounded,
and testable. The author's product choices are given — do not re-litigate them; find where the
document is unmeasurable, unbounded, or leaking into implementation.

**Out of scope — do not report:** disagreement with the product decision itself; style or tone;
requests for sections the author didn't ask for.

---

## P-1 — Unmeasurable success criterion (blocker)

A success criterion no one could test — no observable outcome, no state to inspect. "Works well",
"is intuitive", "handles errors gracefully" are all unmeasurable. Every criterion must name
something a verifier could later check pass/fail.

> Report as: the criterion, and what specifically cannot be observed.

## P-2 — Implementation detail leaking in (blocker)

The PRD names a module, table, schema, endpoint, class, or file path — a *how*. That belongs in the
design doc. The one allowed exception is a prototype-derived snippet that encodes a *decision* more
precisely than prose (a state shape, a reducer) — and even then only the decision-bearing part.

> Report as: the leaking line, and which layer it belongs to.

## P-3 — Unbounded scope (blocker)

No "Out of Scope" section, or one so thin the feature's edges are undefined — leaving the design grill
an open field. A scope lock that doesn't say what's *out* hasn't locked anything.

## P-4 — Solution stated as mechanism, not user value (concern)

The "Solution" section describes what the system does internally rather than what the user can now
do. The PRD's solution is the user's-eye view; the mechanism is the design doc's.

## P-5 — User stories don't cover the solution (concern)

A capability named in the Problem/Solution with no user story exercising it, or stories that
contradict the stated scope. The stories are the coverage check on the solution.

## P-6 — Problem not grounded (concern)

The problem is asserted abstractly with no sense of whose pain it is or what it costs — so there's no
way to tell whether the solution actually addresses it.

---

## Reporting

- **`file`** / **`line`** — where the defect starts.
- **`criteria_rule`** — the rule ID (`P-2`).
- **Severity**: `blocker` for P-1 to P-3 (the PRD is unusable as a scope lock or wrong-altitude);
  `concern` for P-4 to P-6 (it will mislead the design grill).
- Quote the offending text. **Do not pad** — three real defects should produce exactly three
  findings.
