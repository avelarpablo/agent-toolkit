# Standards templates

Templates for `.agents/standards/` files. Each template has **generic**
sections (applicable to any project) and **detected** sections (populated
from project inspection). Generic sections are always included; detected
sections are included only when evidence exists.

## "Not yet implemented" sections

When a standards file covers a concern that is relevant but not yet
configured (e.g., testing without a test runner, security without auth),
mark forward-looking sections with this comment pattern:

```markdown
<!-- NOT YET IMPLEMENTED: The guidance below is a recommendation based on
     project inspection. When this concern is first implemented, review
     and confirm these conventions with the user before treating them as
     established. -->
```

This tells agents that the section is directional, not confirmed. On the
first task that touches this concern, the agent should present the
guidance to the user for validation and remove the comment once confirmed.

## code.md — always created

```markdown
# Code standards

General coding principles and patterns for this project. These apply to all
source code regardless of layer or feature.

## Principles

### Single responsibility

Every function, module, and component does one thing. If a description
requires "and," split it. Prefer small, focused units over large
multi-purpose ones.

### DRY

Extract shared logic only when duplication is real and proven (three or more
occurrences). Premature abstraction is worse than duplication. When
extracting, name the abstraction after what it does, not where it came from.

### Self-documenting code

Names carry meaning. Choose descriptive names for variables, functions, and
types so the code reads as prose. Do not add comments that restate what the
code does. Only comment the *why* when it would surprise a reader: hidden
constraints, workarounds, non-obvious invariants.

### Guard clauses

Handle edge cases and invalid states at the top of a function with early
returns. This keeps the main logic at the lowest nesting level.

### Functional style

Prefer pure functions, immutable data, and composition over mutation and
inheritance. Avoid classes unless a library requires them.

## Language and syntax

<!-- DETECTED: populate from project manifests and config -->

- **Language:** {{detected language and version}}
- **Style:** {{detected formatter/linter — e.g., "follow the project ESLint
  and Prettier configuration" or "follow ruff/black configuration"}}
- **Imports:** {{detected import conventions — path aliases, grouping}}
- **Naming:**
  - {{detected naming conventions by entity type — variables, functions,
    types, files, directories}}

## Patterns

<!-- DETECTED: populate only if enough signal from the framework -->

### Error handling

{{Adapted to detected framework. Examples:
  - React/Next.js: "Use state to represent errors in the UI. At system
    boundaries, validate with Zod and catch errors into state."
  - Python/FastAPI: "Raise typed exceptions. Use exception handlers for
    HTTP error responses."
  - Go: "Return errors explicitly. Wrap with context using fmt.Errorf."
  Omit if no clear framework pattern.}}

### Validation

{{Adapted to detected validation library or pattern. Examples:
  - "Validate at system boundaries with Zod schemas."
  - "Use Pydantic models at API boundaries."
  - "Validate input at handler level; trust internal function calls."
  Omit if no validation library detected.}}

## Architecture

<!-- DETECTED: populate only if a clear pattern is visible -->

{{Describe the project's directory structure and organization pattern if
  detectable. Reference other standards files for specific conventions.
  Omit entirely if the project is too early or has no clear structure.}}
```

## testing.md — when test runner detected or testable logic exists

