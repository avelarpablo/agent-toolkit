# Governance template

This is the template for `.agents/governance.md`. The skill copies the
generic principles and expansion guide verbatim, then generates the
project-specific mapping section from inspection results.

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
└── standards/             # Coding and architecture standards (source of truth)
    ├── code.md            # Language, patterns, principles
    ├── components.md      # UI component conventions (if applicable)
    ├── database.md        # DB naming, migrations, data handling (if applicable)
    ├── security.md        # Auth, access control, sensitive data (if applicable)
    └── testing.md         # Testing philosophy and requirements (if applicable)
```

`code.md` is always present — it contains universal coding principles plus
language-specific conventions detected from the project. Other standards
files are created when the project has the relevant concern (UI components,
database, security, testing). Each file should cover one concern, stay under
150 lines, and document only conventions not obvious from the code itself.
Add new files as concerns emerge rather than expanding existing ones.

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

### Optional documentation files

These files provide domain knowledge that agents read on demand. They
are referenced by path in `AGENTS.md` and `CLAUDE.md`, never imported
with `@`. In monorepos, modules can have their own documentation files
referenced from nested `AGENTS.md` files.

| File / Directory | When to create |
|---|---|
| `docs/adr/` | Architecture Decision Records. One file per significant decision (database choice, auth strategy, framework migration). Standard format: status, context, decision, consequences. Prefer individual ADRs over monolithic decision logs — they are individually addressable and carry status. |
| `CONTEXT.md` | Domain terminology, glossary, business rules, entity relationships, and deferred decisions. Create when the project has domain knowledge not obvious from the code. |
| `DESIGN.md` | Visual design system: tokens, layout patterns, navigation, component composition patterns. Create when the project has a UI with established visual conventions. |
| `REFERENCES.md` | External projects that influenced this one. Documents what was ported from where and when to consult the original. Create when patterns were adapted from other codebases. |

## Maintenance rules

1. **Standards go in `.agents/standards/` first.** Never write a coding
   standard only in `.claude/rules/`. The vendor-neutral version is the
   source of truth.
2. **Keep `AGENTS.md` under 100 lines.** It is the map, not the encyclopedia.
3. **Keep each `.agents/standards/` file under 150 lines.** Split by concern.
4. **Review agentic files after significant development phases.** If new
   patterns, constraints, or conventions emerged, update the relevant files.
5. **Delete stale guidance.** Outdated instructions cause more harm than
   missing ones.

## Cross-agent compatibility

- `AGENTS.md` is the portable, vendor-neutral convention understood by Claude
  (via import), Codex, Copilot, Cursor, Gemini, and others.
- `CLAUDE.md` imports `AGENTS.md` and adds Claude-specific behavior.
- Other agents (Codex, Copilot, Cursor) discover `AGENTS.md` natively.

## Project-specific mapping

<!-- GENERATED: The skill replaces this section with project-specific content -->

This section maps the generic principles above to this repository's actual
structure. Update it as the agentic file structure evolves.

- **Root `AGENTS.md`:** {{describe scope — e.g., "covers the entire app" or
  "covers the monorepo root; nested files exist in apps/"}}
- **`.agents/standards/`:** {{list files that exist — at minimum code.md;
  list others if created during init}}
- **`.claude/rules/`:** {{list files if they exist, or "not yet created —
  add when standards need path-matching"}}
- **Documentation:** {{list docs that exist: ADRs in docs/adr/, CONTEXT.md,
  DESIGN.md, REFERENCES.md — or "none yet"}}

---

END TEMPLATE
