#!/usr/bin/env python3
"""ralph/lib/core.py — unified helper for ralph-core.

Replaces all inline python3 calls and separate Python files (journal.py,
preflight.py, sched_meta.py) with a single dispatch point.

Usage from bash:  python3 "$LIB" <subcommand> [args...]
"""
import os
import re
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ── Constants ────────────────────────────────────────────────────────────────

EXHAUSTION_PATTERNS = [
    "usage limit",
    "session limit",
    "rate limit",
    "quota exceeded",
    "billing",
    "too many requests",
    "try again later",
    "temporarily unavailable",
]

EXHAUSTION_STATUS_CODES = {429}

RESUMABLE_STATUSES = {"usage_exhausted", "agent_failed", "standby"}

HIGH_EFFORT_KEYWORDS = ["alembic", "generate-client", "migration"]

CROSS_REPO_KEYWORDS = json.loads(os.environ.get("RALPH_CROSS_REPO_KEYWORDS", "{}")) or {}

# ── Utility ──────────────────────────────────────────────────────────────────

def _atomic_write_json(path, data):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _get_nested(data, key):
    if "." in key:
        outer, inner = key.split(".", 1)
        return (data.get(outer) or {}).get(inner, "")
    return data.get(key, "")


def _format_val(val):
    if isinstance(val, bool):
        return "1" if val else "0"
    if val is None:
        return ""
    return str(val)

# ── Subcommands ──────────────────────────────────────────────────────────────

def cmd_json_get(args):
    """Read fields from a JSON file, tab-separated output."""
    try:
        data = json.load(open(args.file))
    except Exception:
        print("\t".join("" for _ in args.keys))
        return
    print("\t".join(_format_val(_get_nested(data, k)) for k in args.keys))


def cmd_json_stdin(args):
    """Read JSON from stdin, extract fields, tab-separated output."""
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("\t".join("" for _ in args.keys))
        return
    print("\t".join(_format_val(_get_nested(data, k)) for k in args.keys))


def cmd_json_build(args):
    """Build a JSON object from key=value pairs. Types: int if numeric, null, bool."""
    data = {}
    for kv in args.pairs:
        if "=" not in kv:
            continue
        key, val = kv.split("=", 1)
        if val == "null" or val == "":
            data[key] = None
        elif val in ("true", "false"):
            data[key] = val == "true"
        else:
            try:
                data[key] = int(val)
            except ValueError:
                data[key] = val
    print(json.dumps(data))


def cmd_md_refs(args):
    """Extract issue #N references from a named markdown section. Reads stdin."""
    body = sys.stdin.read()
    pattern = rf"## {re.escape(args.section)}\n(.*?)(?:\n## |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    if not m:
        return
    for num in re.findall(r"#(\d+)", m.group(1)):
        print(num)


def cmd_prd_filter(args):
    """Filter issues JSON (stdin) for PRD children. Output: num\\x1ftitle\\x1flabels\\x1fbody\\x1e per record."""
    data = json.load(sys.stdin)
    prd = args.prd_num
    data.sort(key=lambda d: d.get("number", 0))
    for issue in data:
        body = issue.get("body") or ""
        m = re.search(r"## Parent\n(.*?)(?:\n## |\Z)", body, re.DOTALL)
        if not m:
            continue
        if prd not in re.findall(r"#(\d+)", m.group(1)):
            continue
        num = issue["number"]
        title = issue.get("title", "")
        labels = ",".join(l["name"] for l in issue.get("labels", []))
        safe_body = body.replace("\n", "\x1d")
        sys.stdout.write(f"{num}\x1f{title}\x1f{labels}\x1f{safe_body}\x1e")


