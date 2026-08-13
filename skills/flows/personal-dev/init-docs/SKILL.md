---
name: init-docs
description: Scaffold agentic instruction files AND documentation skeletons for a project. Interviews the user about project-specific patterns, generates tailored templates, and sets up the full knowledge file structure. Use when user wants to set up agentic files, initialize documentation, add CLAUDE.md or AGENTS.md, or bootstrap agent guidance for a repository.
---

# Init docs

Scaffold the full knowledge file structure for a project: agentic
instruction files, documentation skeletons, and project-adapted templates.
The goal is to give coding agents enough context to navigate the
repository, follow conventions, and verify their work — and to give
sync-docs a complete structure to maintain over time.

## Output

### Always produced

| File | Purpose |
|------|---------|
| `AGENTS.md` | Vendor-neutral entry point. Repo map, tech stack, commands, constraints, verification. |
| `CLAUDE.md` | Imports `AGENTS.md` via `@`. Adds Claude-specific guidance. Includes sync-docs reminder. |
| `.agents/governance.md` | Unified manifest: file structure, documentation locations, template locations, issue-tracker conventions, last-synced metadata. |
| `.agents/standards/code.md` | Coding principles and language/syntax conventions. |
| `.agents/templates/adr.md` | Project-adapted ADR template. |
| `.agents/templates/context.md` | Project-adapted CONTEXT.md template. |
| `.agents/templates/design.md` | Project-adapted DESIGN.md template. |
| `.agents/templates/references.md` | Project-adapted REFERENCES.md template. |
| `CONTEXT.md` | Domain context skeleton with section headings. |
| `docs/adr/README.md` | ADR index explaining format and numbering. |

### Produced when relevant

| File | Created when |
|------|-------------|
| `.agents/standards/testing.md` | Test runner detected or testable logic exists |
| `.agents/standards/database.md` | Database dependency or ORM detected |
| `.agents/standards/components.md` | UI framework detected (React, Vue, Svelte, etc.) |
| `.agents/standards/security.md` | User-facing app or data sensitivity concerns detected |
| `.agents/standards/observability.md` | Always/most projects — any logging or diagnostic output present |
| `.agents/standards/ci-cd.md` | CI config (`.github/workflows`) or a deployment target present |
| `.agents/standards/web/actions.md` | Next.js App Router / server-first web app detected |
| `.agents/standards/web/errors.md` | Server-first web app detected |
| `.agents/standards/web/i18n.md` | User-facing web app detected |
| `.agents/standards/web/a11y.md` | User-facing web UI detected |
| `.agents/standards/web/auth.md` | Auth detected OR internet-facing user app |
| `.agents/standards/web/navigation.md` | Web UI with navigation detected |
| `DESIGN.md` | UI framework detected |
| `REFERENCES.md` | External references or ported patterns detected |

### Produced in monorepos (per workspace member)

