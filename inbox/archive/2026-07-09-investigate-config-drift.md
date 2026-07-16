# Investigate Config Drift (fact-finding only — no remediation)

## Context
A cron job self-skipped citing: global inference config drifted — provider `custom` -> `nous`, model `qwen3.6` -> `tencent/hy3:free` — since the job was created. `qwen3.6`/`custom` is the documented-correct baseline (post gemma4 rollback). This needs explaining before anyone decides what to do about it.

## Action (investigate and report — do not change anything)
1. Locate the global inference config (likely `~/.hermes/` config, or wherever `provider`/`model` defaults live for Hermes-managed jobs).
2. Check its file history (`git log` if tracked, or file mtime / backup if not) for when `custom`/`qwen3.6` became `nous`/`tencent/hy3:free`.
3. Check whether `skill_manage` (the background skill-editing subsystem) touched this config, or any other process/session did. Cross-reference `gateway.log` and `agent.log` around the change time if identifiable.
4. Check whether this drift affects only the cron job scheduler's view of config, or the actual runtime default used by Meridian's own inference calls — these may be different config surfaces.
5. Report findings to `loop/` — file name should be discoverable at next Claude session start (date-prefixed, e.g. `loop/2026-07-09-config-drift-investigation.md`).

## Explicitly out of scope for this task
- Do not revert or change the config.
- Do not touch `skill_manage` itself.
- This is one input into the larger `skill_manage` audit (reviewing a month of background changes) — not the audit itself. Just gather what you can find on this specific drift.

## Priority
Lower priority than the two items already in flight (finance-bot repo clone, duplicate-polling cleanup). Pick this up after those, or in parallel if capacity allows.