def cmd_codex_parse(args):
    """Parse + validate codex review output. mode=counts: verdict\\tbl\\tco\\tnits. mode=findings: markdown."""
    VALID_VERDICTS = {"clean", "issues_found"}
    VALID_SEVERITIES = {"blocker", "concern", "nit"}
    VALID_CATEGORIES = {"correctness", "security", "tenant_isolation", "test_coverage", "convention", "performance"}
    REQUIRED = {"severity", "category", "description", "file", "line"}

    try:
        d = json.load(open(args.file))
        verdict = d.get("verdict", "unknown")
        if verdict not in VALID_VERDICTS:
            verdict = "unknown"
        issues = d.get("issues", [])
        if not isinstance(issues, list):
            verdict = "unknown"
            issues = []
        else:
            for i in issues:
                if (not isinstance(i, dict)
                        or not REQUIRED.issubset(i.keys())
                        or i.get("severity") not in VALID_SEVERITIES
                        or i.get("category") not in VALID_CATEGORIES
                        or not isinstance(i.get("description"), str) or not i.get("description")
                        or not isinstance(i.get("file"), str) or not i.get("file")
                        or not isinstance(i.get("line"), int)):
                    verdict = "unknown"
                    issues = []
                    break
        bl = sum(1 for i in issues if i.get("severity") == "blocker")
        co = sum(1 for i in issues if i.get("severity") == "concern")
        ni = sum(1 for i in issues if i.get("severity") == "nit")
        if verdict == "clean" and (bl > 0 or co > 0):
            verdict = "issues_found"
        elif verdict == "issues_found" and (bl + co + ni) == 0:
            verdict = "unknown"
    except Exception:
        verdict, bl, co, ni = "unknown", 0, 0, 0
        d = {}
        issues = []

    if args.mode == "counts":
        print(f"{verdict}\t{bl}\t{co}\t{ni}")
    elif args.mode == "findings":
        lines = [
            "**Verdict:** " + d.get("verdict", "?"),
            "",
            "**Summary:** " + d.get("summary", ""),
        ]
        if issues:
            lines += ["", "### Findings", ""]
            for i in issues:
                cat = f" [{i.get('category', '')}]" if i.get("category") else ""
                loc = ""
                if "file" in i:
                    loc = f" (`{i['file']}"
                    if "line" in i:
                        loc += f":{i['line']}"
                    loc += "`)"
                lines.append(f"- **[{i['severity']}]**{cat} {i['description']}{loc}")
        else:
            lines.append("No findings.")
        print("\n".join(lines))


def cmd_issue_fields(args):
    """Extract title, body, labels (CSV), state from gh issue JSON on stdin.
    Output: title\\tlabels_csv\\tstate on line 1, body on remaining lines."""
    data = json.load(sys.stdin)
    title = data.get("title", "")
    body = data.get("body", "") or ""
    labels = ",".join(l["name"] for l in data.get("labels", []))
    state = data.get("state", "")
    print(f"{title}\t{labels}\t{state}")
    sys.stdout.write(body)


def cmd_preflight_check(args):
    """Run preflight body analysis. Reads issue JSON (body+comments) from stdin.
    Outputs one warning per line to stdout."""
    data = json.load(sys.stdin)
    body = data.get("body", "") or ""
    comments = data.get("comments", [])
    comment_count = len(comments)
    route = args.route

    body_kb = round(len(body.encode("utf-8")) / 1024, 1)
    if body_kb > 8:
        print(f"body is {body_kb} KB (> 8 KB threshold)")

    if comment_count > 50:
        print(f"issue has {comment_count} comments (> 50 threshold)")

    body_lower = body.lower()
    high_effort = [kw for kw in HIGH_EFFORT_KEYWORDS if kw in body_lower]
    if high_effort:
        print(f"high-effort signals detected: {', '.join(high_effort)}")

    opposite = CROSS_REPO_KEYWORDS.get(route, [])
    cross_repo = [kw for kw in opposite if kw in body_lower]
    if cross_repo:
        print(f"cross-repo signals in {route} issue body: {', '.join(cross_repo)}")


def cmd_lock_payload(args):
    """Generate lock file JSON."""
    data = {
        "pid": int(args.pid),
        "host": args.host,
        "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": args.command,
        "job_id": None,
        "workdir": args.workdir,
    }
    print(json.dumps(data, indent=2))


def cmd_resume_hints(args):
    """Generate resume hints JSON."""
    data = {
        "issue": int(args.issue),
        "branch": args.branch,
        "expected_head": args.head,
    }
    print(json.dumps(data))


def cmd_gen_id(args):
    """Print a short UUID."""
    import uuid
    print(str(uuid.uuid4())[:8])


