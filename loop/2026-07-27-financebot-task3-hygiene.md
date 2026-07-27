# Task 3 — Repo hygiene

**Status:** COMPLETE

**Commit SHA (full 40-char, pushed to finance-bot@master):**
`c76c5cb70752beabbdc121fff9466b00f4066751`

## 3.1 — .gitignore additions

Added (preventive — see 3.3 evidence that some of these files are absent on disk):

```
# Task 3 hygiene: prevent accidental credential/secrets commits.
*.pickle
oauth_params.json
client_secret*.json
```

Verification (`git check-ignore -v`):
```
.gitignore:8:*.pickle            token.pickle
.gitignore:8:*.pickle            oauth_flow.pickle
.gitignore:9:oauth_params.json   oauth_params.json
.gitignore:10:client_secret*.json client_secret.json
.gitignore:10:client_secret*.json client_secret_dev.json
```
`token.pickle` (the live credential) remains ignored and **was NOT deleted**. ✓

## 3.2 — Do NOT delete token.pickle

Confirmed present and untouched:
```
1375 token.pickle
```
Per instruction, left in place as the live credential. ✓

## 3.3 — Which oauth_step*.py produced the working token (mtime analysis)

Three scripts can write `token.pickle`:
- `oauth_run.py` — `flow.run_local_server(port=0)` → `pickle.dump(creds, …)`.
- `oauth_step2.py` — redeems the auth code left by `oauth_step1.py` → `pickle.dump(creds, …)`.
- `oauth_step1.py` — writes `oauth_params.json` only (no token).

**Determination: NOT determinable from file mtimes.** All three scripts carry stale
mtimes (oauth_step1.py / oauth_step2.py: 2026-07-10 23:00; oauth_run.py: 2026-07-16
19:48). None was modified on 2026-07-26 — the date the working token was minted. The
live `token.pickle` itself shows mtime 2026-07-27 09:00, which is an artefact of this
session's `git reset --hard origin/master`, not the original mint time. With no script
edit on the 26th and no other provenance signal in the repo, the responsible answer is
"cannot be determined," not a guess. All three scripts are left in place (instruction:
list and stop; deletion is the human's decision).

Additional evidence: `oauth_flow.pickle` and `oauth_params.json` named in the brief are
**ABSENT** from the working tree (`ls` → not found). The `.gitignore` additions for them
are therefore preventive against future creation.

## Unuploaded artefact (left in place, reported only)

```
-rw-r--r--  1 sleeperservice  staff  3020938  Jul 26 14:36  finance_videos/finance_20260726_143636.mp4
```
Size 3,020,938 bytes; mtime 2026-07-26 14:36 — matches the failed 14:36 run on 26 July.
Per instruction, left in place. Not deleted, not uploaded. ✓

## Files changed
- `.gitignore` (+4 lines)

## Could not do / notes
- Could not attribute the working token to a specific `oauth_step*.py` from mtimes;
  reported honestly rather than guessing (see 3.3).
- No deletions performed of any kind (token.pickle, oauth_*.py, or the unuploaded mp4),
  per explicit instruction.
