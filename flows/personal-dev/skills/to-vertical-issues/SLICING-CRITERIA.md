# Slicing criteria — for a set of vertical slices

Grade whether these slices are **genuinely vertical, independent, and buildable**. The design is
given; find the slices that are horizontal layers in disguise, whose demos don't prove them, or whose
plans a build loop couldn't execute. This gate has a reality anchor — the demo commands run — so a
demo that can't fail-before-pass-after is a hard defect.

**Out of scope — do not report:** preferring a different decomposition granularity as taste; style;
sections not asked for. (Too-many-thin-slices *is* in scope when they're horizontal — see S-1.)

---

## S-1 — Horizontal layer disguised as a slice (blocker)

A slice that touches one architectural layer, or whose "after this merges, a developer can now…" can
only be completed by referencing a future slice. "Add the library", "add the type/schema", "write the
tests", "set up config" — none change observable behavior alone.

> Report as: the slice, and the layer it's stuck in / the future slice it leans on.

## S-2 — Demo doesn't prove the slice (blocker)

The demo command would pass **without** the slice (it exercises unchanged code), has no real
fail-before, or its execution path never traverses the slice's new code. The anchor is broken.

> Report as: the demo, and why it doesn't discriminate.

## S-3 — False independence (blocker)

Two slices where deleting one breaks the other, or a "Blocked by: None" that actually depends on
another slice's code. The dependency graph must be truthful and acyclic.

## S-4 — Implementation plan not executable (blocker)

The checkbox plan is missing, or so vague a build loop couldn't work it (no concrete steps, or steps
that assume decisions the Design Doc never made). A slice a loop can't execute isn't ready.

## S-5 — Doesn't deliver a PRD success criterion (concern)

The slice set, taken together, leaves a PRD success criterion with no slice that delivers it — or a
slice delivers scope the Design Doc/PRD never asked for.

## S-6 — Merge-order hazard unflagged (concern)

Two parallel slices modify overlapping lines in the same file with no note of the conflict or which
merges first.

---

## Reporting

- **`file`** / **`line`** — where the defect starts (the slice's title line).
- **`criteria_rule`** — the rule ID (`S-1`).
- **Severity**: `blocker` for S-1 to S-4 (the slice is horizontal, unproven, dependent, or
  unbuildable); `concern` for S-5 to S-6. **Do not pad.**
