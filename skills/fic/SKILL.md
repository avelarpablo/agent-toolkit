---
name: fic
description: Run any open-ended piece of work under Frequent Intentional Compaction — a per-topic working file with a live resume header, checkpoint-as-you-go, and loss-free compaction, so a fresh session can pick the work up from the file alone. Use when starting something open-ended whose size is unknown, when a session is getting long and you want to compact without losing state, or to resume earlier work by slug. Triggers: "/fic", "start a FIC session", "resume <slug>", "let's start fresh", "this session is getting long", "checkpoint this", "compact and hand off".
argument-hint: "<slug> — the topic to start or resume"
---

# FIC — the general session

The catch-all profile of the [FIC protocol](PROTOCOL.md): "I'm starting something open-ended and
don't know how big it is." It keeps generic work resumable with no ceremony, and it **graduates** —
because every FIC-aware skill shares this file format, re-entering a specific skill later picks up
the same session.

**Read [PROTOCOL.md](PROTOCOL.md) before running this skill.** It is the contract; this file is only
the generic profile's parameters and flow.

## Profile

| Parameter | Value |
|---|---|
| dotdir | `.fic/` |
| resume command | `/fic <slug>` |
| checkpoint | any decision, finding, dead end, or user answer that settles something |
| promotion | when work crystallizes into a deliverable, publish it to the issue tracker |

```bash
FIC="$(command -v fic || echo "$HOME/.agents/skills/fic/fic")"
```

## Flow

### 1. Open or resume the session

If the user gave a slug, use it. Otherwise derive a short kebab-case one from the topic and tell them
what you picked — they will retype it to resume.

```bash
"$FIC" init <slug> --dir .fic --skill fic --resume-cmd "/fic <slug>" --title "<topic>"
```

`init` is idempotent. If it reports the session already exists, this is a **resume**:

```bash
"$FIC" resume <slug>
```

Read the header, state the `Next step` back to the user in one line, and continue from there. Do not
re-derive what the log already settled; pull `--full` only if you genuinely need the detail.

If the user asks to resume but gives no slug, run `"$FIC" list` and offer what's there.

### 2. Work, checkpointing as you go

```bash
"$FIC" checkpoint <slug> "chose X over Y because <evidence>"
```

Every decision, the moment it lands — never batched at the end. Record killed alternatives and dead
ends too; they are what stops a resumed session from re-treading old ground.

Keep the next step honest as the work moves:

```bash
"$FIC" header <slug> --next "…"
```

Push heavy research and codebase sweeps into **subagents** and checkpoint only what they return.

### 3. Compact when the session gets long

On the user's cue ("let's start fresh"), at a natural phase boundary, or when the checkpoint nudge
fires — refresh the whole header first, then:

```bash
"$FIC" header <slug> --progress "…" --next "…" --open "…" --pointers "…"
"$FIC" compact <slug>
```

`compact` refuses while any header field is empty. Give the user the printed resume command and stop
— a fresh session continues from the file alone.

### 4. Promote what must outlive the topic

The `.fic/` directory is gitignored scratch. Anything durable — a decision worth an ADR, a spec worth
an issue — gets published to the tracker, with a pointer left in `--pointers`.

## Graduating to a specific skill

If a generic session turns out to be a grill, a verification, or a design doc, hand it to the skill
that owns that shape. The working-file format is shared, so point the specific skill at the existing
session rather than starting a second one — carry the log across, keep one file per topic.
