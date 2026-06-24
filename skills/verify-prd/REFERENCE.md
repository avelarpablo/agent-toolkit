# Verify PRD — Reference

Workflow logic for each command. For file templates and format conventions, see [FORMATS.md](FORMATS.md). For Trello card format, see [TRELLO_FORMAT.md](TRELLO_FORMAT.md).

## Phase 1: Generate (`/verify-prd <number>`, directory doesn't exist)

1. **Fetch PRD** — `gh issue view <number> --repo shopstackio/discount-genie-core --json title,body`
2. **Fetch child issues** — find issues referenced in the PRD body, fetch each
3. **Derive test cases:**
   - Primary: PRD user stories + implementation decisions (the final intended behavior)
   - Secondary: child issue acceptance criteria (supplementary detail)
   - Child criteria that conflict with PRD's final state → skip or mark `🔄 Superseded`
4. **Assign verification method tags** to each test case:
   - `[code]` — verifiable by reading source code (grep, file inspection)
   - `[unit]` — a relevant unit test exists or should exist
   - `[browser]` — behavior observable in the running app
   - A test can have multiple tags
   - **Any test describing behavior a user or developer could observe in the running app MUST include `[browser]`** — this is not optional even if `[code]` and `[unit]` also apply
   - Tests describing pure implementation details (e.g., "no import of X remains") are `[code]` only
5. **Scan for unit tests** — run `find` + `grep` to match test case subjects to existing test files. Tag `[unit]` and record the test file path in the chunk file. This upfront scan saves token cost across future sessions.
6. **Create directory structure** — `VERIFY-{number}/` with INDEX.md and chunk files (see [FORMATS.md](FORMATS.md))
7. **Split test cases into chunks:**
   - Default: PRD-level tests = one chunk, each child issue = one chunk
   - If a chunk exceeds ~10 tests, split further by theme with descriptive names
   - If the PRD has no child issues, still use the directory structure (one chunk + INDEX.md)
8. **Create Trello card** (if Trello enabled) per `TRELLO_FORMAT.md` (see Trello Integration below)
9. **Present first untested case** and ask "ready to test?"

## Phase 2: Resume (`/verify-prd <number>`, directory exists)

### Resume logic

1. Read `VERIFY-{number}/INDEX.md` — show progress stats
2. Find first non-`-done` chunk file
3. Open chunk → find first ⬜ test case
4. Begin the test flow (see below)
5. Human can override: "skip to test 08" or "switch to the other chunk"

### Test flow (per test case)

1. **Present** the test case and its method tags
2. **Run pre-work** based on tags:
   - `[code]` → grep, read source files, show relevant file:line references
   - `[unit]` → find and run the specific unit tests, show output
   - `[browser]` → describe what to look for in the app, wait for human to report observations
3. **For `[browser]` tests:** optionally ask the human to share logs (browser console, Remix server, Docker containers, database) as corroborating evidence. The agent can also check things it has access to (database, containers).
4. **Present draft evidence** — compact summary of what was found
5. **Ask: "Pass, fail, or concerns?"** — wait for explicit human response
6. **On human response:**
   - **Pass** → write ✅ status + evidence to chunk file, update INDEX.md stats
   - **Fail** → write ❌ status + finding entry to chunk file, ask "fix now or continue testing?"
     - Fix now → work on fix → re-test (restart from step 1) → if passes, flip to ✅ and append `**Fix:**` to finding
     - Continue → move to next untested case
   - **Concerns** → write ⚠️ status + finding entry to chunk file, move to next
   - **Defer** → write ⏸️ status + reason to chunk file, move to next
7. **Move to next ⬜ test case** in the chunk
8. **On non-related finding:** if testing surfaces a bug outside the PRD's scope, log it under `## Non-Related Findings` in the active chunk file with an `NF-{sequential}` ID. Do not block the PRD's pass/fail on non-related findings.

### Tag discovery during testing

The agent may discover during phase 2 that a test needs additional tags:
- If a relevant unit test is found → add `[unit]`, inform the human, run the test
- If a test is observable in the browser but wasn't tagged → add `[browser]`, inform the human
- **Never remove a `[browser]` tag** — can only add, never downgrade

### Chunk completion

A chunk is renamed to `-done` when all its tests have a non-⬜ status AND none are ❌:
- All ✅/⚠️/⏸️ → eligible for `-done`
- **If any ⏸️ tests exist:** ask the human "This chunk has deferred tests — mark as done with them deferred, or test them now?"
- On confirmation → rename file (e.g., `prd-level.md` → `prd-level-done.md`), update INDEX.md
- Any ❌ present → chunk stays active, agent lists the failures
- Any ⬜ remaining → still in progress

### Context loss between sessions

If the human left mid-test in a previous session, any draft evidence held in conversation is lost. The agent re-prepares the evidence from scratch. This is correct — re-preparing is cheap and maintains the "only write after human confirms" guarantee.

## `--diff` command

> **No-Trello mode:** print "No Trello card to diff — showing local progress summary" and display the INDEX.md stats instead.

