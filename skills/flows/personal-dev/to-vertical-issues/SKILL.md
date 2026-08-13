---
name: to-vertical-issues
description: Break a plan, spec, or PRD into independently-demoable vertical slice issues on GitHub. Use when user wants to convert a PRD/plan into implementation tickets, break down work into issues, or slice a spec into shippable increments. Enforces mandatory code exploration, demo-command validation, and anti-pattern rejection before publishing.
---

# To Vertical Issues

You are breaking a plan into vertical slice issues that an engineer can implement and ship independently. Your job is to find the thinnest end-to-end paths through the system — NOT to decompose by layer or module.

The litmus test for every slice you produce: **"After ONLY this slice merges, what can a developer DO that they could not do before?"** If the answer is "nothing observable" or "run a test that proves an interface exists," it is not a slice — merge it into the slice that gives it meaning.

**Fewer, fatter slices are almost always better than more, thinner ones.** Each additional slice adds coordination overhead, merge-conflict risk, and integration surface. Default to 2-4 slices unless the plan is genuinely large (10+ person-days). If you have more than 5, critically ask whether some are horizontal layers pretending to be independent.

## Process

### 1. Gather the source material and execution context

Work from conversation context. If the user passes an issue reference (number, URL, or path), fetch its full body and comments from the issue tracker.

**Before drafting slices, understand the execution context.** Ask (or infer from the PRD/conversation):
- How much time is available? (tonight vs. a sprint vs. a quarter)
- Is this being implemented by one person or many? (serial vs. parallel execution)
- What's the critical path for a demo or delivery?
- What happens if only half the slices ship — is the system still demoable?

These constraints determine optimal slice thickness and ordering. A one-night deadline with one engineer demands 2-3 fat slices. A two-week sprint with a team can support finer decomposition.

### 2. Explore the codebase (MANDATORY)

Before drafting any slices, read the files that the plan will touch:

- Every existing file the plan mentions modifying
- Test files in the affected areas (for existing patterns)
- Dependency manifests and build configuration
- Architectural docs, decision records, or project conventions
- CI/coverage config or deployment manifests

**Why:** You cannot draw a slice boundary without knowing the current shape of the code. Every assumption you make about a file you haven't read is a potential horizontal layer hiding as a slice.

After exploring, write a brief "Current State" summary noting: what exists, what's missing, what patterns you must follow, and anything surprising.

### 3. Draft slices with inline validation

For each candidate slice, write these fields IN ORDER. The order is intentional — it forces you to justify before detailing:

1. **Title** — short name
2. **After this merges, a developer can now:** — complete this sentence in concrete terms. This is the slice's reason to exist. If you cannot complete it without referencing a future slice, this is not independent.
3. **Demo command** — the ONE command that proves it. Must exercise real infrastructure when available. See the demo validation rules below.
4. **Fail-before evidence** — describe what happens when you run the demo command today (before the slice). If it already passes, your demo doesn't prove your slice. Acceptable fail-before examples: `ModuleNotFoundError`, `No such file or directory`, a test assertion failure, a missing CLI subcommand, a UI element that doesn't exist. If you cannot articulate a fail-before, the demo is not exercising new behavior.
5. **What the demo proves** — not "class exists" but what *integration behavior* is verified. Trace the demo: does the command's execution path cross through the new/modified code? If it only exercises unchanged code, it's not proving your slice.
6. **Layers cut** — which files/modules, end-to-end
7. **Type** — AFK (implementable without human decisions) / HITL (requires architectural decision or design review)
8. **Blocked by** — which other slices must complete first, or "None"
9. **User stories covered** — if the source material has them

#### Demo validation rules

The demo command is the slice's proof of life. Apply these rules strictly:

1. **It must FAIL before and PASS after.** If the command would succeed identically before your slice (e.g., opening a file that already exists, running tests that already pass on other code), it is NOT a valid demo.

2. **Prefer real infrastructure over mocks.** The demo hierarchy (strongest → weakest):
   - Real app running against real infrastructure (DB, API, browser)
   - Integration test against real infra
   - Unit test with synthetic data (no mocks)
   - Unit test with mocked dependencies (weakest — acceptable only when real infra is unavailable)

3. **The execution path must traverse your new code.** Trace the command mentally: does it actually invoke the functions you wrote? "Run the app" only counts if the new behavior is visible in the running app.

4. **Test suites are secondary validation, not primary demos.** `pytest` proves correctness of logic. The primary demo proves the system WORKS end-to-end. Include both where applicable, but lead with the real-infrastructure demo.

### 3.5. Self-Grill (MANDATORY)

Before restructuring, **attack your own draft.** Pretend you're a senior engineer receiving these tickets. Write 3-5 sentences of honest critique:

