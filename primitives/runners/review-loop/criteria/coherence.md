# Coherence criteria — for plans, specs and design documents

Grade a document on whether it **holds together**, not on whether you like its decisions. The
author's choices are given; your job is to find the places where the document contradicts itself,
points at nothing, or cannot be executed as written.

A plan is where mistakes are cheapest to fix. Every defect found here is one that would otherwise
be found during implementation, at many times the cost.

**Out of scope — do not report these:** disagreement with a decision the document records; style,
tone or formatting; suggestions to add sections the author didn't ask for; anything that amounts to
"I would have designed this differently."

---

## C-1 — Contradiction (blocker)

Two statements in the document that cannot both be true. The most valuable finding and the hardest
to see, because the halves are usually far apart.

Includes a decision recorded in one section and silently reversed in another; a rule stated
absolutely and then broken by a later example; two sections that assign the same responsibility to
different owners.

> Report as: both locations, both statements, and why they conflict.

## C-2 — Duplicate concept under two names (blocker)

The same state, role or artifact appearing twice under different names, where nothing in the
document distinguishes them. Left unresolved, each name grows its own behavior and the two drift.

> Report as: both names, and the evidence they denote one thing.

## C-3 — Orphaned reference (blocker)

Something **named but never defined**, or **defined but never consumed**:

- a label, state, file or command referenced but never specified
- a producer with no consumer — something written that nothing reads
- a consumer with no producer — something read that nothing writes
- a cross-reference to a section, document or issue that does not exist

> A step that writes state nothing acts on is a dead end, and is a blocker even when every
> individual sentence is correct.

## C-4 — Ordering violation (blocker)

A step whose prerequisite comes later, or a dependency graph that cannot be topologically sorted.
Check declared prerequisites against the order actually presented, and check that anything called
"first" or "foundation" truly has no upstream dependency.

## C-5 — Unfalsifiable acceptance criterion (concern)

A "done-when", success criterion or definition of done that no one could test — no observable
output, no command to run, no state to inspect. "Works well", "is clean", "handles errors
gracefully" are all unfalsifiable.

> Report as: the criterion, and what specifically cannot be observed.

## C-6 — Resolved but not decided (concern)

A question marked RESOLVED, DECIDED or ✅ where the resolution is missing, vague, or does not
actually answer the question asked. Also: an open question that a later section silently answers
without marking it resolved.

## C-7 — Unstated assumption load-bearing for a decision (concern)

A decision that only holds if something unstated is true — a capability that may not exist, a
tool's behavior taken on faith, a claim about a system nobody verified. Flag the assumption and
what depends on it.

> Especially: "the agent will watch/notice/remember X" — self-monitoring assumptions that fail
> silently.

## C-8 — Scope leak (nit)

A section that specifies something belonging to a different layer or altitude — implementation
detail inside a requirements document, policy inside a mechanism spec, or a decision that the
document elsewhere says is deferred.

---

## Reporting

- **`file`** — the document path. **`line`** — the line the defect starts on. Cite the *earlier*
  location when a defect spans two places, and name the other location in the description.
- **`criteria_rule`** — the rule ID above (`C-3`), so findings can be grouped.
- **Severity**: `blocker` for C-1 to C-4 (the document is wrong or unexecutable); `concern` for C-5
  to C-7 (it will mislead someone); `nit` for C-8.
- Quote the offending text. A coherence finding no one can locate is worthless.
- **Do not pad.** A document with three real contradictions and no other defects should produce
  exactly three findings. Inventing minor findings to look thorough buries the real ones.
