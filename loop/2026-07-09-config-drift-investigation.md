# Config Drift Investigation — Fact-Finding Report

_Date: 2026-07-09 ~14:55 BST. Actioned by Meridian (Hermes-native agent session). INVESTIGATION ONLY — no config changes made, per inbox instruction._

## The drift (current state of `~/.hermes/config.yaml`)
```
model:
  base_url: ''
  default: tencent/hy3:free
  provider: nous
```
The cron scheduler reported the job was created when global config was `provider: custom`, `model: qwen3.6` (unpinned), and flagged it as drifted → `nous` / `tencent/hy3:free`.

## Root cause: the v0.12 → v0.17 Hermes update rewrote the config
- A pre-update backup snapshot exists: `~/.hermes/state-snapshots/20260629-152908-pre-update/config.yaml` (timestamped with the 2026-06-29 update).
- **Pre-update (v0.12, `_config_version: 23`):**
  ```
  model:
    default: qwen3.6:latest
    provider: ollama-launch
  ```
  Also had `openrouter` provider, `fallback_providers: []`, full `terminal:`/`browser:`/`agent:` blocks.
- **Post-update (v0.17, `_config_version: 32`):**
  ```
  model:
    base_url: ''
    default: tencent/hy3:free
    provider: nous
  ```
  The update migrated the config to the new schema and **set the default model/provider to the new v0.17 baseline** (`nous` / `tencent/hy3:free`) — i.e. the documented default for a fresh v0.17 install, NOT `qwen3.6`/`custom`.

## Timeline (from `~/.hermes/logs/agent.log`)
- `2026-07-09 09:36:59` — `nous login completed` (device OAuth). First appearance of `nous` in logs.
- `2026-07-09 10:01:02` — cron scheduler **SKIPPED** job `ef3c3ec4260d` ("Meridian Inbox Poll"): _"global inference config drifted since creation (provider 'custom' → 'nous'; model 'qwen3.6' → 'tencent/hy3:free') and this job is unpinned. Skipped to prevent unintended spend."_
- `2026-07-09 10:30:06` — gateway (re)started and began serving on `provider=nous base_url=https://inference-api.nousresearch.com/v1 model=tencent/hy3:free`. All subsequent agent turns (incl. this one) run on that config.

## Was `skill_manage` / any process responsible?
- No evidence `skill_manage` (or any background process) edited `config.yaml`. The change is the **update migration**, not a runtime/skill edit.
- `~/.hermes` is **not a git repo**, so no `git log`; mtime of `config.yaml` = `Jul 9 09:37`, consistent with the gateway restart after the 09:36 nous login / config rewrite.
- The "provider `custom`" the scheduler cites is the job's *creation-time* snapshot; the job was created under the older config and the unpinned job inherits "current global" at run time, tripping the anti-spend guard on mismatch.

## Two different config surfaces (inbox §4)
1. **Runtime default** (what Meridian's own inference calls actually use): `nous` / `tencent/hy3:free` — confirmed active in `agent.log` and in this session's own model line.
2. **Cron scheduler's job view**: jobs capture provider/model at *creation*; unpinned jobs compare against current global and self-skip on drift. That's the surface that errored — and is now moot because the job (`ef3c3ec4260d`) has been **removed** (see duplicate-polling report).

## Conclusion
The drift is **expected behavior of the v0.12→v0.17 upgrade**, not corruption or an errant process. The `qwen3.6`/`custom` "baseline" referenced in the inbox corresponds to the *pre-update* config; the post-update correct baseline is `nous`/`tencent/hy3:free` (the v0.17 default). No remediation warranted unless Tomasz wants to pin a specific model.

## Out of scope (honored)
- Did NOT revert/change `config.yaml`.
- Did NOT touch `skill_manage`.
- This is one input to the larger `skill_manage` audit, not the audit itself.

## Recommended follow-up (for Tomasz)
If you want the cron jobs to use a specific model rather than inheriting global, pin them explicitly (`cronjob update … provider=… model=…`). Otherwise, with the inbox-poll job removed, no job is affected by the drift guard.
