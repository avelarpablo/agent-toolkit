# Claude Code environment — one setup, every account

Make every Claude Code account (personal, shopstack, any future one) show the
**same information** and run the **same hooks**, from one version-controlled
source. A companion script,
[`setup-claude-env.sh`](./setup-claude-env.sh), provisions it idempotently.

This is the sibling of
[`runners/ralph/MULTI_ACCOUNT_SETUP.md`](../runners/ralph/MULTI_ACCOUNT_SETUP.md):
that one decides **which** account a project uses; this one makes every account
**look and behave alike** once selected.

---

## The problem

Each account is a separate `CLAUDE_CONFIG_DIR` with its own `settings.json`
(`~/.claude`, `~/.claude-shopstack`). Nothing keeps them in sync, so they drift:
one account gets a status line, hooks and a default model, the other silently
runs bare. Worse, the scripts they point at lived **inside the personal config
dir**, so the shopstack account depended on `~/.claude/` — untracked, on one
machine only, and invisible to this repo.

## The fix, in one line

Keep the scripts **in this repo**, keep the shared settings in one
`settings.base.json`, and let a script write both accounts' `settings.json`
from it.

```
settings.base.json ──▶ setup-claude-env.sh ──▶ every account's settings.json
                                           └─▶ managed ~/.zshrc alias block
```

---

## Layout

| Path | What it is |
| --- | --- |
| `settings.base.json` | Shared settings applied to every account. `__CLAUDE_ENV__` is replaced with this directory's absolute path at install time. |
| `setup-claude-env.sh` | Idempotent installer. `--dry-run` shows the diff without writing. |
| `statusline.sh` | The status line every account renders. |
| `bin/claude-bg` | Detail view of agent-started background tasks. Alias: `cbg`. |
| `bin/devports` | Detail view of every local dev server, agent-started or not. Alias: `devports`. |
| `hooks/postedit-review.sh` | `PostToolUse` — async Codex review after each edit. |
| `hooks/stop.sh` | `Stop` — structured Codex review of commits made during the session. |
| `hooks/review-schema.json` | Verdict schema for `stop.sh`. Lives next to the hook so the component is self-contained. |

## Setup

```bash
cd claude-env
./setup-claude-env.sh --dry-run   # inspect
./setup-claude-env.sh             # apply
source ~/.zshrc                   # pick up the aliases
```

For each account it links `<config-dir>/skills` at the shared library
`~/.agents/skills` (symlinks into this repo's `skills/`, so a skill written once
is available to every account), merges `settings.base.json` into
`<config-dir>/settings.json` (backing up to `settings.json.bak`), then writes the
managed `~/.zshrc` block.
Settings changes apply to **new** sessions; a running session keeps whatever it
started with.

Re-run it any time — it reports `already in sync` when there is nothing to do.

---

## What the status line shows

```
~/Dev/shopstack/discount-genie-core (main)
Claude Opus 5 │ Medium │ █░░░░░░░░░░░░░░ 7% 67.1k/1M
⬢ shopstack │ ▶ 1 bg http://localhost:8899
```

The URL is printed in full on purpose: terminals linkify it, so **cmd-click on
the status line opens the running app** — the closest thing a terminal has to a
start button. Two URLs at most, to keep the line short; `cbg` lists the rest.

When nothing is listening there is no URL to show, so the segment names the
first task instead of leaving a bare count — `▶ 2 bg · npm run dev +1` rather
than `▶ 2 bg`, which says nothing about what is actually running.

| Segment | Source |
| --- | --- |
| cwd + git branch | `workspace.current_dir`, `git` |
| model, effort | `model.id`, `effort.level` |
| context bar + **tokens** | `context_window.used_percentage`, `total_input_tokens`, `context_window_size` |
| **account** | derived from `transcript_path` |
| **background tasks** | `bin/claude-bg --short` |

The last two are not in the payload — they are derived. The details matter if
you ever change them:

**Account.** The payload has no account, organization or config-dir field, and
a status line script does **not** inherit `CLAUDE_CONFIG_DIR` (Claude Code sets
only `COLUMNS` and `LINES`). But `transcript_path` points inside the config dir
— `~/.claude-shopstack/projects/.../x.jsonl` — so the directory name identifies
the account exactly. Parsed generically: `~/.claude-<label>` renders as
`⬢ <label>`, plain `~/.claude` renders as `⬢ personal`. A third account labels
itself with no code change.

**Tokens.** `used_percentage` alone hides the ceiling, which matters when
accounts or models differ in context size. The absolute pair (`67.1k/1M`,
`126.4k/200k`) makes it explicit.

---

## `cbg` — what agents left running

```
$ cbg
PID      SESSION  ACCOUNT    PORT   UP    COMMAND
65283    this one shopstack  8899   8m    python3 -m http.server 8899 --bind 127.0.0.1
                                http://localhost:8899
                                cbg open 8899 · cbg logs 8899 · cbg stop 8899
87602    other    shopstack  -      3m    cd ~/Dev/shopstack/… && npm run dev
                                cbg open 87602 · cbg logs 87602 · cbg stop 87602
```

