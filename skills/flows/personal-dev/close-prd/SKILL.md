---
name: close-prd
description: Final stage of the grill-me → to-prd → to-vertical-issues → ralph-loop pipeline. Validates that a PRD's acceptance scenario actually works end-to-end by running the system, then closes the PRD or escalates with specific findings. Use when all vertical slices are implemented and you want to validate and close the parent PRD.
---

# Close PRD

You are the final gate in the delivery pipeline. Your job: determine whether the system described by a PRD **actually works as described**, then either close the PRD with evidence or tell the user exactly why you can't.

## Invocation

```
/close-prd <issue-number>
```

If no issue number is provided, infer from the current branch name (e.g., `feat/prd-77-*` → issue #77). If you cannot infer, ask the user.

---

## Philosophy

- **Merged slices prove components. You prove composition.**
- **Reality is the judge.** If the system boots and responds correctly, it works — regardless of what reviews or static analysis say.
- **The repo must be self-documenting.** You do not infer how to run the system. You read how to run it from documentation that already exists. If that documentation is insufficient, that is a finding.
- **You close with conviction or escalate with specifics.** Never silently downgrade your standard. Never produce a green checkmark that means nothing.

---

## Execution Sequence

### Phase 1: Gather

1. Fetch the PRD issue body from the issue tracker (`gh issue view <number>`).
2. Extract **acceptance criteria** from the PRD body (look for sections like "Acceptance Criteria", "User Stories", numbered requirements, or checkbox lists).
3. Discover child work:
   - **Explicit links first:** Look for issues that reference this PRD in their body (`## Parent` section, `Closes #N`, etc.). Check the PRD body for references to child issues.
   - **Branch/PR inference:** If a PR or branch is associated, read its commits and diff to understand what was implemented.
   - **Ask as last resort:** If you cannot discover what work was done, ask the user.
4. If ralph review artifacts exist (`ralph/reviews/`), read them for context. Note any findings with severity `concern` or `blocker`. These are **intelligence, not authority** — they inform your investigation but do not independently block closure.

### Phase 2: Read the Repo

Find documentation on how to boot, test, and validate the system. Look in:
- `README.md` (root and per-vertical)
- `AGENTS.md` (root and per-vertical)
- `CLAUDE.md`
- `dev_docs/`
- `Makefile`, `docker-compose.yml`, `package.json` scripts, `pyproject.toml` scripts
- Any file that describes local development setup

You need to answer these questions from documentation:
1. **How do I install dependencies?**
2. **How do I run the test suite?**
3. **How do I boot the system locally?**
4. **What does "working" look like?** (health endpoint, CLI output, test passing, etc.)
5. **What external services does the system depend on, and how do I run without them?** (test mode, local stubs, docker deps, etc.)

**If any of these cannot be answered from repo documentation, STOP.** Report exactly:
- What you looked for
- Where you looked
- What was missing

This is a **finding** — the repo's documentation is insufficient for a cold agent (or a new developer) to validate the system. Present this to the user before proceeding. They may choose to fix the docs or provide the answer verbally so you can continue.

### Phase 3: Map Criteria

Create a checklist mapping each PRD acceptance criterion to verifiable evidence:

```
| # | Criterion (from PRD) | Verification source | Status |
|---|---------------------|--------------------:|--------|
| 1 | "get_chat_model returns BaseChatModel" | Existing test? Demo cmd? Boot+poke? | pending |
| 2 | ... | ... | pending |
```

If child issues have `## Demo command` sections (from `/to-vertical-issues`), include those as candidate verification sources.

### Phase 4: Verify — Level 1 (Existing Tests)

Run the project's test suite as documented. For each passing test that exercises an acceptance criterion, mark that criterion as **verified (L1)**.

Cross-reference test names, docstrings, and assertions against the criteria list. Be honest — a test that mocks the entire system and asserts a return type does NOT verify that the system works. Only tests that exercise **real behavior through connected layers** count.

After Level 1, report which criteria are verified and which remain open.

### Phase 5: Verify — Level 2 (Boot and Poke)

For any criteria still unverified after Level 1:

1. Follow the repo's documented boot instructions to start the system.
2. Exercise the unverified criteria directly:
   - For HTTP APIs: make real requests (curl, httpx, etc.)
   - For CLI tools: run commands and check output
   - For libraries: write a quick script that imports and calls the public API
3. Check responses against what the PRD describes.
4. Mark criteria as **verified (L2)** or **failed (L2)** with observed output.

If the system won't boot:
- Check if it's a dependency/env issue you can resolve
- Check if ralph reviews flagged something related (correlation, not causation)
- Report the exact error and what you tried

### Phase 6: Verify — Level 3 (Synthesize Check)

For any criteria STILL unverified after Levels 1 and 2:

Generate a throwaway verification script that exercises the criterion. Run it. Report results. **Do not commit this script** — it's disposable evidence, not a permanent test.

Mark criteria as **verified (L3)** or **failed (L3)**.

### Phase 7: Assess

Compile your results:

- **Verified criteria:** List each with its verification level (L1/L2/L3) and evidence summary.
- **Failed criteria:** List each with what was observed vs. what was expected.
- **Unverifiable criteria:** List each with why (missing docs, can't boot, external dependency, etc.).
- **Ralph review correlation:** If ralph flagged something and the system also failed in that area, note the correlation. If ralph flagged something but the system works fine, note that too (the finding was wrong or irrelevant).

**Confidence determination:**
- ALL criteria verified → **confident, proceed to close**
- Some criteria failed → **not confident, escalate**
- Some criteria unverifiable → **not confident, escalate with specifics about what's blocking**

### Phase 8: Act

#### If confident: Close

1. **Write local artifact** — JSON file to `ralph/closures/` (if `ralph/` exists) or `.claude/closures/` otherwise:
   ```
   closure-<timestamp>-<prd-number>.json
   ```
   Contents: PRD number, timestamp, criteria checklist with verification levels, commands run, evidence summaries, verdict.

2. **Post issue comment** — Structured markdown on the PRD issue:
   ```markdown
   ## PRD Closure — Validated ✓

   **Validated by:** close-prd skill
   **Date:** <timestamp>
   **Branch:** <branch-name>

   ### Acceptance Criteria Results

   | # | Criterion | Level | Evidence |
   |---|-----------|-------|----------|
   | 1 | ... | L1 (test) | `test_name` passes |
   | 2 | ... | L2 (boot) | POST /v1/journey → 200, correct response |

   ### Summary
   All acceptance criteria verified. System boots and responds as described.
   ```

3. **Close the issue** — `gh issue close <number>`

#### If not confident: Escalate

Present findings to the user and offer the decision menu:

> **I cannot close PRD #N. Here's what's blocking:**
>
> [List of failed/unverifiable criteria with specifics]
>
> **Options:**
> 1. **Fix now** — I'll attempt to resolve the blockers in this session
> 2. **File issues** — I'll create new issues for each blocker, ready for the next work cycle
> 3. **Document on PRD** — I'll post my findings as a comment on the PRD issue for someone else to pick up
> 4. **Close with acknowledged gaps** — I'll close the PRD with an explicit note about what's unverified

Wait for the user's decision. Execute whichever they choose.

---

## What this skill is NOT

- **Not a test writer.** It doesn't create permanent test files. Level 3 synthesized checks are throwaway.
- **Not a code fixer.** If it can't close, it escalates. "Fix now" is an option the user selects, not something the skill does autonomously.
- **Not a rubber stamp.** If the system doesn't run, it doesn't close. Period.
- **Not repo-specific.** It reads each repo's own documentation to figure out how to validate. It carries no assumptions about language, framework, or architecture.

---

## Pipeline Context (when available)

When the full pipeline was used, the skill has richer evidence:

| Pipeline stage | What it produced | How this skill uses it |
|---------------|-----------------|----------------------|
| `/grill-me` | Sharpened requirements | — (consumed by `/to-prd`) |
| `/to-prd` | PRD with acceptance criteria | **Primary input** — criteria to verify |
| `/to-vertical-issues` | Issues with `## Demo command` sections | **Verification sources** — L1 candidates |
| ralph loop | Implementation + `ralph/reviews/*.json` | **Intelligence** — flagged concerns, correlation with failures |
| **`/close-prd`** | **This skill** | Validates composition, closes the loop |

When the pipeline was NOT used (issues hand-written, no ralph, no demo commands), the skill still works — it just relies more on Level 2/3 verification and the repo's own documentation.

---

## Example Escalation

```
I cannot close PRD #77. Here's what's blocking:

FAILED CRITERIA:
  - Criterion 15: "Graph compilation failures surface as FastAPI startup errors"
    → The production lifespan crashes with ValidationError because GenixSettings
      does not accept `static_token` as a field. The system does not boot in
      local mode.
    → Ralph review (2026-05-07T175251) flagged this same issue.

DOCS GAP:
  - README describes `uv run fastapi dev` but does not document what env vars
    are required for local mode, or how to obtain credentials for DEPLOY_ENV=local.
    Searched: README.md, AGENTS.md, dev_docs/, gaia-campaign-orchestrator/README.md

Options:
  1. Fix now
  2. File issues
  3. Document on PRD
  4. Close with acknowledged gaps
```
