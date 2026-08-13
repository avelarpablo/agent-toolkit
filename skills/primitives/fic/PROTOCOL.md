# The FIC protocol

**Frequent Intentional Compaction.** Agent performance degrades past roughly half a context window,
so long-running work must be able to survive a restart without losing anything. FIC is how.

This file is the **shared contract**. It is not per-skill best practice anyone has to remember — it
is one protocol that every long-running skill implements *identically*, through the `fic` script in
this directory. Skills differ only in **what** they record, never in **how** FIC works.

> **A skill that holds its state only in the conversation is non-compliant.** The conversation is
> the one thing guaranteed not to survive.

Spec: [`docs/PROCESS.md` → FIC — context management](../../../docs/PROCESS.md).

---

## Calling the script

```bash
FIC="$(command -v fic || echo "$HOME/.agents/skills/fic/fic")"
```

`~/.agents/skills/fic/fic` is where `toolkit sync` symlinks it. Inside this repo it is also at
`skills/fic/fic`. Run `"$FIC" help` for the full command surface.

---

## The four-part contract

### 1. Working file — standard location and format

On start, open a per-topic working file:

```bash
"$FIC" init <slug> --dir <dotdir> --skill <skill-name> --resume-cmd "/<skill> <slug>" --title "<title>"
```

- **`<dotdir>`** is the skill's own: `.grill/`, `.verify/`, `.wayfind/`, `.fic/` (generic).
- **`<slug>`** is short, kebab-case, and typeable — the human retypes it to resume.
- `init` is **idempotent**: on an existing session it prints the path and tells you to resume, so
  "start" and "resume" are the same call. You never have to check first.
- The dotdir is added to `.gitignore` automatically. Working files are scratch, never commits.

### 2. A live resume header, always current

The header leads with a **copy-pasteable resume command** — this is the whole point. It fixes the
"I made a handoff and didn't know what to tell the next session" problem.

```markdown
## Resume
▶ To resume: start a new session and run  `/fic <slug>`
  (or: "continue the FIC session at .fic/<slug>/progress.md")
- **Progress so far:** …
- **Next step:** …
- **Open threads / undecided:** …
- **Pointers:** <issue, prior docs, artifacts>
```

Update it with `fic header`; only the fields you pass change:

```bash
"$FIC" header <slug> --progress "…" --next "…" --open "…" --pointers "…"
```

Refresh **`--next` whenever the next step actually changes**, and all four before any compaction.
A stale header is a lossy handoff — `fic compact` refuses to run while any field is still empty.

### 3. Checkpoint-as-you-go — hard requirement

Write each decision or finding **the moment it lands**, not in a batch at the end:

```bash
"$FIC" checkpoint <slug> "D-003: LRU over TTL — measured 3x hit rate on the replay set"
printf '%s\n' "$long_finding" | "$FIC" checkpoint <slug> -
```

This is what actually guarantees safety. Compaction is then always loss-free and the final flush is
tiny — because there is nothing left to flush. **Get this rock-solid before worrying about
triggers.** A session that checkpoints faithfully survives even an unplanned death; one that
compacts on a perfect schedule but batches its writes does not.

Checkpoint-worthy: a decision and its rationale, a killed alternative and why, a verified fact about
the code, a dead end (so it isn't re-explored), a user answer that settles a question. Not
checkpoint-worthy: narration, restating the plan, or anything already published to the tracker.

### 4. Resume & compact — identical everywhere

**Resume.** Re-invoke the skill with the topic. It finds the working file and loads the **header**,
not the transcript:

```bash
"$FIC" resume <slug>          # the header — the cheap re-entry
"$FIC" resume <slug> --full   # the whole file, when the log actually matters
"$FIC" list                   # every session in this repo, newest first
```

Read the header first and start work from `Next step`. Reach for `--full` only when the log's detail
is genuinely needed — pulling the whole file back in defeats the purpose.

**Compact.**

```bash
"$FIC" compact <slug>
```

It verifies the header is complete, stamps a compaction marker, and prints the resume instructions.
Then tell the user to start a fresh session and run the printed command. Nothing else carries over —
that is the point, and it is safe precisely because of rule 3.

---

## When to compact

Self-measured context usage is **not reliable** — an agent cannot introspect its own token count.
So the triggers are ordered by how much they can be trusted:

1. **On demand (primary).** The user says "let's start fresh", or you are about to do something
   context-expensive (a large file sweep, a long tool output) with a full session behind you.
2. **Heuristic (secondary).** `fic checkpoint` nudges every 10 entries. Other honest signals: many
   large files read, a long tool-output run, an obvious phase boundary in the work. Treat the nudge
   as a prompt to refresh the header — the cheap, always-correct response — and to consider
   compacting.
3. **Self-assessed proactivity (best-effort only).** If the harness surfaces a real usage signal,
   use it. Never build the protocol's safety on it.

**Never block work waiting for a trigger.** The discipline is rule 3; the triggers are convenience.

---

## Layered state — what goes where

| Lives for | Goes to | Examples |
|---|---|---|
| **Across sessions** (durable) | the **issue tracker** | PRDs, design docs, verification reports, stage labels |
| **Within a session** (scratch) | the **working file** | in-flight decisions, evidence, dead ends, next step |
| **Across stages** | the **published artifact** | the next skill reads the PRD/design doc, never the prior transcript |

When something in the working file crystallizes, **promote it** to the tracker and leave a pointer
behind. The working file is disposable by design; anything that must outlive the topic must leave it.

**Offload to subagents** — the strongest single lever. Run research and codebase search in isolated
subagents that return only findings. The driver's context stays clean and the findings get
checkpointed.

---

## Implementing FIC in a skill

A FIC-aware skill sets four parameters and inherits everything else:

| Parameter | Example |
|---|---|
| dotdir | `.grill/` |
| resume command | `/grill <slug>` |
| what counts as a checkpoint | a resolved question + its evidence |
| what gets promoted, and where | the synthesized PRD → a tracker issue |

Then in the skill body:

1. **On start** — `fic init` with those parameters (idempotent, so it doubles as resume). If it
   reports an existing session, `fic resume` and continue from `Next step` instead of starting over.
2. **During** — `fic checkpoint` at every decision; `fic header --next` whenever the next step moves.
3. **On compact** — refresh the full header, `fic compact`, hand the user the resume command.

### Compliance checklist

- [ ] Working file opened via `fic init` before any real work
- [ ] Every decision checkpointed at the moment it lands, not batched
- [ ] `Next step` never stale
- [ ] A fresh session can resume from the working file **alone** — no transcript
- [ ] Durable outcomes promoted to the tracker, not left in the dotdir
