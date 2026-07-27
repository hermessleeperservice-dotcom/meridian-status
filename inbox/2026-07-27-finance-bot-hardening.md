# Finance Bot — failure detection and daily reporting

**Date:** 2026-07-27
**Repo under change:** `~/Projects/financebot` (branch `master`)
**Reporting repo:** `hermessleeperservice-dotcom/meridian-status` (branch `main`)

---

## Context — read before starting

The Finance Bot pipeline produced no videos between 19 and 26 July. launchd
recorded seven consecutive runs that exited **zero**. All seven produced
nothing. The outage was invisible for a week because the pipeline treats upload
failure as a warning, not an error.

The root causes are fixed. **The blindness is not.** These tasks fix the
blindness.

Two changes, in order:

1. Make the pipeline fail loudly when the upload does not produce a video.
2. Make every scheduled run write a report to `loop/` in this repo, whether it
   succeeded or failed.

Task 2 depends on Task 1. A reporting layer built on a pipeline that lies about
success will produce a daily report saying "success" while the channel stays
empty — the same outage with paperwork attached.

---

## Rules for this whole instruction

- **Path.** The repo is at `~/Projects/financebot`. Any reference anywhere to
  `~/Documents/Youtube/financebot` is stale. `~/Documents` is TCC-protected and
  launchd-spawned processes cannot read it.
- **Branch.** `master` is the only branch of the finance-bot repo. Verify with
  `git rev-parse --abbrev-ref HEAD` before any push. Do not create `main`.
- **Gating.** Do not begin a task until the previous task is complete and
  verified. If a task fails, **stop and report**. Do not improvise a fix, do not
  skip ahead, do not proceed to the next task.
- **No secrets in git.** Read the Telegram bot token from wherever the existing
  Hermes config holds it. Do not write a token into any file in either repo. Do
  not commit `token.pickle`, `client_secret*.json`, or `*.pickle`.
- **No uploads while testing.** Every test run in these tasks uses
  `--no-upload`, except where a step explicitly says otherwise. An accidental
  public upload already happened once on this project.
- **Evidence.** Every completion claim must carry the command you ran and its
  actual output. "Done" is not a report. Commit SHAs must be full 40-character
  hashes obtained from `git rev-parse HEAD`, not abbreviated or recalled.

---

## Task 1 — Make upload failure a real failure

### 1.1 Read the current behaviour

Open `finance_bot_v2.py`. Find the upload step (step 5 of 5) and the function
that calls the YouTube API. Identify:

- where an upload exception or error response is caught
- what is logged
- what the function returns
- what the script's exit code is on that path

Report these four things before changing anything.

### 1.2 Make the upload path assert a video ID

The YouTube Data API returns a response containing the new video's `id` on
success. That ID is the only trustworthy proof a video exists. A completed HTTP
call is not proof. A logged "upload finished" is not proof.

Change the upload function so that:

- On success it returns the video ID string.
- If the API call raises, or returns a response with no `id` field, it raises or
  returns a clear failure — not `None` swallowed by the caller.

### 1.3 Make the script exit non-zero on failure

In the top-level path that runs the daily job:

- If the upload step did not yield a video ID, log at `ERROR` level with the
  underlying exception or response, and `sys.exit(1)`.
- Only exit `0` when a video ID was obtained.
- `--no-upload` runs must still exit `0` on success. Do not make `--no-upload`
  look like a failure — it is the normal test path.

### 1.4 Add a Telegram alert on failure

On the failure path, before exiting non-zero, send a Telegram message to chat ID
`5109089813` using the existing bot.

Message content:

```
Finance Bot FAILED <ISO 8601 timestamp>
Stage: <generation | upload>
Error: <first line of the exception or API error>
Log: ~/Projects/financebot/launchd-daily-error.log
```

Requirements:

- Read the bot token from the existing Hermes configuration. Do not hardcode it
  and do not write it into the repo.
- Wrap the Telegram call in its own try/except. **If the alert fails to send,
  the script must still exit 1.** A broken alerting path must never suppress the
  failure exit code.
- Do not send a Telegram message on success. Daily green notifications train you
  to ignore them.

### 1.5 Verify Task 1

Run all four checks and record the actual terminal output of each:

1. **Success path.**
   `cd ~/Projects/financebot && python3 finance_bot_v2.py --generate daily --no-upload; echo "exit=$?"`
   Expect `exit=0`. No Telegram message.

2. **Forced upload failure.** Temporarily induce a failure in the upload path —
   for example by pointing the credential path at a non-existent file, or by
   raising inside the upload function behind a temporary
   `FINANCE_BOT_FORCE_UPLOAD_FAIL` environment variable. State clearly which
   method you used.
   Expect: `ERROR` in the log, one Telegram message received, `exit=1`.
   **Then revert the induced failure and confirm the revert with a diff.**

3. **Alert-failure isolation.** With the induced upload failure still active,
   break the Telegram send (e.g. invalid chat ID passed locally, not committed).
   Expect: still `exit=1`. Revert.

4. **Syntax and import check.**
   `python3 -c "import ast,sys; ast.parse(open('finance_bot_v2.py').read())"`

### 1.6 Commit Task 1

```
git add finance_bot_v2.py
git commit -m "finance-bot: fail loudly on upload failure — assert video ID, exit 1, Telegram alert"
git push origin master
git rev-parse HEAD
```

