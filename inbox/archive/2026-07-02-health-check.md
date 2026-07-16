# Instruction — Post-Recovery Health Check

**Date:** 2026-07-02
**Context:** Extended outage. Last confirmed report: 2026-06-28. Reported blocker: `ImportError: cannot import name 'build_tool_label' from 'agent.display'`, traced to gemma4 provider setup, blocking all tools.

## Do this, in order, once tools are functional again

1. **Confirm the fix holds.** State what was changed (reverted patch / restored file / rolled back to qwen3.6) and confirm no other imports in `agent/` are broken. Run whatever smoke test proves tool calls actually execute (not just that the process starts).

2. **Full health check** — run and report raw output for each:
   - `crontab -l` (is `meridian-daily` registered? — it was missing as of 2026-06-28)
   - `ps aux | grep -i hermes` (daemon confirmed running)
   - `git -C ~/.hermes/hermes-agent status` and `git log -1` (confirm clean tree, no stray uncommitted patches)
   - `git -C <finance bot path> status` if touched during recovery
   - disk space (`df -h`) and OpenRouter key validity (`curl` against `/api/v1/key`)

3. **Push a status file** to `status/2026-07-02.md` in this repo — not just a loop entry — summarising: what broke, what fixed it, current state of each item above, and whether the gemma4 migration is being retried or shelved.

4. **Do not start anything new.** Finance Bot OAuth is still the standing objective. Once health check is clean, resume there — do not pick gemma4 work back up without an explicit go-ahead.

## Explicitly not required right now
Do not re-attempt the gemma4 provider switch as part of this instruction. Get back to a known-good baseline first.
