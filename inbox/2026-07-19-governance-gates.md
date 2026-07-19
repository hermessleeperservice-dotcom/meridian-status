# Authorisations — 2026-07-19 — Governance Gates

Execute in this order. Do not merely acknowledge — perform each task and write one completion report per task to `loop/`, verified against `agent.log`, not UI summaries.

**Before anything: `git pull` in the meridian-status clone.**

Read `GOVERNANCE.md` at repo root first — it defines the two gates below and is now canonical.

---

## Task 1 — Skill-patch audit (outstanding, do first)

1. Cross-reference every `skill_manage` action in `agent.log` to date against what it claims to have applied.
2. For each, record: timestamp, target skill, claimed outcome, actual outcome per log.
3. Note any skill currently live on disk that was self-patched and never reviewed.
4. Write findings to `loop/2026-07-19-skill-manage-audit.md`.

## Task 2 — Implement the self-patch gate

1. Modify `skill_manage` so it writes proposals to `skills/proposals/<date>-<skill-name>.md` instead of applying changes directly (see GOVERNANCE.md §2).
2. Confirm it no longer applies changes without a matching authorisation in `inbox/`.
3. Any skill it already self-patched (per Task 1) should get a retroactive proposal file for the record, even though it's already live.
4. Report to `loop/` with a `skill-gate` tagged filename, including a test: trigger a trivial skill edit and confirm it stops at proposal stage.

## Task 3 — Confirm the execution gate

1. Check `poll-worker.py` against GOVERNANCE.md §1: it should only log/pull on the 20-minute cycle, never act on task content, and never phrase acknowledgement commits in a way that implies completion.
2. If current commit messages ("auto-acknowledged new files") already satisfy this, just confirm and report — no code change needed.
3. Report to `loop/` with an `execution-gate` tagged filename.

---

Constraints: local model stays pinned to `qwen3:6`; `openrouter/auto` remains excluded.
