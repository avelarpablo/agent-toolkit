# The Development System

How we take software from a vague idea (or an empty repo) to shipped, verified, documented
code — and how feedback loops back. This is the umbrella. Its one **fully-designed** part is the
[Feature Lifecycle](#the-feature-lifecycle); the other parts are designed skeletons we will
deepen later.

> Status: **in design, not built.** We are defining the standard. Existing skills/runners are
> referenced as the building blocks; they will be extended when we implement. Sections marked
> _Open_ or _Stub_ are not final.

---

## System map

Three **altitudes** of scope, two **lifecycles**, and a set of **cross-cutting axes**. The whole
thing is a **cycle**, not a line:

```
        ┌──────────────────── Project lifecycle ────────────────────┐
        │  init-docs (deep product/vision/domain grill + analyze     │
        │  existing code) → CONTEXT.md, glossary, ADRs, agentic      │
        │  files, MONITORING.md   ·   sync-docs keeps it fresh       │
        └───────────────────────────┬───────────────────────────────┘
                                     │ establishes context for everything
                                     ▼
   Wayfinding (the universal front door — always a grill)
                                     │  scope triage picks a shape:
             ┌───────────────────────┼───────────────────────┐
             ▼                        ▼                        ▼
        PRODUCT / EPIC            FEATURE                    TASK
        wayfinder:map          PRD → Design →            one self-
        children = features    Design Doc → slices       contained issue
             │                        │                        │
             └───────────┬────────────┴────────────┬───────────┘
                         ▼                          ▼
                 ══════════════ Feature Lifecycle (build) ══════════════
                 dev → refactor → QA → verification → docs
                         │
                         ▼
                    Release / merged
                         │
                         ▼
        Feedback (monitoring → log → triage → diagnose) ──┐
                         ▲                                 │
                         └───────── loops back ────────────┘
```

**Altitudes** — every entry is a grill; scope decides the output:

| Altitude | Question | Output |
|---|---|---|
| **Product** | What should this app *become*? | a `wayfinder:map`; children = candidate features |
| **Feature** | What & how for one feature | PRD → Design → Design Doc → (slices) |
| **Task** | One small, clear job | a single self-contained issue |

**Lifecycles** — orthogonal:

- **Project lifecycle** — set up & maintain a project's knowledge base (`init-docs` / `sync-docs`).
- **Feature lifecycle** — build one feature end-to-end (the fully-designed part below).

---

## Guiding principles

1. **Understand → design → build → verify.** Never collapse these; each answers a different
   question and has a different owner.
2. **GitHub issues are the state machine and the source of truth.** Labels drive transitions;
   the issue is the durable, portable record. Durable cross-session state lives here — not in
   temp files.
3. **One issue per independently-buildable unit.** A task is one issue; slices become issues
   only when each ships on its own. Don't multiply issues for work that isn't separately
   shippable.
4. **Context before features.** A project's knowledge base (`CONTEXT.md`, glossary, ADRs) is
   established first so agents stop needing to be re-briefed.
5. **Prototype before build.** UI is pinned down as an approved prototype before implementation,
   because agent UI *discussion* reliably diverges from delivered UI.
6. **Mechanism vs. policy.** Runners own primitives; skills own pipeline knowledge; scripts own
   deterministic steps. See [Layering](#layering).
7. **Main stays pristine.** All build work happens in worktrees; the main tree is for human
   verification, one thing at a time.
8. **The first version is never clean.** Build to make it work, then a separate loop refactors
   it to standard.
9. **Frequent Intentional Compaction (FIC).** Keep any session under ~50% context (~100k
   tokens); compact early, offload to subagents, reload low-resolution summaries. See [FIC](#fic--context-management).

---

## Wayfinding — the universal front door

Everything starts here, and it is always a grilling session. Wayfinding's **first act is a
scope triage** that routes the work into one of three shapes. This is what prevents a small
task from exploding into a pile of issues.

| Shape | When | Issues created |
|---|---|---|
| **Task** | small, self-contained | **one** issue — decisions, plan, checklist all inside it. No map, no children. |
| **Feature** | one coherent feature | a PRD (+ Design Doc); **slice** issues only if large enough to ship in parts. |
| **Product / Epic** | app-scale or foggy vision | a `wayfinder:map` whose children are candidate features; each graduates into a PRD. |

Wayfinding is **scale-free**: at product altitude the map's tickets are *candidate features*; at
feature altitude they are *decisions*. Same mechanism, different altitude. (Model borrowed from
the wayfinder skill — a `wayfinder:map` issue holding Destination, Decisions-so-far, Fog, and
Out-of-scope; sharp decisions become child tickets resolved via grilling / prototyping /
research; fog graduates into tickets as clarity grows.)

**Research & POC are informal feeders, not stages.** Research runs in **subagents** (context
isolation = FIC) and returns findings into the map/PRD. POCs use the existing `prototype` skill;
their value is a *decision*, which lands in the PRD or Design Doc.

---

## The Feature Lifecycle

The fully-designed spine. Documents are grilled into being; build loops turn them into verified
code.

```
 PRD ──▶ Design (prototype) ──▶ Design Doc ──▶ [Vertical slices] ──▶ Implementation Plan
 what     approved look/feel     how, verified   independently         agent-executable
 & why    (binding input)        against code    shippable units       steps
                                                                            │
 ───────────────────── build phase (in a worktree) ─────────────────────────┼──────
                                                                            ▼
 Dev loop ──▶ Refactor loop ──▶ QA loop ──▶ Verification ──▶ stage:docs
 Claude↔Codex  structure/       Playwright   human gate on    PRD-level doc
 unit/integ    standards        e2e tests    main, 1 at a     sync after all
 TDD           (review+fix)      + prototype  time; loops      slices verified
                                 as reference  until clean
```

Grilling appears **twice**, in two flavors: a **product grill** (`grill-me`) decides *what*
(→ PRD/Task); a **verified grill** (`grill-verified`, checked against the code) decides *how*
(→ Design Doc).

### Documents

**PRD — *what & why*.** The scope lock. Problem, solution (user's view), user stories, success
criteria, out-of-scope. **No implementation detail** — that goes in the Design Doc. Product grill.

**Design (prototype) — *look & feel*.** Its own step because UI discussion diverges from
delivered UI. Produces an **approved prototype** (via the `prototype` skill + design skills) that
is a **binding input**: the Design Doc references it and the QA loop uses it as the visual
acceptance reference. Has its own human gate — you approve the prototype.

**Design Doc — *how*.** How we build it, **verified against the real codebase**: modules,
interfaces, schema changes, API contracts, testing strategy, and the approved prototype as
reference. One per PRD (fan out only for genuinely independent sub-features). Verified grill.

**Vertical slices — *incremental delivery* (optional).** Only when the Design Doc is large. Each
slice is independently shippable and is the **unit of parallelism** (one worktree/branch each).

**Implementation Plan — *agent-executable steps*.** The checkbox-level plan a build loop
consumes. One per slice (or per feature if slicing was skipped).

### Build loops

All loops run **inside a worktree** on a dedicated branch. Loops run **serially** within a
worktree; independent slices run in **parallel** across worktrees.

**Dev loop.** `ralph` drives two models (Claude ↔ Codex) against the Implementation Plan until
its checkboxes are done. TDD at the **unit/integration** level. **e2e tests are NOT written here**
(UI still churning → brittle).

**Refactor loop.** Not a new runner — **orchestrator policy chaining existing runners**:
`review-loop` (find) → `ralph` (fix) → `review-loop` (re-check) → … until zero blockers.
`review-loop` stays a pure critic; `ralph` stays the only thing that writes code.

**QA loop.** A **single exploratory agent** (not two-model) using the Playwright MCP acts as a QA
engineer against the **real, assembled, refactored app**: takes screenshots, checks against the
approved prototype, and — because the surface is now stable — **writes the e2e suite here**. The
one genuinely **new** runner/skill the build phase needs.

**Verification — the human gate.** You test on main, one feature at a time, against a
verification plan + proof. **The outcome lands in the tracker**, not just `.verify/` temp files:

- During: `.verify/` working doc (within-session FIC scratch).
- At close: a **verification report** posted to the issue (what was tested, pass/fail, findings).
- **Findings loop back**: fixes re-run the relevant build loop → re-verify; out-of-scope findings
  spawn **linked task issues**. `stage:verify` stays until the slice passes clean.

**stage:docs — the tail.** After **all** of a PRD's slices are verified, one **PRD-level**
`sync-docs` pass. It reads **git diffs + the verification report(s) + the issue tree** (not live
conversation — it's long gone by now → FIC), so docs reflect verified reality *including*
verification-driven changes. AFK-able; you give the doc changes a light review.

### Worktrees & artifacts

One branch + worktree per slice (or per Implementation Plan for small work). Loops run inside;
on completion the branch is pushed and the worktree is **torn down**. Main is only ever touched
by you, verifying.

| Artifact | Location | Rationale |
|---|---|---|
| Loop scratch / working state | `.build/` in the worktree (gitignored) | Dies with the worktree; no loss |
| Heavy proof (screenshots, video, logs) | `~/.ralph/builds/<branch>/` | Survives teardown; too heavy for git |
| e2e tests | committed to the branch | It's code; merges naturally |
| Proof summary + verification report | the GitHub issue | Portable, permanent, canonical |

Cleanup is **state-aware**: a build dir is freed only once its issue is verified/closed — human
verification is the trigger. Keys off the same issue state machine as everything else.

### State machine & labels

**Triage axis (existing)** governs getting an issue *ready*:
`needs-triage → needs-info → ready-for-agent / ready-for-human / wontfix` (+ `bug`/`enhancement`).

**Build-stage axis (new)** takes over once implementation starts — one label at a time, on the
**slice issue** (the shippable/worktree unit):

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:ready` | eligible to start (today: `ready-for-agent`) | orchestrator picks it up |
| `stage:dev` | dev loop running | dev-loop checkboxes done |
| `stage:refactor` | refactor loop running | review-loop returns zero blockers |
| `stage:qa` | QA loop running | e2e written, proof captured |
| `stage:verify` | **human gate** | you sign off → close issue (→ triggers cleanup) → PRD `stage:docs` |

A waiting slice carries the existing `blocked` label. **Convention:** all lifecycle-position
labels share one namespace (`stage:`); `ready-for-agent` maps to `stage:ready` (relabel deferred).
`stage:verify` ≠ `ready-for-human` (verify = check completed work; ready-for-human = implement).
These are **canonical** names; real strings per repo come from `setup-agent-skills`.

### Parallelism & scheduling

Because every slice is an isolated worktree, **different slices can occupy different stages at
once**. The orchestrator schedules across slices respecting four conflict dimensions:

| Dimension | Risk | Mitigation |
|---|---|---|
| **Dependency** | B needs A's merged code | `blocked` graph (from `to-vertical-issues`) |
| **Shared-file merge** | parallel slices edit overlapping lines | shared-file conflict check → order merges |
| **Machine / API resources** | N loops = N procs, rate limits | global **concurrency cap** |
| **Runtime resources (QA)** | two QA loops clash on ports / test DB | **serialize QA (cap = 1) to start**; dev/refactor parallelize |

Per-worktree runtime isolation (dynamic ports, DB-per-branch) is a later upgrade. **Verification
is always serial** — one at a time, by you, on main.

**The orchestrator: a manual pass first.** You invoke it; it reads the board and, for every issue
it can legally advance (respecting conflicts + caps), launches the next background loop and flips
the `stage:` label, then reports and exits. Driven entirely by durable labels, so it's
**idempotent and resumable** — a crashed loop just leaves its issue at the old label. The
**standing autonomous loop is the same pass on a cron** (later, near-free). Builds on the existing
`ralph-orchestrator` skill.

---

## The Project Lifecycle _(designed stub)_

How a project's knowledge base is established and maintained — so agents have context and you stop
re-briefing.

- **`init-docs`** — extended with a **deep product/vision/domain grill** (what the app *is*, who
  it's for, where it's going), plus analysis of any existing code. Produces `CONTEXT.md`, domain
  glossary, ADRs, agentic files (CLAUDE.md/AGENTS.md), and `MONITORING.md`. (Today it already
  grills for patterns and scaffolds `CONTEXT.md`/ADRs; the extension is the deeper product grill.)
- **`sync-docs`** — keeps all of the above fresh as the project evolves; also the engine behind
  the feature lifecycle's `stage:docs`.

Global/general skills that generate project-specific templates. They will gain more in-repo
references over time.

---

## Cross-cutting axes

Threads through every altitude and lifecycle.

- **Knowledge / Context** — `CONTEXT.md`, glossary, ADRs. Produced by the project lifecycle,
  consumed by every grill and loop.
- **Documentation** — `init-docs`/`sync-docs` (create + maintain) **plus** the `stage:docs` tail.
- **Monitoring / Observability** _(new)_ — a `MONITORING.md` describing how to observe the app
  (log locations, how to pull logs, dashboards); later, optionally, a skill to fetch/inspect logs.
  Feeds the feedback loop.
- **FIC — context management** — see below.
- **Orchestration & state machine** — labels + the orchestrator pass.
- **Layering** — mechanism vs. policy (below).
- **Standards & quality** — standards templates, review-loop criteria, testing split (unit in
  dev, e2e in QA).
- **Feedback loop** — post-release, `monitoring → log → triage → diagnose` returns work to the
  Product/Feature altitude. Makes the system a cycle.

### FIC — context management

Keep any session under **~50% context (~100k tokens)** — agent performance degrades past that.

- **Durable cross-session state → the issue tracker** (map issue, stage labels, resolution &
  verification reports). Not temp files.
- **Within-session scratch + a resume pointer → stage dotdirs** (`.grill/`, `.verify/`, `.build/`),
  promoted to the issue when it crystallizes.
- **Compact via `handoff`** (exists): summarize → a fresh session reloads the summary + the durable
  artifact (map / PRD / Design Doc), never the transcript.
- **Offload to subagents** — the strongest technique: run research and codebase search in isolated
  subagents that return only findings, keeping the driver's context clean.

### Layering

| Layer | Owns | Knows pipeline terms? |
|---|---|---|
| **Runner (ralph)** | Primitives: run a loop, two models, in a worktree on a branch, with config | **No** |
| **Orchestrator skill** | Policy: stage order, naming, labels, when to run which loop, artifacts | **Yes** |
| **Scripts** | Deterministic steps: worktree create/teardown, label flips, cleanup | No judgment |

If we rename "vertical slices" or reorder stages, **only the orchestrator skill changes**; ralph
is untouched. Worktree lifecycle is owned by a **script** the orchestrator calls — ralph never
creates/destroys worktrees.

---

## Open questions

Being grilled into shape. Not final.

1. ~~Pre-PRD stage~~ — RESOLVED. Wayfinding is the universal front door (optional/scale-triaged);
   research/POC are informal subagent-driven feeders.
2. ~~Loops as concrete skills~~ — RESOLVED. Dev = `ralph`; Refactor = orchestrator policy chaining
   `review-loop` + `ralph`; QA = one new single-agent Playwright runner/skill.
3. ~~Meta-orchestrator~~ — RESOLVED. Manual pass first; standing loop = same pass on a cron.
4. ~~Label vocabulary~~ — RESOLVED. `stage:` namespace, on the slice issue.
5. **Build inventory** — the final list of what is a skill vs a runner primitive vs a script
   (produced once the design settles).
6. **`to-prd` fix** — split the current `to-prd` (which fuses PRD + design detail) into separate
   PRD and Design Doc producers.
7. **Design step depth** — how much prototype fidelity is "approved"; how the prototype is stored
   and referenced by the Design Doc and QA loop.
8. **Monitoring axis** — whether it stays doc-only (`MONITORING.md`) or becomes a log-fetching
   skill.
9. **Release/deploy** — the terminal "merged & released" step (likely CI/CD, mostly out of scope)
   and how it flips the issue to closed/released.