def cmd_auth_cache_path(args):
    """Print the auth cache file path for a given config dir."""
    h = hashlib.sha256(args.config_dir.encode()).hexdigest()[:16]
    print(f"/tmp/.ralph_claude_auth_{h}")


def cmd_format_comments(args):
    """Format issue comments from JSON stdin."""
    data = json.load(sys.stdin)
    comments = data.get("comments", [])
    if not comments:
        print("No prior comments.")
        return
    parts = []
    for c in comments:
        author = c.get("author", {}).get("login", "?")
        date = c.get("createdAt", "")[:10]
        body = c.get("body", "")
        parts.append(f"**{author}** ({date}):\n{body}")
    print("\n---\n".join(parts))


def cmd_plist_cal(args):
    """Print month day hour minute for a unix epoch."""
    dt = datetime.fromtimestamp(int(args.epoch))
    print(f"{dt.month} {dt.day} {dt.hour} {dt.minute}")


# ── Reset epoch ──────────────────────────────────────────────────────────────

def cmd_reset_epoch(args):
    """Parse Claude's usage-limit reset time message, print unix epoch."""
    try:
        from zoneinfo import ZoneInfo
    except Exception:
        ZoneInfo = None

    msg = args.message
    m = re.search(
        r"resets?\s+([0-9]{1,2})(?::([0-9]{2}))?\s*([ap]m)?(?:\s*\(([^)]+)\))?",
        msg, re.I,
    )
    if not m:
        sys.exit(1)

    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").lower()
    tz_name = m.group(4)

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    tz = None
    if tz_name and ZoneInfo is not None:
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            pass

    now = datetime.now(tz) if tz else datetime.now().astimezone()
    reset = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reset <= now:
        reset += timedelta(days=1)
    print(int(reset.timestamp()))


def cmd_is_exhaustion(args):
    """Exit 0 if message matches exhaustion patterns, 1 otherwise."""
    msg = args.message.lower()
    for p in EXHAUSTION_PATTERNS:
        if p in msg:
            sys.exit(0)
    sys.exit(1)

# ── Journal ──────────────────────────────────────────────────────────────────

def _event_indicates_exhaustion(event):
    if not isinstance(event, dict) or event.get("type") != "result":
        return False
    if event.get("api_error_status") in EXHAUSTION_STATUS_CODES:
        return True
    if not event.get("is_error"):
        return False
    fields = []
    for key in ("error", "result", "subtype"):
        val = event.get(key)
        if isinstance(val, str):
            fields.append(val.lower())
    haystack = " ".join(fields)
    return any(p in haystack for p in EXHAUSTION_PATTERNS)


