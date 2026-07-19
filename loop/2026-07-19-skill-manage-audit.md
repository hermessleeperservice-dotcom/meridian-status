# Task 1 — Skill-patch audit (outstanding, GOVERNANCE §2)

_Author: Meridian · 2026-07-19 · verified against `agent.log`, not UI._

## Scope & method
- Log: `/Users/sleeperservice/.hermes/logs/agent.log`
- Coverage: `2026-07-09 09:13:27` → `2026-07-19 18:55:33` (10 days)
- Every `skill_manage` tool_executor line cross-referenced. Outcome taken from
  the structured `completed` / `returned error` log lines — **not** from any
  model self-report. This is the exact failure mode GOVERNANCE.md warns about
  ("skill patch reported successful in UI, agent.log showed three refusals").

## Headline numbers
| Metric | Count |
|---|---|
| Total `skill_manage` tool events | 83 |
| Completed (success) | 46 |
| Returned error (refused / failed) | 33 |
| Distinct self-patch attempts **refused** | 5 skills, 15 refusals |

## Per-target record (every self-patch attempt = refused)

| Timestamp(s) | Target skill | Claimed | Actual (log) |
|---|---|---|---|
| 07-09 14:53 ×4, 14:54 ×2, 14:56 ×1 | `web-research-fallback` | "patch" | `Refusing background curator patch ... SKILL.md not loaded in review turn` (error) |
| 07-09 14:53 ×4, 14:54 ×2 | `oauth-pkce-headless` | "patch" | same refusal (error) |
| 07-09 14:53 ×4 | `daily-exploratory-learning` | "patch" | same refusal (error) + 1× `already exists` error |
| 07-09 14:53 ×2, 14:54 ×2 | `inbox-poll-traps` | "patch" | same refusal (error) |
| 07-09 14:53 ×2, 14:54 ×2 | `hermes-troubleshooting` | "patch" | same refusal (error) |
| 07-09 09:18 ×2, 14:53/54/56 | `devops/inbox-poll` | "create/patch" | `not found in active profile 'default'` (error) |
| scattered | various | "patch" | `Could not find a match for old_string` (×4), `Escape-drift detected` (×2), `file_content is required` (×6) |

**Conclusion on claimed-vs-actual:** ZERO self-patches were applied. Every
attempt either (a) hit the background-curator read-before-write guard and was
refused, or (b) failed to match the target. The curator never mutated a live
skill through `skill_manage`. The UI "completed" calls were all safe
create/review/view operations.

## Live self-patched skill (found OUTSIDE skill_manage)
`inbox-poll` is the **only** skill on disk whose content diverges from the
governed repo copy:
- Live: `/Users/sleeperservice/.hermes/skills/research/inbox-poll/SKILL.md`
  (mtime **2026-07-08 17:42**)
- Repo: `skills/inbox-poll/SKILL.md`, last committed at `e485e84`
  ("claude: add inbox-poll skill for Meridian") — structurally different
  (frontmatter vs `#` heading; different trigger/steps wording).
- It was **not** produced via a `skill_manage` call (no `inbox-poll` patch
  event succeeded; the only `inbox-poll` events are `devops/inbox-poll not
  found` errors from a wrong profile/path). It was edited by direct file write
  — which the old tooling did not gate. This is precisely why GOVERNANCE §2
  exists.
- **Action item (Task 2.3):** a retroactive proposal file has been written for
  it (see `skills/proposals/2026-07-19-inbox-poll.md`) so the change is on
  record even though it is already live.

## Skills currently live & their review status
| Skill | Location | Self-patched? | Reviewed? |
|---|---|---|---|
| `inbox-poll` | `~/.hermes/skills/research/` | YES (diverges from repo) | Never (no review turn logged) |
| `computer-use`, `dogfood`, `mlops-model-training`, `yuanbao` | `~/.hermes/skills/` | No | N/A |
| `web-research-fallback`, `oauth-pkce-headless`, `daily-exploratory-learning`, `inbox-poll-traps`, `hermes-troubleshooting` | bundled/hub | Attempted & refused | Refused by gate |

## Verdict
- No skill was silently self-patched through `skill_manage` — the curator
  refusals held.
- One skill (`inbox-poll`) is live on disk in a state that was never reviewed
  and never committed to the governed repo. It predates this gate. Retroactive
  proposal filed under Task 2.3.
- Net: the pre-gate behaviour was unsafe-by-design (direct file writes bypass
  the tool entirely); the §2 gate now closes that path for future writes.
