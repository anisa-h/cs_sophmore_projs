# Agentic Coding — group repository

This is your group's repository for the whole semester. Labs, both projects,
and your decision log all live here.

## Setup (Week 1)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then paste your Chatterbox key into .env
export CHATTERBOX_KEY=$(grep CHATTERBOX_KEY .env | cut -d= -f2-)

python llm.py                 # should print a four-word greeting
                              # this is how YOUR CODE calls Gemma; your coding
                              # agent is configured separately, in its own config
```

Get your key at https://chatterbox.ee.cooper.edu/ — profile → Settings → Account.

**`.env` is gitignored. Never commit your key.** Every push runs an automatic
scan, and a committed key fails the build. If it happens, tell the instructor —
the key has to be revoked, not just deleted.

## Recording your work

After each meaningful exchange with your agent, run this in your terminal from
the root of this repository:

```bash
python snapshot.py 6 "asked for a JSON parser; it assumed one call; added a loop"
```

The **`6` is the lab number** — change it to whichever lab you are on. The quoted
text is your own description. It stages and commits everything, tagged with that
lab. **What you asked for, what came back, what you did about it.**

The script refuses anything too short or too generic to be useful later —
`wip`, `fixes`, `update` are what people type out of habit, and they tell a
reader nothing. In three weeks that reader is you, sitting a quiz on this code.

Three per lab, minimum, and `check.py` enforces it. Your decision log is
assembled from these, so snapshotting as you go means the log costs you nothing
at the end.

Some agents auto-commit, most don't, and those that do describe the *diff*
rather than your intent. Your quiz asks about intent — so we record it
ourselves rather than depending on whichever tool you chose.

## Checking your work

```bash
python check.py        # every lab
python check.py 6      # just lab 6
python check.py --secrets
```

`check.py` verifies that the file-based items on each lab's **checklist** are
present. It runs automatically on every push, and you can run it yourself as
often as you like.

**It checks that your files exist. It cannot tell whether your work is any
good** — that is what the quiz is for.

## Layout

```
llm.py                    your programs call this to reach Chatterbox
opencode.json             points your coding agent at Chatterbox
snapshot.py               records one step of your work
check.py                  the checker
FAILURES.md               one entry per lab — append, never edit others'
labs/lab01/               findings.md
labs/lab02/               spec.md, questions.md, their-spec-implemented/
labs/lab04/               review-own.md, review-blind.md
labs/lab05/               loop.py, notes.md
labs/lab06/               format.md, your tools, parser tests
project-a/                spec-v1.md, spec-v2.md, SPEC-DIFF.md, tests/, the tool
project-b/                the agent, MCP server, context-rot.*, memory-design.md,
                          attack-report.md, defense.md, eval-report.md
project-b/eval/           cases.json, score.py, run.py
decision-log.md           what you asked for, what came back, what you rejected
```

Labs 3 and 7–10 write into the project directories rather than `labs/`, because
those labs *are* the project milestones.

## Submitting

There is nothing to upload. **Committing and pushing to `main` is submitting.**

- Labs are due at the start of the following session.
- Projects are due **9:00 AM on the day of the quiz**; also fill in the Google
  form with your group members and this repo's URL.
- Late work is what is in `main` at the deadline, so push early and often.

## Two things that will cost you points

**Your decision log.** Required with both projects, and assembled from your
snapshots. Scrub any key from transcripts before you push.

**Your `FAILURES.md` entry**, every lab. A specific input and a specific wrong
output. "It didn't work" does not count.
