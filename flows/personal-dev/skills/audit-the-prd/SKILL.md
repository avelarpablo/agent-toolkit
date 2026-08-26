---
name: audit-the-prd
description: Zero-trust audit of a PRD. Grills the user one question at a time to surface every gap, missing UX detail, and logical contradiction, then compiles findings into a Requirements Gap Document to send back to the PO.
---

# /audit-the-prd - zero-trust PRD audit

Product Requirements Documents arrive with confidence but without
completeness. This skill treats the PRD as an unverified claim and
interrogates it against the live codebase, established domain language,
and UX common sense until every gap is named.

The output is a professional **Requirements Gap Document** — a list of
blockers the user can hand directly to the PO without further editing.

## Operating principle: Zero Trust

If the PRD does not **explicitly state** a detail, this skill treats it
as unknown. "Reasonable inference" is not acceptable evidence. Specific
categories that must be explicitly addressed or flagged:

- Button/element placement and visual hierarchy
- Error states (validation, network, auth, conflict)
- Loading states and optimistic UI
- Empty states and zero-data scenarios
- Data persistence (where, how long, who owns deletion)
- Edge cases (concurrent edits, partial failures, retries)
- Accessibility requirements (ARIA, keyboard nav, screen readers)
- Auth/permission boundaries (who can see/do this?)
- Mobile/responsive behavior (if applicable)
- Copy/microcopy for every user-facing string
- Success confirmation and next-step navigation
- Undo/reversibility of destructive actions

If a category is irrelevant to the feature, the PRD should say so
explicitly. Silence is a gap.

## Inputs

The user provides the PRD in one of these forms:

1. Pasted text in the conversation
2. A file path (local markdown, PDF, etc.)
3. A URL to an issue tracker (GitHub issue, Linear, Jira — fetched via
   appropriate tool)

If the user did not provide a PRD, ask for one before doing anything
else. Do not invent requirements.

## What you do, in order

### 1. Ingest and parse the PRD

Read the full PRD. Identify its stated scope: which system, which
user-facing surface, which API boundary. State the scope back to the
user in one sentence for confirmation before proceeding.

### 2. Explore the codebase for context

Before asking any questions, ground yourself in the project's reality.
Explore the repository structure to understand what already exists:

- Find the relevant source files, modules, and directories that the
  PRD's feature would touch.
- Read existing route handlers, models, schemas, or UI components in
  that area.
- Check for project documentation (README, CONTRIBUTING, architecture
  docs, ADRs) that establishes domain vocabulary or conventions.

You need this context to detect when the PRD contradicts existing
behavior, duplicates something that already exists, or invents concepts
that already have established names in this codebase.

State in 1-2 sentences what you found that is relevant to the PRD's
scope.

If there is no codebase (greenfield project or the PRD is for a system
that doesn't exist yet), skip this step and note that the audit is
purely document-based with no implementation to cross-reference.

### 3. Interrogate — one question at a time

Work through the PRD section by section. For each section, ask **one
question** that targets the most critical gap you've identified. Wait
for the user's answer before asking the next question.

Questioning priorities (in order):

1. **Logical contradictions** — where the PRD says two incompatible
   things, or contradicts existing system behavior.
2. **Missing state transitions** — what happens between the happy-path
   steps? What triggers failure? What does recovery look like?
3. **Unspecified UX details** — placement, copy, responsive behavior,
   empty/loading/error states.
4. **Data lifecycle gaps** — who creates it, who reads it, who deletes
   it, when does it expire?
5. **Auth and permission boundaries** — who can see this? Who can't?
   What happens when an unauthorized user tries?
6. **Integration assumptions** — does the PRD assume an API, service,
   or data source exists that doesn't?

For each question:

- Name the PRD section or sentence you're challenging.
- State what is missing or contradictory.
- If relevant, cite what the codebase currently does (with file path
  and line number).
- Ask one specific, closed-ended question the PO must answer.

Do **not** batch questions. Do **not** move to the next gap until the
current one is resolved or the user explicitly says "I don't know."

### 4. Track responses

Maintain a running internal tally of three categories:

- **Resolved** — the user provided a clear answer that closes the gap.
- **Unknown** — the user said "I don't know" or "that's a question for
  the PO." These become blockers.
- **Contradicted** — the user's answer contradicts something else in the
  PRD or the codebase. Flag immediately and resolve before continuing.

When a response creates a new question (cascading gaps), pursue it
immediately before returning to the original sequence.

### 5. Confirm exhaustion

When you have no more questions, tell the user: "I've exhausted my
questions for this PRD. Ready to compile the gap document?" Wait for
confirmation.

If the user wants to stop early, proceed to artifact generation with
whatever gaps have been identified so far.

### 6. Artifact generation — Requirements Gap Document

Compile all findings into a structured document with this format:

```markdown
# Requirements Gap Document

**PRD:** [title or identifier from the original]
**Audited:** [today's date]
**Scope:** [one-line scope statement from step 1]

## Blockers (must be resolved before implementation)

| # | PRD Section | Gap | Why it blocks | Suggested question for PO |
|---|-------------|-----|---------------|---------------------------|
| 1 | ...         | ... | ...           | ...                       |

## Contradictions found

| # | Statement A (PRD location) | Statement B (PRD or codebase location) | Nature of conflict |
|---|---------------------------|---------------------------------------|-------------------|
| 1 | ...                       | ...                                   | ...               |

## Resolved during audit

| # | Original gap | Resolution | Resolved by |
|---|-------------|-----------|-------------|
| 1 | ...         | ...       | ...         |

## Assumptions the PRD makes about existing system

| # | Assumption | Verified against codebase? | Notes |
|---|-----------|---------------------------|-------|
| 1 | ...       | Yes / No / Partially      | ...   |

---

**Recommendation:** [Ship as-is / Resolve blockers first / Rewrite required]

Total gaps identified: X
Blockers: Y
Resolved in session: Z
```

Output the document in the conversation. If the user wants to persist
it, ask where they'd like it saved — do not assume a directory
structure.

## What this skill must not do

- Do not accept "it's obvious" or "standard practice" as answers to
  gaps. If it's obvious, the PRD should state it. Push back once; if
  the user insists, mark it as Resolved with a note.
- Do not suggest solutions or implementations. This skill identifies
  gaps; it does not fill them. The PO fills them.
- Do not batch questions. One question, one answer, then the next.
  This prevents the user from giving shallow bulk answers.
- Do not skip codebase exploration (when a codebase exists). A gap
  document that ignores what already exists is useless.
- Do not edit the PRD itself. The output is a separate gap document,
  not a "fixed" version of the PRD.
- Do not invent requirements. Every gap must point to something the
  PRD claims or omits — never to something the auditor wishes the
  feature did.

## When to invoke

- A PO or PM has handed off a PRD and the user wants to validate it
  before committing engineering effort.
- The user suspects a PRD is incomplete or contradictory and wants a
  structured way to enumerate the problems.
- Before breaking a PRD into implementation tickets, to ensure the
  source material is solid.
- The user says "audit this PRD", "grill this spec", "find the gaps",
  or "what's missing from this PRD."
