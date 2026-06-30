#!/usr/bin/env python3
"""review-loop/lib/helpers.py — helpers for the review-loop runner.

Usage from bash:  python3 "$LIB" <subcommand> [args...]
"""
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


def strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def parse_claude_envelope(raw: str) -> tuple[dict | None, str | None]:
    """Extract model result from claude --output-format json envelope.

    Returns (parsed_json, error_message).
    """
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"envelope parse error: {e}"

    if envelope.get("is_error"):
        return None, f"claude error: {envelope.get('result', 'unknown')}"

    result_text = envelope.get("result", "")
    stripped = strip_code_fences(result_text)

    try:
        return json.loads(stripped), None
    except json.JSONDecodeError:
        return _fallback_finding(result_text), "unparseable JSON, wrapped as raw finding"


def _fallback_finding(raw_text: str) -> dict:
    return {
        "summary": "Round produced unparseable output — raw text included as finding.",
        "findings": [
            {
                "severity": "concern",
                "criteria_rule": "unparsed",
                "description": raw_text[:2000],
                "file": "unknown",
                "line": 0,
                "stance": "new",
            }
        ],
    }


def _load_criteria(path: str) -> str:
    p = Path(path)
    if p.is_file():
        return p.read_text()
    if p.is_dir():
        parts = []
        for f in sorted(p.glob("*.md")):
            parts.append(f"# {f.name}\n\n{f.read_text()}")
        if not parts:
            print(f"error: no .md files in criteria directory: {path}", file=sys.stderr)
            sys.exit(1)
        return "\n\n---\n\n".join(parts)
    print(f"error: criteria path not found: {path}", file=sys.stderr)
    sys.exit(1)


# ── Subcommands ─────────────────────────────────────────────────────────────


def cmd_load_criteria(args):
    """Load and concatenate criteria from file or directory."""
    print(_load_criteria(args.path))


def cmd_parse_claude(args):
    """Parse claude --output-format json envelope, write extracted JSON to output file."""
    raw = sys.stdin.read()
    data, warning = parse_claude_envelope(raw)
    if warning:
        print(f"warning: {warning}", file=sys.stderr)
    if data is None:
        data = _fallback_finding(raw)
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)


def cmd_build_prompt(args):
    """Assemble a round prompt from template + criteria + diff + prior findings."""
    template = Path(args.template).read_text()
    criteria = _load_criteria(args.criteria)
    diff = sys.stdin.read()
    schema = Path(args.schema).read_text().strip()

    prompt = template.replace("{schema}", schema)
    prompt = prompt.replace("{criteria}", criteria)
    prompt = prompt.replace("{diff}", diff)

    if args.prior:
        for i, prior_file in enumerate(args.prior):
            content = Path(prior_file).read_text().strip()
            round_num = i + 1
            prompt = prompt.replace(f"{{round{round_num}_findings}}", content)
        if len(args.prior) == 1:
            prompt = prompt.replace("{prior_findings}", Path(args.prior[0]).read_text().strip())

    print(prompt)


def cmd_assemble(args):
    """Assemble round JSON files into final Markdown artifact."""
    rounds = []
    reviewers = []
    for i, rf in enumerate(args.round_files):
        data = json.loads(Path(rf).read_text())
        rounds.append(data)
        reviewers.append("Claude" if i % 2 == 0 else "Codex")

    all_findings = _merge_findings(rounds, reviewers)

    blockers = [f for f in all_findings if f["severity"] == "blocker"]
    concerns = [f for f in all_findings if f["severity"] == "concern"]
    nits = [f for f in all_findings if f["severity"] == "nit"]
    withdrawn = [f for f in all_findings if f.get("_withdrawn")]

    active = [f for f in all_findings if not f.get("_withdrawn")]
    blockers = [f for f in active if f["severity"] == "blocker"]
    concerns = [f for f in active if f["severity"] == "concern"]
    nits = [f for f in active if f["severity"] == "nit"]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Code Review — {args.target} | {now}",
        "",
        f"**Criteria:** `{args.criteria}`  ",
        f"**Diff:** {args.target}  ",
        f"**Rounds:** {len(rounds)} ({' -> '.join(reviewers)})",
        "",
        "---",
        "",
    ]

    lines += _render_section("Blockers", blockers, rounds, reviewers)
    lines += _render_section("Concerns", concerns, rounds, reviewers)
    lines += _render_section("Nits", nits, rounds, reviewers)
    lines += _render_withdrawn(withdrawn)
    lines += _render_summaries(rounds, reviewers)

    output = "\n".join(lines)
    Path(args.output).write_text(output)
    print(args.output)


def _finding_key(f):
    return (f.get("file", ""), f.get("line", 0), f.get("criteria_rule", ""))


