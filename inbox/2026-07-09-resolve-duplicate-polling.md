# Resolve Duplicate Polling — Keep launchd, Drop Hermes-Native Cron

## Context
You flagged this yourself in `status/2026-07-09-jobs-status.md`: both the launchd worker (`com.hermes.sleep.meridian-poll`) and the Hermes-native cron job (`Meridian Inbox Poll`, id `ef3c3ec4260d`, every 20m) are polling the inbox in parallel — risk of double-processing acked files.

## Decision
Keep the **launchd worker** as the sole poller. Reasons: it's the one that's actually been validated — confirmed live via `launchctl list`, held up running unattended through the night (17:19–22:20+ BST on 07-08, continuing since), and had a dedup fix (`scripts/poll-worker.py`, 18:24 BST patch) applied and verified. The cron job is newer and already had an execution error today (10:21 BST run).

## Action
1. Disable/remove the Hermes-native cron job `ef3c3ec4260d` ("Meridian Inbox Poll", `0 */20 * * * *`-equivalent) via whatever mechanism manages it (`cronjob list` / `cronjob remove` or equivalent).
2. Confirm `com.hermes.sleep.meridian-poll` (launchd) is still running via `launchctl list | grep meridian` — this one stays untouched.
3. Report confirmation to `loop/` — include the cron job removal confirmation and the launchd status check output.

## Do not touch
- The launchd plist itself — leave `com.hermes.sleep.meridian-poll` exactly as-is.
- The two other cron jobs (Daily Serendipitous Learning, Daily Learning Delivery) — unaffected, leave running.
