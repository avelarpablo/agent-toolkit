---
name: log
description: Quick-capture an item as a GitHub issue with the appropriate label. Use when user says /log, /log-wishlist, /log-tech-debt, /log-bugfix, or wants to capture a wishlist idea, tech debt item, or bug without a full triage flow.
---

# log

Capture an item as a GitHub issue and move on. No grilling, no triage — just
log it.

This skill requires interactive use — a human must confirm before the issue is
created.

## Supported types

Each type is a `kind:` label — the namespace the pipeline's inbox is built on. A logged item carries
its `kind:` and **no `stage:` label**: absence of a stage label *is* the inbox, so the orchestrator
(which only acts on `stage:*`) never picks up something unanalyzed. The `kind:` decides which analysis
runs when the item is later picked up (`bug`→`diagnose`, `tech-debt`→scoped refactor, `wishlist`→
wayfinding), all converging at `stage:ready`.

| Type | Label | Label color | Description |
|------|-------|-------------|-------------|
| `wishlist` | `kind:wishlist` | `#0E8A16` (green) | Feature ideas and future enhancements |
| `tech-debt` | `kind:tech-debt` | `#D93F0B` (red) | Known shortcuts, outdated patterns, scaling concerns |
| `bug` | `kind:bug` | `#E4E669` (yellow) | Bugs observed during development or conversation |

(Aliases: `/log-bugfix` still works → `kind:bug`.) The canonical strings come from
`setup-agent-skills`; use those if they differ.

## Invocation

```
/log <type> "description of the item"
/log <type>                              # synthesize from conversation
/log <type> --repo owner/other-repo "description here"
```

Aliases (for backwards compatibility):
- `/log-wishlist ...` → `/log wishlist ...`
- `/log-tech-debt ...` → `/log tech-debt ...`
- `/log-bugfix ...` → `/log bugfix ...`

If the type is omitted, ask the user which type they mean.

## Process

### 1. Parse the type

Extract the type from the first argument. It must match one of the supported
types above. If it doesn't match, show the supported types and ask.

### 2. Gather the idea

- **If args contain a description:** use it as the item description.
- **If no args (or only `--repo`):** synthesize from the current conversation
  context. Identify what the user was discussing that prompted the capture.

### 3. Inspect the code area (when relevant)

If the conversation or args reference specific code — especially for `tech-debt`
and `bugfix` types — briefly inspect the relevant files to enrich the issue:

- File paths and line numbers
- Current state of the code
- Why it's a problem

Keep inspection lightweight — read a few files, don't deep-dive. The goal is
enough context to act on later, not a full analysis.

For `bugfix`, also look for error messages, stack traces, or reproduction steps
mentioned in the conversation.

### 4. Draft the issue

Write a short title (under 80 chars) and a body using the template at
`templates/<type>.md` relative to this skill file. Fill in each section of the
template based on gathered context.

Target repo: use `--repo` if provided, otherwise the current git repo.

### 5. Check for duplicates

Search existing issues with the same label for potential duplicates:

```bash
gh issue list --label <label> --state all --search "<keywords from title>" --json number,title,state
```

Extract 2-3 keywords from your drafted title for the search.

### 6. Confirm with the user

Present everything in one step:

**If duplicates found:**

```
## Potential duplicates

- #42: "Similar issue title" (open)
- #17: "Related issue" (closed)

## Draft issue

**Repo:** owner/repo
**Title:** <drafted title>
**Labels:** <label>

<full body preview>

Create this issue? (yes / edit / cancel)
```

**If no duplicates:**

```
## Draft issue

**Repo:** owner/repo
**Title:** <drafted title>
**Labels:** <label>

<full body preview>

No duplicate <label> issues found.

Create this issue? (yes / edit / cancel)
```

Wait for the user's response:
- **yes** — create the issue
- **edit** — ask what to change, revise, re-confirm
- **cancel** — abort, acknowledge

### 7. Create the issue

```bash
gh issue create \
  --repo <repo> \
  --title "<title>" \
  --label <label> \
  --body "<body>"
```

If the label doesn't exist on the target repo, create it first:

```bash
gh label create <label> --description "<description from table>" --color "<color>" --force
```

**Never apply a `stage:` label** — a logged item is inbox, not buildable.

For **`kind:wishlist`**, set the item's Project `Status` to **Ideas** (`log` is the disjoint writer
of that Status value — see the dev-flow provisioning). `bug` and `tech-debt` get no Status until they
are picked up.

### 8. Report

Return the issue URL. One line. Done.
