---
name: grill-ticket
description: Grill a single open decision on a wayfinder:map to resolution — a focused interview that walks one branch of the decision tree and records the resolution back onto the map ticket. Use when resolving a sharp decision surfaced by wayfinding on a product/epic map. A profile of the grill engine.
argument-hint: "<slug or map-ticket #> — the decision to resolve"
---

# Wayfinding-ticket profile

A profile of the [`grill` engine](../../../../primitives/skills/grill/SKILL.md) — follow its spine and
FIC wiring, scoped to **one decision**. A [`wayfinding`](../wayfinding/SKILL.md) map holds Destination,
Decisions-so-far, Fog, and Out-of-scope; a sharp decision became a child ticket, and this resolves it.

## Knobs

- **verification: `as-needed`** — if the decision turns on a fact about the code or a library, resolve
  it with evidence (or a research subagent / a `prototype` POC) rather than asking; bring the finding
  back. If it's a pure direction/values call, just grill it.
- **doc integration: `none`** here (terminology lives on the map / in `CONTEXT.md`).

## Framing

1. **The decision, stated sharply** — what exactly is being decided, and what turns on it (which
   downstream tickets or fog it unblocks).
2. **The live options** — with your recommended one and its reasoning; kill dead options with evidence.
3. **The commitment** — the chosen answer, and what it now makes decidable next.

## FIC & output

```bash
FIC="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/fic/fic"
"$FIC" init <slug> --dir .grill --skill grill-ticket --resume-cmd "/grill-ticket <slug>" --title "Decision: <topic>"
```

Output is a **resolved map ticket**: record the resolution (and the killed alternatives) back onto the
ticket and update the parent map — move the item from Fog/Decisions-so-far to resolved, and surface any
new decision or candidate feature the resolution unlocked. A resolved candidate feature graduates into
a PRD via `grill-prd`.