def _merge_findings(rounds, reviewers):
    """Merge findings across rounds, tracking stance evolution."""
    findings = []
    seen_keys = set()

    for f in rounds[0].get("findings", []):
        entry = dict(f)
        entry["_history"] = [(0, reviewers[0], f.get("stance", "new"))]
        entry["_withdrawn"] = False
        findings.append(entry)
        seen_keys.add(_finding_key(f))

    for round_idx in range(1, len(rounds)):
        round_data = rounds[round_idx]
        for f in round_data.get("findings", []):
            stance = f.get("stance", "new")
            ref = f.get("references_finding", "")

            matched = _find_referenced(findings, ref, f) if (ref or stance != "new") else None

            if matched:
                matched["_history"].append(
                    (round_idx, reviewers[round_idx], stance)
                )
                if stance == "dispute":
                    matched["_dispute_reason"] = f.get("description", "")
                if f.get("severity") and f["severity"] != matched["severity"]:
                    matched["_severity_changed"] = (matched["severity"], f["severity"])
            else:
                key = _finding_key(f)
                if key in seen_keys:
                    existing = next((e for e in findings if _finding_key(e) == key), None)
                    if existing:
                        existing["_history"].append(
                            (round_idx, reviewers[round_idx], stance or "agree")
                        )
                        continue
                entry = dict(f)
                entry["_history"] = [(round_idx, reviewers[round_idx], stance or "new")]
                entry["_withdrawn"] = False
                findings.append(entry)
                seen_keys.add(key)

    if len(rounds) >= 3:
        final_findings = rounds[-1].get("findings", [])
        final_keys = {_finding_key(f) for f in final_findings}

        for entry in findings:
            if _finding_key(entry) not in final_keys:
                entry["_withdrawn"] = True

    return findings


def _find_referenced(findings, ref, current_finding=None):
    if ref:
        ref_lower = ref.lower()
        for f in findings:
            rule = f.get("criteria_rule", "").lower()
            if rule and (rule in ref_lower or ref_lower in rule):
                return f
            fpath = f.get("file", "").lower()
            if fpath and fpath in ref_lower:
                return f

    if current_finding:
        key = _finding_key(current_finding)
        for f in findings:
            if _finding_key(f) == key:
                return f

    return None


def _render_section(title, findings, rounds, reviewers):
    if not findings:
        return [f"## {title} (0)", "", "_None._", "", "---", ""]

    lines = [f"## {title} ({len(findings)})", ""]
    for i, f in enumerate(findings, 1):
        lines.append(f"### {i}. {f.get('criteria_rule', 'N/A')} — `{f.get('file', '?')}:{f.get('line', '?')}`")
        lines.append("")
        lines.append(f.get("description", ""))
        lines.append("")

        history = f.get("_history", [])
        if len(history) > 1:
            lines.append("| Round | Reviewer | Stance |")
            lines.append("|-------|----------|--------|")
            for round_idx, reviewer, stance in history:
                lines.append(f"| {round_idx + 1} | {reviewer} | {stance} |")
            lines.append("")

    lines += ["---", ""]
    return lines


def _render_withdrawn(findings):
    if not findings:
        return ["## Withdrawn (0)", "", "_None._", "", "---", ""]

    lines = [f"## Withdrawn ({len(findings)})", ""]
    lines.append("_Findings disputed and withdrawn during the review._")
    lines.append("")
    for i, f in enumerate(findings, 1):
        lines.append(f"### {i}. ~~{f.get('criteria_rule', 'N/A')} — `{f.get('file', '?')}:{f.get('line', '?')}`~~")
        lines.append("")
        lines.append(f.get("description", ""))
        if f.get("_dispute_reason"):
            lines.append("")
            lines.append(f"**Disputed:** {f['_dispute_reason'][:200]}")
        lines.append("")

    lines += ["---", ""]
    return lines


def _render_summaries(rounds, reviewers):
    labels = {0: "Initial Review", 1: "Challenge", 2: "Convergence"}
    lines = ["## Round Summaries", ""]
    for i, (rd, rev) in enumerate(zip(rounds, reviewers)):
        label = labels.get(i, f"Round {i + 1}")
        lines.append(f"### Round {i + 1} ({rev} — {label})")
        lines.append("")
        lines.append(rd.get("summary", "_No summary._"))
        lines.append("")
    return lines


# ── CLI dispatch ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="helpers.py")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("load-criteria")
    p.add_argument("path")

    p = sub.add_parser("parse-claude")
    p.add_argument("--output", required=True)

    p = sub.add_parser("build-prompt")
    p.add_argument("--template", required=True)
    p.add_argument("--criteria", required=True)
    p.add_argument("--schema", required=True)
    p.add_argument("--prior", nargs="*")

    p = sub.add_parser("assemble")
    p.add_argument("--round-files", nargs="+", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--criteria", required=True)
    p.add_argument("--output", required=True)

    args = parser.parse_args()
    cmds = {
        "load-criteria": cmd_load_criteria,
        "parse-claude": cmd_parse_claude,
        "build-prompt": cmd_build_prompt,
        "assemble": cmd_assemble,
    }
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
