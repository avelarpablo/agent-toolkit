# Multi-account setup (gh + Claude), per-project auto-routing

Run different GitHub **and** Claude Code accounts per project directory, with
**zero manual switching** — automatically for ralph runs and for your own
terminal `gh`/`claude` commands. Two projects (and two ralph loops) in
different trees can run **at the same time** without fighting over a shared
"active account".

This captures a working setup and the non-obvious mechanics behind it. A
companion script, [`setup-multi-account.sh`](./setup-multi-account.sh),
provisions everything idempotently.

---

## The problem

`gh` and `claude` each keep **one global "active account"**:

- `gh` → `~/.config/gh/hosts.yml` has a single `user:` field. `gh auth switch`
  (or just working in another account's project) rewrites it. Every `gh` call
  anywhere then uses whatever was switched last — so a command in project A
  silently talks to account B.
- `claude` → one credential in the OS keychain for the default config dir.

Git push/pull is unaffected (it routes per-repo via SSH host aliases). Only the
**CLIs** have the single-global-switch design.

## The fix, in one line

Give each account its **own isolated config directory**, then **auto-select the
directory from the current path**. The account lives in a per-process env var
(`GH_CONFIG_DIR` / `CLAUDE_CONFIG_DIR`), not a shared global field — so nothing
can flip it, and concurrent runs never collide.

```
repo path ──▶ account map ──▶ isolated config dir ──▶ names ONE account ──▶ keychain token
```

Three layers select the directory:

| Layer | Covers | Mechanism |
| --- | --- | --- |
| `~/.ralph/accounts.toml` | ralph runs | ralph matches repo path → exports `GH_CONFIG_DIR` + `CLAUDE_CONFIG_DIR` |
| `gh` shell wrapper | manual `gh` in any terminal | function picks `GH_CONFIG_DIR` from `$PWD` |
| `claude` aliases | manual `claude` | `alias cm=…`, `csh=…` set `CLAUDE_CONFIG_DIR` |

---

## Part 1 — isolated gh config dirs

`gh` reads its config from `$GH_CONFIG_DIR` if set (default `~/.config/gh`).
Create one dir per account, each pinned to a single account:

```bash
mkdir -p ~/.config/gh-<label>
cp ~/.config/gh/config.yml ~/.config/gh-<label>/config.yml   # shared prefs
cat > ~/.config/gh-<label>/hosts.yml <<'EOF'
github.com:
    git_protocol: https
    users:
        <gh-username>:
    user: <gh-username>
EOF
chmod 600 ~/.config/gh-<label>/hosts.yml
```

**Why no token in the file:** `gh` stores tokens in the OS keychain keyed by
**account name**, not by config dir. `hosts.yml` only names the account; the
keychain hands over that account's token. So a fresh config dir works with **no
re-login** — as long as that account has logged in on this machine once
(`gh auth login`). Verify isolation:

```bash
GH_CONFIG_DIR=~/.config/gh-<label> gh api user -q .login    # prints <gh-username>
# ...and stays correct even after `gh auth switch` flips the global default.
```

## Part 2 — isolated Claude config dirs

`claude` reads `$CLAUDE_CONFIG_DIR` if set (default `~/.claude`). Everything —
credentials, settings, history, plugins — is isolated per dir.

**Claude is NOT like gh here.** Its keychain entry is namespaced by a
**sha256 of the `CLAUDE_CONFIG_DIR` path**:

```
Claude Code-credentials              ← legacy slot, used when the var is UNSET
Claude Code-credentials-<hash8>      ← used when CLAUDE_CONFIG_DIR is SET (even to ~/.claude)
```

Consequences that will bite you if unknown:

1. **You must log in once per config dir** — there's no shared token to inherit
   (unlike gh). `CLAUDE_CONFIG_DIR=~/.claude-<label> claude` then `/login`.
2. **Legacy vs hashed slot mismatch.** A plain `claude` login (var unset) writes
   the legacy slot; ralph and the aliases set `CLAUDE_CONFIG_DIR` explicitly and
   read the **hashed** slot. If you log in one way and run the other, auth
   "fails" despite a successful login. **Fix:** always log in *with the var set*
   the same way it's consumed — e.g. `CLAUDE_CONFIG_DIR=~/.claude claude`
   (the `cm` alias), not bare `claude`.
3. **Different config dirs → different slots → true simultaneous isolation.**
   Two accounts can be logged in at once; neither clobbers the other.

Check any dir's account/auth:

```bash
CLAUDE_CONFIG_DIR=~/.claude-<label> claude auth status
```

### Same-account concurrency caveat

Do **not** run two sessions on the *same* account at once (e.g. an interactive
`claude` **and** a ralph loop, both on `~/.claude`). They share one OAuth
credential; when one refreshes the token it rotates the refresh token out from
under the other, expiring it. *Different* accounts in parallel is fine. If you
need same-account parallelism, give the second one its **own** config dir logged
into the **same** account (e.g. `~/.claude-ralph`) — separate slot, no race.

## Part 3 — ralph routing (`~/.ralph/accounts.toml`)

ralph's `_resolve_account` matches the repo path against each `path` (longest
prefix wins) and exports the dirs for its run. Dormant until the file exists.

```toml
[accounts.<label>]
path = "~/Dev/<tree>"                       # repos under here use this account
gh_config_dir = "~/.config/gh-<label>"
claude_config_dir = "~/.claude-<label>"     # omit to use the default ~/.claude
# codex_home = "~/.codex-<label>"           # optional, same idea
```

## Part 4 — manual-terminal auto-routing (`~/.zshrc`)

A `gh` wrapper function selects the config dir from `$PWD`, mirroring
`accounts.toml`. Plus per-account `claude` aliases.

```bash
# >>> gh account auto-routing >>>
gh() {
  local ghdir=""
  case "$PWD/" in
    "$HOME/Dev/shopstack/"*) ghdir="$HOME/.config/gh-shopstack" ;;
    "$HOME/Dev/personal/"*)  ghdir="$HOME/.config/gh-avelarpablo" ;;
  esac
  if [[ -n "$ghdir" ]]; then GH_CONFIG_DIR="$ghdir" command gh "$@"; else command gh "$@"; fi
}
# <<< gh account auto-routing <<<

# >>> claude accounts >>>
alias cm="CLAUDE_CONFIG_DIR=~/.claude claude"
alias csh="CLAUDE_CONFIG_DIR=~/.claude-shopstack claude"
# <<< claude accounts <<<
```

`command gh` bypasses the wrapper when a script needs the raw binary.

---

## Verification checklist

```bash
# gh: right account per tree, immune to a flipped global default
( cd ~/Dev/personal/<any-repo>  && gh api user -q .login )   # personal account
( cd ~/Dev/shopstack/<any-repo> && gh api user -q .login )   # shopstack account

# claude: each dir authenticates independently
CLAUDE_CONFIG_DIR=~/.claude           claude auth status
CLAUDE_CONFIG_DIR=~/.claude-shopstack claude auth status

# ralph: resolves per tree (account + gh config + claude line)
( cd ~/Dev/personal/<any-repo>  && ralph check | grep -E 'account|gh config|claude' )
( cd ~/Dev/shopstack/<any-repo> && ralph check | grep -E 'account|gh config|claude' )
```

## Prerequisites

- Each GitHub account logged in once: `gh auth login` (populates the keychain).
- Each Claude account logged in once **into its config dir**:
  `CLAUDE_CONFIG_DIR=~/.claude-<label> claude` → `/login`.
