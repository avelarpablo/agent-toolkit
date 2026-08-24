# The Development System

How we take software from a vague idea (or an empty repo) to shipped, verified, documented
code — and how feedback loops back. This is the umbrella. Its **fully-designed core** is the
[Feature Lifecycle](#the-feature-lifecycle) and the [cross-cutting axes](#cross-cutting-axes)
(FIC, tracking, grilling, layering); the [Project lifecycle](#the-project-lifecycle-designed-stub)
and a few later upgrades (log-fetch skill, standing orchestrator cron) remain designed skeletons.

> Status: **in design, not built.** We are defining the standard from zero. Sections marked
> _Open_ or _Stub_ are not final.
>
> **Reuse philosophy — existing skills are references, not mandates.** When this doc names an
> existing skill/runner (`grill-me`, `review-loop`, `ralph`, `prototype`, `init-docs`, …), read it
> as *"the closest existing analog to what we want here"* — **not** a commitment to reuse it. The
> design is driven by what we want; each component is decided at build time as **reuse / adapt /
> replace-with-new / remove**. Purpose-built replacements (and retiring superseded skills) are
> expected. The [Build inventory](#build-inventory-draft) is where every such call is made deliberately.

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
7. **Main stays pristine.** All build work happens in worktrees; `main` is only ever touched by the
   final verified promote. Human verification happens on the worktree of the branch that will
   promote — the feature's `feat/…` for multi-slice work, the unit's own branch for single-unit
   work — one promotable unit at a time.
8. **The first version is never clean.** Build to make it work, then a separate loop refactors
   it to standard.
9. **Frequent Intentional Compaction (FIC).** Keep any session under ~50% context (~100k
   tokens); compact early, offload to subagents, reload low-resolution summaries. See [FIC](#fic--context-management-a-uniform-protocol).
10. **Two-family dialogue.** Every build loop pairs two different model families (e.g. Claude +
    Codex) — different families catch different things, so the output is more accurate and closer to
    intent. This applies to **documents too**: a plan gets the same adversarial pass as a diff, via
    the [critique loop](#the-critique-loop--one-engine-two-targets). A defect caught in the plan is
    the cheapest defect there is.
11. **No artifact is final until a second family has reviewed it — and every gate names its
    anchor.** Principle 10 says *pair the families*; this says *where the pairing is enforced* —
    every stage that emits an artifact passes a
    [gate](#stage-gates--no-artifact-is-final-unreviewed) before that artifact is published and the
    stage advances. But a second model is **not** an external verifier: models sharing a context can
    agree at industrial scale. So each gate must declare the **reality anchor** it rests on — a test
    that ran, a build that compiled, a human who signed off. Where an anchor exists the gate is
    binding; where none does (documents), the gate is **advisory input to your judgment**, never a
    green light. See [Grounding](#grounding--anchors-caps-and-counter-metrics).
12. **Every cycle has two exits.** Success is one. A hard cap is the other. A loop whose only exit is
    success will, on a blocker it cannot fix, run until it is stopped by hand — and bill silently
    the whole way.

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

**Wayfinding routes to grill _profiles_ — it does not run the grilling itself.** Grilling is one
reusable engine parameterized by per-stage profiles (see
[Grilling engine & profiles](#grilling-engine--profiles)); wayfinding is policy (which profile,
when, at what scope) — the same mechanism/policy split as ralph vs. the orchestrator. Wayfinding
owns exactly two things: **scope triage** (Task/Feature/Product) and **dispatch** (route each open
decision to the right grill profile — product/what → PRD; technical/how → Design Doc; domain/
terminology → knowledge-base sharpening).

"Universal front door" is conceptual, not "always run a heavy map." **Product/foggy** → full
wayfinding (map + dispatch). **Feature** → skip the map; product-grill profile → PRD, later
verified-grill profile → Design Doc. **Task** → a brief product grill → one issue. A clear feature
never pays the map tax.

**Research & POC are informal feeders, not stages.** Research runs in **subagents** (context
isolation = FIC) and returns findings into the map/PRD. POCs use the existing `prototype` skill;
their value is a *decision*, which lands in the PRD or Design Doc.

### Grilling engine & profiles

Grilling is **one reusable engine** (the behavior: one question at a time, recommend an answer, walk
the decision tree, verify claims against code when the profile calls for it, and **checkpoint every
decision to the working file** per the [FIC protocol](#fic--context-management-a-uniform-protocol)).
It is **parameterized by a per-stage profile** — the mechanism/policy split applied to grilling:
engine = mechanism (reusable), profile = policy (stage-specific prompt, no unrelated baggage).

| Profile | Questions | Verifies vs code? | Output (→ producer) |
|---|---|---|---|
| **PRD** | product / what / scope | no | PRD (→ `to-prd`) |
| **Design Doc** | technical / how | **yes** | Design Doc (→ `to-design-doc`) |
| **Task** | lightweight, scoped | as needed | task issue |
| **Wayfinding ticket** | resolve one decision | as needed | a resolved map ticket |

Grill = interrogate; the `to-*` producer = synthesize & publish to the tracker (the producer does
**not** interview — it synthesizes what the grill established). Existing `grill-me` / `grill-verified`
/ `grill-with-docs` are **references for the engine's behavior**; they are likely **replaced by this
unified engine + profiles and retired** (per the [reuse philosophy](#the-development-system)).

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
 Dev loop ──▶ Refactor loop ──▶ QA loop ──▶ Verification ──▶ stage:docs ──▶ promote
 Claude↔Codex  structure/       Playwright   feature-level    feature-level    feat → main
 unit/integ    standards        e2e tests    on the feat/     sync-docs pass   (deploy
 TDD           (review+fix)      + prototype  worktree, 1 at   before promote   trigger)
                                 as reference  a time; loops
                                               until clean
```

Slices run their build loops in parallel worktrees and merge into the **feature integration
branch** (`feat/…`); verification, docs, and the promote-to-`main` gate happen at the **feature
level** on that branch. See [Branch naming](#branch-naming).

Grilling appears **twice**, in two profiles: a **product grill** decides *what* (→ PRD/Task); a
**verified grill** (checked against the code) decides *how* (→ Design Doc).

### Documents

**PRD — *what & why*.** The scope lock. Problem, solution (user's view), user stories, success
criteria, out-of-scope. **No implementation detail** — that goes in the Design Doc. Product grill.

**Design (prototype) — *look & feel*.** Its own step (and its own stage — `stage:design`, see
[State machine](#state-machine--labels)) because UI discussion diverges from delivered UI. Runs in a worktree (produces code → main stays pristine). Uses a HITL variant of the
`prototype` skill + design skills to generate several variations; you approve one at a human gate.
The approved prototype is a **binding input** — the Design Doc references it and the QA loop uses
it as the visual acceptance reference.

Two paths, chosen per feature by design-step triage:

- **Salvage (default for UI-meaningful features).** The prototype is built in the project's **real
  design system / component library** (not a throwaway aesthetic — a throwaway look that gets
  re-styled is itself a divergence source). On approval it becomes the **dev loop's starting
  point**: the refactor loop then cleans it to standard, and the QA loop validates against the
  frozen screenshots. Divergence is killed *structurally*, not caught after the fact.
- **Throwaway (minor / low-risk UI).** Keep only frozen screenshots as the reference; the dev loop
  builds from scratch against them.

**Storage of the approved prototype** splits by resource kind:

- **Frozen screenshots** (visual acceptance reference) → the **Design Doc / feature issue**
  (proof-style artifact, canonical, in the tracker; QA reads them). Both paths.
- **Salvaged code** → a short-lived **`design/<issue>-<slug>` branch** (code belongs in git, not
  as an issue attachment). On feature-branch creation it **seeds the `feat/…` integration branch**,
  so every slice that branches off `feat/…` inherits the prototype automatically; the `design/…`
  branch is then deleted (its content lives on in `feat/…`; the screenshots remain the durable
  reference). For single-unit work with no `feat/…` branch, the `design/…` branch seeds the lone
  `slice/…` or `task/…` branch instead.

**Design Doc — *how*.** How we build it, **verified against the real codebase**: modules,
interfaces, schema changes, API contracts, testing strategy, and the approved prototype as
reference. One per PRD (fan out only for genuinely independent sub-features). Verified grill.

**Vertical slices — *incremental delivery* (optional).** Only when the Design Doc is large. Each
slice is independently **integrable/demoable** and is the **unit of parallelism** (one
worktree/branch each). Slices merge into the `feat/…` integration branch as they finish; the
**customer-facing release is feature-level** (`feat → main`). Truly standalone work ships directly
as a `task/…` to `main` instead.

**Implementation Plan — *agent-executable steps*.** The checkbox-level plan a build loop
consumes. One per slice (or per feature if slicing was skipped).

### Build loops

All loops run **inside a worktree** on a dedicated branch. Loops run **serially** within a
worktree; independent slices run in **parallel** across worktrees.

**Every build loop is a two-family dialogue.** Two agents of different model families
(e.g. Claude + Codex) converge on the result — different families catch different things, so the
output is more accurate and closer to intent. Dev = implement ↔ correctness-review; Refactor = find
↔ fix (structure + patterns); QA = execute ↔ test-strategy critique.

**Dev loop.** An **adapted `ralph`** (not rebuilt, not as-is). `ralph` already does the core: Claude
implements the issue → a **blocking Codex correctness gate** reviews the commit → blockers loop back
for a fix → re-review (that's the two-family dialogue). TDD at the **unit/integration** level.
**e2e tests are NOT written here** (UI still churning → brittle). The loop is **focused strictly on
making it work** — no refactor, no design patterns (refactor loop), no e2e (QA). Three adaptations
to fit the pipeline:

- **Stops at "dev-done"; the orchestrator owns stage transitions.** ralph must *not* close the issue
  or unlock downstream (that's policy now) — it signals completion and the orchestrator flips the
  `stage:` label and merges into `feat/…`.
- **Runs in the worktree/slice-branch it's handed** — self-branching (`RALPH_FEATURE_BRANCH`)
  disabled; ralph never creates/destroys branches (orchestrator + scripts do).
- **Implementation-only prompt**, replacing the current project-specific `prompt.md`.

The inline Codex gate is a **fast correctness check** ("is it broken?") and is kept *alongside* the
separate refactor loop, which owns the different concern of structure + patterns ("is it clean?").
`ralph` is also reused as the **fix actor in the refactor loop** — the same engine, a different
prompt/role.

**Refactor loop.** Not a new runner — **orchestrator policy chaining existing runners**:
`review-loop` (find) → `ralph` (fix) → `review-loop` (re-check) → … until zero blockers **or the
round cap is hit** — then it stops, flips `needs:human`, and reports what it could not fix
(principle 12).
`review-loop` stays a pure critic; `ralph` stays the only thing that writes code. **This loop also
owns design patterns** — agents tend not to reach for proper patterns, so this is where the code is
assessed and refactored to the **best design pattern for the feature and for maintainability**.
Patterns are found-and-applied *here*, against the real written code, rather than guessed up front
(the Design Doc may name candidate patterns; the refactor loop confirms and applies them).

**QA loop.** A **two-agent dialogue** (different families) against the **real, assembled, refactored
app**: a **driver** owns the Playwright MCP (only one hand on the browser) and executes; a
**strategist/critic** proposes what & how to test and challenges coverage ("empty state? error path?
the prototype's hover states?"). They converge on a test plan, capture screenshots, check against
the approved prototype, and — because the surface is now stable — **write the e2e suite here**. The
one genuinely **new** runner/skill the build phase needs.

**Verification — the human gate.** Feature-level and serial: once all slices have merged into the
`feat/…` integration branch, you test the **assembled feature** in the `feat/…` worktree (the
"main tree" for that feature), one feature at a time, against a verification plan + proof.
Feature-level is the default gate because integration bugs only surface once slices combine; slices
still demo continuously on `feat/…` for your visibility, and a very large feature can opt into
incremental per-slice verification. **The outcome lands in the tracker**, not just `.verify/`:

- During: `.verify/` working doc (within-session FIC scratch).
- At close: a **verification report** posted to the issue (what was tested, pass/fail, findings).
- **Findings loop back**: fixes re-run the relevant build loop on the slice → re-merge → re-verify;
  out-of-scope findings spawn **linked task issues**. `stage:verify` stays until the feature passes
  clean, or until the re-verify cap is hit — then it holds with `needs:human` rather than cycling.

**stage:docs — the tail, and the debt payment.** This stage exists because of **comprehension
debt**: every AFK loop widens the gap between what the repo contains and what you understand, and
that gap compounds until the day you must debug something nobody has read. Docs are how it is paid
down.

**stage:docs — the mechanics.** After the feature passes verification (and before promoting to `main`),
one **feature-level** `sync-docs` pass on the `feat/…` branch. It reads **git diffs + the
verification report(s) + the issue tree** (not live conversation — long gone by now → FIC), so docs
reflect verified reality *including* verification-driven changes. AFK-able; you give the doc changes
a light review. Then `feat → main`.

### The critique loop — one engine, two targets

`ralph` and `review-loop` look alike but are not: `review-loop` is an **N-round dialogue** —
alternating Claude and Codex, each round fed the prior rounds' findings, read-only, terminating at a
fixed round count. `ralph` is an autonomous **mutating** loop with a *single-shot* Codex gate. The
shared primitive is narrower than either:

> **Critique an artifact against explicit criteria using a second model family, structured output.**

`review-loop` is the N-round form; ralph's gate is the 1-round form.

That primitive is **target-agnostic**, so one runner serves both:

| Target | Adapter | Profile | Criteria |
|---|---|---|---|
| code | a git diff (`--pr` / `--base`) | `code` | per-repo standards |
| a plan, spec or design doc | files read as-is (`--files`) | `coherence` | `criteria/coherence.md` |

Everything downstream — rounds, schema, assembly — is identical; only what is put in front of the
models differs.

**Why documents need it.** The design front half had no adversarial gate: grill → PRD → Design Doc →
publish, unchecked, at exactly the altitude where mistakes are cheapest to fix. The coherence
criteria don't judge decisions — they find **contradictions, duplicate concepts under two names,
orphaned references, ordering violations, unfalsifiable acceptance criteria, resolved-but-not-decided
questions, load-bearing unstated assumptions, and scope leaks** (C-1…C-8). Every one of those was found by hand in
this system's own spec before the loop existed.

**On demand now, a gate later** — `to-prd`/`to-design-doc` will run it pre-publish once the criteria
have proven themselves on real documents.

### Stage gates — no artifact is final unreviewed

Principle 11. Every stage that produces an artifact runs it through the
[critique loop](#the-critique-loop--one-engine-two-targets) before publishing. The pattern is always
the same — **artifact + criteria + a second family → blockers must be zero** — and the stages differ
only in *which criteria* and *how many rounds*.

| Stage | Artifact | Criteria | Rounds | **Reality anchor** |
|---|---|---|---|---|
| PRD grill | the PRD | success criteria measurable? scope bounded? implementation detail leaking in? | 1–2 | **none** → advisory; you decide |
| Design Doc grill | the Design Doc | claims verified against code? alternatives considered? coherence | 3 | partial — claims checked **against the code** |
| Slicing | slice + implementation plan | independently shippable? demo command real? plan executable? | 1 | the **demo command runs** |
| Dev | the diff | correctness | 1 (inline) | **unit + integration tests pass** |
| Refactor | the diff | per-repo standards | 3 | **tests still pass** after each fix |
| QA | the assembled app | e2e vs the frozen prototype | — | **e2e suite passes**; screenshots compared |
| Verification | the verification report | every success criterion actually exercised? | 1 | **you signed off** |

**Rounds scale with stakes**, and this is the same primitive throughout: `review-loop` at N rounds
is the dialogue; ralph's inline Codex gate is the same thing at one round. A cheap stage pays one
round; a Design Doc that will spawn a dozen slices pays three.

**The criteria are the work, not the wiring.** A gate with vague criteria produces vague findings
and trains you to ignore it. Each criteria doc is written like
[`coherence.md`](../runners/review-loop/criteria/coherence.md): numbered rules, explicit
out-of-scope, and an explicit ban on padding.

**Why gates and not good intentions:** the failure mode is finishing an artifact, feeling done, and
publishing it — precisely when a second opinion is most valuable and least wanted. Making it a
stage transition removes the choice.

### Grounding — anchors, caps and counter-metrics

The system is a directed graph of loops: stages are nodes, label transitions are edges, the
orchestrator is the runtime, and several edges cycle (refactor, verification findings). Graphs of
agents fail in a characteristic way — **circularly**. Reviewers everywhere, every node agreeing,
nothing touching reality. A graph without anchors is a larger hallucination with better project
management.

Three defences, structural rather than a matter of care:

**1. Reality anchors.** Some evidence must come from outside the agents: a test that actually ran, a
build that compiled, an e2e suite against the running app, a human who looked. Every gate in the
table above declares its anchor — and the honest entries are the ones that declare **none**. A
document gate has no test that can fail, so it informs your judgment instead of replacing it. Two
model families are *more* independent than one, not independent.

**2. Hard caps (principle 12).** Every cycle declares its second exit:

| Cycle | Success exit | Hard cap |
|---|---|---|
| Dev loop | implementation plan complete, tests pass | `ralph --max` iterations |
| Refactor loop | `review-loop` returns zero blockers | max find→fix rounds, then escalate |
| QA loop | e2e written and passing | max attempts, then escalate |
| Verification findings | feature passes clean | max re-verify rounds, then escalate |

Hitting a cap is **not** a failure to hide — it flips `needs:human` and reports what it could not
resolve. Silent looping is the failure; a cap is how the loop tells the truth.

**3. Counter-metrics.** The board measures throughput — issues advancing through stages. Optimise
throughput alone and Goodhart's law does the rest: a pipeline that merges slices quickly while
escaped defects climb looks *excellent* on a stage board. So progress reporting pairs every
throughput number with a quality number (see [Progress & tracking](#progress--tracking)).

**Comprehension debt** is the standing cost of an AFK pipeline: the faster loops ship code you did
not write, the wider the gap between what the repo contains and what you understand. That gap is
what `stage:docs`, `CONTEXT.md` and the ADRs exist to pay down — not bureaucracy, debt service. It
is also why verification stays a **human** gate: reading the assembled feature is how you keep
contact with what was built.

### Worktrees & artifacts

One branch + worktree per slice (or per Implementation Plan for small work). Loops run inside;
on completion the slice branch merges into the `feat/…` integration branch and the worktree is
**torn down**. A multi-slice feature also has a **`feat/…` worktree** where slices integrate and
where you verify the assembled feature. `main` itself is only ever touched by the final
`feat → main` (or `task → main`) promote.

| Artifact | Location | Rationale |
|---|---|---|
| Loop scratch / working state | `.build/` in the worktree (gitignored) | Dies with the worktree; no loss |
| Heavy proof (screenshots, video, logs) | `~/.ralph/builds/<branch>/` | Survives teardown; too heavy for git |
| e2e tests | committed to the branch | It's code; merges naturally |
| Proof summary + verification report | the GitHub issue | Portable, permanent, canonical |

Cleanup is **state-aware** and keyed to the **merge** — a build dir is freed once its branch has
merged, never on the close, so a deploy schedule can never hold worktrees hostage. Keys off the same issue state machine as everything else.

### Branch naming

**A branch exists if and only if there is a buildable unit.** Planning issues (`wayfinder:map`,
PRD, Design Doc) hold no code and get no branch; only slices, tasks, fixes, and the transient
design branch do.

**Format:** `<type>/<issue-number>-<kebab-slug>` — lowercased, slug length-capped.

- **Type prefix, always** — mechanism pattern-matches on it (orchestrator routing, cleanup, ralph's
  protected-branch guard). `main` and any deploy branches are protected; nothing branches *as* them.
- **Issue number, always** — the tracker is the source of truth; the number makes branch ↔ issue
  traceability automatic (orchestrator, cleanup, and humans all map a branch to its state). A
  branch with no issue is a smell. Cleanup keys off this number, same rule as `~/.ralph/builds/`.
- **Base is contextual, not encoded** (slices off their `feat/…`; `feat/…` and `task/…` off main).

| Type | For | Branches off | Lifecycle |
|---|---|---|---|
| `feat/` | a multi-slice feature's integration branch ("main feature branch") | main (seeded by `design/…` if any) | receives slice merges; verified + docs here; **promoted to main** (deploy trigger); torn down |
| `slice/` | one vertical slice | its `feat/…` branch | build loops in a worktree; merged into `feat/…`; torn down |
| `design/` | salvaged prototype for a feature | main (in a worktree) | short-lived; seeds `feat/…` (or the lone slice/task), then deleted |
| `task/` | one small, self-contained unit (no `feat/…`) | main | build (dev → verify); merged straight to main; torn down |
| `fix/` | a verification finding or feedback-loop bug (`bug`) | the `feat/…`/slice if in-scope & open, else main | merged; torn down |

**The standard is [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)** —
one long-lived branch (`main`), short-lived branches off it, merge-to-`main` as the deploy trigger.
Not GitFlow: GitFlow is *defined* by a second long-lived branch, and its `hotfix` exists to merge
into **both** `master` and `develop`. With no `develop`, that double merge — the entire point —
collapses into an ordinary merge to `main`. Borrowing GitFlow's names without its branches would
mislead everyone who knows GitFlow. **If a project gains `develop`/`staging`, adopt GitFlow properly
at that point**, and `hotfix`/`bugfix` regain real meaning because there are then two targets to
distinguish. Until then there is one target, so the distinction carries no information.

Type prefixes are therefore **descriptive**, not permissions — and they are **our** vocabulary, not
[Conventional Commits](https://www.conventionalcommits.org/), which governs commit *messages*.
`feat/` and `fix/` happen to coincide; `slice/`, `design/` and `task/` have no CC equivalent.

The **integration branch (`feat/…`) exists only when a feature has ≥2 slices**. Single-unit work
(a `task/…`, a lone `slice/…`, a one-off `fix/…`) skips it and merges to `main` once verified.

**What protects `main` is verification, not the prefix.** `main` and any deploy branches are
protected, and **`main` accepts only a branch that has passed `stage:verify`** — whatever its type.
Stating the invariant directly (rather than as a whitelist of permitted prefixes) is what keeps
principle 7 true: the whitelist had already drifted out of sync with the branch table, permitting
and forbidding `fix/ → main` one line apart.

The **type vocabulary is orchestrator policy**, not ralph's — ralph only needs "you're on a
non-protected branch." This supersedes ad-hoc conventions (`feature/*`, `standards/…`). Canonical
for projects using the system; the agent-toolkit repo itself may stay looser (it often has no
per-change issue).

### State machine & labels

Three namespaces, each answering a different question — never overlapping:

| Namespace | Answers | Owner |
|---|---|---|
| `kind:` | what triggered this work | `log`, at capture |
| `triage:` | is it ready to build? (**pre**-buildable) | you, via `triage` |
| `stage:` | where is it in the build? (**buildable**) | the orchestrator |
| `needs:human` | who executes it — a **modifier**, not a state | you, or a loop hitting its cap |
| **Environment** *(Project field)* | where merged code has actually reached | **CI**, never the orchestrator |

**One writer per field.** The orchestrator never writes Environment; CI never writes `stage:`. Two
writers on one field is two sources of truth wearing a disguise.

**Triage axis** governs getting an issue *ready*: `needs-triage → needs-info → wontfix`, and the
single exit into the build machine is **`needs-triage → stage:ready`**.

`ready-for-agent` is **deleted** — it was `stage:ready` under another name. `ready-for-human` is
**not a state**: it answers *who executes*, while every `stage:` answers *where it is*. An issue can
be fully analyzed and buildable and still need you (judgment, credentials, design taste). So it
becomes the modifier `needs:human`, which the orchestrator reads to skip that issue when dispatching
loops. As a state it would force every stage to fork into agent and human variants.

**Build-stage axis (new)** takes over once implementation starts — one label at a time. The stages
split across two altitudes: **slice-level** loops run on each slice issue and end when the slice
merges into `feat/…`; **feature-level** verify and docs run on the feature (PRD) issue.

*On the feature (PRD) issue, **before** slicing — optional, only for UI-meaningful features:*

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:design` | prototype variations generated in a `design/…` worktree; carries `needs:human` while awaiting your pick | **you approve one** → screenshots frozen onto the issue, `design/…` seeds `feat/…` (or the lone slice/task branch), `design/…` deleted |

It is a stage rather than a roadmap activity because it **produces code in a worktree** and holds a
human gate — the two signatures of a build stage. PRDs and Design Docs are documents; this one
commits. Non-UI features skip it entirely.

*On the slice issue:*

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:ready` | eligible to start | orchestrator picks it up |
| `stage:dev` | dev loop running | dev-loop checkboxes done |
| `stage:refactor` | refactor loop running | review-loop returns zero blockers |
| `stage:qa` | QA loop running | e2e written, proof captured → **merge into `feat/…`**; slice done |

*On the feature (PRD) issue, once all slices have merged into `feat/…`:*

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:verify` | **human gate** — verify on the worktree of the branch that will promote (`feat/…` for a multi-slice feature; the unit's own branch otherwise) | you sign off |
| `stage:docs` | feature-level `sync-docs` pass on `feat/…` | docs reviewed → **promote `feat → main`** (deploy trigger) → close |

A waiting slice carries the existing `blocked` label. These are **canonical** names; real strings per
repo come from `setup-agent-skills`. (Single-unit `task/…` work carries all stages on its one issue
and promotes straight to `main`.)

### Work kinds — the inbox and its exits

Not all work is a feature someone set out to build. Most of it is **logged and forgotten**: a bug
noticed mid-task, a shortcut you knew you were taking, an idea you had once. That shared property —
*captured, unanalyzed, deferred* — is a *state*, not a kind. The **kind only decides which analysis
runs when you pick it back up**, and every path converges at `stage:ready` carrying a plan:

| `kind:` | Analysis on pickup | Produces |
|---|---|---|
| `bug` | **`diagnose`** — reproduce, root-cause | a failing test as the acceptance criterion + a fix plan |
| `tech-debt` | scope the refactor (target usually already known) | a refactor plan; often skips design entirely |
| `wishlist` | **wayfinding** → PRD (research/POC as needed) → Design Doc | the full feature front-half |

For a *hard* bug the diagnosis **is** the design doc — root cause, blast radius, chosen fix,
rejected fixes. For a trivial one it's a sentence. Ceremony scales with difficulty, exactly as it
scales with scope at the [altitudes](#wayfinding--the-universal-front-door).

**The inbox is `kind:` with no `stage:` label.** Absence of a stage label *is* the inbox, so the
orchestrator — which only ever acts on `stage:*` — can never pick up something unanalyzed.

**Research and POC are not kinds.** They are **wayfinder-created**: a map ticket names an unresolved
decision, and research or a POC is *how it gets resolved*. They produce decisions that land in a map,
PRD or Design Doc — never commits. Nothing logs them; nothing builds them.

**Findings are routed, never stored as a kind.** Something important surfaced mid-conversation is
disposed of by what it *implies*: buildable → `kind:wishlist`; broken → `kind:bug`; structurally
wrong → `kind:tech-debt`; and if it is simply **knowledge about how the system works**, it belongs in
`CONTEXT.md` or an ADR via `sync-docs` — **not in the tracker**, where knowledge goes to die.

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
is always serial** — one promotable unit at a time, by you, on the worktree of the branch that
will promote (`feat/…` for a multi-slice feature, the unit's own branch otherwise).

**The orchestrator: a manual pass first.** You invoke it; it reads the board and, for every issue
it can legally advance (respecting conflicts + caps), launches the next background loop and flips
the `stage:` label, then reports and exits. Driven entirely by durable labels, so it's
**idempotent and resumable** — a crashed loop just leaves its issue at the old label. The
**standing autonomous loop is the same pass on a cron** (later, near-free). Builds on the existing
`ralph-orchestrator` skill.

### Release & deploy

The standard owns everything **up to and including the merge to `main`**; the deploy itself is
CI/CD and **out of scope** (project-specific). The contract at the boundary:

- **Verification gates the merge.** Unverified code never reaches `main` — you verify the assembled
  feature on `feat/…` first, then promote.
- **`feat → main` (or `task → main`) is the deploy trigger.** The standard defines the trigger
  point; the project's own pipeline defines what happens after.
- **Cadence: continuous by default.** Each feature is verified before its merge, so features release
  as they finish. Batch/held releases (feature flags, release trains) are a project layer on top.
- **GitHub's auto-close already matches this model** (verified 2026-08). Closing keywords
  (`closes`/`fixes`/`resolves #N`) fire **only when a PR merges into the repository's default
  branch**. So slice PRs — which target `feat/…`, not the default — never auto-close their issues,
  and the orchestrator keeps ownership; the `feat → main` promote PR *does* auto-close whatever it
  references, which is exactly where the feature issue should close. Cross-repo closes work with
  `owner/repo#N`, so a code-repo promote PR can close a PRD living in the umbrella repo. **The
  promote PR must reference the issues** or nothing closes — orchestrator's job, via a PR template.
- **Issue lifecycle: close on merge.** verify → docs → promote → **closed (Done)**. Cleanup keys off
  the **merge**, not the close, so branches and `~/.ralph/builds/` are never held hostage to a deploy
  schedule.
- **Deployment is tracked on a closed issue.** A closed issue stays a project item and its fields
  stay editable, so **CI keeps writing an `Environment` field after the issue closes**:

  ```
  promote feat → main → issue CLOSED (Done)
                          ↓  CI writes, post-close
                  Environment: Staging → Production
  ```

  This is why no `released` stage exists: holding an issue open until deploy would stall cleanup and
  add a stage the orchestrator must reason about, to answer a question a field already answers.

- **`Environment` is a Project single-select, values per project** (tier 2). Default **Staging +
  Production**; a simple app configures Production only; a complex one adds Dev/UAT. **Environments
  are never `stage:` labels** — the canonical stage set must stay small and identical everywhere, or
  the orchestrator has to reason about a machine that differs per project.
- **Scope line:** the standard defines the field, its writer, and a `gh` snippet for a deploy job.
  The pipeline itself stays the project's. *The tracker must tell the truth about where code is; how
  it gets there is not ours.*

This closes the cycle: verified feature → merge (deploy trigger) → released → monitoring/feedback →
back to intake.

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
- **Monitoring / Observability** _(new)_ — **doc-first**. A `MONITORING.md` describing how to
  observe the app (log locations, how to pull logs, dashboards, key signals). It **mirrors the
  `CONTEXT.md` hierarchy**: per-project `{project}/MONITORING.md` beside each app's `CONTEXT.md`,
  plus an optional **root** `MONITORING.md` for shared/cross-cutting infra (shared DB, gateway, CI).
  Lives at project root next to `CONTEXT.md`, **not** in `.agents/` (knowledge, not config), so
  `init-docs`/`sync-docs` place & maintain it with the monorepo logic they already have. **Later**,
  optionally, a log-fetching skill that **resolves the nearest `MONITORING.md`** for its path and
  pulls logs/errors — closing the feedback loop into `log → triage → diagnose`.
- **FIC — context management** — see below.
- **Orchestration & state machine** — labels + the orchestrator pass.
- **Layering** — mechanism vs. policy (below).
- **Standards & quality** — standards templates, review-loop criteria, testing split (unit in
  dev, e2e in QA).
- **Feedback loop** — post-release, `monitoring → log → triage → diagnose` returns work to the
  Product/Feature altitude. Makes the system a cycle.
- **Progress & tracking** _(new)_ — see below.

### FIC — context management (a uniform protocol)

Keep any session under **~50% context (~100k tokens)** — agent performance degrades past that. FIC
is **not per-skill best-practice** the engineer must remember; it is **one native protocol every
long-running skill implements identically**, via a **shared FIC primitive**. Skills differ only in
*what* they record, never in *how* FIC works (the "one engine, many profiles" shape — see
[Grilling engine](#grilling-engine--profiles)).

**The four-part contract (identical in every FIC-aware skill):**

1. **Working file, standard location & format.** On start, open a per-topic working file in a
   dotdir (`.grill/<slug>/`, `.verify/<slug>/`, `.wayfind/<slug>/`, …).
2. **A live resume header — always current — leading with a copy-pasteable resume command** (fixes
   the "I made a handoff and didn't know what to tell the new session" problem):
   ```
   ## Resume
   ▶ To resume: start a new session and run  /wayfind <slug>
     (or: "continue the FIC session at .grill/<slug>/progress.md")
   - Progress so far: …
   - Next step: …
   - Open threads / undecided: …
   - Pointers: <issue, prior docs, artifacts>
   ```
3. **Checkpoint-as-you-go (hard requirement).** Decisions/findings are written to the working file
   the moment they're made — so compaction is always loss-free and the flush is tiny. A skill that
   holds state only in the conversation is **non-compliant**.
4. **Resume & compact, identical everywhere.** *Resume*: re-invoke the skill with the topic → it
   detects the working file → loads the resume header (not the transcript) → continues. *Compact*:
   triggers ranked by how much they can be trusted — **on-demand** ("let's start fresh", or before
   something context-expensive) is primary; a **heuristic nudge** (the primitive nudges every 10
   checkpoints) is secondary; **self-assessed proactivity is best-effort only and never
   load-bearing**, because an agent cannot reliably measure its own token usage. What guarantees
   safety is rule 3, not the trigger. `handoff` produces the cutover summary.

**Layered state:** durable **cross-session** state → the **issue tracker** (map issue, stage
labels, verification reports), never temp files; **within-session** scratch → the working file,
promoted to the issue when it crystallizes. Across stages, the next skill loads the **published
prior artifact** (PRD → Design Doc grill → tasks), never the previous transcript.

**Offload to subagents** — the strongest lever: run research and codebase search in isolated
subagents that return only findings, keeping the driver's context clean.

**A general FIC skill** exposes the primitive directly with a *generic* profile — the "starting
something open-ended, don't know how big" catch-all. It **degrades gracefully** (generic
checkpointing) and **graduates** (the shared file format means re-entering a specific skill picks up
the same file). It is the base layer the stage skills specialize, so building it makes them cheaper.

### Progress & tracking

The system already *produces* all the progress data (issues + `stage:` labels + parent/child trees
+ altitudes). Tracking is a **view over that**, never a second source of truth — which is why an
external board (Trello) is the wrong tool: it would be a second place to keep in sync.

**GitHub Projects (v2) as the canonical view.** A Project is a live, native view layer that
*references* issues/PRs (doesn't copy them). Multiple **views** over the same items, each with its
own layout/filter:

- **Board view** = the **build phase** — buildable units grouped by `stage:*`
  (`ready → dev → refactor → qa → verify → docs`). Early columns hold **slices** (`dev`/`refactor`/
  `qa`); later columns hold the **feature** at its feature-level gates (`verify`/`docs`).
- **Roadmap view** = the **planning altitude** — wayfinder maps, PRDs, Design Docs on a timeline
  (the "what's coming / 6-month" picture). Plus table views filtered by feature (PRD), assignee, or
  altitude for team lanes.

**Throughput needs a counterweight.** A stage board reports movement, and movement alone is a metric
worth gaming. Progress reporting therefore pairs it with quality signals — **cost per accepted
change** (an acceptance rate under ~50% means you are doing the review work the loop was meant to
remove), **escaped defects** (`kind:bug` filed against already-verified features), and
**human-rework rate** (how often `needs:human` fires). These reveal a pipeline shipping fast and
wrong; the board alone never will.

**The Project is org-level and spans repos.** GitHub Projects (v2) belong to a **user or
organization, not a repository** — one project can hold issues from many repos, and one repo can be
linked to many projects. That fits the umbrella-repo pattern directly:

```
org project "Discount Genie"
  ├─ core repo      → PRDs, Design Docs, wayfinder maps   (the planning altitude)
  ├─ frontend repo  → slice issues                        (the build phase)
  └─ backend repo   → slice issues                        (the build phase)
```

The PRD is the parent issue in the umbrella repo; slices are children in the code repos; everything
appears on one board. This is the feature/slice model expressed across repositories.

**One project, audience views — not two projects.** The planning altitude (product, design,
architecture) and the build phase (dev) are different audiences with different questions, and views
separate them for free. Two *projects* would split the one issue that lives in both worlds — the
feature issue is born as a PRD, carries `stage:design`, and later carries `stage:verify` and
`stage:docs` — giving it two Status fields to drift apart, which is the second-source-of-truth
problem that ruled out an external board in the first place. Split into separate projects only when
separate **teams** need separate **access**; merging two drifted Status fields later is far harder
than splitting a view.

| View | Audience | Filter |
|---|---|---|
| **Roadmap** | product / design / architecture | Ideas (`kind:wishlist`) → Shaping (PRD, design, Design Doc) → **In development** (any `stage:*`, collapsed to one column) → Done → Environment |
| **Board** | dev | `stage:ready` → `stage:docs`, every stage granular |
| **Deployment** | everyone | grouped by `Environment` — **includes closed items** |
| **Inbox** | triage | has `kind:`, no `stage:` |

Product sees *one* "In development" column where dev sees six — same items, different grouping. That
is the whole argument for views over separate projects.

**Closed items do not vanish.** A built-in workflow sets Status to Done when the issue closes; the
card stays. Use **auto-archive** to keep views fast (archived items remain in the project and can be
restored, and archiving is how a project stays under the 50,000-item cap).

**Provisioned, not hand-built.** A repo's Project is created by `setup-agent-skills` alongside its
labels — every project the system touches gets its board without a manual step. The orchestrator
then keeps Status in sync as it flips `stage:` labels.

**GitHub issue *types* vs `kind:` labels — verified, 2026-08.** Issue types are an
**organization-level** feature: an org (`OutputLabs`) exposes `Task`/`Bug`/`Feature`, while a
personal-account repo returns `issueTypes: null`. So **`kind:` labels are canonical** — they are the
only mechanism that works on every repo. Where an org *does* have types, `setup-agent-skills`
**mirrors** `kind:` onto the native type (`kind:bug` → `Bug`, `kind:wishlist` → `Feature`) for the
nicer native UI. `kind:tech-debt` has no native equivalent and stays label-only. The label is the
source of truth in both cases; the type is a projection.

**The boundary is `stage:ready`:** an item lives in the roadmap while it's being shaped (map → PRD →
Design Doc); the moment it's cut into a buildable unit and labeled `stage:ready`, it appears on the
board and flows through the pipeline.

**Consistency:** the **orchestrator already owns `stage:` transitions**, so in the same step it flips
a label it also sets the Project's Status field via the API — one writer, no drift. Labels stay
canonical; Project Status is a derived mirror. (Don't rely on Projects' built-in automations for
this.)

**Agent-driven reporting — a `status`/standup skill.** Progress reporting becomes an agent task, not
a human one: an agent queries the tracker/Project (`gh` + GraphQL) and produces a narrative report on
demand — *"3 features in flight: A in QA, B in refactor (2/3 slices), C blocked on #47; 2 awaiting
your verification."* Same canonical state, no new data. **Trello is dropped** (retire the `trello`
skill and `verify-prd`'s Trello sync) in favor of Projects.

### Standards — enforced, configured, or yours

Installing this process into a project raises a question the design has to answer: **which standards
does the system impose, and which does the project choose?** One test decides it:

> **Does a script or the orchestrator parse it?**

| Tier | Rule | Examples |
|---|---|---|
| **1 · Enforced shape** | mechanism depends on it; a project that changes it breaks the system | branch format `<type>/<issue#>-<slug>` and its type set · the label **namespaces** (`kind:`/`triage:`/`stage:` + `needs:human`) · `main` accepts only what passed `stage:verify` · every gate names an anchor · every cycle has a cap |
| **2 · Configured values** | shape is fixed, the strings are per project — the system must be *told* them | actual label strings · base branch (`main`/`master`) · tracker · test command · demo command · design system · monitoring locations |
| **3 · The project's own** | nothing mechanical reads it; the installer proposes a default the project may decline | **commit convention** (default: Conventional Commits) · code standards (the `review-loop` criteria docs) · ADR format · docs layout · language/framework conventions |

**Branch naming is tier 1** because three separate mechanisms parse that string: the orchestrator
routes on the prefix, cleanup keys off the issue number, and ralph's guard checks it for protection.

**Commit messages are tier 3** because — today — nothing in the machinery reads them. Conventional
Commits is worth *proposing* (most commits are agent-written, and machine-readable history is how you
audit what the loops did), but enforcing a standard the system does not depend on would be borrowing
authority we have no mechanical need for. Should a changelog or release automation ever parse
commits, that promotes it to tier 1 — deliberately, not by drift.

Tier 2 is already how `setup-agent-skills` works: *canonical names here, real strings per repo*. So
**installing the process means: enforce the shapes, ask for the strings, propose the rest.**

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

## Build inventory _(draft)_

The bridge from design to implementation. For each capability: closest existing analog, the call
(**reuse** as-is / **adapt** / **replace** / **new**), what kind of artifact it is, and notes. Per
the [reuse philosophy](#the-development-system), naming an existing skill is not a commitment.

**Type key:** 🟦 skill · 🟧 runner · ⬛ script · 📄 doc/template.

**Organization — three groups, and the group decides who gets the skill.** _(Resolved at build time;
see [BUILD_PLAN §0.1a](BUILD_PLAN.md).)_ Skills live at `skills/<group>/<name>/`:

| Group | Contains | Test |
|---|---|---|
| `primitives/` | portable mechanism — FIC, grilling engine, tdd, diagnose, prototype | names **no** stage, label, artifact type or branch convention |
| `flows/<flow>/` | this process — `to-prd`, slicing, orchestrator, verification, docs tail | speaks the pipeline's vocabulary |
| `general/` | tool references, stack guidance, machine setup | neither |

This is the [mechanism/policy split](#layering) one level up, and it is what makes the process
**portable**: an employer's mandated flow becomes another `flows/<name>/`, sharing every primitive
while replacing the policy. The split runs *inside* single capabilities too — the grilling **engine**
is a primitive, its **PRD/Design-Doc profiles** are flow.

**The group is the unit of installation.** [`accounts.json`](../accounts.json) maps each Claude Code
account (`CLAUDE_CONFIG_DIR`) to the groups it gets, and `toolkit sync` installs them into
`<config-dir>/skills`. A work account takes `primitives` + `general` and none of this flow. The
install tree stays **flat**, so a skill's own path never changes and regrouping is free.

### Project lifecycle & knowledge

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Deep product/vision/domain grill + scaffold context | `init-docs` | **adapt** | 🟦 | add the deep product/vision grill layer on top of today's pattern-grill |
| Maintain docs; feature-level `stage:docs` pass | `sync-docs` | **adapt** | 🟦 | add feature-level mode reading git + verification report + issue tree |
| `MONITORING.md` (per-project + root-shared) | (none) | **new** (in `init-docs`/`sync-docs`) | 📄 | mirrors the `CONTEXT.md` monorepo hierarchy |
| Tracker / label / branch vocabulary setup | `setup-agent-skills` | **adapt** | 🟦 | teach it the `stage:` labels + `<type>/<issue#>-<slug>` branch convention |
| Standards templates | `init-docs/STANDARDS_TEMPLATES.md` | **reuse** | 📄 | already broad; extend as needed |

### Front door & grilling

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Wayfinding: scope triage + map + dispatch | (ref: Matt Pocock wayfinder) | **new** | 🟦 | the universal front door; routes to grill profiles |
| Grilling **engine** (behavior + checkpointing) | `grill-me` / `grill-verified` / `grill-with-docs` | **replace** | 🟦 | one engine; **retire all three** (incl. `grill-with-docs`) once it covers them |
| Grill **profiles** (PRD / Design Doc / Task / ticket) | — | **new** | 📄 | config/prompts parameterizing the engine |

### Document producers

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| PRD producer (what/why + success criteria) | `to-prd` | **adapt** | 🟦 | slim down; strip impl detail; **add success criteria** |
| Design Doc producer (how, verified, prototype ref) | back half of `to-prd` | **new** | 🟦 | `to-design-doc`; links parent PRD |
| Slice + implementation-plan producer | `to-vertical-issues` (+ `to-issues`) | **adapt** | 🟦 | align to `feat/`+`slice/` model & `stage:` labels; emit checkbox plan. **Keep `to-issues` and `to-vertical-issues` separate** (not consolidated) |

### Design / prototype

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Prototype (salvage/throwaway, freeze screenshots) | `prototype` | **adapt** | 🟦 | add HITL salvage path in real design system; seed `design/…`→`feat/…`; freeze screenshots to issue |

### Build loops

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Dev loop | `ralph` | **adapt** | 🟧 | stop at dev-done (orchestrator owns labels); run in given worktree (no self-branch); impl-only prompt; keep inline Codex correctness gate; unit/integ TDD (`tdd` guidance) |
| Refactor loop = find→fix→recheck | `review-loop` + `ralph` | **reuse** (as chained) | 🟧 | chaining is orchestrator policy; `ralph` is the fix actor with a refactor prompt; owns structure + **design patterns** |
| QA loop (Playwright, e2e, vs prototype) | (none) | **new** | 🟧 | **two-agent** (driver holds Playwright + strategist/critic); the one genuinely new runner |
| **Critique loop** — N-round two-family review of an artifact | `review-loop` | **adapt** | 🟧 | target adapter: a diff (code) or files read as-is (plans/specs). Profiles = prompt sets |
| Coherence criteria (plans/specs) | — | **new** | 📄 | `criteria/coherence.md` — C-1..C-8; operationalizes "does this document hold together" |
| `ralph-dg` | — | (per-project config) | 🟧 | project-specific variant, not core |

### Orchestration & scripts

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Orchestrator pass (advance stages, caps, QA=1) | `ralph-orchestrator` | **adapt** | 🟦 | add stage machine, `feat/` model, concurrency caps |
| Worktree create/teardown **+ seed** | (none) | **new** | ⬛ | called by orchestrator; ralph never does this. **Seed** = `design/…` becomes the target branch's first commit |
| Label flips / stage transitions | (none) | **new** | ⬛ | drive the `stage:` machine |
| State-aware cleanup (`~/.ralph/builds`, branches) | (none) | **new** | ⬛ | keyed to the **merge**, never the close |

### Verification, FIC & feedback

| Capability | Closest existing | Call | Type | Notes |
|---|---|---|---|---|
| Feature-level verification + report to tracker | `verify-prd` (+ `audit-the-prd`, `close-prd`) | **adapt** | 🟦 | run on `feat/…` worktree; report + findings→linked issues; use PRD success criteria |
| Shared **FIC primitive** (working file, resume header, checkpoint, resume/compact) | `handoff` (+ `session-keeper` for keep-alive) | **new** | 🟦 | the base every long-running skill inherits; `handoff` **adapts** into the cutover step |
| General FIC skill | — | **new** | 🟦 | primitive + generic profile; base layer stage skills specialize |
| Capture inbox (`kind:bug`/`tech-debt`/`wishlist`) | `log` | **adapt** | 🟦 | add the `kind:` namespace; no `stage:` label = the inbox |
| Triage **engine** | `triage` | **adapt** → `primitives/` | 🟦 | mechanism: read the board, evaluate, apply a state, post templates |
| Triage **state profile** | (inside `triage`) | **new** → `flows/` | 📄 | the vocabulary is policy — a work flow is another profile, not a second skill |
| Bug front-half | `diagnose` | **reuse** | 🟦 | peer of the grill: for a hard bug the diagnosis *is* the Design Doc |
| `needs:human` modifier | `ready-for-human` | **replace** | 📄 | who-executes, not where-it-is; orchestrator skips these when dispatching |
| Log-fetching skill | — | **new** (later) | 🟦 | resolves nearest `MONITORING.md`; optional/deferred |
| GitHub Projects view (board + roadmap) | (none) | **new** (in `setup-agent-skills`) | 📄 | orchestrator sets Status alongside labels; a view, not a source of truth |
| `status`/standup progress reporter | — | **new** | 🟦 | agent narrates progress from tracker/Project (`gh` + GraphQL) |
| Trello tracking | `trello` + `verify-prd` sync | **remove** | 🟦 | superseded by GitHub Projects |

### Suggested build order

1. **FIC primitive + general FIC skill** — everything else depends on it (checkpoint discipline).
2. **Grilling engine + PRD/Design-Doc profiles** + `to-prd`/`to-design-doc` — the design front half.
3. **Branch/label conventions + worktree & cleanup scripts** — the state-machine substrate.
4. **Orchestrator pass** + **QA runner** + dev/refactor wiring — the build phase.
5. **verify-prd adapt** + **sync-docs `stage:docs`** — the tail.
6. **Wayfinding** wraps the front; **monitoring/log-fetch** and the standing cron come last.

---

## Open questions

Being grilled into shape. Not final.

1. ~~Pre-PRD stage~~ — RESOLVED. Wayfinding is the universal front door (optional/scale-triaged);
   research/POC are informal subagent-driven feeders.
2. ~~Loops as concrete skills~~ — RESOLVED. Dev = **adapted** `ralph` (+ inline Codex gate);
   Refactor = orchestrator policy chaining `review-loop` + `ralph` (owns patterns); QA = one new
   **two-agent** Playwright runner/skill. Every build loop is a two-family dialogue.
3. ~~Meta-orchestrator~~ — RESOLVED. Manual pass first; standing loop = same pass on a cron.
4. ~~Label vocabulary~~ — RESOLVED. `stage:` namespace; slice-level labels (`dev`/`refactor`/`qa`)
   on the slice issue, feature-level (`verify`/`docs`) on the PRD/feature issue.
5. ~~Build inventory~~ — DRAFTED & confirmed. See [Build inventory](#build-inventory-draft). Grills
   retired for the unified engine; `to-issues`/`to-vertical-issues` kept **separate**; process skills
   get their own directory; build order starts with the FIC primitive.
6. ~~`to-prd` fix~~ — RESOLVED. Split into **`to-prd`** (what/why + **success criteria**, no impl
   detail) and a new **`to-design-doc`** (how, verified, references the prototype), each fed by its
   matching grill profile. See [Grilling engine](#grilling-engine--profiles).
7. ~~Design step depth~~ — RESOLVED. Salvage-as-default for UI-meaningful features (real design
   system → dev-loop starting point → refactor → QA vs frozen screenshots), throwaway for minor UI.
   Screenshots → issue; salvaged code → short-lived `design/…` branch that **seeds the `feat/…`
   integration branch**. See [Documents](#documents).
8. ~~Monitoring axis~~ — RESOLVED. Doc-first: `MONITORING.md` mirrors the `CONTEXT.md` monorepo
   hierarchy (per-project + optional root-shared), at project root not `.agents/`; log-fetching
   skill later resolves the nearest one. See [Cross-cutting axes](#cross-cutting-axes).
9. ~~Release/deploy~~ — RESOLVED. Standard ends at the verified `feat → main` promote (the deploy
   trigger); deploy itself is CI/CD, out of scope. Continuous cadence and close-on-merge; deployment is tracked by the
   `Environment` **field** on a closed issue, so there is **no** `released` state. See [Release & deploy](#release--deploy).

Also resolved this session: **branch naming standard** (`<type>/<issue#>-<slug>`, buildable-unit
only, with the `feat/…` integration branch) — see [Branch naming](#branch-naming); and the
**`feat/…` integration-branch model** with **feature-level verification**.