1. Find the `VERIFY-*/` directory in project root (error if none)
2. Read INDEX.md to get the Trello card ID and chunk file list
3. Fetch Trello card's current checklist state
4. Iterate chunk files, map checklist items to local test case statuses by number
5. Display changes table:

```
| # | Test Case                        | Trello | Local |
|---|----------------------------------|--------|-------|
| 03 | Cache TTL respects config        | ⬜     | ✅    |
| 05 | Action path bypasses cache       | ⬜     | ❌    |
```

6. List any new findings (F-entries and NF-entries) not yet synced
7. Print summary: "X changed, Y unchanged, Z non-related findings"

## `--sync` command

> **No-Trello mode:** print "No Trello card — nothing to sync" and exit.

1. Find `VERIFY-*/` directory, read all chunk files for test case statuses
2. For each test case, check/uncheck the corresponding Trello checklist item:
   - ✅ or ⚠️ → checked
   - ⬜, ❌, or ⏸️ → unchecked
3. Ask: "Want to add a sync comment?" — user writes their own update or skips
4. If all tests are ✅, ⚠️, or ⏸️, print: "All tests resolved — run `/verify-prd --close` when ready."

Note: Evidence does NOT sync to Trello. Trello stays a lightweight mirror (checked/unchecked items + optional comments).

## `--close` command

Only runs when all chunks are `-done`. If any active chunk remains, refuse and list what's left. Non-related findings (NF-*) and design decisions (D-*) do not block closure.

1. **Update agentic files** — if findings revealed context gaps or codebase misunderstandings, update relevant `CLAUDE.md` or `docs/` files
2. **Post final Trello comment** (if Trello enabled) — condensed summary (not full evidence), move card to Done list
3. **Comment on GitHub PRD issue** — condensed summary: X/Y passed, Z deferred (with reasons), key findings, agentic file updates. If non-related findings exist, include a summary with links to any follow-up issues/PRDs created. If design decisions exist, reference the follow-up PRD.
4. **Delete `VERIFY-{number}/` directory** — permanent record lives on the GitHub issue comment
5. **Suggest PR creation** — ask user, don't auto-create

## `--refresh-format` command

1. Read `TRELLO_FORMAT.md` for current reference card ID (or accept a new card URL as argument)
2. Fetch reference card details via Trello API
3. Fetch 3 most recent cards from the target list
4. Extract from all 4 cards: card name pattern, description structure, checklists (names + item format), labels
5. Compare across cards to find common pattern; flag discrepancies and ask user to resolve
6. Write/overwrite `TRELLO_FORMAT.md` with discovered format

---

## Trello Integration (optional)

Trello is skipped entirely when `--no-trello` is passed, or when both `TRELLO_API_KEY` and `TRELLO_TOKEN` env vars are unset. All verification logic works without Trello — markdown files are always the source of truth.

### Env vars

`TRELLO_API_KEY` and `TRELLO_TOKEN` — same as the `/trello` skill.

Configured in project settings:
`~/.claude/projects/-Users-pablo-avelar-Dev-shopstack-discount-genie-core/settings.json`

### Card structure

- **Title:** Feature name from PRD (e.g., "Mantle authorization cache — loader/action freshness split"), NOT "Verify PRD #118"
- **Description:** per template in `TRELLO_FORMAT.md`
- **List:** as configured in `TRELLO_FORMAT.md` (expected: "Ready To Implement")
- **Labels:** per conventions in `TRELLO_FORMAT.md`
- **Checklists:**
  - One for PRD-level tests: `PRD #{number} — {feature name}`
  - One per child issue: `#{child-number} — {child issue title}`
  - Each item: `{number} — {test case name}` (e.g., `01 — Cache disabled by default`)

Evidence does NOT sync to Trello. Trello is a lightweight checked/unchecked mirror.

### TRELLO_FORMAT.md

Lives at `~/.claude/skills/verify-prd/TRELLO_FORMAT.md`. Contains:

- Board ID (hardcoded: `uJoa6Wbp`)
- Target list ID + name
- Reference card ID (updatable)
- Description template
- Checklist naming conventions
- Label conventions

This file is seeded by `--refresh-format` and refined by hand over time. The reference card ID in this file determines which card `--refresh-format` inspects on subsequent runs.

### API patterns

All Trello calls use curl + jq, matching the `/trello` skill:

```bash
# Fetch a card
curl -s "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN&checklists=all" | jq

# Create a card
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}" -d "name=Card Title" -d "desc=Description"

# Create a checklist
curl -s -X POST "https://api.trello.com/1/checklists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idCard={cardId}" -d "name=Checklist Name"

# Add checklist item
curl -s -X POST "https://api.trello.com/1/checklists/{checklistId}/checkItems?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "name=Item text"

# Check/uncheck a checklist item
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}/checkItem/{checkItemId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "state=complete"  # or "incomplete"

# Add a comment
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "text=Comment text"

# Move card to a list
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}"

# Get board lists
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'

# Get cards in a list
curl -s "https://api.trello.com/1/lists/{listId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN&checklists=all" | jq
```
