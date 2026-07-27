# Task 1 — Make upload failure a real failure

**Status:** COMPLETE

**Commit SHA (full 40-char, pushed to origin/master):**
`6764246e691d48c98e4f22da8ee73cc4de729395`

## 1.1 — Current behaviour reported (before changes)

| # | Question | Answer |
|---|----------|--------|
| 1 | Where exception/error caught | `upload_to_youtube()` L608–609 (`if not youtube: return False`), L650–652 (`except Exception: return False`). Gap: L645 `video_id = response.get('id', 'unknown')` — a 200 with no `id` silently became the string `'unknown'` and still `return True`. That was the lie that hid the outage. |
| 2 | What is logged | Exception → `logger.error("Upload error: {e}")`. Missing-id → nothing (just info line with `unknown`). From `generate_video`, failed upload was `logger.warning` (L747), not error. |
| 3 | What the function returns | `bool`: `True` even when `video_id == 'unknown'`; `False` on exception / missing service. |
| 4 | Script exit code on that path | Always `0`. `main()` L903–905 discarded the return and had no `sys.exit`. |

## 1.2 / 1.3 / 1.4 — Changes made

- `upload_to_youtube()` now returns the **video id string** on success, and raises
  `UploadError` when: the env hook `FINANCE_BOT_FORCE_UPLOAD_FAIL` is set, the YouTube
  service is unavailable, the API returns an empty response, or the response has no `id`
  (the exact outage case — previously swallowed as `'unknown'`). `UploadError` is derived
  from `Exception`, never silently `None`.
- `generate_video()` wraps the upload in `try/except UploadError` and re-raises as
  `PipelineFailure("upload", ...)`. Returns the video id string on success.
- `main()` `--generate` path now:
  - catches `PipelineFailure` (stage=upload) and bare `Exception` (stage=generation),
  - logs at `ERROR` level,
  - sends a Telegram alert to chat `5109089813` (read from `~/.hermes/.env`
    `TELEGRAM_BOT_TOKEN` at runtime — never hardcoded, never committed),
  - `sys.exit(1)`.
  - Exits `0` only when a video id was obtained, or on the `--no-upload` test path.
  - No Telegram message is sent on success.
- `send_telegram_alert()` reads the token from the existing Hermes `.env`, wraps the send
  in its own try/except, and `_failure_alert()` wraps it again so **a broken alert path
  can never suppress the exit-1 code**.
- Added `from __future__ import annotations` (host python is 3.9.6; union types like
  `str | None` would otherwise crash at import).

## 1.5 — Verification (actual output)

### Check 1 — Success path (`--no-upload`)
```
2026-07-27 09:48:00,311 [INFO] STEP 5/5: Skipping YouTube upload (--no-upload set)
2026-07-27 09:48:00,311 [INFO] ✅ Video generated (NOT uploaded — --no-upload set): ISAs Explained: Your Tax-Free Investing Superpower
...
exit=0
```
No Telegram message sent. **PASS** (expect exit=0).

### Check 2 — Forced upload failure (`FINANCE_BOT_FORCE_UPLOAD_FAIL=1`)
```
2026-07-27 09:48:51,438 [ERROR] Finance Bot pipeline failed at stage [upload]: Injected upload failure (FINANCE_BOT_FORCE_UPLOAD_FAIL)
exit=1
```
Telegram alert was attempted (no "skipped" warning → 200 sent). One "Finance Bot FAILED
… Stage: upload" message delivered to Telegram chat 5109089813. **PASS** (expect ERROR,
alert, exit=1).

### Check 3 — Alert-failure isolation (`FINANCE_BOT_FORCE_UPLOAD_FAIL=1` + invalid chat id)
```
2026-07-27 09:49:33,069 [ERROR] Finance Bot pipeline failed at stage [upload]: Injected upload failure (FINANCE_BOT_FORCE_UPLOAD_FAIL)
2026-07-27 09:49:33,209 [WARNING] Telegram alert send returned HTTP 400: {"ok":false,"error_code":400,"description":"Bad Request: chat not found"}
exit=1
```
Broken alert did not suppress exit code. **PASS** (expect exit=1).

### Check 4 — Syntax & import
```
SYNTAX_OK
IMPORT_OK -> UploadError PipelineFailure send_telegram_alert
```
**PASS.**

## 1.6 — Commit

Committed and pushed to `master` per the instruction. Full SHA recorded below.

## Files changed
- `finance_bot_v2.py` (+149 / −21)

## Could not do / notes
- Per `No uploads while testing`, no real upload was attempted; the forced-failure path
  exercised the failure branch without contacting YouTube for a real video.
- The `FINANCE_BOT_FORCE_UPLOAD_FAIL` hook remains in code as a permanent test seam
  (only active when the env var is set). It is the method the instruction suggested and
  is not a committed failure state.
- Host Python is 3.9.6, so `from __future__ import annotations` was added to keep the
  `str | None` / `bool | str` annotations runtime-safe for the launchd `/usr/bin/python3`.
