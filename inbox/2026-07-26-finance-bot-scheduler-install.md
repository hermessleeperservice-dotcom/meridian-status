# SUPERSEDED — do not execute

This task was resolved directly on the Mac Studio on 2026-07-26 before Meridian
picked it up. **Do not action it.** All paths in the original are stale.

Outcome and root cause: `status/2026-07-26-finance-bot-scheduler-fixed.md`.

Summary:

- The launchd job was already installed and had been firing — and failing —
  every morning since 19 July. The original premise here (that it was never
  installed) was wrong.
- Root cause was macOS TCC blocking launchd-spawned processes from reading
  `~/Documents`, plus an expired OAuth refresh token.
- The repo has moved to **`~/Projects/financebot`**. Any instruction
  referencing `~/Documents/Youtube/financebot` will fail.
- Pipeline verified green end-to-end 2026-07-26 14:53:59 BST, video
  `EDt0o-qrejc`.

If you are reading this as a new inbox item: acknowledge and take no action.
