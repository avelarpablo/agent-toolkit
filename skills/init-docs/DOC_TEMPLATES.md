# Documentation templates

Bundled format references for project documentation files. The init-docs
skill reads these during generation and produces two things from them:

1. **Documentation skeletons** — actual files (`CONTEXT.md`, `docs/adr/README.md`,
   etc.) with section headings and guided placeholders, populated where the
   grill produced concrete answers.
2. **Project-adapted templates** — stored in `.agents/templates/` for use by
   sync-docs, grill-with-docs, and other skills that create documentation.

These bundled templates are the bootstrap source. Once init-docs has run,
the project's own templates in `.agents/templates/` take precedence.

## Files created by init-docs

| File / Directory | Created when |
|---|---|
| `CONTEXT.md` | Always — skeleton with section headings, populated from grill results. |
| `docs/adr/README.md` | Always — explains ADR format, numbering, and when to create one. |
| `DESIGN.md` | UI framework detected — skeleton with design system sections. |
| `REFERENCES.md` | External references detected or mentioned during grill. |

## ADR — Architecture Decision Record

One file per decision in `docs/adr/`. File naming: `NNN-short-title.md`
(e.g., `001-use-sqlite.md`, `002-catalog-pattern.md`).

```markdown
# NNN. {{Title}}

**Status:** {{Proposed | Accepted | Deprecated | Superseded by [NNN](NNN-title.md)}}
**Date:** {{YYYY-MM-DD}}

## Context

{{What is the issue that motivates this decision? What forces are at play?
Include technical constraints, business requirements, and tradeoffs.
Be specific — name the alternatives that were considered.}}

## Decision

{{What is the change that is being proposed or decided? State it as an
active voice declaration: "We will use X" not "X was chosen."}}

## Consequences

### Positive

- {{What becomes easier or better as a result of this decision?}}

### Negative

- {{What becomes harder? What tradeoffs are accepted?}}

### Neutral

- {{What changes but is neither clearly positive nor negative?}}
```

ADR numbering is sequential. Do not reuse numbers from deprecated ADRs.
When a decision is superseded, update the old ADR's status to point to
the new one rather than deleting it — the history of why things changed
is valuable.

## CONTEXT.md — Domain context

Lives at project root or `docs/CONTEXT.md`. One per project (or per
module in monorepos).

```markdown
# {{Project name}} — Domain context

## Domain overview

{{One paragraph: what problem does this project solve? Who uses it?
What is the core domain?}}

## Glossary

{{Define domain-specific terms that appear in the code. Format as a
definition list. Only include terms where the code meaning differs from
the common English meaning, or terms that a developer unfamiliar with
the domain would not know.}}

- **{{Term}}:** {{Definition as used in this project.}}

## Business rules

{{Rules that the code enforces but that are not obvious from reading it.
Each rule should explain what and why.}}

- {{Rule description.}} — {{Why this rule exists.}}

## Entities and relationships

{{High-level description of the core data model. Not a schema dump —
describe the concepts, their relationships, and any non-obvious
constraints. Reference schema files or ADRs for details.}}

## Deferred decisions

{{Decisions that have been explicitly postponed. Document what was
considered and why it was deferred, so future contributors do not
re-investigate from scratch.}}

- **{{Decision}}:** {{Why deferred, and what would trigger revisiting it.}}
```

## DESIGN.md — Design system

Lives at project root. Relevant for projects with a UI.

```markdown
# {{Project name}} — Design system

## Tokens

### Colors

{{List semantic color tokens and their CSS custom property names.
Do not list raw hex values — list the token names that the code uses.}}

### Typography

{{Font families, sizes, weights used in the project. Reference the
CSS custom properties or Tailwind config.}}

### Spacing

{{Spacing scale and conventions. Reference the CSS or Tailwind config.}}

## Layout

### Breakpoints

{{List breakpoints and what changes at each. Reference the Tailwind
or CSS config.}}

### Page structure

{{Describe the page layout pattern: header, sidebar, main content,
footer. Note what changes between mobile and desktop.}}

## Navigation

{{Describe the navigation pattern. Include mobile and desktop variants
if they differ.}}

## Component patterns

{{Document established UI patterns that agents should follow when
building new features. Not individual component APIs — those are in
`.agents/standards/components.md`. Focus on composition patterns and
layout conventions.}}

## Iconography

{{Icon library used, sizing conventions, where to find available icons.}}
```

## REFERENCES.md — External references

Lives at `docs/REFERENCES.md` or project root. Documents external
projects that influenced this one.

```markdown
# References

External projects, libraries, and resources that influenced this
project's patterns. Consult the original when extending a pattern
that was ported from one of these sources.

## {{Reference project name}}

- **URL:** {{link}}
- **What was ported:** {{specific components, patterns, or approaches}}
- **Where it lives:** {{paths in this project}}
- **When to consult:** {{what kind of task should prompt reading the
  original — e.g., "when modifying the data table component"}}
```

## Module-level documentation

In monorepos or projects with distinct modules, documentation files can
live alongside the module's `AGENTS.md`:

```
apps/my-app/
├── AGENTS.md          # References module-level docs
├── CONTEXT.md         # Domain context specific to this module
└── docs/
    └── adr/           # Decisions specific to this module
```

The module's `AGENTS.md` references these docs in its Documentation
section. Root-level `AGENTS.md` should not duplicate module-level
documentation — reference by path or let the nested `AGENTS.md` handle it.
