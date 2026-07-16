# Finance Bot — Clone Repo Onto Mac Studio

## Context
The financebot repo was never missing — it was never cloned here. It lives on GitHub at `hermessleeperservice-dotcom/finance-bot` (private). Confirmed from the Claude side that `finance_bot_v2.py` on `main` already has the correct OAuth call (`flow.run_local_server(port=0)`) — the `run_console()` regression (commit `e262a9b3`) is NOT in this repo, so no revert needed on the pushed code.

## Action
1. `git clone https://github.com/hermessleeperservice-dotcom/finance-bot.git ~/Documents/Youtube/financebot` (use existing `gh` auth under `hermessleeperservice-dotcom`).
2. Confirm `finance_bot_v2.py` contains `flow.run_local_server(port=0)` (not `run_console()`) — sanity check against what's on GitHub.
3. Run `python3 finance_bot_v2.py --setup` and report the dependency check output (edge-tts, Pillow, google-auth-oauthlib, ffmpeg, etc.) to `loop/`.
4. Do NOT attempt OAuth yet — `client_secret.json` is not in the repo (correctly gitignored) and is not on this machine. Tomasz needs to transfer it via AirDrop or scp — never via git. Hold here and report setup status.

## Do not touch
- Commit `e262a9b3` / `run_console()` — irrelevant to this repo, leave as-is wherever it lives.
- No OAuth flow execution until `client_secret.json` is confirmed present.
