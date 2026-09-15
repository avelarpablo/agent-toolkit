---
name: grill-task
description: Grill a small, self-contained task into one buildable issue — a lightweight scoped interview that settles the few open questions and leaves decisions, a plan, and a checklist inside a single issue. No PRD, no map, no children. Use when wayfinding triaged the work as a Task, or the user wants a small clear job turned into one ticket. A profile of the grill engine.
argument-hint: "<slug> — the task to shape"
---

# Task profile

A profile of the [`grill` engine](../../../../primitives/skills/grill/SKILL.md) — follow its spine and
FIC wiring, lightly. A task is small and self-contained, so this is the **cheapest** grill: settle the
handful of real questions, no more. Ceremony scales with scope, and a task has little.

## Knobs

- **verification: `opportunistic`** — investigate when a question is quickly answerable from the code;
  don't mount a campaign.
- **doc integration: `none`** (respect existing ADRs/glossary, but this isn't where they're sharpened).

## Framing

1. **The one job** — what, concretely, and how you'll know it's done.
2. **The blast radius** — what it touches; anything surprising there?
3. **Any real fork** — the few decisions that aren't obvious. Recommend an answer to each.

## FIC & output

```bash
FIC="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/fic/fic"
"$FIC" init <slug> --dir .grill --skill grill-task --resume-cmd "/grill-task <slug>" --title "Task: <job>"
```

Output is **one issue** carrying, inline: the decisions, a short implementation plan (checkbox steps),
a demo/acceptance check, and a `kind:` (usually none — a task is often just work). It goes through
`triage` to `stage:ready`; no separate producer, no slicing.
