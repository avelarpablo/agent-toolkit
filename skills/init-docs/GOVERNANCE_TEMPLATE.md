# Governance template

This is the template for `.agents/governance.md`. The skill copies the
generic principles and expansion guide verbatim, then generates the
project-specific sections from inspection and grill results.

---

BEGIN TEMPLATE

---

# Agentic files governance

How agent instruction files are structured, maintained, and extended in this
repository. The principles in this document are generic; the project-specific
mapping is at the bottom.

## Core principles

### 1. Instruction files are guidance, not enforcement

Agent instruction files (`AGENTS.md`, `CLAUDE.md`) provide context to coding
agents. They reduce unnecessary exploration and prevent recurring mistakes,
but they do not replace code reading. For behavior that must happen
deterministically, use hooks, permissions, linters, or CI.

### 2. Keep files concise

Each instruction file should stay under 200 lines. Longer files consume more
context and degrade instruction adherence. If a file grows past this limit,
extract sections into referenced documents or path-scoped rules.

### 3. Don't duplicate across scopes

A nested instruction file should not repeat what the root file already says.
It should only contain information that is local to that directory: different
commands, different constraints, different conventions.

### 4. Create boundaries where constraints change

Add a nested instruction file only when at least one of these is true:

- The directory is independently buildable or deployable.
- It has different test, lint, or generation commands.
- Its architectural boundaries are not obvious from the code.
- It uses materially different conventions.
- It has security or data-handling constraints.
- Agents repeatedly make the same mistake there.
- Work in the directory should not modify certain neighboring areas.

Do not create one merely because a directory exists.

### 5. Reference, don't import, large documents

Importing a file with `@` expands its contents into the context at startup.
This does not save tokens. For background material that is only sometimes
relevant, reference the path in backticks so agents read it on demand.

### 6. Update based on observed failures

Add guidance to instruction files when agents repeatedly make the same
mistake, not speculatively. Instruction content should emerge from real
problems.

## File hierarchy

### Vendor-neutral layer (`.agents/`)

The `.agents/` directory holds agent-readable documentation that any tool
can use.

```
.agents/
├── governance.md          # This file
├── standards/             # Coding and architecture standards (source of truth)
│   ├── code.md            # Language, patterns, principles (universal)
│   ├── security.md        # Auth, access control, sensitive data (universal)
│   ├── testing.md         # Testing philosophy and requirements (universal)
│   ├── observability.md   # Logger facade, structured event codes (universal)
│   ├── ci-cd.md           # Release channels, mandatory test gate (universal)
│   ├── components.md      # UI component conventions (single-stack repos)
│   ├── database.md        # DB naming, migrations (single-stack repos)
│   ├── web/               # Stack-specific (monorepos with multiple stacks)
│   │   ├── components.md  # UI component conventions
│   │   ├── database.md    # DB conventions for the web stack
│   │   ├── actions.md     # Server actions (server-first apps)
│   │   ├── errors.md      # Error codes and client resolution
│   │   ├── i18n.md        # Localization: locale maps + t() resolver
│   │   ├── a11y.md        # Accessibility: WCAG 2.1 AA, axe in CI
│   │   ├── auth.md        # Authentication: credentials, sessions, step-up
│   │   └── navigation.md  # Navigation shells, command palette, DataList
│   └── rust/              # Stack-specific
│       ├── conventions.md # Shared Rust conventions
│       └── tauri.md       # Framework-specific within Rust stack
└── templates/             # Project-adapted documentation templates
    ├── adr.md             # ADR format for this project
    ├── context.md         # CONTEXT.md format for this project
    ├── design.md          # DESIGN.md format (if applicable)
    └── references.md      # REFERENCES.md format
```

`code.md` is always present — it contains universal coding principles plus
language-specific conventions detected from the project. Other standards
files are created when the project has the relevant concern (UI components,
database, security, testing). Each file should cover one concern, stay under
150 lines, and document only conventions not obvious from the code itself.
Add new files as concerns emerge rather than expanding existing ones.

**Stack subdirectories** (e.g., `web/`, `rust/`, `python/`) are used in
monorepos where workspace members use different tech stacks. In single-stack
repos, standards stay flat at the root level. The rule: use subdirectories
when the same concern (e.g., "component conventions") would need materially
different guidance for different projects. See the init-docs skill for the
full organization rules.

Templates in `.agents/templates/` are project-adapted versions of
documentation formats. Skills that create documentation (sync-docs,
grill-with-docs) read templates from here when available, falling back to
their own bundled defaults for repos without init-docs setup.

### Vendor-specific layer (`.claude/`)

Claude-specific files **reference** `.agents/standards/` and add only what
is Claude-specific: path-matching metadata and tool guidance.

```
.claude/
├── settings.json
├── rules/                 # Path-scoped rules (reference standards + add path patterns)
│   ├── code.md
│   ├── components.md
│   └── ...
└── skills/                # Procedural instructions loaded on demand
    └── skill-name/
        └── SKILL.md
```

**Relationship between standards and rules:**

- `.agents/standards/` files are the **source of truth** for conventions.
  They are vendor-neutral and readable by any agent or human.
- `.claude/rules/` files are thin (5–10 lines). They add `paths:` frontmatter
  so Claude auto-loads the right guidance for matching files, and they
  reference the corresponding `.agents/standards/` file. Example:

  ```markdown
  ---
  paths:
    - "src/**/*.ts"
  ---

  Read and follow `.agents/standards/code.md` for coding principles.
  ```

