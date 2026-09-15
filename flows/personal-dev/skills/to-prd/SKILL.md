---
name: to-prd
description: Synthesize a grill-prd working file into a PRD and publish it to the project issue tracker — the product what & why & scope with measurable success criteria, no implementation detail. Does NOT interview (grill-prd already did); it synthesizes, gates against a second family, and publishes. Use when a PRD grill is complete and the user wants it published.
argument-hint: "<slug> — the grill-prd session to publish"
---

# to-prd — the PRD producer

Synthesizes, it does not interview. The [`grill-prd`](../grill-prd/SKILL.md) profile already ran the
interview and left a working file; this skill turns that file into a published PRD. If there is no
working file, stop and point the user at `grill-prd` — do not start asking questions here.

The issue tracker, label vocabulary and Project (with its `Status` field) come from
`setup-agent-skills`; run `/setup-agent-skills` if they aren't set up.

## Process

1. **Load the working file** — `fic resume <slug> --full` (dir `.grill`). Everything the PRD needs
   was settled and checkpointed there; read it, not the live conversation.

2. **Draft the PRD** from the [template](#prd-template). It is **what & why only** — no modules,
   schemas, API contracts, or file paths (those are the design doc's, via `to-design-doc`). Use the
   project's domain glossary throughout.

3. **Gate before publishing** (principle 11 — no artifact is final until a second family reviews it):

   ```bash
   REVIEW="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/review-loop/review-loop"  # or primitives/runners/review-loop
   "$REVIEW" --files <draft.md> --criteria <this skill>/PRD-CRITERIA.md --rounds 2
   ```

   Two rounds is the floor (round 1 is your own family; the second family enters at round 2). Address
   every blocker, re-run if needed, and only then publish. A PRD gate has **no reality anchor** — the
   findings are advisory input to your judgment; you decide when they're resolved.

4. **Publish** — create the issue with the PRD body. It is the parent **feature** issue: it carries a
   `kind:` if it came from the inbox, **no `stage:` label** (it is being shaped, not built), and the
   producer sets its Project **`Status` to `Shaping`** (the producers' disjoint Status write). Leave a
   pointer back in the working file's header (`fic header <slug> --pointers`).

## PRD template

```
## Problem
Whose pain, and what it costs them today. Concrete.

## Solution (user's view)
What the user can now do — described without a single implementation word.

## User Stories
A long, numbered list: "As an <actor>, I want <capability>, so that <benefit>." Cover every aspect.

## Success Criteria
Numbered and MEASURABLE — each names an observable outcome someone could test. A criterion no one
can check ("works well", "is fast") is not a criterion. These become the verification plan later.

## Out of Scope
What this feature explicitly does not cover — so the design grill isn't handed an open field.
```

**No implementation detail.** If a line names a module, table, endpoint, or file, it belongs in the
design doc — move it. The one exception the design carries, not this: a prototype-derived snippet.
