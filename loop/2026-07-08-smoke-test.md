# Smoke Test — 10:50 BST

## Pull confirmed
**yes** — pulled at 10:50, saw inbox/2026-07-08-loop-smoke-test.md and inbox/2026-07-08-overnight-kickoff.md via Fast-forward fb2b02a..941db6d

## Skill path
/Users/sleeperservice/.hermes/skills/devops/inbox-poll/SKILL.md

**First 5 lines:**
```
---
name: devops/inbox-poll
description: Poll ~/meridian-status for new inbox instructions, execute them, push results
category: devops
---
```

## Push mechanism
- `git push origin main` = actual Git push to the remote (moves files)
- Cron `deliver='origin'` = message delivery back to chat thread (moves messages)
- **Both are live and functional** in this session

## Cron type
Hermes internal scheduler (NOT OS-level crontab/launchd). Runs via Hermes gateway daemon.

### Cron survives without open session?
**Yes.** Confirmed: the gateway is supervised by launchd (PID 1482). As long as the gateway process stays running, the cron fires autonomously — no chat session or screen required. The cron will run every 20m regardless of whether Claude or Meridian has an open conversation.

## Proof status
Smoke test file created and committed locally. Now pushing to origin/main...
