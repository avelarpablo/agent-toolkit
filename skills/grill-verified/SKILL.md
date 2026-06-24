---
description: Scientifically rigorous grilling session where the machine verifies every technical assumption before presenting human-facing questions. Dead options are killed by evidence, not by asking the human to investigate. The human only answers direction questions (priority, scope, values, policy). Use when user says "grill verified", "verified grill", "technical grill", "verify-first grill", "scientific grill", or wants a design session where claims are evidence-backed before decisions are made.
---

# /grill-verified — Evidence-first design grilling

You are running a scientifically rigorous design session. The structural
difference from a normal grill: you do NOT ask the human technical questions
whose answers can be determined by investigation. You verify claims yourself,
kill dead options before they reach the human, and present only genuine human
decisions — pre-loaded with evidence.

**The human answers:** direction, priority, scope, values, policy.
**The machine answers:** "does this work?", "is this possible?", "what does
the code actually do?", "what does the library support?"

## The scientific method, applied

For every question you formulate during the session:

1. **Hypothesis** — your recommended answer, written as a falsifiable claim
2. **Assumptions** — what must be true for this recommendation to hold
3. **Experiments** — one verification per assumption (adapted to available tools)
4. **Observations** — run experiments, record results
5. **Conclusion** — confirmed, falsified, or inconclusive. Kill or present.

This is the invariant. Every question passes through it. No exceptions.

## Workspace

Session artifacts live in `.grill/<timestamp>-<slug>/`:

```
.grill/<timestamp>-<slug>/
  session.md          — running log (questions, decisions, outcomes)
  assumptions/        — per-question breakdowns (Q-001.md, Q-002.md, ...)
  evidence/           — verification results (grep, MCP, test output)
  spikes/             — POC test files (runnable, ephemeral instruments)
  decisions.md        — crystallized decisions with full evidence trail
```

Create the session directory on invocation. Format: `YYYYMMDDTHHMMSS-<slug>`
(slug from topic, max 40 chars, lowercase, hyphens).

If `.grill/` is not already in `.gitignore`, add it. These are lab notes, not
maintained artifacts.

## Phase 0: Reconnaissance

On invocation, before asking the human anything:

1. **Read context** — whatever the user provides (docs, PRDs, issues,
   conversation history, prior `.grill/` sessions).

2. **Explore the codebase** — current state relevant to the topic. Use Explore
   agents for parallelism when the search space is wide.

3. **Discover available verification infrastructure:**
   - MCP servers: check `ListMcpResourcesTool` — note which knowledge sources
     are available (docs MCPs, API specs, etc.)
   - Test runner: detect from project files (pyproject.toml → pytest,
     package.json → jest/vitest, Cargo.toml → cargo test, etc.)
   - Search/research tools: look for research scripts, web search helpers,
     or other discovery tools available in the project
   - Documentation: existing deep-dive sessions, architecture docs, ADRs
   - If the topic would benefit from an MCP that isn't connected, tell the
     human: "This would be stronger with a [X] MCP — want to connect one?"

4. **Anchor the current reality** — measure what actually exists for THIS
   topic before mapping decisions. Dimensions to ground-truth (adapt to domain):
   - How many instances/components/consumers exist TODAY?
   - What's the actual scale? (not aspirational — measured)
   - What quality/compliance gates are enforced? (CI checks, scanning
     thresholds, type safety rules — whatever the project enforces)
   - What's the integration topology? (what calls what, what depends on what)

   This kills premature complexity: if a scenario the human worries about
   does not exist today, the skill never presents it as a live question.

5. **Map the decision space** — what axes does this topic split on? For each:
   - **TECHNICALLY DETERMINED** — one viable answer, provable by investigation
   - **HUMAN DECISION** — requires human judgment (priority, scope, taste)
   - **AMBIGUOUS** — needs verification before classification

6. **Write reconnaissance summary** to `session.md` and present to the human:
   - Topic and scope
   - Current reality snapshot (from step 4)
   - Axes identified with classifications
   - Available verification infrastructure
   - Proposed question order (dependency-aware)

   Then ask THREE framing questions before proceeding:

   **a) Governing principle (multi-axis):**
   Ask these as separate sub-questions — they are NOT the same axis:
   - "Is there anything this system must ALWAYS do, regardless of config?
     (The non-negotiable floor — what can never be disabled or skipped?)"
   - "For things that CAN vary, what's the default posture?
     (Open/permissive vs restricted/locked-down?)"
   - "How strong should enforcement be?
     (Convention/recommendation vs static-analysis-gated vs runtime-enforced
     vs absolute-ban?)"

   These distinguish BEHAVIORAL GUARANTEES from POLICY DEFAULTS from
   ENFORCEMENT STRENGTH. Collapsing them into one question produces
   answers that only cover one dimension.

   **b) Scope anchor:** "Are we designing for current state or anticipated
   growth? Should I optimize for what's in front of us today, or for what
   you expect in 6-12 months?"

   **c) Decision space check:** "Does this capture the decision space? Any
   axes I'm missing?"

   Wait for answers before proceeding. The governing principle shapes EVERY
   downstream question — it determines where the skill recommends strict vs
   flexible, mandatory vs optional, complex vs simple.

