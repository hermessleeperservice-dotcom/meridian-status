# Authorisations — 2026-07-20 — Finance Bot Test & Scheduler

Execute in this order. Do not merely acknowledge — perform each task and write one completion report per task to `loop/`, verified against `agent.log`, not UI summaries.

**Before anything: `git pull` in the meridian-status clone.**

Repo: `~/Documents/Youtube/financebot`. Token confirmed working as of 2026-07-19 (`token.pickle` present, gitignored).

---

## Task 1 — Manual pipeline test run (do first)

1. Trigger the full pipeline manually: video generation → YouTube upload, using the existing `token.pickle`.
2. Confirm end-to-end success: video generated, upload API call succeeds, video appears on the channel (Wealth Secrets 1970).
3. Log any failure verbatim from `agent.log` — do not paraphrase errors.
4. Report to `loop/` with a `finance-bot-test` tagged filename.

## Task 2 — launchd scheduler (gate: only if Task 1 succeeds)

1. If and only if Task 1 confirms a full successful upload, set up a launchd job to run the pipeline on a recurring schedule.
2. Pin any inference calls involved to `qwen3:6`; `openrouter/auto` remains excluded.
3. Confirm the plist loads (`launchctl list` shows it) and document the schedule chosen.
4. Report to `loop/` with a `finance-bot-scheduler` tagged filename.

**If Task 1 fails:** do not proceed to Task 2. Report the failure to `loop/` and stop — flag it for the next session rather than guessing at a fix.

---

Constraints: local model stays pinned to `qwen3:6`; `openrouter/auto` remains excluded. Credentials never via git.
