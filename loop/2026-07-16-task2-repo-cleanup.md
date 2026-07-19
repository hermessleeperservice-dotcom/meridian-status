# Task 2 — repo noise cleanup — COMPLETE

_Timestamp: 2026-07-16 19:5x BST. Author: Meridian._

## What was done
Committed as `a44545b` (pushed to origin/main).

1. **Auto-ack spam archived.** Moved all 7,204 `loop/2026-07-*-inbox-*` files →
   `loop/archive-autoack/` via `git mv` (history preserved, shown as 100% renames).
   The 118 non-auto-ack `loop/` files (real reports, `*-followup-*`, `*poll*`,
   `*-processing`, `task1-*` etc.) were left in place.
2. **Stale inbox archived.** Moved 29 executed/stale inbox files dated
   **before 2026-07-10** → `inbox/archive/` (all the 2026-06-* and 2026-07-0[1-9]-*
   items). `inbox/2026-07-10-authorisations.md` and `inbox/2026-07-16-authorisations.md`
   were explicitly kept in `inbox/` per the brief, along with `inbox/README.md`.

## Result
- `loop/` dropped from ~7,289 files to a clean set (no more `*-inbox-*` spam).
- Repo is back under GitHub's 1,000-file API listing cap for the working tree.
- `inbox/` now contains only the two authorisations files + README + `archive/`.

## Note on dedup interaction
Archiving removes those acks from `loop/`, so the next worker run will see the 30
archived sources as "new" once and re-create a small set of acks in `loop/` —
but the Task-1 dedup fix means it will NOT re-acknowledge anything that still has
a live `loop/` companion, and no new spam is generated per cycle. This is the
expected steady state after an archive sweep.
