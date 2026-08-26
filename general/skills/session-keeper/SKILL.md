---
name: session-keeper
description: Schedule ralph ping commands throughout the day to keep Claude Code sessions alive, with optional night slots for real ralph loops. Use when user says "keep sessions alive", "session keeper", "schedule pings", "plan my day sessions", or invokes /session-keeper.
---

# session-keeper

Schedule `ralph ping` commands to keep Claude Code usage sessions alive throughout the day, then optionally schedule real ralph loops for overnight work.

## How it works

Claude Code sessions last ~5 hours. A `ralph ping` starts a minimal Claude invocation that resets the session counter. By scheduling pings every 5h02m, the user always has a fresh session available.

## Process

### 1. Gather inputs

Ask the user (skip any they provide upfront):

1. **Current session remaining** — e.g., "3h left", "just started", "about to expire"
2. **Active hours** — when they'll be working (e.g., "9am to 10pm")
3. **Night window** — free hours for real ralph loops (e.g., "11pm to 7am"), or "none"

### 2. Calculate the ping schedule

```
SESSION_DURATION = 5 hours
PING_GAP = 2 minutes (buffer after session expires)
INTERVAL = 5h02m = 302 minutes
```

**Algorithm:**
1. Parse current time and session remaining → compute when current session ends
2. First ping = session end + 2 minutes
3. Each subsequent ping = previous ping + 5h02m
4. Stop pinging when the next ping would land inside the night window (if night loops are planned) or after active hours end (if no night loops)
5. If night loops: leave the night window clear for real work

### 3. Ask about night loops (if night window provided)

Ask the user:
- Which issues or PRDs to run overnight?
- Any env vars needed? (e.g., `RALPH_FEATURE_BRANCH`, `RALPH_SKIP_CODEX`)
- How much gap between loops? (default: 4 hours per loop)

### 4. Generate commands

Output the full command list, ready to copy-paste:

```bash
# Session pings — [date]
ralph ping --schedule "YYYY-MM-DD HH:MM"
ralph ping --schedule "YYYY-MM-DD HH:MM"
...

# Night loops — [date] (if applicable)
RALPH_FEATURE_BRANCH=feature/xxx ralph once --issue NNN --schedule "YYYY-MM-DD HH:MM"
RALPH_FEATURE_BRANCH=feature/xxx ralph once --issue NNN --schedule "YYYY-MM-DD HH:MM"
```

### 5. Multi-day support

If the user wants coverage across multiple days:
- After the night window, resume pings from early morning (e.g., 4am or whenever the last night loop is expected to finish + 2min)
- Continue the ping chain through the next day's active hours
- Ask if they want another night window for day 2

## Edge cases

- **Session already expired:** First ping is "now + 2 minutes" or immediate (`ralph ping` without `--schedule`)
- **No night loops:** Pings run continuously through active hours, no gap
- **Overlapping times:** Warn if a night loop would collide with a ping
- **Next-day dates:** Use YYYY-MM-DD format — always include the date, never rely on "today"

## Example

User: "I have 2h left, active until 10pm, night loops from 11pm to 5am, then keep sessions going tomorrow until 10pm"

```
Current: 10:30 AM, session ends 12:30 PM

Pings:
  12:32 PM today
   5:34 PM today
  (10:36 PM would be in night window — stop)

Night loops (11:00 PM – 5:00 AM):
  11:00 PM — ralph once --issue 153
   3:00 AM — ralph once --issue 154

Resume pings after night:
   5:02 AM tomorrow
  10:04 AM tomorrow
   3:06 PM tomorrow
   8:08 PM tomorrow
  (next would be 1:10 AM — into night, stop)
```
