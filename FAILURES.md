# Failure log

One entry per lab, per group. Append yours at the bottom; never edit anyone else's.

**An entry must name a specific input and a specific wrong output.** "It didn't work"
is not an entry. Bugs in your own Python are not entries either — this file is only
for what the *model* did.

By Week 11 this is a catalogue of a hundred real failure modes of the model we are
all building on. You will use it when you write your eval cases in Lab 9.

---

## Lab 0 — Example (delete nothing, just append below)

```
Input:    asked for one tool call, prompt in format.md v2
Expected: a single JSON object
Got:      two JSON objects, the second malformed, wrapped in prose
Did:      parser now takes the first valid object and logs the rest
```

---