```markdown
# Testing standards

Testing philosophy and conventions for this project.

## Philosophy

- **Test behavior, not implementation.** Tests verify what the code does
  from the outside, not how it does it internally. Refactoring should not
  break tests.
- **Focus on logic, not boilerplate.** Pure functions, business logic, and
  algorithms deserve thorough tests. Simple wrappers and pass-through code
  do not.
- **Integration over unit for IO-heavy code.** For code that interacts with
  databases, APIs, or UIs, integration tests that exercise real flows
  provide more value than isolated unit tests.

## What to test

### Always test

- Data transformations — any function that transforms, filters, or sorts.
- Business logic — core algorithms, rule engines, calculations.
- Validation schemas — accept valid input, reject invalid input with
  useful messages.

### Test selectively

- Integration flows — critical user journeys or API contracts.
- Side effects — functions that mutate state or call external services.

### Skip

- Simple pass-through code — wrappers that delegate without logic.
- Type-only files — types are verified by the compiler.
- Configuration files — static config that rarely changes.

## Tools

<!-- DETECTED: populate from project manifests. If no test runner is
     configured yet, state that and include project-specific constraints
     that will apply when testing is added (e.g., "use a separate test
     database", "mock external API calls"). -->

{{If not yet configured, add the NOT YET IMPLEMENTED comment before
  the Tools section and include project-specific constraints:}}

- **Test runner:** {{detected — e.g., Vitest, Jest, pytest, go test, cargo test.
  Or: "Not yet configured."}}
- **Test location:** {{detected — e.g., colocated .test.ts files, tests/ directory}}

## Conventions

- **Test names describe behavior:** `it("keeps married couples together")`,
  not `it("test case 1")`.
- **Arrange-Act-Assert:** structure every test with setup, execution, and
  verification phases.
- **No test interdependence.** Each test runs in isolation.
- **Factories over fixtures.** Use builder functions to create test data
  with sensible defaults, rather than static JSON fixtures.
```

## database.md — when database detected

```markdown
# Database standards

Database conventions for this project.

<!-- DETECTED: adapt to detected database type -->

## Naming

- **Tables:** plural, `snake_case`.
- **Columns:** `snake_case`.
- **Primary keys:** `id` (UUID or auto-increment, per project convention).
- **Foreign keys:** `referenced_table_singular_id` (e.g., `user_id`).
- **Timestamps:** every table has `created_at` and `updated_at`.
- **Boolean columns:** prefix with `is_` or `has_`.

## Migrations

- Each migration is a single file with a descriptive name.
- Migrations are forward-only. Never edit a migration that has been applied.
- Test migrations against a fresh database before committing.

## Querying

<!-- DETECTED: adapt to detected ORM/query builder -->

{{Examples:
  - "Use Supabase client library. Query from server components or server
    actions — never from client components directly."
  - "Use Prisma client. Keep queries in repository modules."
  - "Use SQLAlchemy sessions. Keep queries in the data access layer."
  Omit if no ORM/query pattern is clear.}}

## Data integrity

<!-- DETECTED: populate only with confirmed constraints -->

{{Project-specific data integrity rules. Examples:
  - "Soft deletes only — records are never physically deleted."
  - "Immutable audit trail — append only, never modify."
  Omit if no constraints are known; the user can add them later.}}

## Project-specific patterns

<!-- DETECTED: document multi-layer patterns that involve the database -->

{{If the project has recurring patterns that span schema → service → API →
  UI (e.g., a lookup/catalog pattern, an entity CRUD pattern), document
  them here with the full sequence of steps. This helps agents follow
  established patterns when extending the project.

  Example:
  "Lookup tables (categories, payment_methods, workers) follow a
  consistent pattern:
  1. Table in schema.sql with id + name (+ type-specific columns).
  2. Service function with search and create.
  3. API route (GET for search, POST for create).
  4. AsyncCreatableSelect component in forms for the UI."

  Omit if no cross-layer patterns are detectable.}}
```

## components.md — when UI framework detected

