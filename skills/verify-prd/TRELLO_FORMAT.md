---
name: trello-format
description: Trello card format template for /verify-prd, derived from board inspection.
last_inspected: 2026-06-08
---

# Trello Format — verify-prd

## Board

- **Board ID:** `uJoa6Wbp`
- **Board name:** Main Board
- **Board URL:** https://trello.com/b/uJoa6Wbp/main-board

## Target list

- **List ID:** `67ae583912e669a5860de6d2`
- **List name:** Ready To Implement

## Done list (for --close)

- **List ID:** `67ae583912e669a5860de6d4`
- **List name:** In Prod / Done

## Reference card

- **Card ID:** `6a18f993735f55cdff97f227`
- **Short ID:** `J5I7Y8c8`
- **URL:** https://trello.com/c/J5I7Y8c8/273-free-plan-limit-entitlement-system-qa-test-log

## Card name pattern

```
[{TAG}] {Feature name} — {qualifier}
```

Examples from board:
- `[FREE-PLAN] Limit entitlement system — QA test log`
- `[KLAVIYO] Klaviyo integration in app`
- `[TABLE-VIEW-PREFERENCES][EPIC] Backend-backed table column layout preferences`
- `[POC] Server-side Mantle billing page`

For verification cards, use the parent feature/epic as the tag:
```
[{PARENT-FEATURE}] {Feature name from PRD}
```

Example: `[FREE-PLAN] Mantle authorization cache — loader/action freshness split`
The tag is the parent epic, NOT a card-type label like `[VERIFY]`.

## Description template

```markdown
**Context:** {One-sentence description of what is being verified and why.}

**Goal:** {What "done" looks like for this verification.}

**Progress ({date}):** {X} / {Y} test cases pass · {Z} fail · {W} findings resolved

**Links:**
- PRD: {GitHub PRD issue URL}
- Branch: `{branch name}` (if applicable)
- Verify file: `VERIFY-{number}.md`

**Related issues:** {child issue numbers, e.g., #123, #124}
```

Update the **Progress** line on each `--sync`.

## Checklist structure

One checklist per test section, named by source:

- **PRD-level tests:** `PRD #{number} — {feature name}`
- **Per child issue:** `#{child-number} — {child issue title}`

### Checklist item format

```
{section}.{number} {Test case name}
```

Examples from reference card:
- `1.1.1 At-limit: all discount type cards disabled`
- `3.1.1 Product discount form redirects at limit`
- `11.2 useIsWithinLimit.test.ts — within/over limit, cache empty (7/7)`

For verification cards, use sequential numbering within each checklist:
```
{number} — {Test case name}
```

Example:
- `01 — Cache disabled by default (TTL=0)`
- `02 — Loader uses cached authorization`

## Labels

Apply labels based on which repos/areas the PRD touches:

| Label | Color | ID | Use when |
|-------|-------|----|----------|
| Growth | lime | `69f2dca50b74320faa670318` | Feature is growth/monetization related |
| BackEnd | blue | `69f2dd080af1b0a13771d1d4` | PRD touches backend code |
| FrontEnd | purple | `69f2dcfe8f0c839f0eeed69a` | PRD touches frontend code |
| Foundation | sky | `69f2dcea57aa17a4747818d6` | PRD touches shared infrastructure |
| High Priority | yellow_dark | `67b3bfffbde8be7ed2e6836f` | Urgent verification |
| Bug | red | `67ae5df594a134321b433cc4` | Verification triggered by a bug |
| Blocked | black_light | `67b3bdf4ce89e48f9f3dfff5` | Verification blocked on something |

Most verification cards will use **FrontEnd** and/or **BackEnd** plus one domain label (Growth, Foundation).
