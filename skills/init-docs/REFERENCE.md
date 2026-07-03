# Reference — AGENTS.md and CLAUDE.md patterns

Section templates for generating `AGENTS.md` and `CLAUDE.md`. Use only
sections that have real content from project inspection. Omit empty sections.

## AGENTS.md section templates

### Repository type

```markdown
## Repository type

{{One sentence: monorepo vs single project, what it does.}}
{{If monorepo: "Do not assume a root-level command applies to every project."}}
```

### Repository map

```markdown
## Repository map

{{List top-level directories with one-line descriptions.}}
{{For monorepos: list apps/ and packages/ contents.}}
{{Only include directories that matter for navigation.}}

- `src/`: application source code
- `tests/`: test suites
- `docs/`: documentation
```

For monorepos:

```markdown
## Repository map

- `apps/admin-web`: internal React application
- `apps/public-api`: customer-facing API
- `packages/contracts`: shared API types
- `packages/database`: persistence utilities

Read the nearest nested `AGENTS.md` before modifying a project or package.
```

### Tech stack

```markdown
## Tech stack

- **Language:** {{from manifest}}
- **Framework:** {{from dependencies}}
- **Database:** {{if detected}}
- **Testing:** {{test runner from manifest}}
- **Deployment:** {{if detectable from CI or config}}
```

### Commands

```markdown
## Commands

- Install: `{{package manager}} install`
- Dev server: `{{dev script}}`
- Test: `{{test script}}`
- Lint: `{{lint script}}`
- Type check: `{{typecheck script}}`
- Build: `{{build script}}`
```

For monorepos, include filtered commands:

```markdown
## Commands

- Install (root): `pnpm install`
- Dev (specific project): `pnpm --filter @repo/project-name dev`
- Test (specific project): `pnpm --filter @repo/project-name test`

Do not run install inside individual workspace directories.
```

### File naming

```markdown
## File naming

{{Only include if a convention is detectable or stated.}}
```

### Key constraints

```markdown
## Key constraints

{{Only include constraints that are:
  - Detectable from the code/config
  - Stated in existing documentation
  - Confirmed by the user

Do not invent constraints. Examples:}}

- **Language:** codebase in English, UI in Spanish.
- **Data integrity:** records are never hard-deleted, only soft-deleted.
- **Privacy:** user PII must not be logged or cached in plain text.
```

### Verification

```markdown
## Verification

Before finishing any task:

1. Run type checking.
2. Run linting on changed files.
3. Run tests for affected areas.
4. Review the diff for unintended changes.
{{Add domain-specific checks when applicable:}}
5. {{e.g., "Ensure schema.sql and service layer stay in sync."}}
6. {{e.g., "Verify the UI renders correctly in mobile and desktop viewports."}}
7. {{e.g., "Run contract tests against shared API types."}}
```

Adapt to detected tooling. Look for domain-specific artifacts that need
cross-checking: schema files, API contracts, UI viewports, generated
code, migration state. Include these as additional verification steps.

### Dependency boundaries (monorepos)

```markdown
## Dependency boundaries

- Applications may depend on packages.
- Packages must not depend on applications.
- {{Specific boundary rules if detectable.}}
```

### Coding standards

```markdown
## Coding standards

Read the relevant file in `.agents/standards/` before writing code:

- General principles and patterns: `.agents/standards/code.md`
{{Include only files that were created:}}
- UI components: `.agents/standards/components.md`
- Database work: `.agents/standards/database.md`
- Security-sensitive code: `.agents/standards/security.md`
- Writing tests: `.agents/standards/testing.md`
```

### Documentation

```markdown
## Documentation

Read only when relevant to the current task:

- {{Discovered docs with one-line descriptions. Examples:}}
- Domain context and business rules: `docs/CONTEXT.md`
- Architecture decisions: `docs/adr/`
- Visual design system: `DESIGN.md`
- API reference: `docs/api.md`
```

Populate from Phase 1 discovery. Include every doc that would help an
agent understand the project. Omit the section entirely if no docs exist.

## CLAUDE.md patterns

### Minimal bridge (no Claude-specific features detected)

```markdown
@AGENTS.md

## Claude-specific guidance

<!-- Add Claude-specific instructions here as they emerge.
     Examples: plan mode triggers, documentation to read for specific tasks,
     path-scoped rules references, skill descriptions. -->
```

### Bridge with detected features

```markdown
@AGENTS.md

## Claude-specific guidance

- Read `{{doc path}}` before {{when to read it — e.g., "proposing schema
  changes", "adding UI patterns"}}.
- {{Other detected Claude-specific instructions.}}

## Workflow recipes

{{Document recurring multi-step patterns detected in the codebase. These
help Claude follow established patterns when extending the project.}}

- When adding a new {{thing}}, follow the existing pattern:
  1. {{step 1 — e.g., "Add table to schema.sql"}}
  2. {{step 2 — e.g., "Create service function in services/"}}
  3. {{step 3 — e.g., "Add API route"}}
  4. {{step 4 — e.g., "Add UI component in forms"}}

## Path-scoped rules

Claude-specific path rules live in `.claude/rules/`. They reference
`.agents/standards/` and add file-pattern matching so the right standards
load automatically when editing matching files.

## Skills

- **{{skill name}}:** `.claude/skills/{{skill-dir}}/SKILL.md` — {{description}}
```

Include only sections that have real content. Workflow recipes are
especially valuable — look for repeating patterns in the codebase where
the same sequence of files is modified together (e.g., schema + service +
route + UI for a new entity type).

## What NOT to include

- Generic advice the agent already knows ("write clean code", "follow best
  practices").
- Duplicated content between AGENTS.md and CLAUDE.md — CLAUDE.md imports
  AGENTS.md, so anything in AGENTS.md is already available.
- Speculative constraints the user hasn't confirmed.
- Full architecture documentation — reference it by path instead.
- Content that belongs in `.agents/standards/` (coding conventions) rather
  than in the root instruction file.