| File | Created when |
|------|-------------|
| `{project}/AGENTS.md` | Project is independently buildable with its own stack/commands |
| `{project}/DECISIONS.md` | Project has architecture decisions distinct from root |
| `{project}/CONTEXT.md` | Project has its own domain terminology distinct from root (rare) |
| `.agents/standards/{stack}/*.md` | Multiple stacks detected across projects (see [Layered standards](#layered-standards)) |

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
   and `adr/` or `adrs/` directories. Catalog what exists and its purpose.
5. **Detect commands**: scripts in manifests, `Makefile` targets, CI config.
6. **Detect existing agentic files**: check for `.claude/`, `.agents/`,
   `.cursor/rules/`, `GEMINI.md`, `.github/copilot-instructions.md`.
7. **Detect project characteristics**: monorepo vs single project, language,
   framework, test runner, linter, formatter, deployment target.
8. **Detect workspace structure** (monorepo detection): check for workspace
   indicators — `[workspace]` in `Cargo.toml`, `workspaces` in
   `package.json`, `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, or
   `turbo.json`. For each workspace member, record:
   - Directory path and project name
   - Tech stack (language, framework — may differ from root)
   - Whether it is independently buildable/testable
   - Existing nested `AGENTS.md` or documentation
   Classify each member as one of: **app** (deployable), **library**
   (consumed by other members), or **tool** (build/dev tooling).
   Recurse one level only — if a workspace member is itself a workspace,
   treat its members as peers of the top-level members rather than
   nesting further.
9. **Detect GitHub repo**: check if the project has a GitHub remote. If so,
   verify that `tech-debt` and `wishlist` labels exist; note if they need
   to be created.

Record findings internally. Do not write any files yet.

### Phase 2 — Grill the user

Interview the user about project-specific patterns, conventions, and
documentation needs. The grill phase replaces guessing — answers here
directly inform what goes into the generated files and templates.

Base questions on inspection results. Skip questions where the codebase
already provides a clear answer. Ask one question at a time, waiting for
the response before continuing.

**Areas to cover** (adapt to what was detected):

- **Domain terminology**: what are the core concepts? Are there terms that
  mean something specific in this project? (informs CONTEXT.md skeleton
  and template)
- **Coding conventions**: anything beyond what the linter/formatter
  enforces? Patterns the team has adopted? (informs standards files)
- **Architecture patterns**: how is new functionality typically added?
  Is there a repeating pattern (e.g., schema → service → route → UI)?
  (informs AGENTS.md workflow section and CLAUDE.md recipes)
- **Testing philosophy**: integration vs unit preference? What must always
  be tested? (informs testing.md)
- **Key constraints**: business rules, compliance, performance requirements?
  (informs AGENTS.md constraints and CONTEXT.md)
- **Design system** (if UI detected): established visual patterns, layout
  conventions? (informs DESIGN.md skeleton)
- **External references**: patterns ported from other projects? (informs
  REFERENCES.md)
- **Documentation needs**: anything the team wishes was documented but
  isn't? Any decisions that should be recorded as ADRs?

**Monorepo-specific areas** (when workspace detected):

- **Project relationships**: which projects depend on which? Is there a
  primary project or are they peers? (informs AGENTS.md structure)
- **Shared vs project-specific conventions**: do all projects follow the
  same coding standards, or do different stacks need different guidance?
  (informs standards organization)
- **Shared vs project-specific documentation**: are architecture decisions
  system-wide or scoped to individual projects? (informs where DECISIONS.md
  and CONTEXT.md live)
- **Stack directory naming**: the default convention names stack
  subdirectories under `.agents/standards/` after the language or runtime
  (`web/`, `rust/`, `python/`). If any workspace member directory shares a
  name with a stack (e.g., a project called `web/`), ask the user what
  naming convention to use for standards subdirectories to avoid confusion.

Keep the grill focused. Stop when you have enough signal to generate
project-specific content rather than generic boilerplate. 3–8 questions
is typical.

### Phase 3 — Generate

Using inspection results, grill answers, and the bundled reference files,
generate all output files.

**Agentic layer** — generate using [REFERENCE.md](REFERENCE.md) for
AGENTS.md/CLAUDE.md patterns, [STANDARDS_TEMPLATES.md](STANDARDS_TEMPLATES.md)
for standards, [GOVERNANCE_TEMPLATE.md](GOVERNANCE_TEMPLATE.md) for
governance:

- **AGENTS.md** — populate only sections with detected content. Omit
  sections that would be empty or generic filler. Keep under 100 lines.
- **CLAUDE.md** — starts with `@AGENTS.md`. Include sync-docs reminder:
  "After significant development, consider running /sync-docs before
  ending the session." Add Claude-specific guidance from grill results.
- **.agents/governance.md** — use expanded governance template. Generate
  the project-specific sections from inspection and grill results.
- **.agents/standards/** — code.md always. Others based on detection.
  Keep each under 150 lines.

**Documentation skeletons** — generate using [DOC_TEMPLATES.md](DOC_TEMPLATES.md)
as the format guide. Each skeleton contains section headings with brief
descriptions of what belongs in each section. Populate sections where the
grill produced concrete answers; leave other sections as guided placeholders.

- **CONTEXT.md** — always created. Populate domain overview and any terms
  surfaced during the grill. Include empty-but-structured sections for
  glossary, business rules, entities, deferred decisions.
- **docs/adr/README.md** — always created. Explains ADR format, numbering,
  and when to create one. References `.agents/templates/adr.md`.
- **DESIGN.md** — created when UI framework detected. Populate what was
  surfaced during the grill; leave other sections structured.
- **REFERENCES.md** — created when external references detected or
  mentioned during grill.

**Adapted templates** — generate project-tailored versions of each doc
format and store in `.agents/templates/`. These adapt the bundled formats
to the project's specific conventions and terminology. Other skills
(sync-docs, grill-with-docs) read from here when available.

- `.agents/templates/adr.md` — ADR format adapted to project conventions
- `.agents/templates/context.md` — CONTEXT.md format adapted to project domain
- `.agents/templates/design.md` — DESIGN.md format (if UI project)
- `.agents/templates/references.md` — REFERENCES.md format

**GitHub labels** — if a GitHub remote is detected, create `tech-debt` and
`wishlist` labels if they don't already exist:

```bash
gh label create tech-debt --description "Technical debt to address" --color "D93F0B" --force
gh label create wishlist --description "Ideas and nice-to-haves" --color "0E8A16" --force
```

#### Monorepo — layered standards and per-project files {#layered-standards}

When multiple tech stacks are detected across workspace members, organize
standards using **stack subdirectories** under `.agents/standards/`:

```
.agents/standards/
  code.md              ← universal (applies to all projects)
  security.md          ← universal
  testing.md           ← universal
  observability.md     ← universal (logging facade, structured events)
  ci-cd.md             ← universal (release channels, test gate)
  web/                 ← stack-specific (React/Vue/Svelte projects)
    components.md
    database.md
    actions.md         ← server actions (server-first apps)
    errors.md          ← error codes / resolution
    i18n.md            ← localization
    a11y.md            ← accessibility
    auth.md            ← authentication
    navigation.md      ← navigation shells + DataList
  rust/                ← stack-specific (Rust projects)
    conventions.md
    tauri.md           ← framework-specific within a stack
  python/              ← stack-specific (Python projects)
    conventions.md
```

**Rules for organizing standards:**

- A standard that applies to **all projects** stays at the root level
  (`code.md`, `security.md`, `testing.md`).
- A standard specific to **one tech stack** goes in a stack subdirectory
  named after the language or runtime (`web/`, `rust/`, `python/`).
- A standard specific to **one framework within a stack** goes in the
  stack subdirectory with a descriptive name (`rust/tauri.md`).
- If a standard is shared by **two or more but not all** projects of the
  same stack, it goes in the stack subdirectory (e.g., `rust/conventions.md`
  shared by a core library and a tray app that both use Rust).
- Default to naming stack subdirectories after the language or runtime
  (`web/`, `rust/`, `python/`). Use `web/` for TypeScript/JavaScript
  frontend stacks rather than `typescript/`. If a workspace member
  directory shares a name with a stack default (e.g., a project called
  `web/`), use the naming convention agreed during the grill phase.

**Per-project files:** each independently buildable workspace member gets:

- **`{project}/AGENTS.md`** — project-specific repo map, tech stack,
  commands, constraints, and verification steps. References shared
  standards by relative path (e.g., `../.agents/standards/rust/conventions.md`).
  Does NOT duplicate content from the root `AGENTS.md`.
- **`{project}/DECISIONS.md`** — architecture decisions scoped to that
  project. Only created when there are decisions that don't belong in the
  root-level `docs/adr/` or `docs/DECISIONS.md`.

**Root AGENTS.md in monorepos:** acts as both monorepo orchestrator AND
primary project documentation when one project lives at root. Structure:

1. Repository type and overview (monorepo)
2. Repository map (all projects with pointers to nested AGENTS.md)
3. Primary project sections (if one lives at root): tech stack, commands,
   constraints, verification
4. Coding standards (points to `.agents/standards/`)
5. Documentation (points to shared docs)

Each project's `AGENTS.md` then says: "Read shared standards X, Y, Z"
(by relative path) plus any project-specific conventions inline or in
its own standards files.

**Shared documentation stays at root:**

| File | Scope |
|------|-------|
| `docs/CODEMAP.md` | Full repo map (all projects) |
| `docs/DEPLOYMENT.md` | System-wide deployment (all artifacts) |
| `CONTEXT.md` or `docs/CONTEXT.md` | Domain/business context (shared) |
| `docs/adr/` | System-wide architecture decisions |

Present all generated files to the user. Explain:
- What was auto-detected and from where
- What was informed by the grill vs inferred
- What sections were omitted and why
- Which additional standards and documentation files were created and why

### Phase 4 — Confirm and write

Wait for the user to review and approve (or request changes). Only write
files after explicit confirmation.

If any files already exist, show a diff of proposed changes and ask
whether to merge, overwrite, or skip each one. Skip files where the
proposed content is identical to the existing file — no diff, no prompt.
When merging, preserve user-added content (e.g., glossary terms in
CONTEXT.md, custom constraints in standards) and integrate the proposed
changes alongside it. New files that don't yet exist are created normally.

## Constraints

- **Do not create `.claude/rules/`.** The governance doc explains when and
  how to add these.
- **Keep AGENTS.md under 100 lines.** It is a map, not an encyclopedia.
- **Keep CLAUDE.md minimal.** The bridge import does the heavy lifting.
- **Keep each standards file under 150 lines.** Split by concern.
- **Standards have generic + detected sections.** Generic principles are
  always included; detected sections are populated from evidence. Do not
  fill detected sections with guesses.
- **Do not duplicate content across files.** AGENTS.md has the substance;
  CLAUDE.md imports it; governance.md explains the structure; standards
  have the conventions.
- **Do not invent conventions.** Only document what is detectable or what
  the user confirms during the grill. If unsure, ask.
- **Skeletons must have structure.** Every documentation skeleton contains
  section headings and brief descriptions of what belongs in each section.
  Empty files are not acceptable. Sections with no content yet should have
  a one-line placeholder describing what will go there.
- **Templates reflect the project.** Templates in `.agents/templates/` are
  adapted to the project's conventions, not copies of the bundled defaults.
  They should reference project-specific terminology, patterns, and
  conventions surfaced during the grill.
