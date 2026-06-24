---
name: verify-prd
description: Verify a PRD implementation interactively — derive test cases from the PRD and child issues, track pass/fail in a VERIFY file, optionally sync progress to Trello. Use when user wants to verify a PRD, test an implementation against its spec, run /verify-prd, or check PRD acceptance criteria.
---

# Verify PRD

Two-phase skill: generate a verification plan from a PRD, then walk through each test case interactively with mandatory human confirmation. Markdown files are source of truth; Trello card optionally mirrors progress.

## Core principle

**Every test case requires explicit human confirmation.** The agent prepares evidence (grep, code reads, unit test runs), presents it, and waits. The human reviews and says "pass", "fail", or "concerns". Only then does the status update. No exceptions.

## Commands

| Command | What it does |
|---------|-------------|
| `/verify-prd <number>` | Generate verification directory + Trello card (phase 1), or resume testing (phase 2) |
| `/verify-prd <number> --no-trello` | Same as above but skip all Trello integration |
| `/verify-prd --diff` | Show local changes vs Trello card state since last sync |
| `/verify-prd --sync` | Push local state to Trello, optionally add a comment |
| `/verify-prd --close` | Close-out: Trello → Done, GitHub comment, delete directory |
| `/verify-prd --refresh-format` | Re-inspect Trello cards, regenerate TRELLO_FORMAT.md |

`--no-trello` can be passed with any command. When active, `--diff` and `--sync` are no-ops (nothing to sync), and `--close` skips Trello card updates.

## Prerequisites

- `gh` CLI authenticated
- `curl` and `jq` available

**For Trello integration (optional):**
- `TRELLO_API_KEY` and `TRELLO_TOKEN` env vars set (project settings or shell)
- `TRELLO_FORMAT.md` generated (run `--refresh-format` on first use)

If `--no-trello` is passed, or both `TRELLO_API_KEY` and `TRELLO_TOKEN` are unset, Trello is skipped automatically.

See [REFERENCE.md](REFERENCE.md) for workflows, [FORMATS.md](FORMATS.md) for file templates, and [TRELLO_FORMAT.md](TRELLO_FORMAT.md) for Trello card conventions.

## Quick start

```
# Start verifying a PRD (no Trello)
/verify-prd 118 --no-trello

# Start verifying a PRD (with Trello — needs env vars + format file)
/verify-prd --refresh-format   # first time only
/verify-prd 118

# Check what changed locally since last Trello sync
/verify-prd --diff

# Push progress to Trello
/verify-prd --sync

# When all tests pass — close out
/verify-prd --close
```

## Key rules

- The PRD is the contract — verify the PRD, not each issue in isolation
- One active verification at a time — `--diff`, `--sync`, `--close` auto-detect the VERIFY directory
- VERIFY directory lives in `discount-genie-core/` root, never sub-repos
- Markdown is source of truth; Trello is an optional mirror synced on demand
- Never auto-close while any ❌ exists

## Hard rules — the agent must NOT

1. **Update a test status without explicit human confirmation in that conversation turn**
2. **Batch-confirm multiple tests** — one at a time, one human response per status change
3. **Remove a `[browser]` tag** — can only add tags, never downgrade
4. **Write evidence to the file before human confirms** — hold in conversation
5. **Mark a chunk `-done` without asking about deferred (⏸️) tests first**
6. **Skip pre-work** — if a test is tagged `[unit]`, run the tests; if `[code]`, show the code
