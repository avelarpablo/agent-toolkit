# AFK Agent — discount-genie (ralph-dg)

`ralph-dg` is a wrapper around the generic `ralph` runner, configured for the
discount-genie-core multi-repo workspace. Issues are tracked on
`shopstackio/discount-genie-core` but code lives in nested sub-repos.

## How it works

1. Fetches `ready-for-agent` issues from `shopstackio/discount-genie-core`
2. Routes each issue to a sub-repo based on its title prefix (`BE:` → backend, `FE:` → frontend)
3. Runs the shared eligibility engine — checks labels, blocker chain, sub-repo presence
4. Ensures the target sub-repo is on a feature branch (creates one from `develop` if needed)
5. Acquires a workspace lock (prevents concurrent runs)
6. Runs Claude inside the sub-repo (Claude reads that repo's CLAUDE.md/AGENTS.md)
7. After Claude finishes: verifies HEAD moved, runs a blocking Codex review gate
8. Closes the issue on the core repo; unlocks any downstream issues

## Commands

```bash
ralph-dg once                           # one iteration (next eligible issue)
ralph-dg once --issue 42                # target a specific issue
ralph-dg once --prd 20                  # pick next child of PRD #20
ralph-dg loop                           # loop until done (default max 10)
ralph-dg loop --max 5 --prd 20          # loop over PRD children (max 5)
ralph-dg resume list                    # list resumable interrupted runs
ralph-dg resume RUN_ID                  # retry an interrupted run
ralph-dg schedule list                  # list scheduled runs
ralph-dg review <sha> -- <issue>        # manual post-commit review
ralph-dg check                          # verify auth, sub-repos, lock, issues
ralph-dg init                           # first-time setup
RALPH_MODEL=claude-sonnet-4-6 ralph-dg once  # override model
```

## Issue convention

Issues **must** have a `BE:` or `FE:` title prefix for routing:

| Prefix | Target sub-repo            | Example                                        |
| ------ | -------------------------- | ---------------------------------------------- |
| `BE:`  | `discount-genie-backend/`  | `BE: KlaviyoIntegration table + config + CRUD` |
| `FE:`  | `discount-genie/`          | `FE: Settings page + nav link`                 |
| `PRD:` | Skipped (not implementable) | `PRD: Klaviyo OAuth Integration`              |

Issues without a recognized prefix are skipped with a warning.

## Protected branches

`main`, `develop`, and `staging` are protected. Feature branches are created
from `develop` when `RALPH_FEATURE_BRANCH` is set.

## See also

- `runners/ralph/CLAUDE.md` — generic ralph documentation
- `runners/ralph-dg/hooks.sh` — DG-specific routing overrides
