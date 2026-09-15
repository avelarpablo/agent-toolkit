---
name: grill-prd
description: Grill a feature into a PRD-ready decision set — the product what & why & scope, no implementation detail. Interviews one question at a time against the project's own domain language, sharpening terminology and catching contradictions with the existing model, and leaves a resumable working file the `to-prd` producer publishes. Use when shaping a feature before a PRD, or when the user says "grill the PRD" / "grill this feature". A profile of the `grill` engine.
argument-hint: "<slug> — the feature to shape"
---

# PRD profile

A profile of the [`grill` engine](../../../../primitives/skills/grill/SKILL.md) — follow its spine
and FIC wiring, with the knobs below. This grill decides **what & why**, never **how**: no modules,
schemas, or API contracts (that is the [`grill-design-doc`](../grill-design-doc/SKILL.md) profile,
later). It **interviews and records**; the separate `to-prd` producer synthesizes and publishes.

## Knobs

- **verification: `cross-ref`.** Investigate to catch **contradictions** between what the user says
  and what the code/docs already show ("you said partial cancellation is possible, but the code
  cancels whole orders — which is right?"). Do *not* prove technical feasibility here — that is the
  design-doc grill's job.
- **doc integration: `read+update`.** Discover the project's `CONTEXT.md` / `docs/adr/` (or a
  `CONTEXT-MAP.md` for a multi-context repo). Challenge fuzzy language against the glossary, sharpen
  it to canonical terms, and update `CONTEXT.md` **inline** as terms settle. Offer an ADR only when a
  decision is hard-to-reverse **and** surprising **and** a genuine trade-off.

## Framing (open with these)

1. **Problem** — whose pain, and what does it cost them today? Push until it's concrete.
2. **Solution, from the user's side** — what they can now do, described without a single
   implementation word.
3. **Scope boundary** — what is explicitly *out*, so the design grill isn't handed an open field.

Then walk the decision tree per the engine spine, one question at a time, recommending an answer to
each.

## FIC

```bash
FIC="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/fic/fic"
"$FIC" init <slug> --dir .grill --skill grill-prd --resume-cmd "/grill-prd <slug>" --title "PRD: <feature>"
```

Idempotent — if the session exists, `"$FIC" resume <slug>` and continue from `Next step`. Checkpoint
every settled question the moment it lands.

## Output — what the working file must hold for `to-prd`

- **Problem** and **solution (user's view)**
- **User stories**
- **Success criteria** — *measurable*; a criterion no one can test is not done
- **Out-of-scope**
- **No implementation detail** — if it names a module, table, or API, it belongs in the design doc

When these are settled, tell the user the grill is complete and point them at `to-prd` to publish
(it reads this working file; it does not re-interview).