7. **Threat-model scan** — AFTER the governing principle is stated:
   - "The human said [X] must always happen. What mechanisms — in libraries,
     runtime behavior, concurrency, configuration, or system interactions —
     could SILENTLY VIOLATE this guarantee?"
   - Search the relevant layer for each threat class:
     - Library/SDK features: suppression flags, disable patterns, permissive
       defaults, silent fallbacks
     - Distributed/concurrent: race conditions, partition behavior, state
       inconsistency, message loss
     - Integration boundaries: what happens when a dependency is unavailable,
       slow, or returns unexpected data
     - Developer patterns: bypass routes, opt-out conventions, undocumented
       overrides
   - Each found mechanism becomes either:
     - A HUMAN DECISION: "Should [mechanism] be banned, gated, or allowed?"
     - A TECHNICALLY DETERMINED risk: "This breaks the guarantee;
       must be validated/prevented"
   - This scan catches threats that are NOT accidental misconfigurations
     but INTENTIONAL features or emergent behaviors that undermine the
     governing principle

8. **Mandatory spike identification** — identify which questions REQUIRE
   empirical evidence before they can be presented as choices:
   - "Can feature A and feature B be used together?" → needs a spike
   - "Does this mechanism cover all cases (all input types, all consumer
     classes, all relevant execution paths)?" → needs a spike
   - "Does this edge case actually occur in our stack?" → needs a spike

   These spikes run in Phase 1 BEFORE the related question is presented.
   Spike results KILL options — without them, the skill presents theoretical
   choices the human must evaluate mentally. With spikes, dead options are
   already dead when the question arrives.

## Phase 1: Per-question verification loop

Process questions in dependency order (resolve blockers first).

### Step 1 — Hypothesis (scratchpad)

Write `assumptions/Q-NNN.md`:

```markdown
# Q-NNN: <question text>

## Classification: TECHNICAL / HUMAN / AMBIGUOUS

## Hypothesis
<your recommended answer — stated as a falsifiable claim>

## Load-bearing assumptions
- A1: <assumption> — method: <verification approach>
- A2: <assumption> — method: <verification approach>
- A3: <assumption> — method: <verification approach>

## If all confirmed: <recommendation>
## If A2 is false, reframe to: <alternative framing>
```

### Step 1.5 — Premise verification (before designing experiments)

Before investing in experiments, verify the PREMISE of the question against
current reality. Ask: "Is the scenario this question addresses actually real?"

Examples of premise-killing:
- "Should we handle burst scenarios differently?" → Check: does traffic
  actually burst, or is it steady-state? If steady, the question is moot.
  Kill it.
- "How should rollback from state X work?" → Check: is state X actually
  reachable? Trace the paths. If unreachable, the question is premature.
  Kill it.
- "Do we need exactly-once delivery?" → Check: is the downstream consumer
  actually non-idempotent? If idempotent, at-least-once suffices. Kill it.
- "Which dependency split minimizes bundle/image size?" → Check: what's the
  actual size difference? If negligible, the question doesn't matter. Kill it.

If the premise is false:
- Record: "Q-NNN: KILLED (premise false). [one-sentence evidence]."
- Report to human: "Resolved: [question] is moot because [evidence]."
- Move to next question.

If the premise is unverifiable, proceed to experiments — but note the
uncertainty so the human knows the question may be premature.

### Step 2 — Design experiments

Choose verification method per assumption, adapted to what is available:

**Code investigation** (always available):
- grep/find for symbols, patterns, implementations
- Read files at specific line numbers
- Trace call paths and dependency chains
- Check dependency lockfiles for transitive deps
- For dependency/technology decisions: assess the full adoption cost —
  - Transitive weight: inspect the dependency tree (language-appropriate
    tool: uv tree, npm ls --all, cargo tree, etc.)
  - Security/maintenance surface: cross-reference against project scanning
    thresholds and advisory burden
  - Operational complexity: what infrastructure, monitoring, or expertise
    does adoption require?
  - Performance characteristics: benchmark under realistic conditions if
    performance is load-bearing
  Evaluate: "What is the total cost of adopting this beyond the direct
  code benefit?"
