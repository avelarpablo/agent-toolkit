---
name: status
description: Narrate development progress from the tracker — query the GitHub Project and issues (gh + GraphQL) and produce a standup-style report of what's in flight, plus the quality counter-metrics (cost per accepted change, escaped defects, human-rework rate) that keep a stage board honest. Same canonical state, no new data source. Use when the user wants a progress report, a standup, or to check how the pipeline is doing.
argument-hint: "[feature# or 'all'] — what to report on"
---

# status — progress from the one source of truth

Progress reporting is an agent task, not a human one. The pipeline already *produces* all the data —
issues + `stage:` labels + parent/child trees + the Project's `Status`/`Environment` fields. This
skill is a **view over that**, never a second source of truth: query it and narrate. No spreadsheet,
no separate board to keep in sync.

## The narrative

Query the Project and issues (`gh` + GraphQL) and produce a short report — e.g.:

> *3 features in flight: **A** in QA (2/3 slices merged), **B** in refactor, **C** blocked on #47.
> 2 awaiting your verification. 1 shipped to Production this week.*

Group by feature; for each, its stage (or the slice spread), what's blocking, and what needs a human.

## Throughput needs a counterweight

A stage board reports **movement**, and movement alone is a metric worth gaming — a pipeline that
merges slices fast while escaped defects climb looks *excellent* on it. So **always pair every
throughput number with a quality number**:

| Counter-metric | Query | Losing when |
|---|---|---|
| **Cost per accepted change** | of the loop's proposed changes, the fraction you accepted vs. reworked | acceptance **< ~50%** — you're doing the review work the loop was meant to remove |
| **Escaped defects** | `kind:bug` filed against a feature already past `stage:verify` | climbing — verification isn't catching enough |
| **Human-rework rate** | how often `needs:human` fires per feature | climbing — the loops stall more than they finish |

Report these **beside** the throughput, every time. A pipeline shipping fast and wrong is invisible on
the board alone; these are how it shows.

## Notes

- **`Status` is maintained by the writers, not this skill** — `status` only reads. (`log`→Ideas,
  producers→Shaping, orchestrator→In development, built-in→Done.)
- **Deployment** comes from the `Environment` field (CI-written, post-close) — read it for the
  "shipped to X" line.
