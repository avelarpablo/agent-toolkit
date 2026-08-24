# Build Plan — The Development System

The implementation plan for the system designed in [PROCESS.md](PROCESS.md). `PROCESS.md` is the
**spec** (what & how it's designed); this is the **plan** (what to build, in what order, and how to
know each piece is done).

> Status: **0.1, 0.1a, 0.1b done**; work-kind model (1.1a), branch standard and stage gates decided. Phase 0 is hand-built; the system starts self-hosting after Phase 3.

## The bootstrapping principle

**You cannot use this pipeline to build this pipeline** — the pipeline is what you're building. So:

- **Phases 0–3 are hand-built** — interactively (with you + an agent), using the *existing* tools
  (today's `ralph`, `grill-*`, etc.). They can't flow through the not-yet-built pipeline.
- **The self-hosting boundary is after Phase 3.** Once the design producers (0), substrate (1),
  loops (2), and orchestrator (3) exist, the system has a working spine — and the remaining items
  (Phase 4+) can be built *through the pipeline itself* (dogfooding), if you choose.
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

**Built as:** `skills/primitives/fic/` — `fic` (the script: `init`/`checkpoint`/`header`/`resume`/
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

**Built as:** `skills/<group>/<name>/` with three groups — `primitives/` (11), `flows/personal-dev/`
(13), `general/` (7); `accounts.json` mapping each account to its groups; `toolkit sync
[--account <name>]` installing per account into `<config-dir>/skills`. Classification test, group
table and rationale: [PROCESS.md → Organization](PROCESS.md#build-inventory-draft).

**Decisions made at build time:**
- **Grouped source, flat install** — supersedes 0.1's "flat `skills/fic/`". `toolkit` maps
  `skills/<group>/<name>` → `<config-dir>/skills/<name>`, so the group is purely an install-time
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
- **↪** Grilling engine (**replace** `grill-me`/`grill-verified`/`grill-with-docs`); Grill profiles.
- **layering (from 0.1a):** the engine ships as `skills/primitives/grill/` — it must name no stage,
  label or artifact type — and the PRD/Design-Doc profiles as `skills/flows/personal-dev/`. Build
  them apart from the start; the engine has to be usable under a flow that isn't this one.

### 0.3 `to-prd` + `to-design-doc` producers
Synthesize the grill's working file into published tracker issues. **Both producers gate before
publishing** (principle 11): `to-prd` against PRD criteria (1–2 rounds), `to-design-doc` against
Design-Doc criteria (3 rounds). Authoring those two criteria docs is part of this item.
- **done-when:** `to-prd` publishes a PRD (what/why + **success criteria**, no impl detail);
  `to-design-doc` publishes a Design Doc (how, verified, prototype reference) linked to its PRD.
  Neither interviews — they synthesize the working file.
- **needs:** 0.2.
- **↪** PRD producer (**adapt** `to-prd`); Design Doc producer (**new** `to-design-doc`).

---

## Phase 1 — State-machine substrate (hand-built)

The mechanics that let work flow as issues + labels + branches + worktrees.

### 1.1 Label & branch conventions in `setup-agent-skills`
- **done-when:** running it on a repo provisions the `stage:*` labels (including `stage:design`), `kind:*` and `triage:*` plus
  the `needs:human` modifier, and documents the `<type>/<issue#>-<slug>` branch convention (incl.
  `feat/`), mapped to real per-repo strings.
- **needs:** nothing (can parallel Phase 0).
- **also provisions the GitHub Project** — **org-level, spanning every repo of the product** (PRDs in
  the umbrella repo, slices in the code repos), with the four audience views (roadmap / backlog /
  board / inbox) plus the `Environment` single-select (default Staging + Production) — and
  **mirrors `kind:` onto native issue types where the owner is an org** — verified
  2026-08: types are org-only (`OutputLabs` exposes Task/Bug/Feature; a personal-account repo returns
  `issueTypes: null`), so labels stay canonical and the type is a projection.
- **branch conventions follow [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)**,
  with `main` accepting only what passed `stage:verify` — prefixes are descriptive, not permissions.
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
- **done-when:** `log` writes `kind:*` and no `stage:` label; picking an item up runs the analysis
  its kind calls for — `bug` → `diagnose`, `tech-debt` → scoped refactor — and lands at `stage:ready`
  with a plan. The triage **engine** moves to `primitives/` with the state vocabulary as a flow
  profile.
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
  `stage:verify` is. On approval it freezes screenshots onto the feature issue, seeds the target
  branch via 1.2(d), deletes `design/…`, and moves the feature to `stage:ready`.
- **needs:** 1.1 (`stage:design` label), 1.2 (worktree + seed scripts), 0.3 (a PRD to design against).
- **feeds:** 1.3 (slices inherit the prototype through `feat/…`), 2.3 (QA's visual acceptance
  reference).
- **↪** Prototype (**adapt** — the HITL salvage path). Salvage is the default for UI-meaningful
  features; throwaway keeps screenshots only.
- **optional by design:** non-UI features skip the stage entirely.

### 1.3 Slice + implementation-plan producer
- **done-when:** `to-vertical-issues` emits slice issues aligned to the `feat/`+`slice/` model with
  `stage:ready`, each carrying a checkbox implementation plan, blocked-by graph, and demo command.
  `to-issues` kept separate.
- **needs:** 1.1, 0.3 (consumes a Design Doc).
- **↪** Slice + implementation-plan producer (**adapt** `to-vertical-issues`).

---

## Phase 2 — Build loops (hand-built)

### 2.1 Dev loop — adapt `ralph`  ⚠ highest-risk item — see [Risks](#risks--focus-points)
- **done-when:** ralph runs in a *handed* worktree (self-branching disabled), implements a slice's
  checkbox plan with unit/integ TDD + the inline Codex correctness gate, **stops at dev-done without
  closing the issue or touching labels**, and signals completion. Impl-only prompt.
- **needs:** 1.2 (worktree), 1.3 (a slice to consume).
- **↪** Dev loop (**adapt** `ralph`).
- **the drift is textual, and now located:** `runners/ralph/prompt.md:34` enforces `feature/*` — the
  convention [PROCESS.md](PROCESS.md#branch-naming) explicitly supersedes — and `:78` says "commit
  and close the issue immediately", which is exactly what this item forbids. Both lines are the
  adapt work, not a vague risk.

### 2.2 Refactor loop wiring
- **done-when:** an orchestrated chain runs `review-loop` (find) → `ralph` (fix, refactor prompt) →
  re-check until `review-loop` returns **zero blockers, or a round cap is hit** — at which point it
  stops, flips `needs:human`, and reports what it could not fix (principle 12: every cycle has two
  exits). Maintainability/pattern quality is gated
  the only way it can be tested — by encoding pattern violations as blockers in the `review-loop`
  criteria file, not by an unfalsifiable "applies the best design pattern" clause. `ralph` fix-actor
  reused with a refactor prompt.
- **needs:** 2.1 (ralph as fix actor), `review-loop` (reuse as-is).
- **↪** Refactor loop (**reuse** `review-loop` + `ralph`, chained).

### 2.3 QA runner (new) + `prototype` adapt
- **done-when:** a two-agent QA runner (driver holds Playwright MCP + strategist/critic) drives the
  assembled app, checks against frozen prototype screenshots, and writes an e2e suite. `prototype`
  gains the HITL salvage path (real design system → seeds `design/…`→`feat/…`, freezes screenshots).
- **needs:** Playwright MCP; **1.2a** (the design step — QA's visual acceptance reference comes from
  its frozen screenshots).
- **↪** QA loop (**new** 🟧); Prototype (**adapt**).

---

## Phase 3 — Orchestrator (the self-hosting turning point)

### 3.1 Orchestrator pass
- **done-when:** a manual pass reads the board and, respecting the four conflict dimensions +
  concurrency caps (QA=1) and skipping anything flagged `needs:human`, advances every
  legally-advanceable issue: creates/tears down worktrees
  (via 1.2), launches the right loop — **including `stage:design`, which it dispatches AFK and then
  holds with `needs:human` for your pick** — flips the `stage:` label, and reports. Idempotent + resumable
  (re-run picks up from labels).
- **Project Status writes are *not* part of this acceptance check** — the Project does not exist
  until 4.4. 4.4 adds the Status write to the pass it already owns. (Requiring it here made 3.1 and
  4.4 mutually blocking.)
- **needs:** Phases 1 + 2 complete.
- **↪** Orchestrator pass (**adapt** `ralph-orchestrator`).

> **── SELF-HOSTING BOUNDARY ──** After 3.1 the spine works end-to-end (design → slices → dev →
> refactor → QA → orchestrated). Phase 4+ items MAY now be built *through the pipeline itself*.

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
  `tech-debt` to a scoped refactor, `wishlist` to the feature front-half.
- **needs:** 0.2 (profiles), 1.1a (kinds). **↪** Wayfinding (**new**); creates research/POC tickets
  on a map rather than treating them as logged work.

### 4.4 Progress & tracking
- **done-when:** a GitHub Project (board by `stage:*` + roadmap for planning) is set up and kept in
  sync by the orchestrator's Status writes; a `status`/standup skill narrates progress from the
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

```
0.1 ─▶ 0.1a ─▶ 0.1b ─▶ 0.2 ─▶ 0.3 ─┬─▶ 1.2a ─┐
                                   ├─▶ 1.3 ──┴▶ 2.1 ─▶ 2.2 ─┐
1.1 ─▶ 1.2 ─▶ 1.1a ────────────────┘              2.3 ─┤─▶ 3.1 ─▶ (self-host) ─▶ 4.x ─▶ 5.x
```

- **Serial spine:** 0.1 → 0.2 → 0.3 gate everything design-related; 3.1 gates self-hosting.
- **Parallelizable:** the `1.1/1.2` substrate track runs alongside Phase 0; `2.3` (QA + prototype)
  runs alongside `2.1/2.2`.
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
  (`skills/primitives|flows/<flow>|general/`), flat install, group = unit of per-account install.
- Whether Phase 4+ items are hand-built or self-hosted (decide at the boundary).
