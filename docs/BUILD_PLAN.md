# Build Plan — The Development System

The implementation plan for the system designed in [PROCESS.md](PROCESS.md). `PROCESS.md` is the
**spec** (what & how it's designed); this is the **plan** (what to build, in what order, and how to
know each piece is done).

> Status: **0.1, 0.1a, 0.1b done**; work-kind model (1.1a), branch standard and stage gates decided. Phase 0 is hand-built; the system starts self-hosting after Phase 3.

## The bootstrapping principle

**You cannot use this pipeline to build this pipeline** — the pipeline is what you're building. So:

- **Phases 0–3 are hand-built** — interactively (with you + an agent), using the *existing* tools
  (today's `ralph`, `grill-*`, etc.). They can't flow through the not-yet-built pipeline.
- **The self-hosting boundary is after Phase 3 — for the *build* phase.** Once the design producers
  (0), substrate (1), loops (2), and orchestrator (3) exist, the build spine (dev → refactor → QA →
  merge) self-hosts — so Phase 4+ items can be *built* through the pipeline (dogfooding). But the
  mergeable **tail** (verify 4.1, docs 4.2, and the promote they gate) isn't built yet, so those
  items' verify/docs/promote is hand-finished until 4.1+4.2 exist; after that the tail self-hosts too.
- **A gentle recursion:** as soon as 0.1–0.3 exist (FIC + grilling engine + producers), even the
  hand-building of later phases can use them to grill and record its own plans.

**Legend:** each item lists **done-when** (acceptance check), **needs** (prerequisites), and **↪**
(the [Build inventory](PROCESS.md#build-inventory-draft) row it implements).

---

## Phase 0 — Design front-half (hand-built)

The pieces that let you produce documents with FIC discipline. After Phase 0 you can grill →
PRD → Design Doc by hand, with loss-free compaction.

### 0.1 FIC primitive + general FIC skill — ✅ **DONE**
The shared contract every long-running skill inherits, and the standalone catch-all.
- **done-when:** a skill can open a per-topic working file with a live resume header (copy-pasteable
  resume command), checkpoint a decision the moment it's made, and a *fresh session* resumes from
  the working file alone (no transcript). The general FIC skill runs on an arbitrary topic. —
  **met:** verified end-to-end from a clean shell knowing only the slug.
- **needs:** nothing (foundation).
- **↪** Shared FIC primitive; General FIC skill. Reference: `handoff`, `session-keeper`.

**Built as:** `primitives/skills/fic/` — `fic` (the script: `init`/`checkpoint`/`header`/`resume`/
`list`/`path`/`compact`), `PROTOCOL.md` (the contract skills inherit by reference), `SKILL.md` (the
generic profile). Working files live at `<dotdir>/<slug>/progress.md`, dotdir per skill (`.fic`,
`.grill`, `.verify`, …), auto-gitignored; `init` is idempotent so start and resume are one call.

**Decisions made at build time:**
- **Script + protocol doc**, not prose alone — deterministic writes, uniform format, and
  checkpointing is one command. Skills inherit by referencing `PROTOCOL.md`.
- **Single `progress.md`** per topic (resume header + append-only log), not the multi-file
  `.grill/` layout — a fresh session reads exactly one file. Profiles may add siblings later.
- `fic compact` **refuses to run on an incomplete header** — the protocol enforces its own
  non-lossiness rather than trusting the agent to remember.

### 0.1a Skill layering + per-account install — ✅ **DONE**
Inserted before 0.2 because the split cuts *through* it: the grilling engine is a primitive, its
PRD/Design-Doc profiles are flow. Building them as one unit would weld them together.
- **done-when:** skills are grouped by layer; an account can be given some groups and not others;
  a work account gets the primitives without this flow. — **met:** `shopstack` now installs 18
  skills (primitives + general) and none of the 13 flow skills.
- **needs:** nothing. **↪** Not in the original inventory — surfaced by "can skills be per-environment?"

**Built as:** `<group>/skills/<name>/` — each group owns its own `skills/` (and `runners/`) tree —
with three groups: `primitives/` (11), `flows/personal-dev/` (13), `general/` (7); `accounts.json`
mapping each account to its groups; `toolkit sync
[--account <name>]` installing per account into `<config-dir>/skills`. Classification test, group
table and rationale: [PROCESS.md → Organization](PROCESS.md#build-inventory-draft).

**Decisions made at build time:**
- **Grouped source, flat install** — supersedes 0.1's "flat `skills/fic/`". `toolkit` maps
  `<group>/skills/<name>` → `<config-dir>/skills/<name>`, so the group is purely an install-time
  concern: a skill's own path never changes and regrouping costs nothing. This removes the
  discovery risk that motivated flat-source in the first place.
  *(Closes the "process-skills directory" open build-time detail.)*
- **`toolkit` owns skills; `claude-env` owns settings/hooks/statusline.** `claude-env` makes accounts
  *alike*; skills are the thing that must *differ*. Its skills-linking block was removed.
- **`toolkit sync` refuses when two accounts resolve to one skills directory** — learned the hard
  way: mid-build, both accounts were symlinked at the shared `~/.agents/skills`, and syncing
  shopstack stripped personal's flow skills from the shared tree.

### 0.1b Critique loop — document target + coherence criteria — ✅ **DONE**
Built before 0.2 so it serves the plan work still ahead of it.
- **done-when:** `review-loop` can review a plan/spec as well as a diff, against coherence criteria,
  and the pass finds real defects in this system's own documents. — **met:** dogfooded on
  `PROCESS.md` + `BUILD_PLAN.md`.
- **needs:** nothing. **↪** Critique loop (**adapt** `review-loop`); Coherence criteria (**new**).

**Built as:** `--files <path>` target adapter (line-numbered, so findings cite jumpable locations)
alongside the existing diff adapter; `--profile` selecting `prompts/<profile>/`, inferred from the
target (files → `coherence`, diff → `code`); `criteria/coherence.md` with rules C-1…C-8;
profile-aware assembly. Rationale:
[PROCESS.md → The critique loop](PROCESS.md#the-critique-loop--one-engine-two-targets).

**Decisions made at build time:**
- **Generalize the runner, don't fork it.** Verified first that `ralph` and `review-loop` are *not*
  the same shape — `review-loop` is an N-round two-family dialogue; ralph is a mutating loop with a
  single-shot Codex gate. The shared primitive is "critique an artifact against criteria with a
  second family"; `review-loop` was already one adapter away from serving both targets.
- ~~**On demand now, gate later**~~ — **SUPERSEDED.** The gate is now principle 11: *every* stage
  artifact passes a two-family gate before publishing, not just the 0.3 producers. Each stage's
  criteria doc is authored in that stage's own build item (see the gate table in
  [PROCESS.md → Stage gates](PROCESS.md#stage-gates--no-artifact-is-final-unreviewed)); `coherence.md`
  is the first of them and the template for the rest.
- **Criteria grade coherence, not judgment** — C-1…C-8 find contradictions, duplicate concepts,
  orphaned references, ordering violations, unfalsifiable criteria, resolved-not-decided questions,
  unstated load-bearing assumptions, scope leaks. Disagreeing with a recorded decision is explicitly
  out of scope, and padding is explicitly forbidden.

### 0.2 Grilling engine + PRD & Design Doc profiles
One engine, parameterized by a profile; checkpoints via 0.1.
- **done-when:** the PRD profile runs a full grill (one question at a time, recommends answers,
  checkpoints each decision) and the Design Doc profile additionally verifies claims against code.
  Both leave a resumable working file.
- **needs:** 0.1, 0.1a.
- **↪** Grilling engine (**replace** `grill-me`/`grill-verified`/`grill-with-docs`); Grill profiles —
  the **PRD + Design-Doc** two here (the Task + Wayfinding-ticket profiles land with wayfinding, 4.3).
- **layering (from 0.1a):** the engine ships as `primitives/skills/grill/` — it must name no stage,
  label or artifact type — and the PRD/Design-Doc profiles as `flows/personal-dev/skills/`. Build
  them apart from the start; the engine has to be usable under a flow that isn't this one.

### 0.3 `to-prd` + `to-design-doc` producers
Synthesize the grill's working file into published tracker issues. **Both producers gate before
publishing** (principle 11): `to-prd` against PRD criteria (2 rounds — the two-family floor, since
`review-loop` round 1 is the authoring family), `to-design-doc` against Design-Doc criteria (3 rounds). Authoring those two criteria docs is part of this item.
- **done-when:** `to-prd` publishes a PRD (what/why + **success criteria**, no impl detail);
  `to-design-doc` publishes a Design Doc (how, verified, prototype reference) linked to its PRD.
  Neither interviews — they synthesize the working file. On publish each sets the feature's Project
  `Status` to *Shaping* (the producers' disjoint writer, per
  [PROCESS.md → Progress & tracking](PROCESS.md#progress--tracking)).
- **needs:** 0.2; **0.1b** (the critique-loop gate mechanism + coherence criteria each producer runs
  before publishing); **1.1** (the publish sets `Status = Shaping`, which needs the Project
  `setup-agent-skills` provisions — the same Project dependency 3.1 makes explicit). In practice 1.1
  (no deps) lands well before this on its own track, but the acceptance check writes `Status`, so the
  prerequisite is declared, not assumed.
- **↪** PRD producer (**adapt** `to-prd`); Design Doc producer (**new** `to-design-doc`).

---

## Phase 1 — State-machine substrate (hand-built)

The mechanics that let work flow as issues + labels + branches + worktrees.

### 1.1 Label & branch conventions in `setup-agent-skills`
- **done-when:** running it on a repo provisions the `stage:*` labels (including `stage:design`), `kind:*`, `triage:*`, `wayfinder:map`, the
  `blocked` label (a waiting slice's marker, consumed by the orchestrator's dependency scheduling) plus
  the `needs:human` modifier, and documents the `<type>/<issue#>-<slug>` branch convention (incl.
  `feat/`), mapped to real per-repo strings.
- **needs:** nothing (can parallel Phase 0).
- **also provisions the GitHub Project** — **org-level, spanning every repo of the product** (PRDs in
  the umbrella repo, slices in the code repos), with the four audience views (roadmap / board /
  **deployment** / inbox — matching [PROCESS.md → Progress & tracking](PROCESS.md#progress--tracking))
  plus the `Status` single-select and its lifecycle values (Ideas / Shaping / In development / Done —
  the Roadmap's grouping field, written per-phase by `log`/producers/orchestrator/built-in) and the
  `Environment` single-select (default Staging + Production) — and
  **mirrors `kind:` onto native issue types where the owner is an org** — verified
  2026-08: types are org-only (`OutputLabs` exposes Task/Bug/Feature; a personal-account repo returns
  `issueTypes: null`), so labels stay canonical and the type is a projection.
- **branch conventions follow [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)**,
  with `main` accepting only what cleared `stage:docs` (after a passed `stage:verify`) — prefixes are descriptive, not permissions.
- **provisions the promote-PR template** — the `feat → main` PR body carries the closing keywords
  (`Closes #<feature>`, and `owner/repo#N` for a PRD in the umbrella repo) so the merge auto-closes
  the feature issue on the default branch. The template is provisioned here; the orchestrator (3.1)
  opens the PR from it. See [PROCESS.md → Release & deploy](PROCESS.md#release--deploy).
- **↪** Tracker/label/branch vocabulary setup (**adapt** `setup-agent-skills`).
- **includes the triage merge:** delete `ready-for-agent` (it *is* `stage:ready`); convert
  `ready-for-human` into the `needs:human` modifier; keep `needs-info`; `wontfix` → closed with a
  reason. See [PROCESS.md → State machine & labels](PROCESS.md#state-machine--labels).
- **migration, measured** (`shopstackio/discount-genie-core`, 2026-08): **≥200** issues carry
  `ready-for-agent`, 18 `ready-for-human`, 48 `needs-triage` — against 99 open, so most are closed.
  `gh`-scriptable, but relabel **open issues only**; closed history keeps its old labels.
- **the three standards tiers** ([PROCESS.md](PROCESS.md#standards--enforced-configured-or-yours))
  are what this item implements: enforce the shapes, ask for the tier-2 strings, propose tier-3
  defaults (commit convention, code standards, ADR format) that a project may decline.
- **field evidence:** that repo independently grew `needs-attention` ("needs a human step or new-UI/
  design attention") — the `needs:human` modifier, arrived at from real use before we designed it.

### 1.1a Work-kind intake — `log` + triage engine split
The inbox and its exits, so captured work has a route in rather than sitting in a parking lot.
- **done-when:** `log` writes `kind:*` and no `stage:` label (and, for a `kind:wishlist` item, sets the
  Project `Status` to *Ideas* — its phase's disjoint writer, per
  [PROCESS.md → Progress & tracking](PROCESS.md#progress--tracking)); picking an item up runs the
  analysis its kind calls for — `bug` → `diagnose`, `tech-debt` → scoped refactor — and lands at
  `stage:ready` with a plan. The triage **engine** moves to `primitives/` with the state vocabulary as
  a flow profile.
- **needs:** 1.1 (labels), 0.1a (the primitive/flow split).
- **`wishlist` is deliberately out of scope here.** Its exit is *promotion into wayfinding*, which
  does not exist until 4.3 — and 4.3 needs this item's kinds. Until then a promoted wishlist item is
  handed to whatever grill profile exists; 4.3 closes the loop. (Naming wayfinding in this item's
  acceptance check made the phase graph unsortable.)
- **↪** Capture inbox (**adapt** `log`); Triage engine (**adapt** → `primitives/`); Triage state
  profile (**new**); Bug front-half (**reuse** `diagnose`).
- **decided:** kinds need no parallel pipelines — they converge at `stage:ready`; research/POC are
  wayfinder-created, not logged; findings route by implication, with pure knowledge going to
  `CONTEXT.md`/ADR rather than the tracker. See
  [PROCESS.md → Work kinds](PROCESS.md#work-kinds--the-inbox-and-its-exits).

### 1.2 Worktree, label-flip & cleanup scripts
Deterministic mechanism the orchestrator will call.
- **done-when:** scripts can (a) create a worktree on `<type>/<issue#>-<slug>` off a given base and
  tear it down; (b) flip an issue's `stage:` label; (c) state-aware cleanup of `~/.ralph/builds/<branch>/`
  and merged branches, **keyed to the merge** (not the close — deployment must never stall cleanup);
  (d) **seed** one branch from a `design/…`
  branch — the design step's unusual move, where approved prototype code becomes the starting commit
  of `feat/…` (or the lone `slice/…`/`task/…`) before `design/…` is deleted. Each runs standalone and
  idempotently.
- **needs:** 1.1 (conventions).
- **↪** Worktree create/teardown; Label flips; State-aware cleanup (all **new** ⬛).

### 1.2a Design step — prototype → approved → seeds the branch
The one planning activity that **produces code**, and the reason `stage:design` exists. Closes the
coherence blocker where 2.3 declared `needs: 0.x` and `0.x` resolved to nothing.
- **done-when:** for a UI-meaningful feature, the step opens a `design/<issue>-<slug>` worktree,
  generates several variations in the project's **real design system**, and holds at
  `stage:design` + `needs:human` until you approve one — visibly on the board, the way
  `stage:verify` is. On approval it freezes screenshots onto the feature issue, **holds** `design/…`
  (the seed + delete via 1.2(d) happen later, at target-branch creation — the target `feat/…` vs
  lone `slice/…`/`task/…` is not known until slicing), clears `stage:design`, and returns the feature
  to **shaping** (Design Doc → slicing) — it carries **no** `stage:` label until the all-slices-merged
  rollup sets `stage:verify` (3.1). It does **not** move the feature to `stage:ready` — that label is
  slice-level (orchestrator-dispatchable), and a feature has no implementation plan or branch.
- **needs:** 1.1 (`stage:design` label), 1.2 (worktree + seed scripts), 0.3 (a PRD to design against).
- **feeds:** 1.3 (slices inherit the prototype through `feat/…`), 2.3 (QA's visual acceptance
  reference).
- **↪** Prototype (**adapt** — the HITL salvage path). Salvage is the default for UI-meaningful
  features; throwaway keeps screenshots only.
- **optional by design:** non-UI features skip the stage entirely.

### 1.3 Slice + implementation-plan producer
- **done-when:** `to-vertical-issues` emits slice issues aligned to the `feat/`+`slice/` model with
  `stage:ready`, each carrying a checkbox implementation plan, blocked-by graph, and demo command —
  and **passes the slicing gate before publishing** (principle 11): a 2-round critique loop
  (independently shippable? demo command real? plan executable?) **plus the reality anchor — the demo
  command actually runs**, per the [gate table](PROCESS.md#stage-gates--no-artifact-is-final-unreviewed).
  `to-issues` kept separate.
- **needs:** 1.1, 0.3 (consumes a Design Doc), 0.1b (the critique-loop gate it runs before publishing).
- **↪** Slice + implementation-plan producer (**adapt** `to-vertical-issues`).

---

## Phase 2 — Build loops (hand-built)

### 2.1 Dev loop — adapt `ralph`  ⚠ highest-risk item — see [Risks](#risks--focus-points)
- **done-when:** ralph runs in a *handed* worktree (self-branching disabled), implements a slice's
  checkbox plan with unit/integ TDD + the inline Codex correctness gate, **stops at dev-done without
  closing the issue or touching labels**, and signals completion by writing
  `~/.ralph/builds/<branch>/status.json` (the [completion signal](PROCESS.md#the-completion-signal--how-a-loop-tells-the-orchestrator-its-done):
  `{issue,branch,loop,outcome:done|capped|failed,summary,anchor}`) plus a matching exit code.
  Impl-only prompt.
- **needs:** 1.2 (worktree), 1.3 (a slice to consume).
- **↪** Dev loop (**adapt** `ralph`).
- **the drift is in the runner, not just the prompt** — re-audited 2026-08, and far larger than
  first recorded. Prompt: `:23` adds the deleted `ready-for-agent`, `:34` enforces the superseded
  `feature/*`, `:21`/`:78`/`:80` close the issue. **Script:** `ralph:1620` `gh issue close`;
  `ralph:675,876,915,1003,1599,2411` `--add-label ready-for-agent`; `ralph:2168` *creates* the
  deleted label set; `ralph:643,705` treat `ready-for-human` as a hard blocker rather than an
  orchestrator-read modifier; `ralph:841-855` **creates branches**, which
  [PROCESS.md](PROCESS.md#layering) says ralph never does. Confirms the fork this item was flagged
  to be.

### 2.2 Refactor loop wiring
- **done-when:** an orchestrated chain runs `review-loop` (find) → `ralph` (fix, refactor prompt) →
  re-check until `review-loop` returns **zero blockers, or a round cap is hit** — at which point it
  stops, flips `needs:human`, and reports what it could not fix (principle 12: every cycle has two
  exits). Like the other backgrounded loops it ends by writing the
  [completion signal](PROCESS.md#the-completion-signal--how-a-loop-tells-the-orchestrator-its-done)
  (`status.json`, `loop:"refactor"`, `outcome:done` on zero blockers / `capped` on the cap) — the
  orchestrator's chaining logic emits it since the loop is orchestrator policy, not a single runner.
  Maintainability/pattern quality is gated
  the only way it can be tested — by encoding pattern violations as blockers in the `review-loop`
  criteria file, not by an unfalsifiable "applies the best design pattern" clause. `ralph` fix-actor
  reused with a refactor prompt.
- **needs:** 2.1 (ralph as fix actor), `review-loop` (reuse as-is).
- **↪** Refactor loop (**reuse** `review-loop` + `ralph`, chained).

### 2.3 QA runner (new)
- **done-when:** a two-agent QA runner (driver holds Playwright MCP + strategist/critic) drives the
  assembled app, checks against frozen prototype screenshots, and writes an e2e suite, then emits the
  same [completion signal](PROCESS.md#the-completion-signal--how-a-loop-tells-the-orchestrator-its-done)
  (`status.json`, `loop:"qa"`) as the dev loop. It **consumes** the frozen screenshots as its visual
  acceptance reference; **producing** them (the `prototype` HITL salvage adaptation) is 1.2a's
  deliverable, not this item's.
- **needs:** Playwright MCP; **1.2a** (the design step — QA's visual acceptance reference comes from
  its frozen screenshots).
- **↪** QA loop (**new** 🟧). *(The Prototype **adapt** inventory row is owned by 1.2a.)*

---

## Phase 3 — Orchestrator (the self-hosting turning point)

### 3.1 Orchestrator pass
- **done-when:** a manual pass reads the board and, respecting the four conflict dimensions +
  concurrency caps (QA=1) and skipping anything flagged `needs:human`, advances every
  legally-advanceable issue: creates/tears down worktrees
  (via 1.2), launches the right loop — **including `stage:design`, which it dispatches AFK and then
  holds with `needs:human` for your pick** — reads each finished loop's
  [completion signal](PROCESS.md#the-completion-signal--how-a-loop-tells-the-orchestrator-its-done)
  (`status.json`: `done` advances, `capped`/`failed` flip `needs:human`), flips the `stage:` label,
  and reports. Idempotent + resumable (re-run picks up from labels + status files).
- **owns the two slice/feature joins** (see [State machine](PROCESS.md#state-machine--labels)):
  (a) on a slice's QA merge into `feat/…` it **closes the slice issue** — closing, not a terminal
  label, is what keeps a stage-less slice out of the [inbox](PROCESS.md#work-kinds--the-inbox-and-its-exits)
  (inbox = **open** + `kind:` + no `stage:`); (b) on closing the **last** open slice child of a
  feature it flips the feature (PRD) issue to `stage:verify` (the rollup that reassembles parallel
  slices). It also **opens the `feat → main` promote PR** from the template (see 1.1) when a feature
  leaves `stage:docs`.
- **Project Status writes are *not* part of this acceptance check** — the Project is provisioned back
  in 1.1, but keeping its Status field in sync is 4.4's deliverable (one writer per field, added
  deliberately), so 3.1 advances labels without touching Status. 4.4 adds the Status write to the
  pass it already owns. (Requiring it here made 3.1 and
  4.4 mutually blocking.)
- **needs:** Phases 1 + 2 complete.
- **↪** Orchestrator pass (**adapt** `ralph-orchestrator`).

> **── SELF-HOSTING BOUNDARY ──** After 3.1 the **build phase** self-hosts: design → slices → dev →
> refactor → QA → merge, orchestrated. The mergeable **tail** — verification (4.1), docs (4.2) and the
> promote it gates (`main` requires `stage:docs`) — does **not** exist yet, so a Phase-4 item can be
> *built* through the pipeline but its verify/docs/promote is still hand-finished until 4.1+4.2 land
> (and verification stays a **human** gate forever — see Risk 4). So 4.1 and 4.2 are the last items
> that must be hand-completed; once they exist, the tail self-hosts too.

---

## Phase 4 — Tail, front door & tracking

### 4.1 Verification — adapt `verify-prd`
- **done-when:** runs feature-level on the worktree of the branch that will promote, against PRD
  success criteria, with a **re-verify cap** (hold with `needs:human` rather than cycling); posts a
  verification report to the tracker, and loops findings back (fixes → re-verify; out-of-scope →
  linked task issues). `stage:verify` holds until clean.
- **needs:** 3.1. **↪** Feature-level verification (**adapt** `verify-prd`).

### 4.2 Docs tail + project lifecycle
- **done-when:** `sync-docs` runs the feature-level `stage:docs` pass (git + report + issue tree);
  `init-docs` gains the deep product/vision grill and emits `MONITORING.md` (mirroring the
  `CONTEXT.md` monorepo hierarchy).
- **needs:** 3.1. **↪** `sync-docs`/`init-docs` (**adapt**); `MONITORING.md` (**new**).

### 4.3 Wayfinding front door
- **done-when:** scope-triages (Task/Feature/Product), builds a `wayfinder:map` for foggy/product
  work, and dispatches decisions to the right grill profile; degrades to a direct grill for clear
  work. Also dispatches by **kind** for items picked up from the inbox (1.1a) — `bug` to `diagnose`,
  `tech-debt` to a scoped refactor, `wishlist` to the feature front-half. **Authors the two
  front-door grill profiles** — **Task** and **Wayfinding-ticket** — on the 0.2 engine (0.2 ships
  only the PRD + Design-Doc profiles; these two are front-door-specific, so they land with wayfinding).
- **needs:** 0.2 (engine + PRD/Design-Doc profiles), 1.1a (kinds). **↪** Wayfinding (**new**); Task +
  Wayfinding-ticket grill profiles (**new** 📄); creates research/POC tickets
  on a map rather than treating them as logged work.

### 4.4 Progress & tracking
- **done-when:** the GitHub Project **provisioned in 1.1** (board by `stage:*` + roadmap for planning)
  is kept in sync by the **orchestrator's** `Status` writes — this item **adds those** (the
  *In development* build-phase transitions) to the 3.1 pass; the pre-build transitions (*Ideas*,
  *Shaping*) are written by `log` (1.1a) and the producers (0.3), not here, and it does not create the
  Project. A `status`/standup skill narrates progress from the
  tracker **and reports the quality counter-metrics alongside throughput** — cost per accepted
  change (flagging acceptance under ~50%), escaped defects (`kind:bug` against verified features),
  and human-rework rate (`needs:human` frequency). `trello` skill + `verify-prd` Trello sync
  **removed**.
- **why the counter-metrics:** a board that only measures movement is a metric worth gaming — a
  pipeline merging slices fast while escaped defects climb looks excellent on it. See
  [PROCESS.md → Grounding](PROCESS.md#grounding--anchors-caps-and-counter-metrics).
- **also ships** the `gh` snippet a deploy job calls to write `Environment` after close — the only
  deployment surface the standard owns.
- **needs:** 3.1 (the orchestrator pass exists). This item **adds** the Project Status write to
  that pass — 3.1 does not depend on the Project. **↪** GitHub Projects view; `status` skill; remove Trello.

---

## Phase 5 — Later upgrades (deferred)

- **Log-fetching skill** — resolves the nearest `MONITORING.md`, pulls logs; closes the feedback loop.
- **Standing orchestrator cron** — the Phase-3 pass on a schedule (near-free once the pass exists).
- **Per-worktree QA runtime isolation** — dynamic ports / DB-per-branch to parallelize QA beyond 1.

---

## Critical path & parallelism

Each edge below is exactly an item's declared **needs:** — the graph *is* the prerequisite list, so it
cannot drift from the items (a hand-drawn arrow diagram did, twice). Schedule by it: an item is
eligible the moment every item to its left is done.

```
Phase 0   0.1 · 0.1a · 0.1b        (all three: no deps)
          0.2   ← 0.1, 0.1a
          0.3   ← 0.2, 0.1b, 1.1     (0.1b = the gate the producers run; 1.1 = the Project whose Status they write)

Phase 1   1.1                       (no deps)
          1.2   ← 1.1
          1.1a  ← 1.1, 0.1a
          1.3   ← 1.1, 0.3, 0.1b     (0.1b = the slicing gate it runs before publishing)
          1.2a  ← 1.1, 1.2, 0.3

Phase 2   2.1   ← 1.2, 1.3
          2.2   ← 2.1
          2.3   ← 1.2a                    (+ Playwright MCP)

Phase 3   3.1   ← all of Phases 1 & 2     ──▶ SELF-HOSTING BOUNDARY
Phase 4+  4.1 ← 3.1 · 4.2 ← 3.1 · 4.4 ← 3.1 · 4.3 ← 0.2, 1.1a · 5.x ← 4.x
          (4.3 has no hard 3.1 dep — it's placed in Phase 4 by sequencing, not prerequisite)
```

- **Serial spine (the longest chain):** `0.1 → 0.2 → 0.3 → {1.2a→2.3 | 1.3→2.1→2.2} → 3.1`. Phase 0's
  design front-half and 3.1 are the two gates everything routes through.
- **Parallelizable:** the `1.1 → 1.2` substrate track runs alongside Phase 0 (it needs no Phase-0
  item until `1.2a`/`1.3` reach for `0.3`); `1.1a` hangs off `1.1`, off the *longest* chain (its one
  distinctive downstream is `4.3`), but still inside Phase 1 — and since 3.1 needs **all** of Phase 1,
  1.1a precedes self-hosting like every other Phase-1 item; `0.1b` (the critique-loop gate) is off the
  design spine but feeds `0.3`, whose producers run it before publishing; `2.3` (QA runner) runs
  alongside `2.1/2.2` because it depends on `1.2a`, not on them.
- **First runnable milestone:** after **0.3** you can produce PRDs + Design Docs by hand with FIC.
- **First AFK milestone:** after **3.1** the system can build its own remaining pieces.

## Risks & focus points

Genuine risks, flagged here so they're not rediscovered mid-build. Read the relevant one *before*
starting its item.

1. **2.1 Dev-loop ralph adaptation — highest risk.** ralph's current control flow is *implement →
   close issue → unlock downstream*. Our dev loop must instead **stop at dev-done, leave the issue
   open, and not touch labels** (the orchestrator owns transitions). This cuts against ralph's core
   end-of-run logic — expect adapt-heavy work, likely a fork of that logic rather than a config
   flag. This is the item most likely to be underestimated by the inventory's "adapt" label.

2. ~~**0.1 Proactive FIC compaction is the hard part.**~~ **RESOLVED in 0.1.** Self-measured context
   usage is unreliable, so `PROTOCOL.md` ranks the triggers by trustworthiness: on-demand
   (primary) → heuristic (`fic checkpoint` nudges every 10 entries) → self-assessed (best-effort
   only, never load-bearing). Safety rests on **checkpoint-as-you-go**, which the script makes a
   one-command habit, plus `fic compact` refusing to run on a stale header.

3. **2.3 Playwright MCP in AFK/headless runs.** Interactively-authenticated MCP servers can be
   *absent* in headless/cron contexts. Confirm the QA runner can authenticate Playwright inside the
   loop environment before committing to the two-agent design; otherwise QA may need to stay
   human-adjacent rather than fully AFK.

4. **The self-hosting boundary is for AFK-buildable items only.** Human-gated items (verification,
   design/prototype approval) can't fully self-host — you remain in the loop for those even after
   Phase 3. "Self-host Phase 4+" means the *mechanical* parts, not the human gates.

## Open build-time details (from PROCESS.md)

- ~~The process-skills **directory/namespace** path.~~ RESOLVED in 0.1a — grouped source
  (`{primitives|flows/<flow>|general}/skills/<name>`), flat install, group = unit of per-account install.
- ~~Whether Phase 4+ items are hand-built or self-hosted.~~ RESOLVED at the boundary (see
  [§0 bootstrapping](#the-bootstrapping-principle) and the SELF-HOSTING BOUNDARY note): after 3.1 the
  **build phase** self-hosts, so Phase 4+ items are *built* through the pipeline, but their
  verify/docs/promote **tail** is hand-finished until 4.1+4.2 exist — after which the tail self-hosts
  too (verification stays a permanent human gate).