def _scan_exhaustion(log_path):
    try:
        with open(log_path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if _event_indicates_exhaustion(event):
                    return True
        return False
    except (FileNotFoundError, IOError):
        return False


def _render_journal_markdown(data):
    run_id = data.get("run_id", "?")
    issue = data.get("selected_issue")
    route = data.get("route") or "?"
    branch = data.get("branch") or "?"
    before_head = data.get("before_head") or "?"
    after_head = data.get("after_head") or "?"
    preflight = data.get("preflight_decision") or "?"
    pf_warnings = data.get("preflight_warnings") or []
    final_status = data.get("final_status") or "?"
    elapsed = data.get("elapsed_s")
    review = data.get("review_result")
    review_file = data.get("review_file")
    usage_exhausted = data.get("usage_exhausted", False)
    resume_hints = data.get("resume_hints")
    resumed_from = data.get("resumed_from")
    command = data.get("command") or "once"

    def short(h):
        return h[:12] if h and h != "?" else "?"

    lines = [
        f"# Run {run_id}",
        "",
        f"**Status:** `{final_status}`  ",
        f"**Command:** `./ralph/ralph-core {command}`  ",
    ]
    if resumed_from:
        lines.append(f"**Resumed from:** `{resumed_from}`  ")
    if issue:
        lines.append(f"**Issue:** #{issue} ({route})  ")
    lines.append(f"**Branch:** `{branch}`  ")
    if elapsed is not None:
        lines.append(f"**Elapsed:** {elapsed}s  ")
    lines += [
        "",
        "## Commits",
        f"- before: `{short(before_head)}`",
        f"- after:  `{short(after_head)}`",
        "",
        "## Preflight",
        f"Decision: **{preflight}**",
    ]
    for w in pf_warnings:
        lines.append(f"- ⚠️  {w}")
    lines.append("")

    if review:
        lines += ["## Code Review", f"Verdict: **{review}**"]
        if review_file:
            lines.append(f"File: `{review_file}`")
        lines.append("")

    if usage_exhausted:
        lines += [
            "## ⚠️  Usage Exhaustion",
            "Claude reported a usage/rate limit during this run.",
            "",
        ]

    if usage_exhausted or final_status in RESUMABLE_STATUSES:
        hint_issue = issue
        if resume_hints:
            hint_issue = resume_hints.get("issue", issue)
        lines += ["## Resume", "```", f"./ralph/ralph-core resume {run_id}"]
        if hint_issue:
            lines.append(f"# or: ./ralph/ralph-core once --issue {hint_issue}")
        lines += ["```", ""]

    return "\n".join(lines) + "\n"


def cmd_journal_write(args):
    """Write JSON + Markdown journal entry."""
    runs_dir = Path(args.runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id

    pf_warnings = [w for w in args.preflight_warnings.split("|") if w] if args.preflight_warnings else []

    def opt_int(val):
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None

    resume_hints = None
    if args.resume_hints and args.resume_hints not in ("null", ""):
        try:
            resume_hints = json.loads(args.resume_hints)
        except json.JSONDecodeError:
            pass

    data = {
        "run_id": run_id,
        "command": args.command,
        "target_flags": {
            "issue": opt_int(args.issue),
            "prd": opt_int(args.prd),
            "allow_risky": bool(opt_int(args.allow_risky)),
        },
        "selected_issue": opt_int(args.issue),
        "route": args.route or None,
        "branch": args.branch or None,
        "before_head": args.before_head or None,
        "after_head": args.after_head or None,
        "preflight_decision": args.preflight_decision or "GO",
        "preflight_warnings": pf_warnings,
        "log_path": args.log_path or None,
        "review_result": args.review_result or None,
        "review_file": args.review_file or None,
        "final_status": args.final_status or "cancelled",
        "elapsed_s": opt_int(args.elapsed_s),
        "usage_exhausted": bool(opt_int(args.usage_exhausted)),
        "resumed_from": args.resumed_from or None,
        "resume_hints": resume_hints,
    }

    json_path = runs_dir / f"run-{run_id}.json"
    md_path = runs_dir / f"run-{run_id}.md"
    _atomic_write_json(json_path, data)

    md_tmp = str(md_path) + ".tmp"
    with open(md_tmp, "w") as f:
        f.write(_render_journal_markdown(data))
    os.replace(md_tmp, md_path)


def cmd_journal_scan(args):
    """Scan JSONL log for exhaustion patterns."""
    print("exhausted" if _scan_exhaustion(args.log_path) else "ok")


def cmd_journal_test(args):
    """Run built-in exhaustion detection tests."""
    import tempfile
    test_cases = [
        ('{"type":"result","subtype":"success","is_error":true,"api_error_status":429,'
         '"result":"You\'ve hit your session limit"}', True),
        ('{"type":"result","subtype":"error_during_execution","is_error":true,'
         '"result":"Claude AI usage limit reached"}', True),
        ('{"type":"result","is_error":true,"error":"rate limit exceeded for this hour"}', True),
        ('{"type":"result","subtype":"success","is_error":false,"api_error_status":null,'
         '"result":"Implemented the Mantle billing and Shopify rate limit handling."}', False),
        ('{"type":"result","subtype":"success","cost_usd":0.12}', False),
        ('{"type":"tool_result","content":[{"type":"text","text":"temporarily unavailable"}]}', False),
        ('{"type":"assistant","message":{"content":[{"type":"text","text":"too many requests"}]}}', False),
        ('{"type":"assistant","message":{"content":[{"type":"text","text":"Done."}]}}', False),
    ]
    passed = failed = 0
    for line, expected in test_cases:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            event = {}
        result = _event_indicates_exhaustion(event)
        ok = result == expected
        passed += ok
        failed += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] expected={expected} got={result}: {line[:70]}")

    exhausted_stream = "\n".join([
        '{"type":"system","subtype":"init","session_id":"abc"}',
        '{"type":"result","subtype":"success","is_error":true,"api_error_status":429,'
        '"result":"You\'ve hit your session limit"}',
    ])
    ok_stream = "\n".join([
        '{"type":"system","subtype":"init","session_id":"abc"}',
        '{"type":"result","subtype":"success","is_error":false,'
        '"result":"Implemented Mantle billing and Shopify rate limit handling."}',
    ])
    for stream, expected in [(exhausted_stream, True), (ok_stream, False)]:
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(stream + "\n")
            result = _scan_exhaustion(path)
        finally:
            os.unlink(path)
        ok = result == expected
        passed += ok
        failed += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] expected={expected} got={result}: scan(<{len(stream)}-byte stream>)")

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


