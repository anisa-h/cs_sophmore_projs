#!/usr/bin/env python3
"""Record one step of your work with the agent.

    python snapshot.py 6 "asked for a JSON tool-call parser; got one that
                          assumed exactly one call; kept it but added a loop"

Stages everything, commits it, and tags the commit with the lab number so the
history can be read back as a decision log.

Write the message for a reader who was not there. The useful shape is:
what you asked for, what came back, what you did about it. "wip", "fixes",
and "update" tell that reader nothing and will not earn credit.
"""
from __future__ import annotations

import subprocess
import sys

LOW_EFFORT = {"wip", "fix", "fixes", "fixed", "update", "updates", "changes",
              "stuff", "work", "asdf", "commit", "done", "misc", "temp"}


def git(*args, **kw):
    return subprocess.run(["git", *args], capture_output=True, text=True, **kw)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    lab = sys.argv[1]
    if not lab.isdigit() or not 1 <= int(lab) <= 12:
        print(f"error: first argument should be a lab number 1-12, got {lab!r}")
        sys.exit(2)

    message = " ".join(sys.argv[2:]).strip()
    if len(message) < 20 or message.lower().strip(".!") in LOW_EFFORT:
        print("error: that message is too short or too generic to be useful later.")
        print("       In three weeks the person reading it is you, sitting a quiz.")
        print("       Say what you asked for, what came back, and what you did about it.")
        sys.exit(2)

    if git("rev-parse", "--git-dir").returncode != 0:
        print("error: not a git repository")
        sys.exit(1)

    if not git("status", "--porcelain").stdout.strip():
        print("nothing has changed since your last snapshot — nothing to record")
        sys.exit(0)

    git("add", "-A")
    r = git("commit", "-m", f"snapshot(lab{lab}): {message}")
    if r.returncode != 0:
        print(r.stdout or r.stderr)
        sys.exit(1)

    n = len([l for l in git("log", "--format=%s").stdout.splitlines()
             if l.startswith(f"snapshot(lab{lab}):")])
    print(f"recorded. lab {lab} now has {n} snapshot(s).")


if __name__ == "__main__":
    main()
