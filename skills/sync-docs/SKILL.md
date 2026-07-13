---
name: sync-docs
description: Detect what changed during development and propose targeted updates to agentic files and documentation. Reads .agents/governance.md as a manifest, uses git history and conversation context for change detection. Use when user wants to sync docs after development, update agentic files, or capture knowledge from a coding session.
---

# Sync docs

Detect what changed during development and propose targeted updates to
all knowledge files: agentic layer, standards, and documentation. The
goal is to capture knowledge gained during implementation before it
evaporates.

## Prerequisites

This skill requires `.agents/governance.md` to exist. If it doesn't,
suggest running `/init-docs` first.

## Workflow

### Phase 1 — Read the manifest

Read `.agents/governance.md` to understand:

1. **What files exist** — the project-specific mapping section lists all
   agentic files, standards, documentation, and templates.
2. **Last sync state** — the sync metadata section has `last-synced` and
   `last-synced-commit` fields.
3. **Template locations** — `.agents/templates/` for documentation formats.
4. **Multi-project structure** — if the per-project mapping subsection
   exists, record which workspace members have their own `AGENTS.md`,
   `DECISIONS.md`, or other project-scoped documentation. Also check for
   stack subdirectories under `.agents/standards/` (e.g., `web/`, `rust/`).

Validate the manifest against the filesystem: check that every file listed
actually exists — including per-project files and stack subdirectories. If
files are missing, note the discrepancy — it may indicate deleted files
that should be removed from the manifest, or files that were never created.

### Phase 2 — Detect changes

Use a hybrid approach to understand what changed:

**Git history** (always available):

```bash
# If last-synced-commit exists and is not "none":
git log --oneline <last-synced-commit>..HEAD
git diff --stat <last-synced-commit>..HEAD
git diff <last-synced-commit>..HEAD -- <specific files when needed>

# If no last-synced-commit (first sync):
git log --oneline -20
git diff --stat HEAD~20..HEAD
```

Look for:
- New files or directories added
- New dependencies in manifests
- Changes to project structure
- New patterns emerging (repeated similar changes)
- Configuration changes (linters, formatters, CI)
- Changes scoped to a specific workspace member (for routing proposals
  to the correct project docs — see Phase 3)

**Conversation context** (when available):

If invoked during an active session where development happened, use the
conversation history to understand:
- Why changes were made (motivation, constraints discovered)
- Decisions that were considered and rejected
- Domain terms that were clarified
- Patterns that were established or changed
- Workarounds or non-obvious implementations

When invoked in a fresh session (no prior conversation context), rely
entirely on git history. State this to the user: "No conversation context
available — working from git history only. I may miss the 'why' behind
some changes."

**Ignore sync-docs's own changes**: when diffing since `last-synced-commit`,
exclude changes to the sync metadata fields in `.agents/governance.md`
(the `last-synced` and `last-synced-commit` rows). These are artifacts
of a prior sync run, not development changes.

### Phase 3 — Scan and propose

Check each category of knowledge file against the detected changes. Only
surface proposals where evidence of a needed update exists. Skip
categories with no relevant changes.

**Categories to scan:**

| Category | File(s) | What to look for |
|---|---|---|
| Agent instructions | `AGENTS.md` | New commands, directories, tech stack changes, verification steps |
| Claude guidance | `CLAUDE.md` | New workflow recipes, skills references, reading instructions |
| Coding standards | `.agents/standards/code.md` | New coding patterns, conventions, language changes |
| Testing standards | `.agents/standards/testing.md` | New test patterns, tools, coverage expectations |
| Database standards | `.agents/standards/database.md` | Schema changes, new query patterns, migration patterns |
| Component standards | `.agents/standards/components.md` | New component categories, UI patterns |
| Security standards | `.agents/standards/security.md` | Auth changes, new security constraints |
| Stack-specific standards | `.agents/standards/{stack}/*.md` | Changes to stack-specific conventions |
| Domain context | `CONTEXT.md` | New domain terms, business rules, entity changes |
| Architecture decisions | `docs/adr/` | Decisions made during development that meet ADR criteria |
| Design system | `DESIGN.md` | New visual patterns, tokens, layout changes |
| External references | `REFERENCES.md` | New external sources consulted or patterns ported |
| Governance | `.agents/governance.md` | Structural changes to the knowledge file setup |
| Per-project agent instructions | `{project}/AGENTS.md` | Project-specific commands, repo map, tech stack changes |
| Per-project decisions | `{project}/DECISIONS.md` | Project-scoped architecture decisions |