def cmd_resume_list(args):
    """List resumable runs."""
    run_dir = Path(args.runs_dir)
    if not run_dir.exists():
        print("No runs directory found.")
        return
    found = False
    for jf in sorted(run_dir.glob("run-*.json"), reverse=True):
        try:
            d = json.load(open(jf))
        except Exception:
            continue
        fs = d.get("final_status", "")
        if fs not in RESUMABLE_STATUSES:
            continue
        if not found:
            print(f"{'RUN_ID':<32} {'STATUS':<18} {'ISSUE':<8} BRANCH")
            print("─" * 80)
            found = True
        h = d.get("resume_hints") or {}
        print(f"{d.get('run_id', '?'):<32} {fs:<18} #{h.get('issue', '?'):<7} {h.get('branch', '?')}")
    if not found:
        print("No resumable runs found.")


def cmd_update_status(args):
    """Atomically update final_status in a journal JSON file."""
    path = Path(args.file)
    d = json.load(open(path))
    d["final_status"] = args.status
    _atomic_write_json(path, d)

# ── Preflight body analysis ──────────────────────────────────────────────────

def cmd_preflight_body(args):
    """Analyze issue body for soft-warning signals. Reads body from stdin."""
    body = sys.stdin.read()
    route = args.route
    try:
        comment_count = int(args.comment_count)
    except (ValueError, TypeError):
        comment_count = 0

    body_kb = round(len(body.encode("utf-8")) / 1024, 1)
    body_lower = body.lower()
    high_effort = [kw for kw in HIGH_EFFORT_KEYWORDS if kw in body_lower]
    opposite = CROSS_REPO_KEYWORDS.get(route, [])
    cross_repo = [kw for kw in opposite if kw in body_lower]

    print(json.dumps({
        "body_kb": body_kb,
        "comment_count": comment_count,
        "high_effort_signals": high_effort,
        "cross_repo_signals": cross_repo,
    }))

# ── Schedule metadata ────────────────────────────────────────────────────────

def _sched_path(sched_dir, job_id):
    return Path(sched_dir) / f"{job_id}.json"


def cmd_sched_create(args):
    """Create a schedule metadata file."""
    Path(args.sched_dir).mkdir(parents=True, exist_ok=True)
    flags = {}
    if args.flags_json:
        try:
            flags = json.loads(args.flags_json)
        except json.JSONDecodeError:
            pass
    pf_warnings = [w for w in (args.preflight_warnings or "").split("|") if w]
    data = {
        "job_id": args.job_id,
        "command": args.command,
        "flags": flags,
        "run_at": args.run_at,
        "created_at": args.created_at,
        "status": "pending",
        "backend": args.backend,
        "backend_id": args.backend_id,
        "allow_risky": bool(int(args.allow_risky or 0)),
        "preflight_at_creation": {
            "decision": args.preflight_decision or "GO",
            "warnings": pf_warnings,
        },
        "preflight_at_runtime": None,
        "log_path": args.log_path,
        "run_id": None,
    }
    _atomic_write_json(_sched_path(args.sched_dir, args.job_id), data)
    print(args.job_id)