- Which slices are actually horizontal layers with a vertical-sounding name?
- Which demo commands would pass even WITHOUT the slice? (They're testing unchanged code.)
- Which slices only touch one layer? Are they faking verticality?
- Are you producing too many thin slices when fewer fat ones would be more honest?
- If the user ran out of time after implementing only the first slice, would the system be better — or would it be half-broken?

Write your critique explicitly in the conversation. Then use it to inform the restructure step. This is not optional — skipping it produces mediocre output.

### 4. Restructure

After drafting all slices AND completing the self-grill, step back and critically re-examine them as a set:

**Independence check:** For each slice, ask — if I delete this slice entirely, does another slice break? If yes, one of them is not truly independent. Either merge them or redraw the boundary so each stands alone.

**Integration check:** Does this slice's demo command prove a *behavior through connected layers*, or does it only prove that a unit satisfies an interface? A unit test asserting "class X has methods Y and Z" is not a vertical demo — the vertical demo is the integration that *uses* X to produce an observable result.

**Layer check (HARD GATE):** If a slice modifies files in only ONE architectural layer and its demo doesn't traverse at least two layers of the system (e.g., data → logic → UI, or API → service → database), it MUST merge into the vertical slice that provides its underlying data or behavior. No exceptions. "Consider merging" is not acceptable — single-layer slices are horizontal by definition.

**Risk ordering:** Order by blast radius. Slices that can break the system or invalidate other work come first. Slices that are cosmetic, additive-only, or depend on stable outputs come last. Ask: "If I run out of time after slice N, is the system still demoable?" Earlier slices should leave the system MORE demoable, not less.

**Parallelism check:** Look at your dependency graph. Could slices be restructured so that more of them start simultaneously? If the plan is large enough that multiple engineers (or agents) would work on it in parallel, prefer a breakdown where independent slices can proceed concurrently. For smaller scoped work where serial execution is natural, fewer coarser slices may be optimal. Use your judgment based on the scope and complexity of the plan.

**Shared-file conflict check:** For every pair of parallel slices, list every file each modifies. Flag overlapping files and assess: are changes on different lines (auto-mergeable) or overlapping lines (conflict risk)? If two slices modify overlapping lines in the same file, either merge the slices or explicitly note the conflict risk and which slice should merge first.

**Slice count check:** If you have more than 5 slices, you are almost certainly producing horizontal layers. Go back and merge until you have 2-4 genuinely vertical slices. The right number of slices for most work is 3.

After restructuring, the number of slices may go up or down — what matters is that each one independently passes the litmus test, not that you hit a target count.

### 5. Present to user

Show the breakdown as a numbered list with all fields from Step 3. Include:

- A dependency graph (ASCII) showing parallel vs serial relationships
- A "Parallelism" note stating which slices can start simultaneously and whether the breakdown is optimized for parallel or serial execution

Then ask:
1. Does the granularity feel right?
2. Are dependencies correct?
3. Should any slices be merged or split?
4. Are HITL/AFK designations correct?

Iterate until approved.

### 6. Publish issues to GitHub

For each approved slice, publish using the template below. Apply `needs-triage` label. Publish in dependency order (blockers first) so you can reference real issue numbers.

<issue-template>
## Parent

Link to the parent issue (if source was an existing issue).

## What to build

Concise description of this vertical slice — end-to-end behavior, not layer-by-layer.

## After this merges, a developer can now:

One sentence. Concrete. Observable.

## Demo command

```
<exact command>
```

## Acceptance criteria

- [ ] Demo command passes and asserts [specific integration behavior]
- [ ] [Additional criteria]

## Files to modify

- `path/to/file` — what changes
- `path/to/other` — what changes

## Blocked by

- #XX (title) — or "None — can start immediately"

## Notes

Optional. Implementation context that isn't an acceptance criterion: infrastructure requirements (VPN, tokens, credentials), gotchas, design decisions from the PRD that constrain implementation, pointers to relevant existing code, or cache/migration concerns.
</issue-template>

Do NOT close or modify any parent issue.

---

## Anti-patterns to reject

These are horizontal layers pretending to be slices:

| Shape | Why it fails | Fix |
|-------|-------------|-----|
| "Add the library/helper/utility" | No consumer proves it works; dead code until something uses it | Merge into the slice that first consumes it |
| "Add the interface/type/schema" | Type definitions alone change no behavior | Include with the first code path that uses the type |
| "Write the tests" | Tests prove a slice works — they ARE the slice's verification, not a separate deliverable | Tests always ship inside the slice they verify |
| "Set up the config/plumbing" | Pure infrastructure with no observable behavior change | Merge into the slice whose behavior it enables |
| "Unrelated housekeeping bundle" | No coherent behavior change; demo is "existing tests still pass" — a grab-bag of fixes grouped because they're all "small" or "prerequisite" | Distribute each fix into the slice whose behavior it enables; if a fix has no downstream consumer, it's a standalone one-liner, not a slice |
| "Single-layer UI/API addition" | Only touches one layer; demo doesn't traverse the stack | Merge into the vertical that provides the underlying data/logic it displays |
| "Presentation/cosmetic first" | Cosmetic work before system is validated; wastes time if system breaks | Move to end; system stability first, polish last |
