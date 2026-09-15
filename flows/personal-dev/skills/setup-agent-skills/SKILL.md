---
name: setup-agent-skills
description: Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the engineering skills know this repo's issue tracker, label vocabulary, and domain doc layout — AND provisions the development-system pipeline: the label state machine (kind/triage/stage/needs:human), the `<type>/<issue#>-<slug>` branch convention, the GitHub Project (with its Status and Environment fields and four views), and the three standards tiers. Run before first use of `to-prd`, `to-vertical-issues`, `triage`, `log`, the orchestrator, `diagnose`, or `tdd` — or if those skills appear to be missing context about the tracker, labels, branch convention, or Project.
disable-model-invocation: true
---

# Setup Agent Skills

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker** — where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels** — the strings used for the five canonical triage roles
- **Domain docs** — where `CONTEXT.md` and ADRs live, and the consumer rules for reading them

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config` — is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root — does either exist? Is there already an `## Agent skills` section in either?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/` — does this skill's prior output already exist?
- `.scratch/` — sign that a local-markdown issue tracker convention is already in use

### 2. Present findings and ask

Summarise what's present and what's missing. Then walk the user through the three decisions **one at a time** — present a section, get the user's answer, then move to the next. Don't dump all three at once.

Assume the user does not know what these terms mean. Each section starts with a short explainer (what it is, why these skills need it, what changes if they pick differently). Then show the choices and the default.

**Section A — Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-issues`, `triage`, `to-prd`, and `qa` read from and write to it — they need to know whether to call `gh issue create`, write a markdown file under `.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub** — issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab** — issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown** — issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.) — ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

**Section B — Triage label vocabulary.**

> Explainer: When the `triage` skill processes an incoming issue, it moves it through a state machine — needs evaluation, waiting on reporter, ready for an AFK agent to pick up, ready for a human, or won't fix. To do that, it needs to apply labels (or the equivalent in your issue tracker) that match strings *you've actually configured*. If your repo already uses different label names (e.g. `bug:triage` instead of `needs-triage`), map them here so the skill applies the right ones instead of creating duplicates.

The triage axis has two roles: `needs-triage` (maintainer must evaluate) and `needs-info` (waiting on
reporter); its single exit is `needs-triage → stage:ready`. These sit inside the **full label state
machine** (kind / triage / stage / needs:human / blocked / wayfinder:map) that Section D provisions —
see [dev-flow-provisioning.md](./dev-flow-provisioning.md). On an existing repo, migrate the old
vocabulary: `ready-for-agent` → delete (it *was* `stage:ready`), `ready-for-human` → the `needs:human`
modifier, relabeling **open issues only**.

Default: each role's string equals its name. Ask the user if they want to override any.

**Section C — Domain docs.**

> Explainer: Some skills (`improve-codebase-architecture`, `diagnose`, `tdd`) read a `CONTEXT.md` file to learn the project's domain language, and `docs/adr/` for past architectural decisions. They need to know whether the repo has one global context or multiple (e.g. a monorepo with separate frontend/backend contexts) so they look in the right place.

Confirm the layout:

- **Single-context** — one `CONTEXT.md` + `docs/adr/` at the repo root. Most repos are this.
- **Multi-context** — `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files (typically a monorepo).

**Section D — the pipeline (labels, branch, Project, standards).**

> Explainer: the development-system pipeline runs on a fixed set of labels, a branch naming
> convention, and a GitHub Project. This section provisions them. The *shapes* are enforced (they're
> what the orchestrator and scripts parse); the *strings* are yours.

Walk the three standards tiers ([dev-flow-provisioning.md](./dev-flow-provisioning.md) → Standards):
**enforce** the tier-1 shapes (branch format + type set, label namespaces, the `main`-accepts-only-
`stage:docs`-cleared rule); **ask** for the tier-2 strings (label strings, base branch, test command,
demo command, design system, monitoring locations, `Environment` values); **propose** the tier-3
defaults the project may decline (commit convention = Conventional Commits, code standards, ADR
format, docs layout). Confirm whether the Project should be **org-level spanning several repos** (the
umbrella/PRD + code-repo/slices pattern) or single-repo.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa) — always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout — "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

Then write the three docs files using the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md) — GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) — GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) — local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) — label mapping
- [domain.md](./domain.md) — domain doc consumer rules + layout

For "other" issue trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

Also write `docs/agents/dev-flow.md` recording the pipeline decisions (chosen label strings, base
branch, test/demo commands, Project number, Environment values, tier-3 choices), seeded from
[dev-flow-provisioning.md](./dev-flow-provisioning.md).

### 4b. Provision the pipeline

Following [dev-flow-provisioning.md](./dev-flow-provisioning.md), actually create the machinery
(confirm each group before running):

- **Labels** — create the kind/triage/stage/needs:human/blocked/wayfinder:map set; migrate the old
  vocabulary on existing repos (open issues only).
- **Branch** — document the convention in `docs/agents/dev-flow.md`, protect `main`, and add the
  promote-PR template under `.github/PULL_REQUEST_TEMPLATE/`.
- **Project** — create/link the (org-level, if multi-repo) Project; provision the `Status` field
  (Ideas/Shaping/In development/Done) and `Environment` field (default Staging/Production) and the
  four views; enable auto-archive. Mirror `kind:` onto native issue types **only if** the owner is an
  org.

Everything here is `gh`/`gh api graphql`-scriptable; show the user the commands before running.

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from these files. Mention they can edit `docs/agents/*.md` directly later — re-running this skill is only necessary if they want to switch issue trackers or restart from scratch.