Record the full SHA.

**Gate: do not start Task 2 until Task 1 is committed, pushed, and all four
checks in 1.5 have passed with output recorded.**

---

## Task 2 — Daily run report committed to `loop/`

### 2.1 What this is

A shell script that runs after the daily job and writes what actually happened
to this repo. It is deliberately **not** an agent task. It must run and report
even when no Hermes session is live. If reporting depends on you being awake,
silence becomes ambiguous — it could mean "nothing happened" or "nobody was
home" — and that ambiguity is what made the July outage invisible.

### 2.2 Create the script

Create `~/Projects/financebot/report_daily_run.sh`, executable.

It must:

1. Read the exit code of the day's run. Get this by having the launchd wrapper
   write it — see 2.3 — or by parsing the tail of `launchd-daily.log`. State
   which approach you used and why.
2. Extract from today's log lines: the video ID if present, the stage reached,
   and the last `ERROR` line if any.
3. `cd` into a local clone of `meridian-status`, `git pull --rebase` **first**,
   then write `loop/YYYY-MM-DD-financebot-daily.md`.
4. `git add`, `git commit`, `git push origin main`.
5. Be idempotent — running it twice on the same day overwrites that day's file
   rather than creating a duplicate or failing.

Report file format — follow exactly:

```markdown
# Finance Bot daily run — YYYY-MM-DD

**Result:** SUCCESS | FAILED
**Exit code:** <n>
**Started:** <ISO 8601>
**Video ID:** <id or "none">
**Video URL:** <url or "none">
**Stage reached:** <generation | upload | complete>
**Last error:** <last ERROR line, or "none">

## Log tail

```
<last 20 lines of launchd-daily.log>
```
```

`Result: SUCCESS` is permitted **only** when a video ID is present. Exit code 0
alone is not sufficient — that is precisely the condition that hid the outage.

### 2.3 Schedule it

Create a launchd plist `com.hermes.financebot.report.plist` that runs the script
at **09:30** daily — 30 minutes after the generation job, leaving room for a
slow render or upload.

- Commit the plist to `launchd/com.hermes.financebot.report.plist` in the
  finance-bot repo, alongside the existing daily plist.
- Install to `~/Library/LaunchAgents/` and load it.
- **The script and its working directory must live outside `~/Documents`.** This
  is the fault that caused the original outage. Confirm the path in your report.
- If you make the launchd wrapper write the exit code to a file for 2.2 step 1,
  put that file somewhere outside `~/Documents` too.

### 2.4 Verify Task 2

1. Run `bash ~/Projects/financebot/report_daily_run.sh` manually. Confirm a file
   appears at `loop/` in this repo and paste its full contents into your report.
2. Run it a second time. Confirm it overwrites rather than duplicating.
3. Confirm the plist is loaded:
   `launchctl list | grep financebot` — paste the output. Expect **two** entries.
4. Confirm no secrets were committed:
   `git log -p -1 | grep -iE "token|secret|api_key"` — expect no matches, or
   explain any match.

### 2.5 Commit Task 2

```
git add report_daily_run.sh launchd/com.hermes.financebot.report.plist
git commit -m "finance-bot: daily run report to meridian-status/loop"
git push origin master
git rev-parse HEAD
```

Record the full SHA.

---

## Task 3 — Repo hygiene (only if Tasks 1 and 2 are complete)

Three half-finished OAuth scripts are sitting in the repo:
`oauth_run.py`, `oauth_step1.py`, `oauth_step2.py`, plus `oauth_flow.pickle` and
`oauth_params.json`. Multiple auth paths risk minting tokens against
inconsistent clients or scopes — a live cause of the kind of token failure that
already bit this project.

1. Add to `.gitignore`: `*.pickle`, `oauth_params.json`, `client_secret*.json`.
2. **Do not delete `token.pickle`.** It is the live credential.
3. Report which of the three `oauth_step*.py` scripts was the one that actually
   produced the working token on 26 July, if determinable from file mtimes.
   **Do not delete any of them** — list them and stop. Deletion is my decision,
   not yours.

There is also an unuploaded artefact at
`finance_videos/finance_20260726_143636.mp4` from the failed 14:36 run on 26
July. Leave it in place. Report its size and mtime.

---

## Reporting

Write **one** file per task to `loop/`, as each task completes — not one file at
the end. If you stop early, the completed tasks are still recorded.

- `loop/2026-07-27-financebot-task1-fail-loudly.md`
- `loop/2026-07-27-financebot-task2-daily-report.md`
- `loop/2026-07-27-financebot-task3-hygiene.md`

Each must contain:

- **Status:** COMPLETE | PARTIAL | FAILED | NOT ATTEMPTED
- The full 40-character commit SHA from `git rev-parse HEAD`
- Every verification command from that task's verify section, with its **actual
  output pasted verbatim** — not summarised, not paraphrased
- Any file you changed, and the diff
- Anything you could not do, and why

### On failure

Stop. Write the loop report describing exactly where you stopped and what the
error was. Do not attempt an unspecified fix. Do not proceed to the next task.
A clean stop with a good report is more useful than a guess that half-works.

### On finishing

Confirm in the final report:

- `git rev-parse --abbrev-ref HEAD` in `~/Projects/financebot` returns `master`
- `git status --short` is clean in both repos
- `git branch -a` shows no `main` branch on the finance-bot repo
