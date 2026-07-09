# Resolve Duplicate Polling: Progress Report

_Date: 2026-07-09 ~14:55 BST. Actioned by Meridian (Hermes-native agent session)._

## Action taken
- **Removed the Hermes-native cron job `Meridian Inbox Poll` (`ef3c3ec4260d`, every 20m).**
  - Confirmed via `cronjob list` / `jobs.json`: only two jobs now remain — `Daily Serendipitous Learning` and `Daily Learning Delivery`. The inbox-poll job is gone.
  - This was also the job that had been **self-skipping with an error** since 10:01 BST (config-drift guard — see config-drift investigation). Removing it clears that error path entirely.

## launchd worker status (kept, per decision)
- `launchctl list | grep meridian` → `com.hermes.sleep.meridian-poll` present (loaded).
- Plist unchanged: `~/Library/LaunchAgents/com.hermes.sleep.meridian-poll.plist`, `StartInterval=1200` (20 min), `RunAtLoad=true`, runs `scripts/poll-worker.py`.
- **Health caveat:** `launchctl list` shows exit status `1` for the last run. Root cause is a benign bug in `poll-worker.py` (see below), NOT a poll failure — the worker still pulls, scans, commits, and pushes every run. It was observed successfully pushing `4cb8b1f` at 14:42:40.

## ⚠️ Discovered defect: poll-worker.py re-acks the same files every run
The worker's dedup logic is broken, causing it to re-process every inbox file on each 20-min cycle and create duplicate `loop/` ack entries. Evidence: ack files exist for the identical sources at 14:02, 14:22, AND 14:42 today.

**Mechanism:**
- Source token for `inbox/2026-07-09-finance-bot-clone-repo.md` = itself (`2026-07-09-…` does not match the `_RUNPREFIX` regex `^\d{4}-\d{2}-\d{2}-\d{4}-`, because after the date comes `-finance`, not `-HHMM`).
- Ack token for `loop/2026-07-09-1442-inbox-2026-07-09-finance-bot-clone-r…` = stripped to `inbox-2026-07-09-finance-bot-clone-r…`.
- These tokens never match, so the source is always seen as "new" → re-acked each run.

**Secondary bug (causes the exit-1):** in the `finally` block, `fcntl.flock(lock.fileno(), LOCK_UN)` runs after the `with open(...) as lock:` context has already closed the file → `ValueError: I/O operation on closed file`. Harmless to function, but makes `launchctl` report exit 1.

**Scope note:** The inbox item said keep the launchd worker as-is and don't touch the plist. The script `poll-worker.py` is a separate file. Fixing the dedup is arguably in-scope (it's precisely the "double-processing acked files" risk the item cites), but I did **not** modify it — reporting for decision. Suggested one-line fix: key the loop-token map on the *source* filename (strip run-prefix from the inbox name the same way) rather than the generated ack name.

## Actions taken vs not taken
- ✅ Removed Hermes-native cron inbox-poll job.
- ✅ Confirmed launchd worker still loaded/running.
- ❌ Did not modify the plist (per explicit instruction).
- ❌ Did not patch poll-worker.py (out of explicit scope; flagged above).

## Next step
Await Tomasz's decision on the poll-worker.py dedup/exit-1 fix (recommend patching).
