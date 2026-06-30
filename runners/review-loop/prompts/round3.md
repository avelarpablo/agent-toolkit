You are producing the final consolidated code review.

## Output format

Respond with ONLY valid JSON — no markdown fences, no explanation, no preamble.

```
{schema}
```

## Criteria

{criteria}

## Diff

```diff
{diff}
```

## Round 1 findings (initial review)

```json
{round1_findings}
```

## Round 2 findings (challenge)

```json
{round2_findings}
```

## Instructions

Produce the definitive findings list by resolving the adversarial exchange:

- **KEEP** findings that both reviewers agree on. Set `"stance": "agree"`.
- **WITHDRAW** findings that were convincingly disputed. Do NOT include them — they are dead.
- **INCLUDE** new findings from the challenger that are valid. Set `"stance": "new"`.
- **RESOLVE** severity disagreements — pick the severity supported by stronger evidence.

Every finding in your output must have `criteria_rule`, `file`, and `line`.

The final list should be the minimum set of real, actionable findings. Prefer precision over volume.
