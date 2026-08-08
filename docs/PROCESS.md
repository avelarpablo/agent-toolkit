# The Development System

How we take software from a vague idea (or an empty repo) to shipped, verified, documented
code — and how feedback loops back. This is the umbrella. Its one **fully-designed** part is the
[Feature Lifecycle](#the-feature-lifecycle); the other parts are designed skeletons we will
deepen later.

> Status: **in design, not built.** We are defining the standard from zero. Sections marked
> _Open_ or _Stub_ are not final.
>
> **Reuse philosophy — existing skills are references, not mandates.** When this doc names an
> existing skill/runner (`grill-me`, `review-loop`, `ralph`, `prototype`, `init-docs`, …), read it
> as *"the closest existing analog to what we want here"* — **not** a commitment to reuse it. The
> design is driven by what we want; each component is decided at build time as **reuse / adapt /
> replace-with-new / remove**. Purpose-built replacements (and retiring superseded skills) are
> expected. The [Build inventory](#open-questions) (#5) is where every such call is made deliberately.

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

**Wayfinding routes to the grill primitives — it does not replace them.** The grill skills are
reusable primitives (the interrogation); wayfinding is policy (which grill, when, at what scope) —
the same mechanism/policy split as ralph vs. the orchestrator. Wayfinding owns exactly two things:
**scope triage** (Task/Feature/Product) and **dispatch** (route each open decision to the right
grill):

| Grill primitive | Kind of question | Hits real code? | Routed to for |
|---|---|---|---|
| `grill-me` | product / "what" | no | PRD, task definition, general design |
| `grill-with-docs` | domain / terminology, vs `CONTEXT.md` + ADRs | reads docs | sharpening against the knowledge base; triage |
| `grill-verified` | technical / "how", evidence-first | **yes** | Design Doc & implementation plans |

"Universal front door" is conceptual, not "always run a heavy map." **Product/foggy** → full
wayfinding (map + dispatch). **Feature** → skip the map; `grill-me` → PRD, later `grill-verified`
→ Design Doc. **Task** → a brief `grill-me` → one issue. A clear feature never pays the map tax.

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

Grilling appears **twice**, in two flavors: a **product grill** (`grill-me`) decides *what*
(→ PRD/Task); a **verified grill** (`grill-verified`, checked against the code) decides *how*
(→ Design Doc).

### Documents

**PRD — *what & why*.** The scope lock. Problem, solution (user's view), user stories, success
criteria, out-of-scope. **No implementation detail** — that goes in the Design Doc. Product grill.

**Design (prototype) — *look & feel*.** Its own step because UI discussion diverges from
delivered UI. Runs in a worktree (produces code → main stays pristine). Uses a HITL variant of the
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
  clean.

**stage:docs — the tail.** After the feature passes verification (and before promoting to `main`),
one **feature-level** `sync-docs` pass on the `feat/…` branch. It reads **git diffs + the
verification report(s) + the issue tree** (not live conversation — long gone by now → FIC), so docs
reflect verified reality *including* verification-driven changes. AFK-able; you give the doc changes
a light review. Then `feat → main`.

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

Cleanup is **state-aware**: a build dir is freed only once its issue is verified/closed — human
verification is the trigger. Keys off the same issue state machine as everything else.

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

The **integration branch (`feat/…`) exists only when a feature has ≥2 slices**. Single-unit work
(a `task/…`, a lone `slice/…`, a one-off `fix/…`) skips it and goes straight to `main`. `main` and
any deploy branches are protected; only a verified `feat/…` or `task/…` promotes into `main`.

The **type vocabulary is orchestrator policy**, not ralph's — ralph only needs "you're on a
non-protected branch." This supersedes ad-hoc conventions (`feature/*`, `standards/…`). Canonical
for projects using the system; the agent-toolkit repo itself may stay looser (it often has no
per-change issue).

### State machine & labels

**Triage axis (existing)** governs getting an issue *ready*:
`needs-triage → needs-info → ready-for-agent / ready-for-human / wontfix` (+ `bug`/`enhancement`).

**Build-stage axis (new)** takes over once implementation starts — one label at a time. The stages
split across two altitudes: **slice-level** loops run on each slice issue and end when the slice
merges into `feat/…`; **feature-level** verify and docs run on the feature (PRD) issue.

*On the slice issue:*

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:ready` | eligible to start (today: `ready-for-agent`) | orchestrator picks it up |
| `stage:dev` | dev loop running | dev-loop checkboxes done |
| `stage:refactor` | refactor loop running | review-loop returns zero blockers |
| `stage:qa` | QA loop running | e2e written, proof captured → **merge into `feat/…`**; slice done |

*On the feature (PRD) issue, once all slices have merged into `feat/…`:*

| Stage label | Meaning | Transition trigger |
|---|---|---|
| `stage:verify` | **human gate** — verify the assembled feature on the `feat/…` worktree | you sign off |
| `stage:docs` | feature-level `sync-docs` pass on `feat/…` | docs reviewed → **promote `feat → main`** (deploy trigger) → close |

A waiting slice carries the existing `blocked` label. **Convention:** all lifecycle-position
labels share one namespace (`stage:`); `ready-for-agent` maps to `stage:ready` (relabel deferred).
`stage:verify` ≠ `ready-for-human` (verify = check completed work; ready-for-human = implement).
These are **canonical** names; real strings per repo come from `setup-agent-skills`. (Single-unit
`task/…` work carries all stages on its one issue and promotes straight to `main`.)

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
is always serial** — one feature at a time, by you, on the `feat/…` worktree.

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
- **Issue lifecycle: close-on-merge by default.** verify → docs → promote → close (→ triggers
  cleanup of `~/.ralph/builds/` and the branch). Add an optional `released` state only if a
  project's deploy is async/gated and "merged but not yet live" must be tracked distinctly.

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
   **proactive** (agent watches its own context; nearing ~50% it flushes, finalizes the header, and
   tells you to restart) or **on-demand** ("let's start fresh"). `handoff` produces the cutover
   summary.

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
5. **Build inventory** *(the last open item)* — a per-capability **decision table** produced once
   the design settles: `desired capability → closest existing analog → {reuse / adapt /
   replace-with-new / new} → what to remove`, and for each, whether it's a skill, a runner
   primitive, or a script. Must at least cover: the **grilling engine + profiles**, the **shared FIC
   primitive** + **general FIC skill**, `to-prd` / `to-design-doc`, the **QA runner**, the
   **orchestrator pass**, worktree-lifecycle scripts, and the label/branch conventions.
6. ~~`to-prd` fix~~ — RESOLVED. Split into **`to-prd`** (what/why + **success criteria**, no impl
   detail) and a new **`to-design-doc`** (how, verified, references the prototype), each fed by its
   matching grill profile. See [Grilling engine](#grilling-engine--profiles).
7. ~~Design step depth~~ — RESOLVED. Salvage-as-default for UI-meaningful features (real design
   system → dev-loop starting point → refactor → QA vs frozen screenshots), throwaway for minor UI.
   Screenshots → issue; salvaged code → short-lived `design/…` branch consumed by slice #1. See
   [Documents](#documents).
8. ~~Monitoring axis~~ — RESOLVED. Doc-first: `MONITORING.md` mirrors the `CONTEXT.md` monorepo
   hierarchy (per-project + optional root-shared), at project root not `.agents/`; log-fetching
   skill later resolves the nearest one. See [Cross-cutting axes](#cross-cutting-axes).
9. ~~Release/deploy~~ — RESOLVED. Standard ends at the verified `feat → main` promote (the deploy
   trigger); deploy itself is CI/CD, out of scope. Continuous cadence, close-on-merge, optional
   `released` state. See [Release & deploy](#release--deploy).

Also resolved this session: **branch naming standard** (`<type>/<issue#>-<slug>`, buildable-unit
only, with the `feat/…` integration branch) — see [Branch naming](#branch-naming); and the
**`feat/…` integration-branch model** with **feature-level verification**.
