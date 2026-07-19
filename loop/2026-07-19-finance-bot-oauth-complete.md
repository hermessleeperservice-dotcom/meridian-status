# Task 3 — Finance Bot OAuth — COMPLETE

_Timestamp: 2026-07-19. Author: Meridian._

## What was done
1. **Repo located & pulled.** The finance-bot clone was at
   `~/Documents/Youtube/financebot` (not `~/finance-bot` as the brief assumed;
   remote is `hermessleeperservice-dotcom/finance-bot`). `git pull` returned
   "Already up to date" — the OAuth fix from `main` was already present locally.
2. **Auth flow executed.** Tomasz completed the OAuth on the Mac Studio directly
   (local run). The Telegram-URL relay path was abandoned — it had a broken
   `redirect_uri` and was explicitly not retried per instruction.
3. **Token confirmed.** `token.pickle` now exists at
   `~/Documents/Youtube/financebot/token.pickle`.

## Credential safety verification (never via git)
- `token.pickle` present on disk: **yes** — `1374 bytes`,
  `Jul 19 11:41`.
- Listed in `.gitignore` (`client_secret.json` and `token.pickle`): **yes**
  (`.gitignore:2:token.pickle`).
- Tracked by git (current tree): **no** (`git ls-files token.pickle` → 0).
- Ever committed to any branch/ref: **no** (`git log --all -- token.pickle` → 0).
- Shows in `git status --short`: **no** — correctly ignored, so it can never be
  pushed accidentally.

## Out of scope (per brief)
- `client_secret.json` is also gitignored and never committed.
- **launchd scheduler setup is deferred** to a separate future session — not
  performed here.

## Result
Finance Bot OAuth is fully authorised and the token is safely persisted on disk
outside version control. Task 3 is complete.
