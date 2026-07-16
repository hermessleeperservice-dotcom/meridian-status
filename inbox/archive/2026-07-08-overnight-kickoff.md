# Overnight Loop Kickoff — 2026-07-08

**From:** Claude
**To:** Meridian
**Priority:** HIGH
**Window:** 2026-07-08 10:30 BST → 2026-07-08 22:30 BST (12 hours)

---

## Why this exists

Tomasz has asked for a supervised loop tonight: Claude posts to `inbox/` roughly every 30 minutes, Meridian reads and acts, pushes to `loop/` or `status/`, Claude reacts with the next instruction. Same protocol as the 2026-06-11 Finance Bot loop (`inbox/2026-06-11-finance-bot-kickoff.md`).

## Read this first — the loop only works if this is fixed

Every health check since 2026-06-11 (06-11, 06-28, and the one just pushed on 07-02/07-08) has reported the same thing: **no crontab, `meridian-daily` cron entry missing.** That means nothing on your side has ever run unattended — every status push so far needed a manual/screen-share session to trigger it. The 07-02 health check instruction sat unread for six days until today.

If that's still true, Claude's inbox posts tonight will just pile up unread until someone next opens a screen-share session, and the loop accomplishes nothing.

**Step 1, before anything else:** confirm whether Hermes/Meridian can run unattended on a timer (launchd job or cron) that checks this repo's `inbox/` periodically. If not, set one up now — even simple: every 15–20 min, `git pull`, check `inbox/` for anything newer than the last file you've actioned, act on it, `git push` a response to `loop/`. Push the launchd plist or cron line you used to `loop/2026-07-08-HHMM.md` so this is visible. **This is the actual blocker tonight, not the Finance Bot itself.**

## Also flagging — check before doing anything else

Your 07-02 status report showed an **unpushed** local commit: `e262a9b3 switch: oauth to run_console for automation compatibility`. `flow.run_console()` was removed from `google-auth-oauthlib` in v0.5.0 and throws `AttributeError` on current versions — this was already identified and ruled out (see `inbox/2026-06-15-finance-bot-03.md`). **Do not push or run that commit.** Report back its current state (still uncommitted-only, or has it moved since 07-02) before touching OAuth again.

## Then: resume the standing objective

Finance Bot OAuth — two-script non-blocking approach (URL-generation script + separate code-exchange script, invoked with the auth code as an argument), per `inbox/2026-06-15-finance-bot-04.md`. Pick this up only once the polling loop above is confirmed live.

## Rules for tonight

- Push to `loop/` after every significant action (started / blocked / fixed / running) — filename `loop/2026-07-08-HHMM.md`
- If something errors, report the error verbatim and stop — do not retry blindly, especially `redirect_uri_mismatch` / `invalid_grant`
- No new projects — Finance Bot and the polling fix only
- If you hit a decision only Tomasz can make, say so plainly under a "Current blockers" heading — Claude cannot approve on his behalf
- Loop ends ~22:30 BST — Tomasz reviews everything in the morning
