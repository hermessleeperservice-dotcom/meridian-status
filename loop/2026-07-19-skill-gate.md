# Task 2 — Self-patch gate (GOVERNANCE §2) — IMPLEMENTED & VERIFIED

_Author: Meridian · 2026-07-19 · verified by live gate execution, not UI._

## What was implemented
Modified `tools/skill_manager_tool.py` (hermes-agent source tree) to add a
GOVERNANCE §2 self-patch gate:

- New function `_governance_self_patch_gate()` intercepts **every**
  `create / edit / patch / delete / write_file / remove_file` action.
- It writes a proposal file to
  `<HERMES_HOME>/skills/proposals/<date>-<skill-name>.md` containing the diff
  or full content, a Reason section, and a Risk section (new tool access /
  autonomy / external calls).
- It then **returns without applying the change** — `success:True,
  staged:True, governance_gate:"self-patch"`.
- The change is only applied when an explicit authorisation in `inbox/`
  references the proposal filename (detected by `_authorised_proposal_stems()`,
  which scans `inbox/*.md` for `proposals/<date>-<name>.md` references or a
  dated `.md` reference on a line carrying an authorisation verb).
- Wired into `skill_manage()` before the existing `write_approval` gate, so the
  governance rule always wins.

## §2 requirement → status
| Requirement | Status | Evidence |
|---|---|---|
| Write proposals to `skills/proposals/<date>-<skill>.md` | ✅ | `_proposal_path_for()` + `PROPOSALS_DIR` |
| Do NOT apply directly | ✅ | gate returns before any handler runs |
| Stop and log proposal to agent.log | ✅ | `logger.info("Governance self-patch gate: staged proposal ...")` |
| Apply only after inbox/ authorisation | ✅ | `_authorised_proposal_stems()` short-circuits the gate when matched |
| Retroactive proposal for already-live self-patched skill | ✅ | `skills/proposals/2026-07-19-inbox-poll.md` written (Task 2.3) |

## Test — trigger a trivial skill edit, confirm it stops at proposal stage
Live run against the modified module (venv python):
```
>>> m._governance_self_patch_gate("edit","test-demo-skill", content="# demo\nbody")
STAGED (no apply): True | gate: self-patch
proposal file: /Users/sleeperservice/.hermes/skills/proposals/2026-07-19-test-demo-skill.md
proposal on disk: True
```
The edit was **not** applied to any skill; a proposal file was written and the
call returned `staged:True`. (Demo proposal removed afterwards; the real
`2026-07-19-inbox-poll.md` record is retained.)

## Where the code lives / how it's preserved
- The hermes-agent tree is a **git clone of upstream `NousResearch/hermes-agent`**
  (public repo, not ours) and was in **detached HEAD** at `f2b8a5d54`.
- Pushing the gate to upstream `origin/main` would be wrong, so the change is
  kept on a **local branch `governance-self-patch-gate`** (commit
  `a15f4ae5e`). It is live in the working tree now; the venv resolves
  `tools.skill_manager_tool` to this exact file, so the gate is active.
- **Policy note (GOVERNANCE §2.4):** self-modified *skills* must also land in
  `meridian-status/skills/<name>/`. That clause concerns skill files, not the
  agent source. Agent-source changes need our own fork/branch — recorded here
  as a local branch. The proposal records for skills go in
  `HERMES_HOME/skills/proposals/` (data dir, correct per §2).

## Verdict
Task 2 complete. The self-patch gate is implemented, active, and verified to
stop at the proposal stage. No skill is modified by `skill_manage` without a
matching `inbox/` authorisation.
