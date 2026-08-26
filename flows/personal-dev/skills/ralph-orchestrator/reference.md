# ralph-orchestrator — reference

Deep mechanics and hard-won gotchas for driving ralph in the background. Every
mechanic below is verified against the ralph source at
[`../../primitives/runners/ralph/ralph`](../../../../primitives/runners/ralph/ralph) and
[`../../primitives/runners/ralph/lib/core.py`](../../../../primitives/runners/ralph/lib/core.py); line
numbers are as of writing — grep to reconfirm if the source has moved.

## <a id="epic-label-hijack"></a>The epic-label hijack (biggest gotcha)

After ralph closes an issue it runs `_unlock_downstream` (`ralph` ~line 632),
which scans open issues and auto-adds `ready-for-agent` to any whose
`## Blocked by` references are **all closed** — UNLESS the issue already carries
a human label. The set is (`ralph` line 643):

```python
human_labels = {'ready-for-human', 'needs-triage', 'needs-info', 'wontfix'}
```

`epic` is **not** in that set, and it is **not** a hard-blocker either — the
eligibility engine's hard-blocker list (`ralph` line 705) is:

```
hard_blockers="needs-triage needs-info ready-for-human wontfix"
```

The engine only auto-skips container issues whose **title** starts with `PRD:`
or `prd:` (`ralph` line 700) — an `epic` **label** with an ordinary title is not
detected.

**Consequence:** a parent/epic tracker whose `## Blocked by` children are all
closed gets auto-relabeled `ready-for-agent`, ralph picks it, and tries to
implement the ENTIRE epic in one iteration — a huge sprawling diff, repeated
review-gate reopens, starving the real sliced children.

**Fix:** always give epic/parent tracker issues a human label (e.g.
`ready-for-human`) *in addition to* `epic`. That makes both the hard-blocker
check (line 705) and `_unlock_downstream` (line 649) skip them. Do this as part
of slicing, before the first loop.

## <a id="allow-risky"></a>Preflight, high-effort keywords, and `--allow-risky`

Preflight flags "high-effort" issues via `HIGH_EFFORT_KEYWORDS` (`core.py` line 35):

```python
HIGH_EFFORT_KEYWORDS = ["alembic", "generate-client", "migration"]
```

Any issue whose body **contains** one of these substrings (lowercased) is
flagged and preflight returns NO_GO without `--allow-risky` (`ralph` lines
557–563). This fires on **false positives** — an issue that merely mentions the
word "migration", even inside a filename like `MIGRATION_PLAYBOOK.md`, trips it.

Pass `--allow-risky` to proceed (turns NO_GO into `GO_WITH_WARNINGS`). This is
safe in an orchestrated batch because the **blocking Codex review gate** after
every commit is the real safety backstop — it reopens the issue with findings if
the diff is unsound. So `ralph loop --max N --allow-risky` is the normal
orchestration invocation.

## <a id="account-isolation"></a>Account isolation vs. the driver's own gh

