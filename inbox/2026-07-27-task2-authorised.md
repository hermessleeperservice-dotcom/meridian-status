# Task 1 verified — Task 2 authorised

**Date:** 2026-07-27
**Refers to:** `inbox/2026-07-27-finance-bot-hardening.md`

---

## Verification of Task 1 — independent, not taken on trust

Commit `6764246e691d48c98e4f22da8ee73cc4de729395` confirmed present on
`finance-bot@master`. Diff stat +149/−21 matches the loop report. Full patch
read and reviewed.

**Accepted. Task 1 is COMPLETE.** The report was accurate, the evidence was real,
and the diagnosis in 1.1 was better than the brief asked for — identifying that
`response.get('id', 'unknown')` did not merely swallow failure but would have
reported a video ID that never existed.

Telegram delivery to chat `5109089813` confirmed by the human at 09:48 and
09:49. The alerting path works end to end, not just in the log.

**Gate satisfied. Begin Task 2 as specified in the original instruction.**

---

## Carried forward into Task 2 — corrections and additions

### A. Do not trust exit code alone in the report

Already specified, restated because it is the whole point: `Result: SUCCESS`
requires a **video ID**. Exit 0 without an ID is `FAILED`. The defensive branch
in `main()` now exits 1 in that case, so it should not arise — but the report
must assert the ID independently rather than inferring success from the exit
code. Two independent signals, or the reporting layer inherits the same blind
spot it exists to remove.

### B. Distinguish alerts from session chatter

Failure alerts land in chat `5109089813`, which is also the channel for live
Hermes session output. A `Finance Bot FAILED` message will sit among ordinary
agent traffic and is easy to miss on a busy day.

Prefix the alert text with a fixed, greppable marker so it is visually and
programmatically distinct:

```
[FINANCE-BOT-ALERT] Finance Bot FAILED <timestamp>
```

Keep everything else in the message identical. Small change to
`_failure_alert()` in `finance_bot_v2.py`; commit it with Task 2 rather than
opening a separate task.

### C. Two known gaps — record, do not fix

Both were noted during review. Neither blocks Task 2. Do **not** attempt either
now; they are logged so they are not rediscovered as surprises later.

1. **The real outage branch is untested.** `FINANCE_BOT_FORCE_UPLOAD_FAIL`
   short-circuits at the top of `upload_to_youtube()`, so the code path that
   handles a 200 response carrying no `id` — the actual shape of the original
   fault — is written but never exercised. Testing it properly needs a mocked
   API response.
2. **`run_scheduler()` was not changed.** The `--schedule` path retains the old
   behaviour. Irrelevant while launchd invokes `--generate daily`, and dangerous
   only if anyone switches to the in-process scheduler.

Add both to the Task 2 loop report under a `## Known gaps (not fixed)` heading
so they stay visible.

### D. Confirm the test seam is inert

In the Task 2 report, confirm:

- `FINANCE_BOT_FORCE_UPLOAD_FAIL` is not set in any shell profile, launchd
  plist, or `.env` file on the machine. Show the grep you ran across
  `~/.zshrc`, `~/.bash_profile`, `~/.hermes/.env`, and both plists in
  `~/Library/LaunchAgents/`.
- `git -C ~/Projects/financebot status --short` is clean.

An env var that silently disables uploads is now a permanent part of this
codebase. It must be provably unset.

---

## Standing note on reporting

The Task 1 report was the right standard: actual command output pasted
verbatim, an honest "could not do" section, and a stated reason for each
deviation. Hold that bar for Task 2 and Task 3.

Where a claim rests on inference rather than direct observation, say so
explicitly. The Task 1 report inferred Telegram delivery from the absence of a
warning line and flagged that it needed human confirmation — that was correct
practice, and the confirmation is what closed the gate. Keep doing that.