- If a standard applies everywhere (not path-specific), it belongs in
  `AGENTS.md` or `.agents/standards/` — not in a rule.

**When to create `.claude/rules/`:** when you have `.agents/standards/` files
and want Claude to auto-load the right standard based on which files are
being edited. Create one rule per standard, matching the relevant file paths.

### Entry points

| File | Purpose |
|------|---------|
| `AGENTS.md` | Vendor-neutral entry point. Repo map, tech stack, commands, constraints, verification. |
| `CLAUDE.md` | Imports `AGENTS.md` via `@`. Adds Claude-specific guidance and references. |

## Documentation

### Documentation files

These files provide domain knowledge that agents read on demand. They
are referenced by path in `AGENTS.md` and `CLAUDE.md`, never imported
with `@`. In monorepos, modules can have their own documentation files
referenced from nested `AGENTS.md` files.

| File / Directory | Purpose |
|---|---|
| `CONTEXT.md` | Domain terminology, glossary, business rules, entity relationships, and deferred decisions. |
| `docs/adr/` | Architecture Decision Records. One file per significant decision. |
| `DESIGN.md` | Visual design system: tokens, layout patterns, navigation, component composition. |
| `REFERENCES.md` | External projects that influenced this one. What was ported and when to consult the original. |

### Templates

Project-adapted templates live in `.agents/templates/`. When creating new
documentation files, read the corresponding template for the project's
expected format:

| Template | Used for |
|---|---|
| `.agents/templates/adr.md` | Creating new ADRs in `docs/adr/` |
| `.agents/templates/context.md` | Updating or creating `CONTEXT.md` |
| `.agents/templates/design.md` | Updating or creating `DESIGN.md` |
| `.agents/templates/references.md` | Updating or creating `REFERENCES.md` |

## Issue tracking

Tech debt and wishlist items are tracked as GitHub issues with labels
rather than repo files. This integrates with the triage → to-prd →
to-vertical-issues → ralph pipeline.

| Label | Purpose | When to use |
|---|---|---|
| `tech-debt` | Technical debt to address | Code smells, shortcuts taken, known improvements deferred during implementation |
| `wishlist` | Ideas and nice-to-haves | Feature ideas, quality-of-life improvements, "it would be nice if..." thoughts |

Create issues with the appropriate label rather than tracking these in
repo files. This keeps the issue tracker as the single source of truth
for work items and allows triage workflows to pick them up.

## Maintenance rules

1. **Standards go in `.agents/standards/` first.** Never write a coding
   standard only in `.claude/rules/`. The vendor-neutral version is the
   source of truth.
2. **Keep `AGENTS.md` under 100 lines.** It is the map, not the encyclopedia.
3. **Keep each `.agents/standards/` file under 150 lines.** Split by concern.
4. **Review agentic files after significant development phases.** If new
   patterns, constraints, or conventions emerged, update the relevant files.
   Consider running `/sync-docs` to detect and propose updates.
5. **Delete stale guidance.** Outdated instructions cause more harm than
   missing ones.

## Cross-agent compatibility

- `AGENTS.md` is the portable, vendor-neutral convention understood by Claude
  (via import), Codex, Copilot, Cursor, Gemini, and others.
- `CLAUDE.md` imports `AGENTS.md` and adds Claude-specific behavior.
- Other agents (Codex, Copilot, Cursor) discover `AGENTS.md` natively.

## Sync metadata

<!-- sync-docs reads and updates this section automatically -->

| Field | Value |
|---|---|
| `last-synced` | `never` |
| `last-synced-commit` | `none` |

## Project-specific mapping

<!-- GENERATED: The skill replaces this section with project-specific content -->

This section maps the generic principles above to this repository's actual
structure. Update it as the agentic file structure evolves.

- **Root `AGENTS.md`:** {{describe scope — e.g., "covers the entire app" or
  "covers the monorepo root + primary project; nested files exist for
  child projects"}}
- **`.agents/standards/`:** {{list files that exist — at minimum code.md;
  list others if created during init. For monorepos with stack subdirs,
  list the directory structure.}}
- **`.agents/templates/`:** {{list template files that exist}}
- **`.claude/rules/`:** {{list files if they exist, or "not yet created —
  add when standards need path-matching"}}
- **Documentation:** {{list docs that exist: CONTEXT.md, ADRs in docs/adr/,
  DESIGN.md, REFERENCES.md — describe what has content vs skeleton-only}}
- **Issue tracking:** {{describe label setup — e.g., "tech-debt and wishlist
  labels created on GitHub"}}

<!--
  CONDITIONAL: include this subsection only for monorepos with nested
  project files. Omit entirely for single-project repos.
-->

### Per-project mapping

For each workspace member with its own agentic files:

- **`{project}/AGENTS.md`:** {{describe scope — what it covers, which
  shared standards it references}}
- **`{project}/DECISIONS.md`:** {{exists / not yet created — describe
  what kinds of decisions belong here vs root}}
- **`{project}/CONTEXT.md`:** {{exists / not yet created — only when
  project has its own domain terminology distinct from root}}

Example:

```
- **`core/AGENTS.md`:** Rust library crate. References shared standards
  code.md, testing.md, and rust/conventions.md.
- **`core/DECISIONS.md`:** Library refactor rationale, API design choices.
- **`tray/AGENTS.md`:** Tauri desktop app. References shared standards
  code.md, testing.md, rust/conventions.md, and rust/tauri.md.
- **`tray/DECISIONS.md`:** Tauri 2 choice, auto-update strategy, tray UX.
```

<!-- END CONDITIONAL -->

---

END TEMPLATE