```markdown
# Component standards

<!-- DETECTED: adapt entirely to detected UI framework -->

{{Framework}} component conventions for this project. Read
`.agents/standards/code.md` for general principles that also apply here.

## Component categories

<!-- DETECTED: derive categories from the actual project structure.
     Do not use the defaults below if the project organizes components
     differently. Walk the component directories and describe what
     actually exists, including the directory path for each category. -->

Components are organized by what they do, not where they appear.

{{Derive categories from the project. Examples of what you might find:

### UI components (`src/components/ui/`)
Generic, reusable presentation components with no business logic.

### App shell (`src/components/`)
Navigation and layout components. App-specific, not reusable.

### Feature components (`src/features/*/components/`)
Components that orchestrate business logic for a specific feature.

### Form components
Components that manage form state, validation, and submission.

The key is to describe what exists with actual paths, not template slots.}}

## Conventions

<!-- DETECTED: adapt to framework -->

{{Framework-specific conventions. Examples:

For React/Next.js:
- Functional components only, no classes.
- Props defined as a type named `ComponentNameProps`.
- Default to server components; add "use client" only when hooks or
  browser APIs are needed.

For Vue:
- Use Composition API with `<script setup>`.
- Props defined with `defineProps<ComponentNameProps>()`.

For Svelte:
- Use runes for reactivity.
- Props defined with `$props()`.

Omit framework-specific conventions if the framework is not detected.}}

## Styling

<!-- DETECTED: adapt to detected styling approach -->

{{Examples:
  - "Tailwind CSS utility classes. Mobile-first responsive design."
  - "CSS Modules colocated with components."
  - "Styled-components with theme tokens."
  Omit if no styling approach is detected.}}

## Project-specific UI patterns

<!-- DETECTED: document UI patterns specific to this project -->

{{If the project has established UI patterns (navigation structure, layout
  system, modal/dialog conventions), document them here. Examples:

  "Mobile: bottom nav bar, hidden on lg:. Desktop: fixed left sidebar,
  hidden below lg:. Primary action always accessible via FAB."

  Omit if no project-specific patterns are detectable.}}
```

## security.md — when user-facing app or data sensitivity concerns detected

```markdown
# Security standards

Security conventions for this project.

## Authentication

<!-- DETECTED: adapt to detected auth library. If no auth is implemented,
     state that clearly, add the NOT YET IMPLEMENTED comment, and
     document what should be done when auth is added. -->

{{Examples:
  - "Supabase Auth with email/password. All routes require authentication."
  - "NextAuth.js with OAuth providers."
  - "JWT-based auth with refresh tokens."
  - "Not implemented. Single-user local application. If auth is added:
    protect all API routes, use httpOnly cookies, validate sessions."
  Populate only what is detected or confirmed.}}

## Input validation

- Validate all user input at system boundaries before it reaches the
  database or business logic.
- Use parameterized queries — never interpolate user input into query
  strings.
- Sanitize user-provided text rendered in the UI to prevent XSS.

## Data protection

<!-- DETECTED: populate only if sensitive data handling is known -->

{{Examples:
  - "Never log personal data to console or external services."
  - "Never include personal data in error messages."
  - "Secrets live in .env.local, never committed."
  Omit if no specific data protection requirements are known.}}

## Dependencies

- Review new dependencies before adding them. Prefer well-maintained
  packages with small dependency trees.
- Keep dependencies up to date.
- Do not install packages with known vulnerabilities.
```

## observability.md — when logging is present (most projects)

Shared standard, not web-only. Applies to server and client code alike.

```markdown
# Observability standards

How this project emits logs and diagnostic events.

## Log through a facade

Never call `console.*` or a logging library directly in feature code. Route
all logging through a single logger facade so format, levels, and
destinations stay swappable.

## Structured, by event code

Emit structured records (JSON) keyed by a stable event code, not free-text
prose. A record carries `code`, `level`, and a typed payload. Event codes
are greppable and survive message-wording changes.

## Levels

Use a small fixed set: `debug`, `info`, `warn`, `error`. Reserve `error`
for conditions that need attention.

## Server and client

The same facade shape exists on both sides. Client logs forward to the
server transport. Never log secrets or personal data from either side.

<!-- DETECTED: name the actual logger module/path and event-code registry
     if one exists. Omit sections that do not apply. -->
```

## ci-cd.md — when CI config (`.github/workflows`) or deployment present

```markdown
# CI/CD standards

How this project builds, tests, and releases.

## Delivery targets

<!-- DETECTED: list the actual release targets. -->

{{Describe each independent delivery target. Example: a cloud/web deploy and
  a local/desktop artifact, released on separate version tags (e.g.,
  `web-v*` and `local-v*`) so one channel never blocks the other.}}

## The quality gate (non-negotiable)

A single test gate must pass before ANY channel publishes. No release —
cloud or local — ships on red. The gate runs the full suite (unit,
integration, E2E) and blocks publishing on failure.

## Release channels

Each channel is triggered by its own tag/branch pattern and is
independently gated by the shared test gate.

## Migrations & secrets

<!-- DETECTED: document how DB migrations run in CI and where secrets come
     from. Omit if not applicable. -->
```

## web/actions.md — when Next.js App Router / server-first web app detected

```markdown
# Server action standards

Conventions for server actions in a server-first {{framework}} app. Read
`.agents/standards/code.md` and `web/components.md` first.

## Server-first data flow

Fetch and mutate on the server. Server components read data directly;
mutations go through server actions, not client-side fetches to API routes.

## The `FormActionResult<T>` contract

Every form-bound action returns a single discriminated result — success with
data, or failure with an error code and optional field errors — and never
throws to the client.

## The `withFormAction` wrapper

Wrap action bodies in a shared `withFormAction` helper that validates input
(Zod), invokes the service layer, maps errors to codes, and returns the
`FormActionResult`. Keeps every action uniform.

## Revalidation

After a successful mutation, revalidate affected data with `revalidateTag`
(tag-based) rather than blanket path revalidation.

## Client integration

Bind actions in the client with a `useServerFormAction` hook exposing
pending state, result data, and field/global errors.

## Actions vs API routes

Default to server actions for app-internal mutations. Reserve API routes for
third-party callers, webhooks, and non-form GET endpoints.

<!-- DETECTED: reference the actual helper/hook module paths and the
     per-feature co-located `actions.ts` layout. -->
```

## web/errors.md — when server-first web app detected

```markdown
# Error handling standards

How errors travel from server to UI. Read `web/actions.md` first.

## The server returns codes, not strings

Server code fails with a typed `ActionError` carrying a stable `code` (and
optional interpolation detail), never a user-facing sentence. The client
owns wording, so messages can be localized and reworded freely.

## Per-feature `errors.ts`

Each feature declares its error codes in a co-located `errors.ts`, namespaced
by feature. Zod validation failures map into the same `ActionError` shape.

## `resolveError` on the client

The client maps a `code` to display text via a `resolveError` resolver
(localized), with `{detail}` interpolation for dynamic parts. Field errors
attach to their corresponding form fields.

## Route-level errors

Use framework `error.tsx` and `not-found.tsx` boundaries for render/route
failures. Log the real cause server-side; show the resolved message
client-side.

<!-- DETECTED: reference the actual ActionError type and error-code registry
     paths. -->
```

## web/i18n.md — when user-facing web app detected

```markdown
# Localization standards

How user-facing text is defined and resolved.

## No user-facing strings in logic

Application and server logic never contain literal user-facing strings. They
reference keys; text lives in locale maps.

## Central + feature-colocated locale maps

Shared/common text lives in a central locale map; feature-specific text lives
in locale maps co-located with the feature. Both feed one resolver.

## The `t()` resolver

Resolve keys to text through a single `t()` function with `{placeholder}`
interpolation. No heavyweight i18n framework — a typed key→string map plus
the resolver.

## What must be localized

All labels, messages, empty states, and error text (see `web/errors.md`).
Log messages and event codes are NOT localized.

<!-- DETECTED: name the locale-map module paths and active-locale
     mechanism. -->
```

## web/a11y.md — when user-facing web UI detected

```markdown
# Accessibility standards

## Target vs mandatory

Target WCAG 2.1 AA across the UI. A programmatically-testable subset is
**mandatory** and enforced in CI; the rest is reviewed but not blocking.

## Free from the primitives

Use accessible UI primitives (Radix-style) so roles, focus management, and
keyboard interaction come for free. Do not re-implement interactive widgets
from raw divs.

## Mandatory checklist

The enforced subset includes: no axe violations, labelled form controls,
sufficient color contrast, keyboard operability, and visible focus.

## Enforcement

Automated a11y checks run in E2E via `@axe-core/playwright` and fail the
build on violations in the mandatory subset.

<!-- DETECTED: reference the axe integration in the test setup. -->
```

## web/auth.md — when auth detected OR internet-facing user app

```markdown
# Authentication standards

<!-- DETECTED: adapt to the actual auth implementation. If no auth exists
     yet but the app is internet-facing, add the NOT YET IMPLEMENTED comment
     and treat this as the target design. -->

## Credential tiers

Support layered credentials: a primary password, a fast-unlock PIN, and
optional WebAuthn/biometrics. Each tier has distinct strength and use.

## Step-up

Sensitive operations require step-up re-authentication beyond an active
session.

## Recovery

Issue a one-time recovery key at enrollment for account recovery; never
recover by weakening a credential.

## Sessions

Server-managed sessions in httpOnly cookies with expiry and rotation.
Protect all non-public routes; validate the session server-side.

<!-- DETECTED: name the auth module, session store, and route-protection
     mechanism. -->
```

## web/navigation.md — when web UI with navigation detected

```markdown
# Navigation standards

Read `web/components.md` first.

## Two shells

Pick one navigation shell per app:
- **SimpleShell** — a few flat destinations.
- **SectionedShell** — apps with hierarchical depth (sections + entities).

## Dual desktop/mobile via CSS breakpoints

One component tree renders both desktop and mobile layouts, switched by CSS
breakpoints — not separate route trees or JS user-agent branching. Desktop
has no global top bar; navigation lives in a sidebar axis.

## Shared primitives

Provide a command palette and a dedicated search page for fast navigation.
Present collections with a `DataList` component rather than raw `<table>`
markup.

## Touch targets and a11y

Meet minimum touch-target sizes and follow `web/a11y.md`.

<!-- DETECTED: reference the actual shell components and DataList path. -->
```

## rust/conventions.md — when Rust detected (shared across Rust projects)

```markdown
# Rust conventions

Shared Rust conventions for all Rust projects in this repository.

## Error handling

- Functions return `anyhow::Result<T>` for application code.
- Use `thiserror` for library error types that cross API boundaries.
- Propagate errors with `?` — avoid `.unwrap()` except in tests.
- Error messages in {{customer-facing language — e.g., English, Spanish}}.

## Naming

- **Crates:** `kebab-case` in `Cargo.toml`, `snake_case` in code.
- **Modules:** `snake_case`, one file per module.
- **Types:** `PascalCase` for structs, enums, traits.
- **Functions:** `snake_case`. Prefix with verb: `create_`, `get_`, `is_`.
- **Constants:** `SCREAMING_SNAKE_CASE`.

## Patterns

<!-- DETECTED: populate from project inspection -->

### Async

{{Adapted to detected async runtime. Examples:
  - "Use tokio as the async runtime. Mark async functions explicitly."
  - "No async — pure synchronous library."
  Omit if not detected.}}

### Testing

- Tests live in `#[cfg(test)] mod tests` inside each module.
- Use `tempfile` for filesystem tests.
- Test names describe behavior: `fn restores_backup_after_failed_update`.

## Project-specific patterns

<!-- DETECTED: populate from Cargo.toml dependencies and code inspection -->

{{Document recurring patterns shared across Rust projects. Examples:
  - "Docker interactions go through docker.rs, never called directly."
  - "Progress reporting uses callbacks, not terminal output."
  Omit if no cross-project patterns are detectable.}}
```

## Stack-specific standards — when to create

Create a stack subdirectory (`web/`, `rust/`, `python/`, etc.) when:

1. The repo has **two or more projects using different tech stacks**.
2. An existing flat standard (e.g., `components.md`) would need
   **materially different content** for different projects.
3. A convention is shared by **multiple projects of the same stack**
   but not all projects in the repo.

Do NOT create stack subdirectories for single-stack repos — keep
standards flat. Do NOT create a subdirectory for a single file — if
only one standard is stack-specific, keep it flat with a clear name
(e.g., `rust-conventions.md`). The subdirectory pattern pays off at
two or more files per stack.

## What NOT to put in standards

- Content that belongs in `AGENTS.md` (repo map, tech stack, commands).
- Content that belongs in `CLAUDE.md` (Claude-specific tool guidance).
- Conventions obvious from the code itself or enforced by linters.
- Speculative rules the user hasn't confirmed.
- Project-specific business logic — that belongs in domain documentation.
