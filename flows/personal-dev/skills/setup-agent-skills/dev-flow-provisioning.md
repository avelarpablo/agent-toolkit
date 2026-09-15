# Dev-flow provisioning

What `setup-agent-skills` provisions so the development-system pipeline can run in a repo: the label
state machine, the branch convention, the GitHub Project (with its `Status` and `Environment`
fields), and the three standards tiers. Canonical definitions live in
[`docs/PROCESS.md`](../../../../docs/PROCESS.md); this file is the operator's checklist.

**Tier discipline (see [Standards](#standards--the-three-tiers)):** *enforce the shapes, ask for the
tier-2 strings, propose the tier-3 defaults.*

---

## Labels — the state machine

Three namespaces plus one modifier, each answering a different question and owned by one writer.
Provision every label; the strings are tier-2 (per-repo, but the **namespaces** are tier-1 — the
mechanism parses them).

| Label | Meaning | Written by |
|---|---|---|
| `kind:bug` / `kind:tech-debt` / `kind:wishlist` | what triggered the work | `log`, at capture |
| `triage:` (`needs-triage`, `needs-info`) | is it ready to build? | you, via `triage` |
| `stage:design` / `stage:ready` / `stage:dev` / `stage:refactor` / `stage:qa` / `stage:verify` / `stage:docs` | where it is in the build | the orchestrator |
| `needs:human` | modifier — who executes it | you, or the orchestrator on a capped loop |
| `blocked` | a slice waiting on a dependency | the orchestrator's scheduler |
| `wayfinder:map` | a product/epic map issue | `wayfinding` |

```bash
# GitHub: create each label (idempotent-ish; ignore "already exists")
for L in kind:bug kind:tech-debt kind:wishlist needs-triage needs-info \
         stage:design stage:ready stage:dev stage:refactor stage:qa stage:verify stage:docs \
         needs:human blocked wayfinder:map; do
  gh label create "$L" --force >/dev/null 2>&1 || true
done
```

### Migration from the old vocabulary (existing repos)

Relabel **open issues only**; closed history keeps its old labels.

- **`ready-for-agent` → delete.** It *was* `stage:ready` under another name. Move open issues to
  `stage:ready`, then delete the label.
- **`ready-for-human` → `needs:human`.** It answers *who executes*, not *where it is* — a modifier,
  not a state.
- **`needs-info`, `needs-triage`** — keep.
- **`wontfix`** — not a label; close the issue with a reason.

## Issue types (org repos only)

Verified: GitHub issue **types** are an organization-level feature (a personal-account repo returns
`issueTypes: null`). So **`kind:` labels are canonical**; where the owner is an org, *mirror* them
onto native types for the nicer UI (`kind:bug`→Bug, `kind:wishlist`→Feature; `kind:tech-debt` has no
native type, stays label-only). Check first:

```bash
gh api graphql -f query='{ repository(owner:"O",name:"R"){ issueTypes(first:10){ nodes{ name } } } }'
```

## Branch convention (tier-1 shape)

`<type>/<issue-number>-<kebab-slug>`, lowercased. Types: `feat/` `slice/` `design/` `task/` `fix/`.
**[GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)**: `main` is the one
long-lived branch; `main` accepts only a branch that has cleared `stage:docs` (after a passed
`stage:verify`). Prefixes are descriptive, not permissions. Document this in `docs/agents/`, and
protect `main` (and any deploy branch).

**Promote-PR template** — provision `.github/PULL_REQUEST_TEMPLATE/promote.md` carrying the closing
keywords so a `feat → main` (or `task → main`) merge auto-closes the feature issue:

```markdown
Closes #<feature-issue>
<!-- umbrella-repo PRD: use `Closes owner/repo#N` -->
```

## The GitHub Project

**One org-level Project (v2) spanning every repo of the product** — PRDs in the umbrella repo, slices
in the code repos, all on one board. Create it (or link an existing one), then provision fields +
views. Projects belong to a user/org, not a repo:

```bash
gh project create --owner <org> --title "<Product>"
gh project link  <number> --owner <org> --repo <code-repo>   # repeat per repo
```

### `Status` field — the Roadmap lifecycle (single-select)

Values, in order: **Ideas · Shaping · In development · Done**. `Status` is written **per phase by
disjoint owners** — `log`→Ideas, the producers (`to-prd`/`to-design-doc`)→Shaping, the
orchestrator→In development (and as it advances stages), GitHub's built-in workflow→Done on close.
Provision the field + values; the skills write the transitions.

### `Environment` field — deployment (single-select)

Values per project (tier-2), default **Staging · Production**. Written by **CI, after the issue
closes** (a closed issue stays a project item with editable fields). Never a `stage:` label.

### The four views

| View | Groups by | Filter/notes |
|---|---|---|
| **Roadmap** (product) | `Status` | Ideas → Shaping → In development → Done; `Environment` shown on Done cards |
| **Board** (dev) | `stage:*` | `stage:design` (optional, UI) → `stage:ready` … `stage:docs`, granular |
| **Deployment** | `Environment` | includes closed items |
| **Inbox** (triage) | filter | open + `kind:` + no `stage:` |

Enable **auto-archive** to keep views fast and stay under the 50k-item cap. Don't rely on Projects'
built-in automations beyond the close→Done one; the orchestrator and CI own the rest via the API.

---

## Standards — the three tiers

| Tier | Rule | This skill's action |
|---|---|---|
| **1 · Enforced shape** | mechanism parses it | **enforce**: branch format + type set, label namespaces, `main` accepts only `stage:docs`-cleared, every gate names an anchor, every cycle has a cap |
| **2 · Configured values** | per-repo strings | **ask**: label strings, base branch, tracker, test cmd, demo cmd, design system, monitoring locations, Environment values |
| **3 · The project's own** | nothing parses it | **propose a default the project may decline**: commit convention (Conventional Commits), code standards (`review-loop` criteria), ADR format, docs layout |
