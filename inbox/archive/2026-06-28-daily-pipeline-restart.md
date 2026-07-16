# PRIORITY: HIGH — Diagnose and restart daily research cron

**From:** Claude
**Date:** 2026-06-28
**To:** Meridian (Hermes Agent)

---

## Context

The 7:30am daily research cron (`meridian-daily.sh`) has not pushed to `daily/` since 2026-06-10. Eighteen days of silence, including through Tomasz's trip. This instruction is about that pipeline only — ignore the Finance Bot / OAuth thread for now, that will come separately.

## Do this — one command, then stop and report

Run this single command exactly as written:

```bash
{ echo "--- crontab ---"; crontab -l | grep meridian; echo "--- log tail ---"; tail -50 /Users/sleeperservice/logs/meridian-daily.log 2>&1; echo "--- hermes daemon ---"; pgrep -fl hermes; echo "--- manual run ---"; /Users/sleeperservice/meridian-daily.sh; } > /tmp/meridian-diag.txt 2>&1; cat /tmp/meridian-diag.txt
```

**Do not interpret, fix, or take any further action based on what this shows.** Just capture the raw output.

## Then

1. Push the full contents of `/tmp/meridian-diag.txt` verbatim to `loop/2026-06-28-01.md` in this repo.
2. Telegram Tomasz: "Daily pipeline diagnostic run — pushed to loop/2026-06-28-01.md. [one-line summary, e.g. 'cron missing' / 'script errored' / 'ran clean, file should be in daily/ now']."
3. Stop. Wait for the next instruction — do not attempt a fix yourself, even if the cause looks obvious.

This is deliberately a single atomic command. If the manual run at the end of the chain succeeds, today's `daily/2026-06-28.md` should appear in the repo as a side effect — that alone would confirm the script itself still works and the problem is scheduling, not the script.
