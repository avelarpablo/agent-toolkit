# Design Doc criteria — for a technical design document

Grade whether this Design Doc is **buildable and verified**: the how is concrete, its claims about the
existing code are backed by evidence, and it traces to the PRD it implements. This gate has a partial
reality anchor — the code — so an unbacked claim about the code is a hard defect, not a matter of
taste. Do not re-litigate the chosen approach; find where it is unverified, incomplete, or incoherent.

**Out of scope — do not report:** preferring a different design; style or tone; sections the author
didn't ask for.

---

## D-1 — Load-bearing claim with no evidence (blocker)

A statement about what the existing code does — an interface, a behavior, a constraint — that a
decision rests on, with **no `file:line` citation or spike result** backing it. The whole point of a
verified grill is that these are checked; an unbacked claim is an assumption wearing a fact's clothes.

> Report as: the claim, and the decision that depends on it.

## D-2 — Incomplete contract (blocker)

A module interface, schema change, or API contract named but left underspecified — a signature with
no inputs/outputs, a schema change with no migration path, an endpoint with no request/response
shape. A slice built from this would have to invent the missing half.

## D-3 — Doesn't trace to the PRD (blocker)

The design doesn't reference its parent PRD, or implements something the PRD's success criteria never
asked for (scope invention), or leaves a success criterion with no design that satisfies it.

> Report as: the criterion or the invented scope, and the gap.

## D-4 — Internally incoherent (blocker)

Two parts of the design that cannot both hold — a module contract that contradicts a schema, a data
flow that can't produce a stated output, an interface used one way here and another there. (This is
coherence's C-1 applied to the design.)

## D-5 — No rejected alternatives where a real fork existed (concern)

A significant decision presented as inevitable when a genuine alternative existed, with no note of
what was considered and why the evidence killed it — inviting the fork to be reopened downstream.

## D-6 — Testing strategy absent or unfalsifiable (concern)

No testing strategy, or one that names no concrete behavior to test and no prior art — so there's no
way to know the build is correct.

---

## Reporting

- **`file`** / **`line`** — where the defect starts.
- **`criteria_rule`** — the rule ID (`D-1`).
- **Severity**: `blocker` for D-1 to D-4 (the design is unverified or unbuildable); `concern` for D-5
  to D-6 (it will mislead the slicing and build).
- Quote the offending text, and for D-1 name the missing evidence. **Do not pad.**
