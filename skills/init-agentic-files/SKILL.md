---
name: init-agentic-files
description: Scaffold agentic instruction files (AGENTS.md, CLAUDE.md, .agents/governance.md, .agents/standards/) for a project. Use when user wants to set up agentic files, initialize agent instructions, add CLAUDE.md or AGENTS.md to a project, or bootstrap agent guidance for a repository.
---

# Init agentic files

Scaffold the core agentic files for a project. The goal is to give coding
agents (Claude, Codex, Copilot, Cursor, Gemini) enough context to navigate
the repository, follow conventions, and verify their work — without
over-documenting or creating empty scaffolding.

## Output

The skill always produces these files:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Vendor-neutral entry point. Repo map, tech stack, commands, constraints, verification. |
| `CLAUDE.md` | Imports `AGENTS.md` via `@`. Adds Claude-specific guidance. |
| `.agents/governance.md` | How agentic files are structured, maintained, and expanded in this project. |
| `.agents/standards/code.md` | Coding principles and language/syntax conventions. Always created. |

The skill may also create additional standards files based on detection:

| File | Created when |
|------|-------------|
| `.agents/standards/testing.md` | Test runner detected or testable logic exists |
| `.agents/standards/database.md` | Database dependency or ORM detected |
| `.agents/standards/components.md` | UI framework detected (React, Vue, Svelte, etc.) |
| `.agents/standards/security.md` | User-facing app or data sensitivity concerns detected |

The governance doc explains how to expand the structure further (rules,
documentation files, domain context). See
[DOC_TEMPLATES.md](DOC_TEMPLATES.md) for templates of optional
documentation files (ADRs, CONTEXT.md, DESIGN.md, REFERENCES.md) that
the governance doc references — the skill discovers and references
existing docs but does not create them.

## Workflow

### Phase 1 — Inspect the project

Before asking the user anything, gather evidence:

1. **Detect project type** from manifests: `package.json`, `pyproject.toml`,
   `Cargo.toml`, `go.mod`, `build.gradle`, `Gemfile`, `*.csproj`, `Makefile`.
2. **Read existing documentation**: `README.md`, `CONTRIBUTING.md`, any
   existing `AGENTS.md` or `CLAUDE.md`.
3. **Map the directory structure**: top-level directories and one level deep
   into `src/`, `apps/`, `packages/`, `lib/`, or equivalent.
4. **Discover documentation files**: scan `docs/`, root-level `.md` files,
   and `adr/` or `adrs/` directories. Catalog what exists and its purpose
   (ADRs, context docs, design system, references). These will be referenced
   in the Documentation section of AGENTS.md — the skill does not create
   documentation files.
5. **Detect commands**: scripts in manifests, `Makefile` targets, CI config.
6. **Detect existing agentic files**: check for `.claude/`, `.agents/`,
   `.cursor/rules/`, `GEMINI.md`, `.github/copilot-instructions.md`.
7. **Detect project characteristics**: monorepo vs single project, language,
   framework, test runner, linter, formatter, deployment target.

Record findings internally. Do not write any files yet.

### Phase 2 — Draft and present

Using the inspection results and the templates in
[REFERENCE.md](REFERENCE.md), draft all files.

**AGENTS.md** — populate only sections with detected content:
- Repository type (mono vs single, what it does)
- Repository map (directories found, one-line descriptions)
- Tech stack (from manifests)
- Commands (detected scripts — dev, test, lint, build, typecheck)
- Key constraints (from README, existing docs, or leave minimal)
- Documentation (paths to discovered docs — ADRs, context, design, etc.)
- Verification checklist (adapted to detected tooling — include
  domain-specific checks like schema consistency, UI viewport testing,
  or contract validation when applicable)

Omit sections that would be empty or generic filler. See REFERENCE.md for
section templates.

**CLAUDE.md** — always starts with `@AGENTS.md`. Add Claude-specific
guidance including:
- Documentation reading instructions (when to read which doc)
- Workflow recipes for recurring multi-step patterns detected in the
  codebase (e.g., "when adding a new X, follow: step 1 → step 2 → ...")
- Existing skills or rules references

If nothing Claude-specific is detected, produce a minimal bridge with a
placeholder section the user can fill.

**.agents/governance.md** — use the template from
[GOVERNANCE_TEMPLATE.md](GOVERNANCE_TEMPLATE.md). The generic principles and
expansion guide are copied verbatim. Generate only the "Project-specific
mapping" section at the bottom from inspection results.

**.agents/standards/code.md** — always created. Structure:
- **Principles** (generic): single responsibility, DRY, self-documenting
  code, guard clauses, functional style. These apply to any project.
- **Language and syntax** (detected): language, style tools, import
  conventions, naming conventions — populated from manifests and config.
- **Patterns** (detected): error handling, state management, validation
  patterns adapted to the detected framework. Omit if not enough signal.
- **Architecture** (detected): directory structure conventions if a clear
  pattern is detectable. Omit if the project is too early.

See [STANDARDS_TEMPLATES.md](STANDARDS_TEMPLATES.md) for all templates.

**Additional standards** — create when the concern is relevant to the
project, even if the tooling is not yet configured. A database dependency
without migrations, a UI framework without a design system, or an app
without auth are all valid reasons to create the file — document the
project-specific constraints that already apply and flag what is not yet
in place. Do not create a file for a concern the project will never have.

- `testing.md`: test runner detected OR testable logic exists → populate
  philosophy (generic) + tools and conventions (detected or "not yet
  configured" with project-specific constraints like "use separate test
  database").
- `database.md`: DB dependency detected → populate naming conventions
  (generic for that DB type) + project-specific patterns spanning multiple
  layers (e.g., a catalog pattern touching schema → service → API → UI).
- `components.md`: UI framework detected → derive component categories
  from the actual directory structure (not just template defaults). Include
  project-specific UI patterns (e.g., navigation pattern, layout system).
- `security.md`: user-facing app or data sensitivity concerns → populate
  generic security principles + detected auth model (or "not yet
  implemented" with constraints that already apply like input validation).

Present all drafted files to the user. Explain:
- What was auto-detected and from where
- What was inferred vs confirmed
- What sections were omitted and why
- Which additional standards were offered and why

### Phase 3 — Confirm and write

Wait for the user to review and approve (or request changes). Only write
files after explicit confirmation.

If any of the three files already exist, show a diff of proposed changes and
ask whether to overwrite, merge, or skip.

## Constraints

- **Do not scaffold empty files.** Every file must contain real content.
  A standards file for a "not yet configured" concern is valid if it
  includes project-specific constraints that already apply.
- **Do not create documentation files** (`DESIGN.md`, `CONTEXT.md`,
  ADRs, etc.) — only discover and reference existing ones. Documentation
  scaffolding is a separate concern.
- **Do not create `.claude/rules/`.**
  The governance doc explains when and how to add these.
- **Keep AGENTS.md under 100 lines.** It is a map, not an encyclopedia.
- **Keep CLAUDE.md minimal.** The bridge import does the heavy lifting.
- **Keep each standards file under 150 lines.** Split by concern.
- **Standards have generic + detected sections.** Generic principles are
  always included; detected sections are populated from evidence. Do not
  fill detected sections with guesses.
- **Do not duplicate content across files.** AGENTS.md has the substance;
  CLAUDE.md imports it; governance.md explains the structure; standards
  have the conventions. AGENTS.md references standards by path.
- **Do not invent conventions.** Only document what is detectable or what
  the user confirms. If unsure, ask.
