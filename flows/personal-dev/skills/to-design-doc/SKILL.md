---
name: to-design-doc
description: Synthesize a grill-design-doc working file into a Design Doc and publish it, linked to its parent PRD — the technical how, verified against the real codebase, with the approved prototype as reference. Does NOT interview (grill-design-doc already did); it synthesizes, gates against a second family over three rounds, and publishes. Use when a design grill is complete and the user wants it published.
argument-hint: "<slug> — the grill-design-doc session to publish"
---

# to-design-doc — the Design Doc producer

Synthesizes, it does not interview. The [`grill-design-doc`](../grill-design-doc/SKILL.md) profile
ran the verified technical interview and left a working file (decisions, each with its `file:line` or
spike evidence). This skill turns that into a published Design Doc linked to its **parent PRD**. If
there's no working file, stop and point the user at `grill-design-doc`.

The tracker, labels and Project come from `setup-agent-skills`.

## Process

1. **Load the working file** — `fic resume <slug> --full` (dir `.grill`). It holds the how, already
   verified against code; carry the evidence citations through, don't re-derive them.

2. **Draft the Design Doc** from the [template](#design-doc-template), referencing the parent PRD and
   (for a UI feature) the approved prototype's frozen screenshots as the visual acceptance target.

3. **Gate before publishing** (principle 11) — **three rounds**, because a design doc spawns slices
   and its mistakes are the most expensive downstream:

   ```bash
   REVIEW="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/review-loop/review-loop"
   "$REVIEW" --files <draft.md> --criteria <this skill>/DESIGN-DOC-CRITERIA.md --rounds 3
   ```

   The design-doc gate has a **partial anchor** — claims are checked against the code — so treat
   "claim without evidence" findings as binding, not advisory. Address every blocker, re-run, publish.

4. **Publish** — create the Design Doc issue, **linked to the parent PRD** (`owner/repo#N` if the PRD
   lives in an umbrella repo). It carries no `stage:` label (still shaping); the producer sets Project
   **`Status` to `Shaping`**. Leave a pointer in the working file's header.

## Design Doc template

```
## Parent PRD
Link. This design implements that PRD's success criteria — restate them as the acceptance target.

## Approach
How we build it, in prose. The chosen shape and why, referencing the prototype for UI.

## Modules & Interfaces
Each module touched or added, its interface, and — for every load-bearing claim about existing code
— the `file:line` (or spike result) that verified it. Prefer deep modules with simple, testable
interfaces.

## Schema & API Contracts
Schema changes and API contracts, concretely.

## Testing Strategy
Unit/integration coverage and prior art in the repo. (e2e is written later, in QA — not here.)

## Rejected Alternatives
Options considered and the evidence that killed each — so they aren't reopened.
```

One Design Doc per PRD; fan out only for genuinely independent sub-features.
