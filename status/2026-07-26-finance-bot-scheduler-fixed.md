# Status — 2026-07-26 — Finance Bot daily scheduler fixed

_Author: Tomasz + Claude, working directly on the Mac Studio. Not a Meridian
execution report — `loop/` remains Meridian's channel and has no entry for this._

## Outcome

The daily Finance Bot job now runs. Verified end-to-end 2026-07-26 14:53:59 BST:
video `EDt0o-qrejc` uploaded to Wealth Secrets 1970.

## Why no videos appeared 19–26 July

Three faults stacked. Each one masked the next.

### 1. Wrong initial diagnosis — the job *was* installed

Session opened by reading `loop/`, found nothing after
`2026-07-20-finance-bot-test.md`, and concluded the launchd job had never been
installed. Wrong. `launchctl bootstrap` returned `Bootstrap failed: 5`, which
means *already bootstrapped*, and `launchd-daily-error.log` held eight failure
entries — one per morning since 19 July.

**Correction to a standing principle.** "`loop/` is ground truth" holds for what
Meridian *reports*, but absence of a report is not evidence of absence of
execution. Meridian executed Task 2 and never reported it. Check the machine
before concluding from the repo.

### 2. macOS TCC blocked the script (the actual seven-day outage)

```
/usr/bin/python3: can't open file 'finance_bot_v2.py':
[Errno 1] Operation not permitted
```

`~/Documents` is TCC-protected. launchd-spawned processes inherit no grant, so
the interpreter could not open the script — the pipeline never reached step 1.
Interactive runs worked because Terminal.app holds its own Documents grant,
which is exactly why this presented as a scheduler fault.

Fixed by moving the repo out of the protected tree:

```
~/Documents/Youtube/financebot  ->  ~/Projects/financebot
```

Full Disk Access for `/usr/bin/python3` was rejected as the alternative:
that path is an `xcode-select` shim, and the error log shows its target drifted
from `CommandLineTools` to `Xcode.app` mid-outage. A grant tied to one binary
would not follow the other.

Plist corrected and committed: `finance-bot@b796da6`.

### 3. OAuth refresh token expired

With TCC beaten, the run reached step 5/5 and failed:

```
[ERROR] YouTube auth error: ('invalid_grant: Token has been expired or revoked.')
```

Token issued 19 July, dead by 26 July — a seven-day life. Initial hypothesis was
that the OAuth client sat in Testing publishing status, which carries a seven-day
refresh-token expiry. **Disproved:** the console shows *In production*, External,
0/100 user cap.

Working hypothesis: the token was minted while the app was still in Testing and
kept its seven-day fuse; publishing afterwards does not retroactively extend
tokens already issued. Re-auth under production status should therefore yield a
long-lived token.

**This is unproven.** Alternative causes if it recurs: the app was removed from
the Google account's third-party access list, or the 100-live-refresh-tokens
per user/client ceiling silently invalidating the oldest.

## Open — must be checked on or after 4 August

Whether the token issued today survives past day seven. If it dies around
2–3 August, publishing status was not the cause and the other two branches
need working. **Nothing before 4 August tells us anything.**

## Known weaknesses, not fixed today

1. **Silent failure.** On upload failure the pipeline logs `WARNING` and exits
   zero. launchd recorded seven consecutive "successful" runs that produced
   nothing. Needs a non-zero exit and a Telegram alert on upload failure. This
   is the reason the outage ran a week undetected — it matters more than any
   individual fault above.
2. **Interpreter is an unpinned shim.** `/usr/bin/python3` resolves via
   `xcode-select` and demonstrably moved during the outage. Both targets are
   3.9.6 sharing `~/Library/Python/3.9` user site-packages, so it works today.
   Pin to an absolute binary if it drifts again.
3. **Untracked OAuth cruft** in the repo: `oauth_run.py`, `oauth_step1.py`,
   `oauth_step2.py`, `oauth_flow.pickle`, `oauth_params.json`. Three
   half-finished auth paths is a live risk of minting tokens against
   inconsistent clients or scopes. Delete or gitignore.
4. **Unuploaded artefact** at `finance_videos/finance_20260726_143636.mp4` from
   the failed 14:36 run.

## Path change — affects all future instructions

Finance Bot is at **`~/Projects/financebot`**. Any instruction referencing
`~/Documents/Youtube/financebot` is stale and will fail under launchd.

`inbox/2026-07-26-finance-bot-scheduler-install.md` was superseded before
Meridian picked it up.
