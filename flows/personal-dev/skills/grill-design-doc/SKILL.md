---
name: grill-design-doc
description: Grill the technical how of a feature into a Design-Doc-ready decision set, verified against the real codebase. The machine resolves every technical question with evidence — grep, read, runnable spikes — and kills dead options before the user sees them, so the user answers only direction, priority, and values. Leaves a resumable working file the `to-design-doc` producer publishes. Use after a PRD exists, or when the user says "grill the design" / "grill the how". A profile of the `grill` engine.
argument-hint: "<slug> — the feature whose design to settle"
---

# Design-Doc profile

A profile of the [`grill` engine](../../../../primitives/skills/grill/SKILL.md) — follow its spine
and FIC wiring, with the knobs below. This grill decides **how**, verified against the real code. It
assumes a **PRD** (the what/why) already exists and, for a UI feature, an **approved prototype** to
build against. It **interviews and records**; the separate `to-design-doc` producer publishes.

## Knobs

- **verification: `evidence-first`.** This is the point of the profile. Split every question:
  - **The machine answers** "does this work?", "does the library support it?", "what does the code
    actually do?" — with evidence: `grep`/read (cite `file:line`), a **runnable spike** in the
    project's test framework, or a research subagent. Resolve these silently; **do not ask the user
    to confirm a fact the code answers.**
  - **The user answers** only genuine direction: priority, scope, values, policy — pre-loaded with
    the evidence you gathered.
  - **Kill dead options with evidence** before they reach the user. A moot question is not asked.
- **doc integration: `none`.** The artifact here is evidence-backed technical decisions, not the
  glossary. (Terminology was sharpened in the PRD grill.)

## Framing (open with these)

1. **The anchor** — the PRD's success criteria and, if any, the approved prototype. Everything must
   trace back to them.
2. **The seams** — which existing modules/interfaces this touches, established by *reading them*, not
   by asking.
3. **The riskiest unknown** — the one "does this even work?" whose answer reshapes the rest. Spike it
   first.

Then walk the decision tree per the engine spine — machine-resolving as you go, surfacing only real
decisions.

## FIC

```bash
FIC="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/fic/fic"
"$FIC" init <slug> --dir .grill --skill grill-design-doc --resume-cmd "/grill-design-doc <slug>" --title "Design: <feature>"
```

Idempotent — if the session exists, `"$FIC" resume <slug>` and continue from `Next step`. Spikes and
evidence live as siblings in `.grill/<slug>/` (`spikes/`, `evidence/`); checkpoint each resolved
question **with its citation** the moment it lands.

## Output — what the working file must hold for `to-design-doc`

- **Modules / interfaces touched**, and how — each verified against the code
- **Schema changes** and **API contracts**
- **Testing strategy** (unit/integration here; e2e is QA's, later)
- **The approved prototype referenced** as the visual acceptance target (UI features)
- **Every load-bearing claim carries its evidence** — a `file:line` or a spike result
- **Rejected alternatives** and why the evidence killed them

When these are settled, tell the user the grill is complete and point them at `to-design-doc` to
publish (it reads this working file and links the parent PRD; it does not re-interview).
