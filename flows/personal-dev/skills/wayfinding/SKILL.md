---
name: wayfinding
description: The universal front door for new work — always a grilling session that first scope-triages the request into Task / Feature / Product, then dispatches it to the right grill profile (or builds a wayfinder:map for foggy product-scale work). Also dispatches inbox items by kind. Prevents a small task from exploding into a pile of issues and a foggy vision from being built blind. Use at the start of any new piece of work, or when picking an item up from the inbox.
argument-hint: "<what you want to build, or an inbox issue #>"
---

# wayfinding — the universal front door

Everything starts here, and it is always a grill. Wayfinding owns exactly two things: **scope triage**
(what shape is this?) and **dispatch** (route it to the right grill profile). It does **not** run the
grilling itself — grilling is the reusable engine; wayfinding is the policy that picks the profile.

"Universal front door" is conceptual, not "always run a heavy map." A clear task never pays the map
tax.

## First act — scope triage

| Shape | When | What it becomes |
|---|---|---|
| **Task** | small, self-contained | **one** issue — decisions, plan, checklist inside it. No map, no children. |
| **Feature** | one coherent feature | a PRD (+ Design Doc); slice issues only if large enough to ship in parts. |
| **Product / Epic** | app-scale or foggy vision | a `wayfinder:map` whose children are candidate features. |

Wayfinding is **scale-free**: at product altitude the map's tickets are *candidate features*; at
feature altitude they are *decisions*. Same mechanism, different altitude.

## Dispatch

- **Task** → a brief [`grill-task`](../grill-task/SKILL.md) → one issue (labelled by `triage`).
- **Feature** → skip the map. [`grill-prd`](../grill-prd/SKILL.md) → PRD; later, after the design
  step, [`grill-design-doc`](../grill-design-doc/SKILL.md) → Design Doc.
- **Product / foggy** → build a **`wayfinder:map`** issue holding **Destination · Decisions-so-far ·
  Fog · Out-of-scope**. Sharp decisions become **child tickets**, each resolved via
  [`grill-ticket`](../grill-ticket/SKILL.md), a prototype, or research; fog **graduates** into tickets
  as clarity grows; resolved candidate features graduate into PRDs (via `grill-prd`).

**Route each open decision by its type:** product/what → `grill-prd`; technical/how → `grill-design-doc`;
domain/terminology → knowledge-base sharpening (`grill` with doc integration, i.e. the old
grill-with-docs behavior).

## Dispatch from the inbox (by kind)

When an item is picked up from the inbox (a `kind:` issue with no `stage:`), dispatch by its kind — the
kind decides which analysis runs, and all paths converge at `stage:ready` with a plan:

| `kind:` | Analysis | Produces |
|---|---|---|
| `bug` | [`diagnose`](../../../../primitives/skills/diagnose/SKILL.md) — reproduce, root-cause | a failing test + a fix plan |
| `tech-debt` | scope the refactor (target usually known) | a refactor plan; often skips design |
| `wishlist` | wayfinding → PRD (research/POC as needed) → Design Doc | the full feature front-half |

## Research & POC — informal feeders, not stages

A map ticket names an unresolved decision; **research** (run in **subagents** for context isolation)
or a **POC** (the [`prototype`](../../../../primitives/skills/prototype/SKILL.md) skill) is *how it
gets resolved*. Their value is a **decision**, which lands in the map/PRD/Design Doc — they are never
logged as work and never build commits.
