# Authorisations — 2026-07-10 (from Tomasz via Claude)

Three outstanding decisions from the 2026-07-10 00:50 consolidated status, all approved. Proceed with all three.

## 1. Finance Bot OAuth — proceed now
Go ahead and run the two-script OAuth flow (URL-generation script, then code-exchange script taking the auth code as an argument) against the existing `~/Documents/Youtube/financebot/client_secret.json`. Send the auth URL to Tomasz via Telegram when ready — he'll complete the Google auth step and reply with the code. Confirm `finance_bot_v2.py` still uses `run_local_server(port=0)` (not `flow.run_console()`) before running. Do not commit `client_secret.json` or any token file to GitHub — local disk only.

## 2. poll-worker.py dedup bug — patch approved
Apply the fix already written up in `loop/2026-07-09-1455-duplicate-polling-progress.md` (source-token vs ack-token regex mismatch, plus the double-close in the `finally` block). After patching, confirm `launchctl list` for `com.hermes.sleep.meridian-poll` reports exit status 0, not 1, over the next couple of cycles before declaring this resolved.

## 3. Model pinning for cron jobs — pin to qwen3.6 local
Pin scheduled/cron jobs (inbox-poll, health checks, etc.) to `qwen3.6` explicitly in their configs rather than inheriting whatever `~/.hermes/config.yaml`'s global default happens to be after a Hermes version migration. This avoids a repeat of the 2026-07-09 config-drift situation where a Hermes update silently changed the default model. Do not use `openrouter/auto` — confirmed credential-burning misconfiguration from before.

---

Report back in `loop/` when each is done (or blocked), one entry per item is fine. No need to touch `meridian-12h-loop` — that's a Cowork-side scheduled task issue on Claude's end, not something for Meridian to action.
