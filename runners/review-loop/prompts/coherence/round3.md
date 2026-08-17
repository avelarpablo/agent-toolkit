You are producing the final consolidated coherence review of a **plan or design document**.

## Output format

Respond with ONLY valid JSON — no markdown fences, no explanation, no preamble.

```
{schema}
```

## Criteria

{criteria}

## Document(s)

{content}

## Round 1 findings

```json
{round1_findings}
```

## Round 2 findings (challenger)

```json
{round2_findings}
```

## Instructions

Produce the final list. This is what the author will act on, so it must be **decided**, not a transcript of the argument.

- **Drop** findings the challenger disputed with evidence you can confirm in the document.
- **Keep** findings both rounds agree on, and findings the challenger raised that hold up.
- **Adjudicate** genuine disagreements yourself by checking the document text. Do not include a finding you could not verify.
- Merge duplicates — the same defect found by both rounds is one finding.
- Set `"stance": "new"` on every surviving finding; this list stands alone.
- Order by severity: blockers first.
- In `summary`, state whether the document is internally coherent, and name the single most important defect if not.