Answers "an agent started a server somewhere — which one, on what port, and
where are its logs", across every terminal and both accounts.

| Command | Does |
| --- | --- |
| `cbg` | list every task |
| `cbg open [port\|pid]` | open it in the browser |
| `cbg logs [port\|pid]` | follow its log |
| `cbg stop [port\|pid]` | terminate it |

The selector is optional when it is unambiguous — with a single server up,
`cbg open` needs no argument even if other tasks are running, because only
something listening can be opened. When several match, `cbg` lists the
candidates instead of guessing.

`cbg` does not **start** anything: that is the agent's job. It finds and acts on
what agents have already left running.

**How it detects them.** Nothing about background tasks appears in the status
line payload or anywhere on disk, so the process table is the only source of
truth. Every Bash tool call runs as a `zsh -c` that first sources a shell
snapshot from its config dir:

```
/bin/zsh -c source ~/.claude-shopstack/shell-snapshots/snapshot-zsh-…sh … && eval 'npm run dev' < /dev/null
```

That single argv gives everything: it proves the process is agent-started, the
path says which **account**, the snapshot filename identifies the **session**,
and the string inside `eval` is the **command as the agent typed it** (far more
readable than the resolved binary path on the child process).

Three non-obvious details, each of which cost a wrong first attempt:

1. **Key off the wrapper, not the process tree.** Walking up from a process to
   its `claude` pid seems natural but fails exactly when it matters: a detached
   background task is reparented to init when its session ends, and the trail
   is gone.
2. **Foreground and background calls are indistinguishable.** Same wrapper, and
   both have stdout redirected to a `tasks/*.output` file. So **age** is the
   discriminator — anything younger than `CLAUDE_BG_MIN_AGE` (default 10s) is a
   command passing through, not something left running. Raise it if transient
   calls from other sessions still surface.
3. **The log path comes from fd 1.** Claude Code points a task's stdout at its
   output file, so `lsof -d 1` recovers the log without knowing the task id.

The status line caches the short form for 5s, so a new task can take that long
to appear.

## `devports` — every local dev server

Complements `cbg`: shows servers **whoever** started, agent or human, with
Docker ports resolved to container names.

```
$ devports
PORT    PID      PROCESS    DIRECTORY
5433    99785    docker     container dental-clinic-db
        http://localhost:5433
```

It filters by process type and port range because macOS Control Center squats
5000 and 7000, and Spotify/Loom/Zed hold high ports — a naive listener dump is
mostly noise. Tune with `DEVPORTS_MAX_PORT` and `DEVPORTS_IGNORE`.

### What is *not* available

**Remote Control state.** There is no way to show whether the current session
has Remote Control on. Verified against a live session: the payload has 16
top-level keys and none of them is remote/control related; `session-env/<id>/`
is empty; and `.claude.json` carries only lifetime flags
(`hasUsedRemoteControl`, `remoteDialogSeen`) that say "you have used it before",
not "it is on now". Inferring it from the process's network connections is
possible in principle but not reliable — a `claude` process holds ~70
established connections, and a badge that says ON when it is off is worse than
no badge. If Claude Code adds a payload field, this is a two-line change.

### Inspecting the payload

To see exactly what a version of Claude Code passes in:

```bash
touch ~/.claude-statusline-capture     # capture on
# …let the status line render…
jq . "$TMPDIR/cl-payload-<session-id>.json"
rm ~/.claude-statusline-capture        # capture off
```

Keyed off a sentinel file because a status line script inherits no environment
from Claude Code beyond `COLUMNS` and `LINES` — an env var would never arrive.

---

## Changing things

**A shared setting** (model, effort, a hook) — edit `settings.base.json`, re-run
`./setup-claude-env.sh`. It reaches every account.

**A per-account setting** — set it directly in that account's `settings.json`.
Keys absent from the base are preserved on re-run; that is how shopstack keeps
`"tui": "fullscreen"` while personal does not. A key **present** in the base is
owned by the base and will be overwritten.

**A new account** — add a `label|~/.claude-<label>` line to the `ACCOUNTS` array
in `setup-claude-env.sh` (mirroring `setup-multi-account.sh`), and re-run. The
status line picks up the label with no further change.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| Status line unchanged | Settings apply to new sessions only — start one. |
| `cbg`/`devports` not found | `source ~/.zshrc`. |
| Status line blank or partial | Run it by hand: `echo '{}' \| sh statusline.sh`. Every segment is optional and is skipped when its field is absent, so a fresh session legitimately shows less. |
| Background task missing | Younger than `CLAUDE_BG_MIN_AGE`, or the 5s status line cache has not expired. |
| Hooks not firing | They shell out to `codex`; confirm it is on `PATH`. |

## Superseded files

The scripts previously lived in the personal config dir. Both accounts now read
this repo, so these are no longer used and are safe to delete once you are
happy with the setup:

```
~/.claude/statusline-command.sh
~/.claude/hooks/postedit-review.sh
~/.claude/hooks/stop.sh
~/.claude/review-schema.json
```
