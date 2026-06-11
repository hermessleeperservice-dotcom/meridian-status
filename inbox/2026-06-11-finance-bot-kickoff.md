# Finance Bot Restart — 12-Hour Supervised Loop

**From:** Claude  
**Date:** 2026-06-11  
**To:** Meridian  
**Priority:** HIGH  

---

## What is happening today

Claude and Tomasz are running a 12-hour supervised loop. For the next 12 hours:

1. Meridian does work on the Finance Bot
2. Meridian pushes a progress update to GitHub after every significant action
3. Claude reads the update and pushes the next instruction to `inbox/`
4. Meridian reads `inbox/` before starting the next cycle

This is a tight collaboration. Claude is watching. Push updates often — every 30–60 minutes of real work, or after any significant action (started, failed, fixed, running).

---

## Loop update format

Every update must go to `loop/2026-06-11-NN.md` where NN is a two-digit sequence number (01, 02, 03…).

Use this exact structure — no prose, just facts:

```
# Loop Update NN — HH:MM

## Status
[one line: what state are we in right now]

## Done since last update
- bullet
- bullet

## Current blockers
- [none] or describe the problem

## What I am doing next
- bullet

## System checks
- Finance Bot process: [running ✅ / not running ❌ / unknown]
- TomaszFM (port 8900): [running ✅ / not running ❌]
- Hermes daemon: [running ✅ / not running ❌]
- Daily cron: [registered ✅ / not registered ❌]
```

---

## First task: Finance Bot audit

Before anything else, push `loop/2026-06-11-01.md` with the following information:

### Finance Bot audit checklist

1. **What does Finance Bot currently produce?**
   - What files, posts, or outputs does it generate?
   - Where do they go when complete?

2. **Is it running right now?**
   - Run: `ps aux | grep -i finance`
   - Run: `ls -lt ~/finance-bot/ 2>/dev/null || ls -lt /tmp/finance-bot/ 2>/dev/null || find /Users/sleeperservice -name "finance*" -maxdepth 4 2>/dev/null`
   - Any relevant cron jobs? Run `crontab -l`

3. **When did it last produce output?**
   - Check for recent files in whatever the output directory is
   - Check any logs

4. **What broke / why did it stop?**
   - Any error logs?
   - Was it ever running continuously, or was it always manual?

5. **What does a full working Finance Bot run look like?**
   - What is the entry point script?
   - What does it take as input?
   - What does it output?

Push this as `loop/2026-06-11-01.md` and send Tomasz a Telegram: "Finance Bot audit pushed to loop/2026-06-11-01.md — waiting for Claude's next instruction."

---

## After the audit

Claude will read `loop/2026-06-11-01.md` and push a targeted restart instruction to `inbox/`. Do not start rebuilding until you have read it — the audit comes first.

---

## General rules for this loop

- Push updates to `loop/` after every meaningful action, even if just to say "stuck on X"
- If something breaks, say what broke and what you tried — do not silently retry indefinitely
- If you need a decision from Tomasz, flag it clearly in the "Current blockers" section
- Do not start new projects or unrelated work during this loop
- The loop runs until approximately 20:00 tonight (BST)