**For standards files that don't exist yet:** if changes suggest a new
concern is now relevant (e.g., first database dependency added, first UI
component created), propose creating the file. Reference the templates
in `.agents/templates/` or fall back to the init-docs bundled templates.

#### Multi-project routing (monorepos)

When the governance manifest lists per-project files, route proposals to
the correct scope based on which files changed:

1. **Classify each changed file by project.** Use the workspace member
   paths from the manifest (e.g., changes under `core/` belong to the
   core project, changes under `tray/` belong to the tray project,
   changes at root belong to the root/primary project).

2. **Route to the narrowest applicable scope:**
   - A change to `tray/src-tauri/src/commands.rs` → propose updates to
     `tray/AGENTS.md` (repo map, commands) not root `AGENTS.md`.
   - A change to `core/src/backup.rs` → propose updates to
     `core/AGENTS.md` and possibly `core/DECISIONS.md`.
   - A change to `schema.sql` or `src/` at root → propose updates to
     root `AGENTS.md` and root-level standards.
   - A change to `.github/workflows/` or `docker/` → propose updates
     to root-level docs (`docs/DEPLOYMENT.md`, `docs/CODEMAP.md`).

3. **Standards routing:** match changed files to the correct standards
   file based on stack. If stack subdirectories exist:
   - Changes to `.rs` files in `core/` or `tray/` → check
     `.agents/standards/rust/conventions.md`
   - Changes to `.tsx`/`.ts` files at root → check
     `.agents/standards/web/components.md` or `web/database.md`
   - Changes that affect all projects → check shared standards
     (`code.md`, `security.md`, `testing.md`)

4. **Propose new per-project files** when a workspace member has
   significant new patterns or decisions but no project-scoped docs yet.
   Criteria: the project has its own `AGENTS.md` (per governance) but
   the proposal doesn't fit in root docs and no project-level doc exists.

**For each proposal, present:**

1. **Which file and section** — exact path and section heading
2. **What the change is** — the specific addition, modification, or removal
3. **What evidence triggered it** — git diff excerpt, commit message, or
   conversation reference
4. **Draft content** — the actual text to add or modify

Format proposals as a numbered list grouped by category. Example:

```
## Proposed updates

### AGENTS.md
1. **Add `docs/` to repository map** — new documentation directory created
   (git: 3 files added to docs/)
   
   Draft: `- docs/: project documentation and ADRs`

### .agents/standards/code.md
2. **Add error handling pattern** — new error boundary pattern established
   in commits abc1234, def5678
   
   Draft: (shows the pattern text)

### CONTEXT.md
3. **Add "Catalog" to glossary** — term used consistently across 4 new
   files with specific meaning
   
   Draft: **Catalog**: A lookup table...
```

### Phase 4 — Confirm

Present all proposals to the user. Allow them to:
- **Accept** individual proposals
- **Reject** individual proposals
- **Modify** the draft content before applying
- **Accept all** if they trust the proposals

Wait for explicit confirmation before writing anything.

### Phase 5 — Write

Apply accepted proposals:

1. Edit the target files with the approved content.
2. Update the sync metadata in `.agents/governance.md`:
   - Set `last-synced` to the current ISO 8601 timestamp
   - Set `last-synced-commit` to the current HEAD commit hash
3. If any new knowledge files were created (e.g., a new standards file),
   update the project-specific mapping section in governance.md.

## Constraints

- **Evidence-based only.** Never propose an update without pointing to
  specific evidence (git diff, commit, conversation context). "This might
  be useful" is not evidence.
- **Don't overwhelm.** If many changes exist, prioritize: structural
  changes and new patterns first, minor wording updates last. Cap at
  ~10 proposals per run. If more exist, note what was deferred.
- **Respect existing content.** Proposals modify or extend — they don't
  rewrite existing sections. If a section already covers the topic
  adequately, skip it.
- **Use project templates.** When creating new documentation content,
  read the project's templates from `.agents/templates/` for format
  guidance. Fall back to the skill's own knowledge of formats only when
  no templates exist.
- **Don't propose ADRs lightly.** Only propose an ADR when all three
  criteria are met: hard to reverse, surprising without context, result
  of a real trade-off. Most development sessions don't produce ADR-worthy
  decisions.
- **Standards files stay under 150 lines.** If a proposal would push a
  standards file over the limit, suggest splitting instead.
- **AGENTS.md stays under 100 lines.** Propose moving content to standards
  or documentation files if it would exceed the limit.
