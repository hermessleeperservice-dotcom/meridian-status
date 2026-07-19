# Governance — Execution Gate & Self-Patch Gate

Canonical rules. If any skill, script, or session behaves differently from this file, this file wins — fix the behaviour, not the doc.

---

## 1. Execution Gate

`inbox/` holds two kinds of file. They must be visually and mechanically distinguishable — no judgement call at read time.

- **`*-authorisations.md`** — contains explicit imperative instructions ("Execute...", "Apply...", numbered tasks). This is the ONLY file type `poll-worker.py` or a live Hermes session may act on.
- Anything else in `inbox/` (notes, proposals, FYIs) is informational. `poll-worker.py` acknowledges its existence (logs it, does not error) but takes no action on its content.

**Hard rule:** `poll-worker.py` running on the 20-minute launchd cycle NEVER executes task content — its only job is to detect, log, and `git pull`. Acknowledgement (a commit saying "new file seen") is not execution and must never be reported or logged in a way that could be mistaken for task completion. Actual execution requires a live Hermes session, triggered via Telegram, with explicit action language from Tomasz or Claude.

**Completion reporting:** every executed authorisation gets one `loop/` file per task, project-tagged, stating what was verified (log output, file existence, commit SHA) — not what the UI claimed. Self-reported UI success is not sufficient evidence; see incident precedent (skill patch reported successful in UI, `agent.log` showed three refusals).

## 2. Self-Patch Gate (`skill_manage`)

`skill_manage` must not create or modify a skill directly. Effective immediately:

1. On any proposed skill creation/edit, `skill_manage` writes a proposal file to `skills/proposals/<date>-<skill-name>.md` containing: the diff or new file content, the reason, and any risk it introduces (new tool access, new autonomy, new external calls).
2. It does NOT apply the change. It logs the proposal to `agent.log` and stops.
3. The proposal is only applied after an explicit authorisation appears in `inbox/` referencing that proposal filename.
4. Once applied, the live skill file is committed to `skills/<skill-name>/` in this repo — self-modified skills must be visible here, not only on local disk. A skill that only exists on the Mac Studio and never lands here is out of policy.

**Outstanding action:** full audit of `skill_manage` activity prior to this gate — cross-reference every patch it claims to have made against `agent.log` to confirm what was actually applied versus attempted/refused. Write findings to `loop/` as `<date>-skill-manage-audit.md`. Do this before trusting any pre-existing self-patched skill.

---

Last updated: 2026-07-19.
