# Build Plan — The Development System

The implementation plan for the system designed in [PROCESS.md](PROCESS.md). `PROCESS.md` is the
**spec** (what & how it's designed); this is the **plan** (what to build, in what order, and how to
know each piece is done).

> Status: **0.1 done.** Phase 0 is hand-built; the system starts self-hosting after Phase 3.

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

**Built as:** `skills/fic/` — `fic` (the script: `init`/`checkpoint`/`header`/`resume`/`list`/
`path`/`compact`), `PROTOCOL.md` (the contract skills inherit by reference), `SKILL.md` (the generic
profile). Working files live at `<dotdir>/<slug>/progress.md`, dotdir per skill (`.fic`, `.grill`,
`.verify`, …), auto-gitignored; `init` is idempotent so start and resume are one call.

**Decisions made at build time:**
- **Script + protocol doc**, not prose alone — deterministic writes, uniform format, and
  checkpointing is one command. Skills inherit by referencing `PROTOCOL.md`.
- **Single `progress.md`** per topic (resume header + append-only log), not the multi-file
  `.grill/` layout — a fresh session reads exactly one file. Profiles may add siblings later.
- **Flat `skills/fic/`**, not a nested `process/` namespace — zero discovery risk; revisit once
  several process skills exist. *(Closes the "process-skills directory" open build-time detail.)*
- `fic compact` **refuses to run on an incomplete header** — the protocol enforces its own
  non-lossiness rather than trusting the agent to remember.

### 0.2 Grilling engine + PRD & Design Doc profiles
One engine, parameterized by a profile; checkpoints via 0.1.
- **done-when:** the PRD profile runs a full grill (one question at a time, recommends answers,
  checkpoints each decision) and the Design Doc profile additionally verifies claims against code.
  Both leave a resumable working file.
- **needs:** 0.1.
- **↪** Grilling engine (**replace** `grill-me`/`grill-verified`/`grill-with-docs`); Grill profiles.

### 0.3 `to-prd` + `to-design-doc` producers
Synthesize the grill's working file into published tracker issues.
- **done-when:** `to-prd` publishes a PRD (what/why + **success criteria**, no impl detail);
  `to-design-doc` publishes a Design Doc (how, verified, prototype reference) linked to its PRD.
  Neither interviews — they synthesize the working file.
- **needs:** 0.2.
- **↪** PRD producer (**adapt** `to-prd`); Design Doc producer (**new** `to-design-doc`).

---

## Phase 1 — State-machine substrate (hand-built)

The mechanics that let work flow as issues + labels + branches + worktrees.

### 1.1 Label & branch conventions in `setup-agent-skills`
- **done-when:** running it on a repo provisions the `stage:*` labels and documents the
  `<type>/<issue#>-<slug>` branch convention (incl. `feat/`), mapped to real per-repo strings.
- **needs:** nothing (can parallel Phase 0).
- **↪** Tracker/label/branch vocabulary setup (**adapt** `setup-agent-skills`).

### 1.2 Worktree, label-flip & cleanup scripts
Deterministic mechanism the orchestrator will call.
- **done-when:** scripts can (a) create a worktree on `<type>/<issue#>-<slug>` off a given base and
  tear it down; (b) flip an issue's `stage:` label; (c) state-aware cleanup of `~/.ralph/builds/<branch>/`
  and merged branches, keyed to issue verified/closed. Each runs standalone and idempotently.
- **needs:** 1.1 (conventions).
- **↪** Worktree create/teardown; Label flips; State-aware cleanup (all **new** ⬛).

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

### 2.2 Refactor loop wiring
- **done-when:** an orchestrated chain runs `review-loop` (find) → `ralph` (fix, refactor prompt) →
  re-check until zero blockers, and applies the **best design pattern** for maintainability. `ralph`
  fix-actor reused with a refactor prompt.
- **needs:** 2.1 (ralph as fix actor), `review-loop` (reuse as-is).
- **↪** Refactor loop (**reuse** `review-loop` + `ralph`, chained).

### 2.3 QA runner (new) + `prototype` adapt
- **done-when:** a two-agent QA runner (driver holds Playwright MCP + strategist/critic) drives the
  assembled app, checks against frozen prototype screenshots, and writes an e2e suite. `prototype`
  gains the HITL salvage path (real design system → seeds `design/…`→`feat/…`, freezes screenshots).
- **needs:** Playwright MCP; 0.x for the prototype's design-step wiring.
- **↪** QA loop (**new** 🟧); Prototype (**adapt**).

---

## Phase 3 — Orchestrator (the self-hosting turning point)

### 3.1 Orchestrator pass
- **done-when:** a manual pass reads the board and, respecting the four conflict dimensions +
  concurrency caps (QA=1), advances every legally-advanceable issue: creates/tears down worktrees
  (via 1.2), launches the right loop, flips the `stage:` label **and** sets the Project Status, and
  reports. Idempotent + resumable (re-run picks up from labels).
- **needs:** Phases 1 + 2 complete.
- **↪** Orchestrator pass (**adapt** `ralph-orchestrator`).

> **── SELF-HOSTING BOUNDARY ──** After 3.1 the spine works end-to-end (design → slices → dev →
> refactor → QA → orchestrated). Phase 4+ items MAY now be built *through the pipeline itself*.

---

## Phase 4 — Tail, front door & tracking

### 4.1 Verification — adapt `verify-prd`
- **done-when:** runs feature-level on the `feat/…` worktree against PRD success criteria, posts a
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
  work.
- **needs:** 0.2 (profiles). **↪** Wayfinding (**new**).

### 4.4 Progress & tracking
- **done-when:** a GitHub Project (board by `stage:*` + roadmap for planning) is set up and kept in
  sync by the orchestrator's Status writes; a `status`/standup skill narrates progress from the
  tracker. `trello` skill + `verify-prd` Trello sync **removed**.
- **needs:** 3.1 (orchestrator Status writes). **↪** GitHub Projects view; `status` skill; remove Trello.

---

## Phase 5 — Later upgrades (deferred)

- **Log-fetching skill** — resolves the nearest `MONITORING.md`, pulls logs; closes the feedback loop.
- **Standing orchestrator cron** — the Phase-3 pass on a schedule (near-free once the pass exists).
- **Per-worktree QA runtime isolation** — dynamic ports / DB-per-branch to parallelize QA beyond 1.

---

## Critical path & parallelism

```
0.1 ─▶ 0.2 ─▶ 0.3 ─┐
                   ├─▶ 1.3 ─▶ 2.1 ─▶ 2.2 ─┐
1.1 ─▶ 1.2 ────────┘                2.3 ─┤─▶ 3.1 ─▶ (self-host) ─▶ 4.x ─▶ 5.x
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

- ~~The process-skills **directory/namespace** path.~~ RESOLVED in 0.1 — flat in `skills/`.
- Whether Phase 4+ items are hand-built or self-hosted (decide at the boundary).
