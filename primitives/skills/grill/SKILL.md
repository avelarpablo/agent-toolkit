---
name: grill
description: Interview relentlessly, one question at a time, to turn a fuzzy plan or design into resolved decisions — walking the decision tree, recommending an answer to every question, investigating instead of asking whenever the answer is knowable, and checkpointing each decision so the session survives a restart. The reusable engine behind stage-specific grill profiles (PRD, Design Doc, …). Use when the user wants to be grilled, to stress-test a plan or design, or mentions "grill me" / "grill this"; a profile invokes it with tighter policy.
argument-hint: "<slug> — the topic to start or resume"
---

# The grilling engine

One reusable interviewing engine. On its own it is the generic grill (the old `grill-me`); a
**profile** ([Profiles](#profiles)) points it at a stage — a PRD, a design doc — by tightening a few
knobs. The engine names no stage, label, or artifact type, so a profile from any flow can drive it.

It is **FIC-aware**: state lives in a working file via the shared
[FIC protocol](../fic/PROTOCOL.md), never only in the conversation, so a fresh session resumes from
the file alone.

## The spine (always, every profile)

1. **Interview relentlessly** until you and the user reach shared understanding — don't stop at the
   first plausible answer.
2. **Walk the decision tree**, resolving dependencies **one-by-one**: a decision that unblocks others
   comes first.
3. **One question at a time.** Ask, then *wait for the answer* before the next — never batch.
4. **Recommend an answer** to every question, with your reasoning. The user corrects; they don't do
   your thinking.
5. **Investigate instead of asking** whenever a question is answerable — from the codebase, the
   docs, or a subagent (research/search in isolation, per FIC). Bring the user the finding, not the
   question.

## FIC wiring (always)

```bash
FIC="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/fic/fic"
```

- **On start** — `"$FIC" init <slug> --dir <dotdir> --skill <skill> --resume-cmd "<cmd>" --title "…"`.
  `init` is idempotent: if the session exists, `"$FIC" resume <slug>` and continue from `Next step`.
  The generic grill uses `--dir .grill --skill grill --resume-cmd "/grill <slug>"`; a profile passes
  its own.
- **Every decision** — `"$FIC" checkpoint <slug> "…"` the moment it lands (the resolved question +
  the evidence or reasoning that settled it, and any killed alternative). This is what makes the
  session loss-free; get it rock-solid before anything else.
- **Keep `--next` honest** — `"$FIC" header <slug> --next "…"` whenever the next open question moves.
- **On "let's start fresh" / a long session** — refresh the full header, `"$FIC" compact <slug>`,
  hand the user the printed resume command.

See [`fic/PROTOCOL.md`](../fic/PROTOCOL.md) for the full contract — the engine implements it, it does
not re-invent it.

## Profiles

A profile is thin: it sets the knobs below and adds stage-specific framing, then runs this spine.

| Knob | Values | What it changes |
|---|---|---|
| **verification** | `opportunistic` (default) · `cross-ref` · `evidence-first` | How hard step 5 investigates. `cross-ref`: catch contradictions between what the user says and what the code/docs show. `evidence-first`: the machine resolves every *technical* question with evidence (grep, read, runnable spikes) and **kills dead options before the user sees them** — the user answers only direction/priority/scope/values. |
| **doc integration** | `none` (default) · `read+update` | Whether to read the project's `CONTEXT.md`/ADRs, sharpen terminology against the glossary, and update them inline as decisions crystallize. |
| **framing** | profile-supplied | Opening questions that anchor the interview (scope, governing principle, the decision space). |
| **output** | profile-supplied | What the working file must contain so the stage's *producer* (a separate skill) can synthesize and publish it. The grill interviews; it does not publish. |

A profile is its own FIC-aware skill: it passes its own `--dir`, `--skill`, `--resume-cmd` to
`init`, so re-entering the profile picks up the same working file. The profile's `SKILL.md` says
"a profile of the `grill` engine — follow its spine and FIC wiring, with these knobs," then lists
them. Keep it short; the behavior lives here.

## Guardrails

- **Never confirm a fact you can check** — under `evidence-first`, resolve it and move on; asking the
  user to confirm what the code already answers wastes the one scarce resource (their judgment).
- **Don't spiral.** If one question spawns more than a handful of branching unknowns, checkpoint the
  branch, surface it, and let the user pick where to dig — don't silently recurse.
- **Checkpoint dead ends too**, so a resumed session doesn't re-explore them.
