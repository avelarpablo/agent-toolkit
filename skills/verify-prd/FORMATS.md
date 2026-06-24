# Verify PRD — File Formats

Templates for all generated files. The agent reads this file when creating or updating verification artifacts.

---

## Directory Structure

```
VERIFY-{number}/
  INDEX.md                              ← progress stats + chunk list
  prd-level.md                          ← PRD-level test cases
  {child#}-{slug}.md                    ← child issue chunk (e.g., 133-layout-hook.md)
  {child#}-{slug}-done.md              ← completed chunk (renamed)
```

Always a directory, even for small PRDs with few tests. Consistency means the agent never handles two different file layouts.

---

## INDEX.md

```markdown
# VERIFY-{number} — {PRD title}

- **PRD:** https://github.com/shopstackio/discount-genie-core/issues/{number}
- **Trello:** {trello-card-url}          ← omit this line when --no-trello
- **Generated:** {date}
- **Progress:** {n}/N ✅ · {n} ⚠️ · {n} ⏸️ · {n} ❌ · {n} ⬜

| File | Tests | Status |
|------|-------|--------|
| prd-level.md | 01-07 | In progress (5/7) |
| 133-layout-hook.md | 08-14 | ⬜ |
| 134-action-cache-done.md | 15-20 | Done |
| 135-delete-decrement.md | 21-25 | In progress (3/5) |
```

Updated by the agent on every test result confirmation.

---

## Chunk File

```markdown
# {Section title}

- **Source:** PRD #{number} | Issue #{child-number}
- **Tests:** {start}–{end}

| # | Test Case | Method | Status | Finding | Date |
|---|-----------|--------|--------|---------|------|
| 01 | {test description} | [code] | ⬜ | — | — |
| 02 | {test description} | [code, browser] | ✅ | — | 2026-06-11 |
| 03 | {test description} | [unit, browser] | ⏸️ | needs premium shop | — |

## Evidence

### E-{prd#}-{test#} — {test case name}

**Method:** [code]
**Evidence:**
- `app/root.tsx:23-47` — loader returns `{auth, authorization, env, mantleTokens}` only
- `grep -r "shopInfoRes" discount-genie/app/root.tsx` → no matches
**Confirmed by:** human ({date})

### E-{prd#}-{test#} — {test case name}

**Method:** [code, browser]
**Evidence:**
- `app/routes/app.tsx:12` — no `getDiscountGenieClientWithCustomToken` import
- User confirmed: home page loaded clean, no flash, no console errors
- Remix server logs: no errors during load (user-provided)
**Confirmed by:** human ({date})

## Findings

### F-{prd#}-{test#} — {test case name}

**Observation:** What was observed during testing.

**Root cause:** Why it failed (only for ❌).

**Fix:** Link to commit or PR (added after fix is applied).

## Non-Related Findings

_(Only added when testing surfaces bugs outside the PRD's scope.)_

### NF-{sequential} — {short description} ({date})

**Severity:** {Low | Medium | High} — {brief impact}

**Scope:** {which repo/system}, outside PRD #{number} scope

**Reproduction:** Steps to reproduce.

**Root cause:** Why it happens.

**Suggested fix:** Brief recommendation.

**Follow-up:** Link to issue/PRD created for the fix (added when created).

## Design Decisions

_(Only added when verification spawns follow-up design work.)_

### D-{sequential}: {decision title}

{Decision description and rationale.}
```

---

## Status Emojis

| Emoji | Meaning |
|-------|---------|
| ⬜ | Not tested |
| ✅ | Passed |
| ❌ | Failed |
| ⚠️ | Passed with concerns |
| ⏸️ | Deferred (cannot test now, with reason) |
| 🔄 | Superseded (criteria no longer applicable) |

---

## Verification Method Tags

| Tag | Meaning | Agent pre-work |
|-----|---------|----------------|
| `[code]` | Verifiable by reading source code | grep, read files, show file:line references |
| `[unit]` | Relevant unit test exists | find test file, run it, show output |
| `[browser]` | Behavior observable in the running app | describe what to look for, wait for human observation |

- A test can have multiple tags (e.g., `[code, unit, browser]`)
- **Any test describing behavior observable in the running app MUST include `[browser]`**
- Tests describing pure implementation details (e.g., "no import of X remains") are `[code]` only
- Agent can add tags during testing but can never remove `[browser]`

---

## Evidence Blocks

- Every test that reaches ✅, ⚠️, or ❌ gets an evidence block
- Keep evidence compact: 3-5 lines max per test case
- Include: file:line references, grep results, unit test output (truncated), user observations
- `**Confirmed by:** human ({date})` is mandatory on every evidence block
- ⏸️ tests do not get evidence blocks — the reason is in the Finding column

---

## Finding References

**Test-linked findings** (bugs in the PRD's own test cases):
- Table cell contains a link: `[F-131-01](#f-131-01)`
- Finding ID format: `F-{prd-issue-number}-{sequential-test-number}`

**Non-related findings** (pre-existing bugs outside the PRD's scope):
- Finding ID format: `NF-{sequential}` (e.g., `NF-01`, `NF-02`)
- Not referenced in test case tables — they live in their own section
- Do not block `--close`

---

## Test Numbering

Sequential across all chunks. PRD-level tests start at 01. Child issue tests continue the sequence. This ensures finding IDs, evidence IDs, and Trello checklist item numbers align globally.
