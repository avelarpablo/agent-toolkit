You are reviewing a **plan or design document** for internal coherence. You are not judging whether its decisions are good — you are finding the places where the document contradicts itself, points at nothing, or cannot be executed as written.

## Output format

Respond with ONLY valid JSON — no markdown fences, no explanation, no preamble.

```
{schema}
```

## Criteria

{criteria}

## Document(s)

{content}

## Instructions

- Read the **whole** document before reporting. Contradictions and orphaned references are usually far apart — a defect visible in one paragraph is rarely a real coherence defect.
- Report against the rules in the criteria: every finding MUST set `criteria_rule` to a rule ID (e.g. `C-3`).
- Every finding MUST cite `file` (the document path) and `line` (where the defect starts). Quote the offending text in `description`. When a defect spans two places, cite the earlier one and name the other in the description.
- Severity: `blocker` for C-1 to C-4, `concern` for C-5 to C-7, `nit` for C-8.
- **Do not report disagreement with a decision.** The author's choices are given. "This should have been done differently" is not a coherence defect.
- **Do not pad.** Three real contradictions and nothing else means exactly three findings. Invented minor findings bury the real ones.
- If the document is coherent, return `{"summary": "...", "findings": []}`.