- For any component with failure modes: check what happens on
  MISCONFIGURATION or UNAVAILABILITY. What does the system do when a
  required value is missing, a dependency is down, or input is unexpected?
  Silent fallback? Error? Degraded mode? If the answer is "silent failure
  that breaks the governing principle," that's a finding that shapes the
  design.

**MCP queries** (if relevant MCPs are connected):
- Search documentation, OpenAPI specs, reference material
- Cross-reference library capabilities against claims

**External research** (if web search or research tools available):
- Library changelogs, release notes, API documentation
- GitHub issues for known limitations
- Spec documents (protocol specs, API contracts, formal models, RFCs,
  vendor documentation)

**Empirical spikes** (if a test runner is available):
- Write a minimal test that exercises the assumption
- Run it and observe actual behavior
- The test IS the evidence — not a doc quote

**Research/deep-dive delegation** (if the project has a research or
  deep-dive skill available):
- For complex claims needing iterative convergence
- Results land in `evidence/` subfolder

**Graceful fallback** (always):
- If you cannot verify an assumption, say so explicitly
- State what tool/access you would need
- Present the uncertainty to the human: "I believe X but can't prove it
  because I lack Y — want to find a way to verify, or proceed with
  the uncertainty noted?"

### Step 3 — Run experiments

- Simple checks (grep, MCP, file reads): fire in parallel within a single turn
- Empirical spikes (file creation + execution + analysis): use the Workflow
  tool to fan out spike creation and execution
- Record all results in `evidence/Q-NNN-A1.md`, `evidence/Q-NNN-A2.md`, etc.

### Step 4 — Observe and classify

For each assumption:
- **CONFIRMED** — evidence supports the claim. Record the citation
  (file:line, test output, API response, doc excerpt).
- **FALSIFIED** — evidence contradicts the claim. The option resting on it
  is dead. Record WHY (specific evidence that kills it).
- **INCONCLUSIVE** — couldn't determine. Escalate options:
  (1) write a spike, (2) ask the human to point to documentation,
  (3) proceed with uncertainty explicitly noted.

Update `assumptions/Q-NNN.md` with verdicts.

### Step 5 — Conclude and present

**TECHNICALLY DETERMINED** (all assumptions resolved, single viable path):
- Record the answer in `session.md` with evidence citations.
- Tell the human: "Resolved: [question] → [answer] because [one-sentence
  evidence]. Details in `assumptions/Q-NNN.md`."
- Move to next question. Do not ask for confirmation on facts.

**DEAD OPTIONS KILLED** (some paths eliminated by evidence):
- Report what was killed and why (one line per killed option with evidence).
- Present surviving options with their evidence stack.

**GENUINE HUMAN DECISION** (verified facts, multiple viable paths remain):
- Present pre-loaded: "X works because [evidence]. Y is dead because
  [evidence]. The remaining choice: A vs B.
  A means [tradeoff]. B means [tradeoff].
  Which direction?"
- **Apply the governing principle**: if the human stated one in Phase 0,
  note which option aligns with it. "Given your stated principle [X],
  option A is the natural fit — but option B is viable if [reason]."
  This makes the recommendation explicit without deciding for the human.
- Wait for the human's answer. Record in `session.md`.

**AMBIGUOUS AND UNRESOLVABLE:**
- Tell the human what you couldn't determine and why.
- Offer options: more investigation, accept uncertainty, or different framing.
- Wait for guidance.

### Loop invariant

After each question resolves, re-evaluate downstream questions:
- If a HUMAN question became TECHNICALLY DETERMINED (because an earlier answer
  eliminated alternatives), reclassify and resolve without asking.
- If new questions emerged from evidence, add them to the queue.

## Phase 2: Synthesis

After all questions are resolved, write `decisions.md`:

```markdown
# Decisions — <topic>

## Summary
<2-3 sentence executive summary>

## Decisions

### D-001: <title>
**Choice:** <what was chosen>
**Evidence:** <citation>
**Killed alternatives:**
- <option> — dead because <evidence>
**Human rationale:** <what the human said, if applicable>

## Confirmed technical facts
<Bullet list of verified facts from the session>

## Open threads
<Anything uncertain or deferred, with what would resolve it>

## Recommended next steps
- [ ] <specific action>
```

Present to the human. Ask if any decisions should be formalized further
(ADRs, PRDs, implementation issues).

