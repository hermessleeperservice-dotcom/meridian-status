# Loop late-disable note — 2026-07-09

The `meridian-12h-loop` scheduled task was supposed to stop itself at 2026-07-08T22:30 BST (see `status/2026-07-08-overnight-summary.md`, which was written correctly at that time). The disable step evidently did not take effect: `list_scheduled_tasks` still showed the task `enabled: true` as of 2026-07-09T14:22 UTC (15:22 BST), with runs continuing every 30 minutes through the following day.

Evidence of continued activity after the intended stop:
- `status/2026-07-08.md`, `status/2026-07-09-config-drift-flag.md`, `status/2026-07-09-daily-status.md`, `status/2026-07-09-jobs-status.md`
- `inbox/2026-07-09-finance-bot-clone-repo.md`, `inbox/2026-07-09-investigate-config-drift.md`, `inbox/2026-07-09-resolve-duplicate-polling.md`

This run (fired 2026-07-09T14:22 UTC) has now explicitly called `update_scheduled_task` with `enabled: false` on `meridian-12h-loop` to stop further firings. No other action was taken this run — the overnight summary already covers the 07-08 window and was not rewritten.

Flag for Tomasz: the newer 07-09 status/inbox files above were generated outside the intended loop window and have not been reviewed against the original overnight-kickoff priority order. Worth a manual look before trusting them as current state.