ralph resolves its account from `~/.ralph/accounts.toml` by longest-prefix match
on the repo path (`_resolve_account`, `ralph` line 76) and exports an **isolated**
`GH_CONFIG_DIR` (plus `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `GH_HOST`). So ralph's
own `gh` calls are immune to the global "active" gh account.

**But your driver session's own direct `gh` calls use the global default.**
Another project or agent on the machine can flip that active account mid-run,
giving you "Could not resolve to a Repository" errors while ralph itself keeps
working fine. Mitigation:

- `gh auth switch --user <acct>` back before your direct `gh` calls, or
- rely on a directory-based `gh` wrapper function if one is installed, or
- prefer letting ralph do the gh work and only reading `ralph check` output.

Full isolation mechanism — isolated config dirs, keychain namespacing by
`sha256(CLAUDE_CONFIG_DIR)`, the legacy-vs-hashed Claude slot trap, and the
same-account OAuth refresh race — is documented in
[`../../primitives/runners/ralph/MULTI_ACCOUNT_SETUP.md`](../../../../primitives/runners/ralph/MULTI_ACCOUNT_SETUP.md).
The idempotent provisioner is
[`../../primitives/runners/ralph/setup-multi-account.sh`](../../../../primitives/runners/ralph/setup-multi-account.sh).

**Never run two sessions on the same Claude account concurrently** — e.g. an
interactive driver and a ralph loop both on `~/.claude`. The OAuth token refresh
race will log one of them out mid-run. If you must, give ralph its own
same-account `CLAUDE_CONFIG_DIR` so each has an independent token slot.

## <a id="one-branch"></a>One integration branch per batch

`main` is protected and ralph refuses to commit to a protected branch
(`ralph` line 842). Set both:

```bash
export RALPH_BASE_BRANCH=main
export RALPH_FEATURE_BRANCH=feature/whatever-integration
```

so ralph creates/uses one feature branch and every loop iteration accumulates
onto it — yielding a single review PR at the end. Keep the same
`RALPH_FEATURE_BRANCH` across all chained loops in the batch.

## <a id="slice-before-you-run"></a>Slice before you run

Big epics (especially greenfield ports) must be broken into dependency-chained
vertical slices **before** launching ralph. Each child issue should have:

- `## Parent` pointing at the tracker (see PRD convention in
  [`../../primitives/runners/ralph/CLAUDE.md`](../../../../primitives/runners/ralph/CLAUDE.md)),
- `## Blocked by #N` for its prerequisites,
- a brief that points at **concrete reference files by absolute path**.

ralph launches Claude with `--permission-mode bypassPermissions` (`ralph` line
1517), so the implementing agent can **read sibling repos on the same machine**
for reference — cite absolute paths in the brief and it will use them.

Keep the irreducible human work as separate `ready-for-human` residue issues:
code-signing certificates/secrets, real-OS install testing, real-device
verification. Slicing this way gives reviewable bounded diffs and keeps each
ralph iteration small.

The skills `to-vertical-issues` and `to-issues` automate this slicing.

## <a id="parallel-testing"></a>Safe parallel testing while ralph runs

ralph mutates the main checkout continuously. To let a human test a stable
snapshot without colliding, create a detached worktree pinned to a known-good
commit:

```bash
git worktree add --detach /path/to/snapshot <good-sha>
```

**PITFALL:** do NOT symlink `node_modules` from the main checkout into the
worktree. Turbopack (Next.js) rejects a `node_modules` symlink that points
outside the worktree root:

```
Symlink node_modules is invalid, it points out of the filesystem root
```

Do a real `bun install` inside the worktree instead — bun's global cache makes
it fast.

## <a id="mechanics"></a>Useful mechanics

- **`ralph check`** prints resolved account, claude config dir, codex home, gh
  config dir, feature branch, lock status, and the eligible `ready-for-agent`
  issue list (`ralph` lines 2040–2111). Run it to verify routing before every
  batch and to count remaining work between loops.

- **Stale auth marker.** ralph caches a "claude auth verified" marker at
  `/tmp/.ralph_claude_auth_<hash>` where `<hash>` is
  `sha256(CLAUDE_CONFIG_DIR)[:16]` (`core.py` line 267), valid for
  `RALPH_CLAUDE_AUTH_CACHE_TTL` seconds (default 300, `ralph` line 428). If a
  session is wrongly skipping auth re-verification, delete the marker to force a
  real check.

- **Resume a usage-exhausted run.** `ralph resume list` shows resumable
  interrupted runs; `ralph resume RUN_ID` retries one. When a background loop
  exits due to usage exhaustion, resume (or launch a fresh loop) rather than
  restarting from scratch.

- **The launch flags** ralph uses for the implementing agent are
  `--permission-mode bypassPermissions --print --output-format stream-json
  --verbose --no-session-persistence` (`ralph` line 1515). The
  `stream-json --verbose` combination is exactly why you must keep the loop's
  output in a log file and out of your context.
