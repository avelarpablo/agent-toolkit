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
| `DESIGN.md` | UI framework detected |
| `REFERENCES.md` | External references or ported patterns detected |

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
8. **Detect GitHub repo**: check if the project has a GitHub remote. If so,
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
