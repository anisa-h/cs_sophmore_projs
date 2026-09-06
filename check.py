#!/usr/bin/env python3
"""Check your lab deliverables before the deadline.

    python check.py          # every lab
    python check.py 6        # just lab 6
    python check.py --secrets  # only the API-key scan

Exit code is 0 if everything checked passes, 1 otherwise. This is the same
script used for grading the file-existence parts of each lab's checklist.
It cannot judge whether your work is any good — only whether it is there.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OK, BAD, WARN = "PASS", "FAIL", "WARN"


# ---------------------------------------------------------------- checks
def exists(path, note=""):
    def run():
        p = ROOT / path
        if p.exists() and (p.is_dir() or p.stat().st_size > 0):
            return OK, f"{path}"
        return BAD, f"{path} missing or empty" + (f" — {note}" if note else "")
    return run


def dir_has(path, pattern="*", minimum=1, note=""):
    def run():
        p = ROOT / path
        if not p.is_dir():
            return BAD, f"{path}/ missing"
        n = len([f for f in p.rglob(pattern) if f.is_file()])
        if n >= minimum:
            return OK, f"{path}/ has {n} {pattern} file(s)"
        return BAD, f"{path}/ has {n} {pattern} file(s), needs {minimum}" + (f" — {note}" if note else "")
    return run


def contains(path, pattern, note):
    def run():
        p = ROOT / path
        if not p.exists():
            return BAD, f"{path} missing"
        if re.search(pattern, p.read_text(errors="ignore"), re.I | re.M):
            return OK, f"{path}: {note}"
        return BAD, f"{path}: {note} — not found"
    return run


def dir_contains(path, pattern, note):
    def run():
        d = ROOT / path
        if not d.is_dir():
            return BAD, f"{path}/ missing"
        for f in d.rglob("*.py"):
            if re.search(pattern, f.read_text(errors="ignore"), re.I):
                return OK, f"{path}/: {note}"
        return BAD, f"{path}/: {note} — not found"
    return run


def json_min(path, minimum, note):
    def run():
        p = ROOT / path
        if not p.exists():
            return BAD, f"{path} missing"
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            return BAD, f"{path} is not valid JSON ({e.msg})"
        n = len(data) if isinstance(data, (list, dict)) else 0
        if n >= minimum:
            return OK, f"{path}: {n} {note}"
        return BAD, f"{path}: {n} {note}, needs {minimum}"
    return run


def snapshots(lab, minimum=3):
    """Provenance is a course mechanism, not a property of whichever tool you use."""
    def run():
        try:
            proc = subprocess.run(["git", "log", "--format=%s"], cwd=ROOT,
                                  capture_output=True, text=True, timeout=20)
        except Exception:
            return WARN, "could not read git log"
        if proc.returncode != 0:
            return WARN, "not a git repository — snapshots not checked"
        n = len([l for l in proc.stdout.splitlines()
                 if l.startswith(f"snapshot(lab{lab}):")])
        if n >= minimum:
            return OK, f"{n} snapshot(s) recorded for lab {lab}"
        return BAD, (f"{n} snapshot(s) for lab {lab}, needs {minimum} — "
                     f"use: python snapshot.py {lab} \"what you asked / what came back / what you did\"")
    return run


def failures_entry(lab):
    def run():
        p = ROOT / "FAILURES.md"
        if not p.exists():
            return BAD, "FAILURES.md missing"
        text = p.read_text(errors="ignore")
        blocks = re.split(r"^##\s+Lab\s+", text, flags=re.M)[1:]
        for b in blocks:
            if not re.match(rf"0*{lab}\b", b):
                continue
            body = b.lower()
            if "input:" in body and ("got:" in body or "output:" in body):
                return OK, f"FAILURES.md has a Lab {lab} entry"
            return BAD, f"FAILURES.md Lab {lab} entry needs both an input and what you got"
        return BAD, f"FAILURES.md has no Lab {lab} entry"
    return run


def branch_unmerged(name):
    def run():
        try:
            merged = subprocess.run(
                ["git", "branch", "--merged", "main"], cwd=ROOT,
                capture_output=True, text=True, timeout=10).stdout
        except Exception:
            return WARN, f"could not check branches (is this a git repo?)"
        if re.search(rf"^\s*\*?\s*{re.escape(name)}\s*$", merged, re.M):
            return BAD, f"branch '{name}' is merged into main — it must not be"
        return OK, f"branch '{name}' not merged into main"
    return run


# ---------------------------------------------------------------- secrets
KEY_PATTERNS = [
    (r"CHATTERBOX_KEY\s*=\s*(?!paste-your-key-here)\S{8,}", "a CHATTERBOX_KEY with a real value"),
    (r"\bsk-[A-Za-z0-9_\-]{16,}", "an sk- style API key"),
    (r"api_key\s*=\s*[\"'][A-Za-z0-9_\-]{16,}[\"']", "a hardcoded api_key"),
    (r"Bearer\s+[A-Za-z0-9_\-]{20,}", "a Bearer token"),
]


def scan_secrets():
    """The most important check here. Returns list of (status, message)."""
    out = []
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                              text=True, timeout=20)
    except Exception as e:
        return [(WARN, f"could not run git ({e}) — SECRET SCAN DID NOT RUN")]
    if proc.returncode != 0:
        return [(WARN, "not a git repository — SECRET SCAN DID NOT RUN")]
    tracked = proc.stdout.split()
    if not tracked:
        return [(WARN, "no files tracked by git yet — SECRET SCAN FOUND NOTHING TO SCAN")]

    if any(f == ".env" or f.startswith(".env.") and f != ".env.example" for f in tracked):
        out.append((BAD, ".env is tracked by git — remove it: git rm --cached .env"))

    hits = []
    for f in tracked:
        p = ROOT / f
        if not p.is_file() or p.suffix in {".png", ".jpg", ".pdf", ".zip"}:
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        for pat, desc in KEY_PATTERNS:
            for m in re.finditer(pat, text):
                line = text[: m.start()].count("\n") + 1
                hits.append(f"{f}:{line} looks like {desc}")
    for h in hits[:10]:
        out.append((BAD, h))
    if len(hits) > 10:
        out.append((BAD, f"...and {len(hits) - 10} more"))
    if not out:
        out.append((OK, "no API keys found in tracked files"))
    return out


# ---------------------------------------------------------------- the labs
LABS: dict[int, tuple[str, list]] = {
    1: ("What is between you and the model", [
        exists("labs/lab01/findings.md", "all five experiments, with numbers"),
        contains("labs/lab01/findings.md", r"\d", "reports actual numbers"),
        exists(".gitignore"),
        contains(".gitignore", r"^\.env\s*$", ".env is ignored"),
    ]),
    2: ("Writing specifications", [
        exists("labs/lab02/spec.md"),
        exists("labs/lab02/questions.md", "every question you could not ask them"),
        dir_has("labs/lab02/their-spec-implemented", "*.py", 1),
    ]),
    3: ("Tests as ground truth", [
        dir_has("project-a/tests", "test_*.py", 1, "acceptance tests from your spec"),
        exists("project-a/spec-v1.md"),
        dir_contains("project-a/tests", r"hypothesis", "at least one property-based test"),
    ]),
    4: ("Reading code you did not write", [
        exists("labs/lab04/review-own.md", "at least three real issues"),
        exists("labs/lab04/review-blind.md"),
    ]),
    5: ("The agent loop", [
        exists("labs/lab05/loop.py"),
        contains("labs/lab05/loop.py", r"MAX_STEPS|max_steps", "has a step limit"),
        exists("labs/lab05/notes.md", "how many model calls a run costs"),
    ]),
    6: ("Tool calling by hand", [
        exists("labs/lab06/format.md", "your tool-call format"),
        dir_has("labs/lab06", "test_*.py", 1, "a test per malformed case"),
        contains("labs/lab06/format.md", r"retry|retries", "documents retry behaviour"),
    ]),
    7: ("MCP", [
        dir_has("project-b", "*mcp*.py", 1, "your MCP server"),
        exists("project-b/README.md", "your schema, for the group consuming it"),
        dir_has("project-b", "*transcript*", 2, "one transcript per client"),
    ]),
    8: ("Context rot", [
        exists("project-b/context-rot.py"),
        exists("project-b/context-rot.png", "the plot, both axes labelled"),
        exists("project-b/memory-design.md"),
        contains("project-b/memory-design.md", r"\d{3,}|\dK|\d+k", "cites a number from your own plot"),
    ]),
    9: ("Evaluation harness", [
        json_min("project-b/eval/cases.json", 20, "cases"),
        exists("project-b/eval/score.py"),
        exists("project-b/eval/run.py"),
        contains("project-b/eval/run.py", r"Semaphore|concurren|sleep|backoff", "caps concurrency"),
    ]),
    10: ("Red team", [
        exists("project-b/attack-report.md"),
        exists("project-b/defense.md"),
        branch_unmerged("redteam"),
    ]),
    11: ("Integration studio", [
        exists("project-b/eval-report.md"),
        contains("project-b/eval-report.md", r"did not fix|not fixed|won't fix|will not fix",
                 "documents a failure you did not fix"),
    ]),
}
# ---------------------------------------------------------------- runner
def run_lab(n):
    title, checks = LABS[n]
    results = [c() for c in checks] + [failures_entry(n)(), snapshots(n)()]
    failed = sum(1 for s, _ in results if s == BAD)
    print(f"\nLab {n} — {title}")
    for status, msg in results:
        mark = {OK: "  [ok]  ", BAD: "  [FAIL]", WARN: "  [warn]"}[status]
        print(f"{mark} {msg}")
    return failed


def main():
    args = [a for a in sys.argv[1:]]
    print("=" * 64)
    print("SECRETS")
    sec = scan_secrets()
    for status, msg in sec:
        print(f"  {'[ok]  ' if status == OK else '[FAIL]' if status == BAD else '[warn]'} {msg}")
    failed = sum(1 for s, _ in sec if s == BAD)

    if "--secrets" in args:
        sys.exit(1 if failed else 0)

    nums = [int(a) for a in args if a.isdigit()] or sorted(LABS)
    print("=" * 64)
    for n in nums:
        if n in LABS:
            failed += run_lab(n)

    print("\n" + "=" * 64)
    print("ALL CHECKS PASSED" if failed == 0 else f"{failed} check(s) failed")
    print("A pass here means your files exist. It does not mean your work is good.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