## Spike test format

When writing spikes to `.grill/<session>/spikes/`:

1. **Detect the project's language and test runner** from project files
   (e.g., pyproject.toml → pytest, package.json → jest/vitest,
   Cargo.toml → cargo test, go.mod → go test, build.gradle → JUnit).
2. **Write the spike in the project's language** using its test framework.
3. **Follow this structure** (adapt syntax to language):

```
Spike Q-NNN: <question being answered>

Assumption under test: <specific assumption from Q-NNN>

VERDICT: <CONFIRMED|FALSIFIED|INCONCLUSIVE> — <one-line result>
```

Name spikes `spike_q_nnn_<slug>` with the appropriate file extension.

Spikes are instruments, not implementations. Keep them minimal. They exist
to produce one observation. If the project has existing spike test examples,
follow that pattern.

To run: invoke the project's test runner appropriately. If the spike needs
project dependencies, run it from within the project's environment.

## What this skill must NOT do

- **Ask technical questions you can investigate.** The fundamental rule. If grep,
  a test, an MCP query, or reading the source can answer it — you answer it.
- **Present unverified claims as evidence.** Every "X works" must cite evidence.
  "I believe X" is not a finding — it's a hypothesis that needs an experiment.
- **Present dead options.** If evidence killed an option, report the kill. Do not
  present it as a choice "for completeness" or "in case you want to reconsider."
- **Present questions whose premise is false.** If the scenario a question
  addresses doesn't exist today (zero affected components, no actual
  variation in behavior, no evidence the problem is real), kill the
  question. Don't ask the human to choose between solutions to a problem
  that doesn't exist.
- **Skip reconnaissance.** Even if the topic seems simple, map the decision space.
  You will discover axes the user hasn't thought of.
- **Skip the governing principle question.** The human's stated principle is the
  load-bearing input that shapes every downstream recommendation. Without it,
  you will default to "flexibility" when the human may want "strictness," or
  present complex options when simple ones satisfy the actual requirement.
- **Skip the threat-model scan.** After the human states their governing
  principle, you MUST scan the relevant system layer for mechanisms that
  could silently UNDERMINE that principle. Look for: library suppression
  features, race conditions, silent fallbacks, configuration overrides,
  permissive defaults, and bypass routes. These may be intentional features
  a developer might use deliberately, or emergent behaviors in distributed
  systems. Each one is either a ban candidate or a validation requirement.
- **Present design options without running spikes.** If the choice between two
  approaches depends on an EMPIRICAL fact (does X work with Y? does Z cover all
  cases?), run a spike FIRST. Present options only after dead ones are killed by
  evidence. Without spikes, you present theoretical choices that force the human
  to evaluate technical feasibility mentally — that's the machine's job.
- **Recommend AGAINST the governing principle.** If the human stated a principle
  (e.g., "this must always happen"), your recommendations MUST align with it.
  If evidence suggests the principle has a cost, present the cost explicitly —
  but do not recommend the weaker option. The human chose strict for a reason.
- **Over-engineer beyond stated scope.** If the human said "design for today,"
  do not present future-proofing options as equally viable. Present what the
  evidence shows is needed NOW, with deferred options noted as "banked for later."
- **Batch questions.** One human-decision at a time. The answer to Q-002 may
  make Q-003 irrelevant.
- **Run forever.** If a question spawns more than 5 branching assumptions, STOP.
  Ask the human: "This is getting deep — should I spin off a focused deep-dive
  on this sub-question?"
- **Modify production code.** Write only to `.grill/<session>/`. Spikes exercise
  existing code but do not change it.
- **Be overconfident.** When evidence is thin, say so. "Medium confidence —
  based on docs only, not empirical verification" is better than "confirmed."
- **Ignore available tools.** If an MCP is connected that could answer the
  question, use it. If there's a research or deep-dive skill available in the project, delegate.
  Don't do shallow investigation when deeper tools exist.

## Resuming a session

If invoked without a topic but a `.grill/` session exists:
1. Read `session.md` from the latest session.
2. Find the last resolved question.
3. Continue from the next unresolved question.
4. If all questions are resolved, go directly to Phase 2 (Synthesis).

## When human overrides a technical determination

If the human says "I know that's what the code says, but I want to change it"
— that's a valid human decision. Record it as:
- **Choice:** <what the human chose>
- **Technical reality:** <what the evidence showed>
- **Implication:** <what implementation cost or risk this introduces>

The skill serves the human's goals, not the status quo. But it makes the cost
of diverging from technical reality explicit.
