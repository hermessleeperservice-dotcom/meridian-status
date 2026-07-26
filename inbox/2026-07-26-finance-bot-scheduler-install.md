# Authorisations — 2026-07-26 — Finance Bot Scheduler: Install & Prove

**You are already authorised.** The Task 1 gate from `inbox/2026-07-20-finance-bot-test-and-scheduler.md`
was satisfied on 2026-07-20 (upload `OiOPwpYV5YQ`, reported in
`loop/2026-07-20-finance-bot-test.md`). Task 2 was therefore unlocked at that point.
It has not been executed and no `finance-bot-scheduler` report exists in `loop/`.

Do not wait for a further go-ahead. Execute all tasks below now, in order, and write one
completion report per task to `loop/`. Verify every claim against `agent.log` and actual
command output — not UI summaries.

**Before anything: `git pull` in the meridian-status clone.**

Repo: `~/Documents/Youtube/financebot` (branch `master`).
Plist in repo at `launchd/com.hermes.financebot.daily.plist`.

---

## Task 0 — Establish ground truth (do first, report before acting)

Run and record verbatim output for each:

```
ls -la ~/Library/LaunchAgents/ | grep -i financebot
launchctl list | grep -i financebot
ls -la ~/Documents/Youtube/financebot/launchd-daily.log ~/Documents/Youtube/financebot/launchd-daily-error.log
log show --predicate 'process == "launchd"' --last 7d 2>/dev/null | grep -i financebot | tail -50
which python3 && /usr/bin/python3 --version
cd ~/Documents/Youtube/financebot && git log --oneline -3 && git status --short
```

State plainly: is the job installed, is it loaded, has it ever run? Do not infer — if a
command returns nothing, say it returned nothing.

Report to `loop/` tagged `finance-bot-scheduler-audit`.

## Task 1 — Install and load the job (gate: Task 0 shows it is not loaded)

If `launchctl list` already shows `com.hermes.financebot.daily`, skip to Task 2.

```
cd ~/Documents/Youtube/financebot && git pull
cp launchd/com.hermes.financebot.daily.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.hermes.financebot.daily.plist
launchctl list | grep financebot
```

If `bootstrap` errors because the job is already bootstrapped, `bootout` first and retry.
Record the exact exit codes. A loaded job shows a line with the label; capture it verbatim.

## Task 2 — Prove it actually fires under launchd (gate: Task 1 shows loaded)

Loading is not running. launchd runs jobs with a minimal environment, a different working
directory resolution, and no login shell — the most likely reason this pipeline works by hand
and not on schedule. Force a real run through launchd:

```
launchctl kickstart -k gui/$(id -u)/com.hermes.financebot.daily
```

Then wait 90 seconds and capture:

```
tail -100 ~/Documents/Youtube/financebot/launchd-daily.log
tail -100 ~/Documents/Youtube/financebot/launchd-daily-error.log
tail -50 ~/Documents/Youtube/financebot/finance_bot.log
```

This will upload a real public video. That is expected and authorised.

If it fails, capture the error verbatim and **stop**. Do not guess at a fix. The three
failure modes to distinguish between, and name explicitly if one occurs:

1. **Interpreter mismatch** — `/usr/bin/python3` (3.9) cannot import a dependency that the
   interactive `python3` can. Symptom: `ModuleNotFoundError` in the error log.
2. **PATH / ffmpeg** — video composition fails because `ffmpeg` is not resolvable from the
   plist's `PATH`. Symptom: failure at STEP 4/5.
3. **Credential path** — `token.pickle` not found or not refreshable under the launchd
   environment. Symptom: failure at STEP 5/5.

Report which one, with the verbatim traceback.

## Task 3 — Confirm the schedule will hold

Only if Task 2 succeeded:

1. Confirm `StartCalendarInterval` is 09:00 and state the machine's current timezone
   (`sudo systemsetup -gettimezone` or `date`).
2. Confirm the Mac Studio does not sleep: `pmset -g | grep -E 'sleep|hibernatemode'`.
   A LaunchAgent will not fire on a sleeping or logged-out machine.
3. Confirm the `sleeperservice` GUI session stays logged in across reboot
   (`sudo defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser` — report
   if unset).
4. State the exact next expected fire time.

Report Tasks 1–3 to `loop/` tagged `finance-bot-scheduler`, with the commit SHA of the
plist you installed from.

---

Constraints: local model pinned to `qwen3:6`; `openrouter/auto` remains excluded.
Credentials never via git. Do not modify `finance_bot_v2.py` in this session.
