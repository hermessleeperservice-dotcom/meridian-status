# Task 1 — poll-worker dedup fix — COMPLETE

_Timestamp: 2026-07-16 19:45 BST. Author: Meridian._

## What was wrong
The launchd worker (`scripts/poll-worker.py`, `com.hermes.sleep.meridian-poll`,
StartInterval=1200) was re-acknowledging every inbox file as new on each 20-min
cycle, since ~09 July. Two root causes:

1. **Dedup keyed on the wrong field.** It compared the *full generated ack
   filename* (which carries this run's own `YYYY-MM-DD-HHMM-` prefix) against
   loop/ entries — those basenames can never collide by construction, so
   nothing was ever deduped. Fix: recover the embedded **source** inbox token
   from each loop/ ack (strip the outer run-prefix + generator prefix
   `inbox-/followup-/kickoff-`), normalize the `.md` suffix (legacy acks were
   truncated and lost it), and match with extension-insensitive two-way
   `startswith` (tolerates one-sided truncation).
2. **`finally` double-close.** `try/finally` were indented level with the
   `with open(lock)` block, so `fcntl.LOCK_UN` ran after the file was already
   closed → `ValueError: I/O operation on closed file` → `launchctl` reported
   exit status 1. Fixed by nesting `try/finally` *inside* the `with`.

Also confirmed `git pull origin main` runs at Step 1 **before** scanning inbox/
(Step 2) — already present per the earlier 1908 follow-up; kept and hardened.

## One-line-significant subtlety discovered
A first pass of the fix added a *nested* `_strip_run_prefix` inside
`source_token`, which mangled the embedded dated source (`2026-07-08-1106-foll`
→ `1106-foll`) so it failed the date-ish guard and was discarded — dedup still
found 15 "new". Removed the nested strip; outer-prefix + generator-prefix strip
is sufficient.

## Verification (against agent.log, not a UI summary)
Ran the patched worker twice after the fix:

- Run 1 (19:45:23 BST): `Found 0 new inbox files (out of 32 total)` →
  `No new inbox files to process — nothing to commit.` → `Worker complete.` exit 0.
- Pre-fix reference: the 19:06 launchd run (old code) re-acked 26 files;
  module-level check on live loop/ now returns 0 NEW of 32.

## Commits
- `cff4b31` fix(poll-worker): source-token dedup + pull-before-scan + lock close bug
- `dc31474` fix(poll-worker): drop nested run-prefix strip in source_token

Both pushed to origin/main.
