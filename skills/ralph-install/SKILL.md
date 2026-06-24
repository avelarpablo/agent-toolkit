---
name: ralph-install
description: Install ralph AFK agent system on this machine. Provisions ~/.ralph/ binary + prompts, Claude Code hooks for inline + session-end Codex review, and (optionally) per-account isolation for users with multiple GitHub/Claude/Codex accounts. Use when user says "install ralph", "set up ralph", "make this machine ralph-ready", or "/ralph-install".
---

# ralph-install

Provision the ralph AFK agent system. One skill = full system reproducible on any machine.

## What ralph is

Autonomous coding loop. Picks GitHub issue labeled `ready-for-agent` -> implements w/ TDD -> commits -> closes -> Codex reviews. Run `ralph once` or `ralph loop`.

## Architecture

- **Global**: `~/.ralph/bin/ralph` (binary), `~/.ralph/prompt.md` (universal agent instructions), Claude Code hooks (`PostToolUse` inline review, `Stop` session-end review), `review-schema.json`
- **Per-repo**: `ralph/prompt.md` (test command only)
- **Per-account** (optional): isolated `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `GH_CONFIG_DIR` per zone

## Process

### 1. Detect

Check installed tools + existing state. Report findings before asking.

```bash
command -v claude && claude --version
command -v codex && codex --version
command -v gh && gh --version
ls -d ~/.claude ~/.claude-* 2>/dev/null
ls -d ~/.codex ~/.codex-* 2>/dev/null
ls -d ~/.config/gh ~/.config/gh-* 2>/dev/null
ls -d ~/.ralph 2>/dev/null
```

Required: `claude`, `gh`. Recommended: `codex` (hooks become no-ops without it; warn but proceed).

### 2. Interview

Ask only what cannot be inferred. Use AskUserQuestion. Adaptive — skip questions answered by detection.

**Q1 — Multi-account?** (skip if no `~/.claude-*` / `~/.config/gh-*` dirs detected; default single-account)
- Single account (default): one `~/.claude`, one `~/.codex`, one `~/.config/gh`
- Multi-account: separate dirs per zone (work/personal/etc.)

**Q2 — Repo zones** (only if multi-account):
- Map each zone to dir + Claude dir + Codex dir + gh dir/host
- Answers generate `~/.ralph/accounts.toml` entries
- Example: `~/work-repos/` -> work (`~/.claude`, `~/.codex`, `gh_host=github.example.com`)

**Q3 — API config** (only if user has corporate Claude gateway, e.g. internal API key helper):
- Default: standard Anthropic API (no `apiKeyHelper`, no `ANTHROPIC_BASE_URL`)
- Custom: ask for `apiKeyHelper` cmd + `ANTHROPIC_BASE_URL` + `ANTHROPIC_MODEL`

### 3. Generate

Write all files inline from this skill. No external deps. Templates in `assets/`:

- `assets/ralph` -> `~/.ralph/bin/ralph` (chmod +x). Same binary for single and multi-account — routing is config-driven via `~/.ralph/accounts.toml`.
- `assets/lib/state.sh` -> `~/.ralph/lib/state.sh` (per-iteration JSON state tracking)
- `assets/lib/footer.sh` -> `~/.ralph/lib/footer.sh` (no-op stubs; footer removed)
- `assets/ralph-diag` -> `~/.ralph/bin/ralph-diag` (chmod +x, troubleshooting tool)
- `assets/prompt.md` -> `~/.ralph/prompt.md` (universal, identical for all)
- `assets/review-schema.json` -> `~/.claude/review-schema.json` (+ each `~/.claude-*/` if multi-account)
- `assets/postedit-review.sh` -> `~/.claude*/hooks/postedit-review.sh` (chmod +x)
- `assets/stop.sh` -> `~/.claude*/hooks/stop.sh` (chmod +x)
- `assets/settings.json.template` -> merged into existing `~/.claude*/settings.json` (preserve user overrides; only add hooks block + apiKeyHelper if missing)

### 4. PATH

Ensure `~/.ralph/bin` in PATH. Check `~/.zshrc` / `~/.bashrc`. Append if missing:

```bash
export PATH="$HOME/.ralph/bin:$PATH"
```

### 5. Verify

```bash
ralph check    # in current repo
```

Report success + next step: `ralph init` for current repo, then file issues w/ `ready-for-agent` label.

## Single vs multi-account: what changes

| File | Single | Multi |
|------|--------|-------|
| `~/.ralph/bin/ralph` | Identical binary — uses defaults (bare `gh`, `~/.claude`, `~/.codex`) | Same binary — reads `~/.ralph/accounts.toml` for per-zone routing |
| `~/.ralph/accounts.toml` | Not created (defaults apply) | Generated from interview answers |
| Hooks | only `~/.claude/hooks/` | also `~/.claude-*/hooks/` w/ correct `CODEX_HOME` |
| `review-schema.json` | only `~/.claude/` | one per `~/.claude*/` |
| `gh` routing | bare `gh` | `GH_HOST` or `GH_CONFIG_DIR` per zone (from config) |

## Hard rules

- Never overwrite existing `settings.json` blindly. Read -> merge hooks block -> write. If conflict, ask.
- Never write API keys. `apiKeyHelper` is a command name; user supplies separately.
- `~/.ralph/prompt.md` is identical everywhere. Repo-specific content goes in `ralph/prompt.md` via `ralph init`.
- Idempotent. Re-running skill must not duplicate hooks or PATH entries.

## After install

Per-repo onboarding:
```bash
cd <repo>
ralph init    # interactive: asks for test cmd, creates GitHub labels
ralph check
ralph loop
```

## Assets

Source-of-truth file content lives in `assets/` next to this SKILL.md. When updating ralph behavior, edit the asset files — re-running the skill on any machine reprovisions to match.
