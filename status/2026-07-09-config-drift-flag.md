# Config Drift — Flagged for skill_manage Audit (not yet investigated)

## Finding (source: Telegram cron-failure notice, 2026-07-09 10:41 BST)
The `Meridian Inbox Poll` cron job (`ef3c3ec4260d`) self-skipped rather than running, with this reason:

> global inference config drifted since this job was created (provider 'custom' -> 'nous'; model 'qwen3.6' -> 'tencent/hy3:free')

This is a **safety-good outcome** (job refused to silently run on different/costlier config) but the drift itself is the concerning part: `qwen3.6`/`custom` was the documented-correct baseline post the gemma4 rollback. Something changed it without a recorded decision.

## Status
Not investigated yet. Queued to fold into the standing **`skill_manage` audit** (reviewing what the background skill-editing subsystem has modified over the past month) rather than chased as a one-off — same category of problem: config/state changing without visibility or approval.

## For next Claude session
Check `loop/` for the investigation entry below before deciding how to proceed with the audit. Do not action remediation until the audit session happens.
