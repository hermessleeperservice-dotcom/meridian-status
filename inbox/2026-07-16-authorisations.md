# Authorisations — 2026-07-16

Execute in this order. Do not merely acknowledge — perform each task and write one project-tagged completion report per task to `loop/`.

**Before anything: `git pull` in the meridian-status clone.** Instructions pushed via the GitHub API are invisible until you pull.

---

## Task 1 — Fix poll-worker dedup bug (PRIORITY)

The patch written up in `loop/2026-07-09-1455-duplicate-polling-progress.md` was authorised but never applied. Since 09 July, every 20-minute poll cycle has re-acknowledged all inbox files as new and written ~15 junk files to `loop/`. The directory now exceeds GitHub's 1,000-file API listing cap.

1. Apply the dedup patch to `poll-worker.py` exactly as specified in that loop file.
2. Add a `git pull` step at the start of each poll cycle, before scanning `inbox/` (known gap — caused the June six-day silence).
3. Verify against `agent.log` that the patched worker runs one clean cycle with no re-acknowledgements. Log verification, not UI summary.

## Task 2 — Clean up repo noise

1. Move all `loop/` files matching `2026-07-*-inbox-*` auto-ack spam into `loop/archive-autoack/` (single commit, or a few batched commits).
2. Move executed/stale inbox files (everything dated before 2026-07-10) into `inbox/archive/`.
3. Leave `inbox/2026-07-10-authorisations.md` and this file in place until their tasks complete.

## Task 3 — Finance Bot OAuth

Repo is cloned; `client_secret.json` present; fix is on `main` of `hermessleeperservice-dotcom/finance-bot`.

1. `git pull` in the finance-bot clone.
2. Run the OAuth flow (`flow.run_local_server(port=0)`).
3. Send the Google auth URL to Tomasz via Telegram (chat ID 5109089813) and wait for the code.
4. On completion, confirm the token file exists on disk and log its path (never commit it — credentials never via git).
5. Report completion to `loop/` with a `finance-bot` tagged filename.

---

Constraints: local model stays pinned to `qwen3:6`; `openrouter/auto` remains excluded. No skill_manage self-patching during this session.