def cmd_sched_update(args):
    """Update fields in a schedule metadata file."""
    path = _sched_path(args.sched_dir, args.job_id)
    if not path.exists():
        print(f"error: schedule not found: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.load(open(path))
    bool_fields = {"allow_risky"}
    dict_fields = {"preflight_at_creation", "preflight_at_runtime", "flags"}
    for kv in (args.kv or []):
        if "=" not in kv:
            continue
        key, val = kv.split("=", 1)
        if key in bool_fields:
            data[key] = val.lower() in ("1", "true", "yes")
        elif "." in key:
            outer, inner = key.split(".", 1)
            if not isinstance(data.get(outer), dict):
                data[outer] = {}
            data[outer][inner] = val
        elif key in dict_fields:
            print(f"error: '{key}' is a dict — use dotted path", file=sys.stderr)
            sys.exit(1)
        else:
            data[key] = val
    if args.preflight_at_runtime_json:
        try:
            data["preflight_at_runtime"] = json.loads(args.preflight_at_runtime_json)
        except json.JSONDecodeError:
            pass
    _atomic_write_json(path, data)


def cmd_sched_list(args):
    """List all schedules."""
    sched_dir = Path(args.sched_dir)
    if not sched_dir.exists():
        print("No schedules directory found.")
        return
    schedules = []
    for p in sorted(sched_dir.glob("sched-*.json")):
        try:
            schedules.append(json.loads(p.read_text()))
        except (json.JSONDecodeError, IOError):
            continue
    if not schedules:
        print("No scheduled runs.")
        return
    schedules.sort(key=lambda d: d.get("run_at", ""))
    print(f"{'JOB_ID':<22} {'RUN_AT':<20} {'STATUS':<12} COMMAND")
    print("-" * 80)
    for d in schedules:
        print(f"{d.get('job_id', '?'):<22} {d.get('run_at', '?'):<20} {d.get('status', '?'):<12} {d.get('command', '?')}")


def cmd_sched_show(args):
    """Pretty-print a schedule."""
    path = _sched_path(args.sched_dir, args.job_id)
    if not path.exists():
        print(f"error: schedule not found: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.load(open(path))
    print(json.dumps(data, indent=2))
    print()
    print("Notes:")
    print(f"  Status   : {data.get('status')}")
    run_at = data.get("run_at", "")
    try:
        dt = datetime.fromisoformat(run_at)
        now = datetime.now()
        if dt > now and data.get("status") == "pending":
            diff = dt - now
            hours = int(diff.total_seconds() // 3600)
            mins = int((diff.total_seconds() % 3600) // 60)
            print(f"  Fires in : {hours}h {mins}m")
        elif data.get("status") == "done":
            print("  Completed.")
        elif data.get("status") == "failed":
            print(f"  Failed — check log: {data.get('log_path', 'N/A')}")
        elif data.get("status") == "cancelled":
            print("  Cancelled — OS job removed.")
        elif data.get("status") == "skipped":
            print("  Skipped — fired >24 h after run_at (stale launchd annual re-fire).")
    except (ValueError, TypeError):
        pass
    pf = data.get("preflight_at_creation") or {}
    if pf:
        w = pf.get("warnings") or []
        print(f"  Preflight (creation) : {pf.get('decision')} ({len(w)} warning(s))")
    pf_rt = data.get("preflight_at_runtime")
    if pf_rt:
        w_rt = pf_rt.get("warnings") or []
        print(f"  Preflight (runtime)  : {pf_rt.get('decision')} ({len(w_rt)} warning(s))")
    if data.get("run_id"):
        print(f"  Journal  : ralph/runs/run-{data['run_id']}.md")
    print(f"  Log      : {data.get('log_path', 'N/A')}")
    print(f"  Backend  : {data.get('backend')} ({data.get('backend_id')})")


def cmd_sched_get(args):
    """Print a single field value from a schedule."""
    path = _sched_path(args.sched_dir, args.job_id)
    if not path.exists():
        print(f"error: schedule not found: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.load(open(path))
    print(_format_val(_get_nested(data, args.field)))


def cmd_parse_dt(args):
    """Validate datetime string, print epoch and ISO."""
    try:
        dt = datetime.strptime(args.datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"error: invalid datetime '{args.datetime_str}' — expected YYYY-MM-DD HH:MM", file=sys.stderr)
        sys.exit(1)
    now = datetime.now()
    if dt <= now:
        print(f"error: '{args.datetime_str}' is in the past (current: {now.strftime('%Y-%m-%d %H:%M')})", file=sys.stderr)
        sys.exit(1)
    dt = dt.astimezone()
    print(f"{int(dt.timestamp())} {dt.strftime('%Y-%m-%dT%H:%M:%S')}")


def cmd_sched_batch(args):
    """Batch-read schedule fields for run-scheduled. One field per line."""
    try:
        d = json.load(open(args.file))
        flags = d.get("flags") or {}
        run_at = d.get("run_at", "") or ""
        now = datetime.now()
        try:
            dt = datetime.fromisoformat(run_at)
            delta = (now - dt).total_seconds()
            stale = "1" if delta > 86400 else "0"
            run_at_epoch = str(int(dt.timestamp()))
        except Exception:
            stale = "0"
            run_at_epoch = ""
        ar = d.get("allow_risky", "")
        print(d.get("status", ""))
        print(run_at)
        print(stale)
        print(d.get("log_path", "") or "")
        print(d.get("command", "") or "")
        print("1" if str(ar).lower() in ("true", "1", "yes") else "0")
        v = flags.get("issue")
        print("" if v is None else str(v))
        print(flags.get("route") or "")
        print(run_at_epoch)
        print(str(int(now.timestamp())))
    except Exception:
        for _ in range(10):
            print("")

# ── Retention sweep ──────────────────────────────────────────────────────────

def cmd_prune_stale(args):
    """Prune old run journals and schedule metadata. Prints: pruned_runs pruned_scheds."""
    days = int(args.days)
    run_dir = Path(args.run_dir)
    sched_dir = Path(args.sched_dir)
    pruned_runs = pruned_scheds = 0
    now = datetime.now().astimezone()

    if run_dir.exists():
        for jf in run_dir.glob("run-*.json"):
            try:
                d = json.load(open(jf))
                fs = d.get("final_status", "")
                rid = jf.stem.replace("run-", "")
                ts_str = rid.split("-")[0]
                dt = datetime.strptime(ts_str, "%Y%m%dT%H%M%S").astimezone()
                age = (now - dt).days
                if age >= days and fs not in RESUMABLE_STATUSES:
                    jf.unlink(missing_ok=True)
                    md = jf.with_suffix(".md")
                    md.unlink(missing_ok=True)
                    pruned_runs += 1
            except Exception:
                continue

    if sched_dir.exists():
        for sf in sched_dir.glob("sched-*.json"):
            try:
                d = json.load(open(sf))
                ss = d.get("status", "")
                ca = d.get("run_at", "") or d.get("created_at", "") or ""
                dt = datetime.fromisoformat(ca)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                age = (now - dt).days
                if ss in ("done", "cancelled", "failed") and age >= days:
                    print(f"PRUNE_SCHED\t{d.get('job_id', '')}\t{d.get('backend', 'none')}\t{d.get('backend_id', 'none')}")
                    sf.unlink(missing_ok=True)
                    pruned_scheds += 1
            except Exception:
                continue

    print(f"PRUNED\t{pruned_runs}\t{pruned_scheds}")

# ── Argparse dispatch ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ralph-core unified helper")
    sub = parser.add_subparsers(dest="subcmd")

    p = sub.add_parser("json-get")
    p.add_argument("file")
    p.add_argument("keys", nargs="+")

    p = sub.add_parser("json-stdin")
    p.add_argument("keys", nargs="+")

    p = sub.add_parser("json-build")
    p.add_argument("pairs", nargs="+")

    p = sub.add_parser("md-refs")
    p.add_argument("section")

    p = sub.add_parser("prd-filter")
    p.add_argument("prd_num")

    p = sub.add_parser("codex-parse")
    p.add_argument("file")
    p.add_argument("mode", choices=["counts", "findings"])

    p = sub.add_parser("lock-payload")
    p.add_argument("pid")
    p.add_argument("host")
    p.add_argument("command")
    p.add_argument("workdir")

    p = sub.add_parser("resume-hints")
    p.add_argument("issue")
    p.add_argument("branch")
    p.add_argument("head")

    p = sub.add_parser("gen-id")

    p = sub.add_parser("auth-cache-path")
    p.add_argument("config_dir")

    p = sub.add_parser("issue-fields")

    p = sub.add_parser("preflight-check")
    p.add_argument("route")

    p = sub.add_parser("format-comments")

    p = sub.add_parser("plist-cal")
    p.add_argument("epoch")

    p = sub.add_parser("reset-epoch")
    p.add_argument("message")

    p = sub.add_parser("is-exhaustion")
    p.add_argument("message")

    p = sub.add_parser("journal-write")
    p.add_argument("runs_dir")
    p.add_argument("run_id")
    p.add_argument("command")
    p.add_argument("issue")
    p.add_argument("prd")
    p.add_argument("allow_risky")
    p.add_argument("route")
    p.add_argument("branch")
    p.add_argument("before_head")
    p.add_argument("after_head")
    p.add_argument("preflight_decision")
    p.add_argument("preflight_warnings")
    p.add_argument("log_path")
    p.add_argument("review_result")
    p.add_argument("review_file")
    p.add_argument("final_status")
    p.add_argument("elapsed_s")
    p.add_argument("usage_exhausted")
    p.add_argument("--resume-hints", default="null")
    p.add_argument("--resumed-from", default="")

    p = sub.add_parser("journal-scan")
    p.add_argument("log_path")

    sub.add_parser("journal-test")

    p = sub.add_parser("resume-list")
    p.add_argument("runs_dir")

    p = sub.add_parser("update-status")
    p.add_argument("file")
    p.add_argument("status")

    p = sub.add_parser("preflight-body")
    p.add_argument("route")
    p.add_argument("comment_count")

    p = sub.add_parser("sched-create")
    p.add_argument("sched_dir")
    p.add_argument("--job-id", required=True)
    p.add_argument("--command", required=True)
    p.add_argument("--flags-json", default="{}")
    p.add_argument("--run-at", required=True)
    p.add_argument("--created-at", required=True)
    p.add_argument("--allow-risky", default="0")
    p.add_argument("--backend", default="none")
    p.add_argument("--backend-id", default="none")
    p.add_argument("--log-path", required=True)
    p.add_argument("--preflight-decision", default="GO")
    p.add_argument("--preflight-warnings", default="")

    p = sub.add_parser("sched-update")
    p.add_argument("sched_dir")
    p.add_argument("job_id")
    p.add_argument("kv", nargs="*")
    p.add_argument("--preflight-at-runtime-json", default="")

    p = sub.add_parser("sched-list")
    p.add_argument("sched_dir")

    p = sub.add_parser("sched-show")
    p.add_argument("sched_dir")
    p.add_argument("job_id")

    p = sub.add_parser("sched-get")
    p.add_argument("sched_dir")
    p.add_argument("job_id")
    p.add_argument("field")

    p = sub.add_parser("parse-dt")
    p.add_argument("datetime_str")

    p = sub.add_parser("sched-batch")
    p.add_argument("file")

    p = sub.add_parser("prune-stale")
    p.add_argument("run_dir")
    p.add_argument("sched_dir")
    p.add_argument("days")

    args = parser.parse_args()
    dispatch = {
        "json-get": cmd_json_get,
        "json-stdin": cmd_json_stdin,
        "json-build": cmd_json_build,
        "md-refs": cmd_md_refs,
        "prd-filter": cmd_prd_filter,
        "codex-parse": cmd_codex_parse,
        "lock-payload": cmd_lock_payload,
        "resume-hints": cmd_resume_hints,
        "gen-id": cmd_gen_id,
        "auth-cache-path": cmd_auth_cache_path,
        "format-comments": cmd_format_comments,
        "plist-cal": cmd_plist_cal,
        "reset-epoch": cmd_reset_epoch,
        "is-exhaustion": cmd_is_exhaustion,
        "journal-write": cmd_journal_write,
        "journal-scan": cmd_journal_scan,
        "journal-test": cmd_journal_test,
        "resume-list": cmd_resume_list,
        "update-status": cmd_update_status,
        "preflight-body": cmd_preflight_body,
        "issue-fields": cmd_issue_fields,
        "preflight-check": cmd_preflight_check,
        "sched-create": cmd_sched_create,
        "sched-update": cmd_sched_update,
        "sched-list": cmd_sched_list,
        "sched-show": cmd_sched_show,
        "sched-get": cmd_sched_get,
        "parse-dt": cmd_parse_dt,
        "sched-batch": cmd_sched_batch,
        "prune-stale": cmd_prune_stale,
    }
    fn = dispatch.get(args.subcmd)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
