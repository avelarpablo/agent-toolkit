---
name: design-step
description: The feature-level design/prototype stage (stage:design) — for a UI-meaningful feature, generate several prototype variations in the project's real design system on a design/ branch, hold for the human's pick, then freeze the approved screenshots onto the feature issue. The one planning activity that produces code. Use when a PRD is ready and the feature has meaningful UI to settle before slicing.
argument-hint: "<issue#> — the feature to design"
---

# design-step — the prototype stage

The one pre-slice activity that **commits code**, and the reason `stage:design` exists: agent UI
*discussion* reliably diverges from delivered UI, so the look & feel is pinned down as an approved
prototype before implementation. Feature-level, optional — **non-UI features skip it entirely.**

Two paths, chosen by design-step triage:

- **Salvage (default for UI-meaningful features).** Build the variations in the project's **real
  design system / component library** — not a throwaway aesthetic (a throwaway look that gets
  re-styled is itself a divergence source). The approved variation becomes the dev loop's starting
  point.
- **Throwaway (minor / low-risk UI).** Keep only frozen screenshots as the reference; the dev loop
  builds from scratch against them.

## Flow

1. **Open the design worktree** — via the [`dev-flow`](../../runners/dev-flow/runner.json) runner:

   ```bash
   dev-flow create design <issue#> <slug> --base main
   ```

   The orchestrator has set the feature to `stage:design` + `needs:human` (board-visible, the way
   `stage:verify` is). Work happens in this worktree so `main` stays pristine.

2. **Generate several variations.** Reuse the [`prototype`](../../../../primitives/skills/prototype/SKILL.md)
   UI branch's approach — several radically different variations on one route, switchable from a
   floating bar — but in **salvage mode**: built in the real design system, and kept, not thrown
   away. (Throwaway path: ordinary prototype rules, screenshots only.)

3. **Hold for the human pick.** This is the gate. Present the variations; the human approves one.
   Do not proceed on your own judgment — `needs:human` is on the issue for exactly this.

4. **On approval:**
   - **Freeze the screenshots** of the approved variation **onto the feature issue** (the durable,
     canonical visual-acceptance reference the QA loop reads later). Both paths do this.
   - **Hold the `design/…` branch.** Do **not** seed or delete it now — the target branch (`feat/…`
     vs a lone `slice/…`/`task/…`) isn't known until slicing decides the shape. `dev-flow seed`
     runs later, at target-branch creation.
   - **Clear `stage:design`** and return the feature to **shaping** (Design Doc → slicing). It carries
     **no** `stage:` label until the all-slices-merged rollup sets `stage:verify`. It does **not**
     go to `stage:ready` — that label is slice-level.

## Handoff

The approved prototype is a **binding input**: the Design Doc references it, and the QA loop validates
against the frozen screenshots. Point the user at `grill-design-doc` next (the how, against this
approved look).
