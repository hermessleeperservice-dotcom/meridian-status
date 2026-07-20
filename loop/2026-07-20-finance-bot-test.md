# Task 1 — Finance Bot Manual Pipeline Test — SUCCESS

_Tags: `finance-bot-test`_
_Timestamp: 2026-07-20 13:54 BST. Author: Meridian._
_Source task: `inbox/2026-07-20-finance-bot-test-and-scheduler.md` (Task 1)._

## Verdict: ✅ FULL END-TO-END SUCCESS

The complete pipeline ran from `~/Documents/Youtube/financebot`:
`python3 finance_bot_v2.py --generate`

All 5 steps passed and the YouTube upload API returned a Video ID. No errors
were encountered. Process exit code: **0**.

## Run evidence (verbatim from `agent.log` → `finance_bot.log`)

```
2026-07-20 13:54:42,846 [INFO] ============================================================
2026-07-20 13:54:42,846 [INFO] STEP 1/5: Selecting script...
2026-07-20 13:54:42,846 [INFO] Title: 5 Realistic Side Income Ideas for 2026 (UK Edition)
2026-07-20 13:54:42,846 [INFO] Category: earning
2026-07-20 13:54:42,847 [INFO] Script length: 304 words
2026-07-20 13:54:42,847 [INFO] STEP 2/5: Generating audio with edge-tts...
2026-07-20 13:54:42,847 [INFO] Using voice: en-GB-RyanNeural
2026-07-20 13:54:50,340 [INFO] Audio generated successfully: finance_videos/finance_20260720_135442.mp3 (772848 bytes)
2026-07-20 13:54:50,341 [INFO] Audio generated in 7.5 seconds
2026-07-20 13:54:50,341 [INFO] STEP 3/5: Creating thumbnail...
2026-07-20 13:54:50,483 [INFO] Thumbnail created: finance_videos/finance_20260720_135442.png
2026-07-20 13:54:50,483 [INFO] STEP 4/5: Composing video...
2026-07-20 13:54:50,540 [INFO] Audio duration: 128.8 seconds
2026-07-20 13:54:54,930 [INFO] Video created: finance_videos/finance_20260720_135442.mp4 (3.6 MB)
2026-07-20 13:54:54,930 [INFO] Video composed in 4.4 seconds
2026-07-20 13:54:54,930 [INFO] STEP 5/5: Uploading to YouTube...
2026-07-20 13:54:55,312 [INFO] file_cache is only supported with oauth2client<4.0.0
2026-07-20 13:54:55,346 [INFO] Uploading: 5 Realistic Side Income Ideas for 2026 (UK Edition)
2026-07-20 13:54:58,389 [INFO] ✅ Upload complete! Video ID: OiOPwpYV5YQ
2026-07-20 13:54:58,389 [INFO]    URL: https://www.youtube.com/watch?v=OiOPwpYV5YQ
2026-07-20 13:54:58,390 [INFO] ============================================================
2026-07-20 13:54:58,390 [INFO] ✅ SUCCESS! Video generated and uploaded: 5 Realistic Side Income Ideas for 2026 (UK Edition)
2026-07-20 13:54:58,390 [INFO]    Files: finance_videos/finance_20260720_135442.mp4
```

Note: the only non-INFO lines during upload were FutureWarning / NotOpenSSLWarning
messages from Google client libraries + urllib3 (Python 3.9 EOL warnings). These
are benign deprecation notices — they did **not** affect execution and the upload
succeeded. No `[ERROR]` lines are present in this run.

## Artifact verification (on disk)

| Check | Result |
|---|---|
| Video file `finance_videos/finance_20260720_135442.mp4` | present, **3,738,851 bytes** (3.6 MB) |
| `token.pickle` (auth, gitignored) | present, **1,375 bytes**, refreshed `Jul 20 13:54` |
| Upload API response | Video ID `OiOPwpYV5YQ`, URL `https://www.youtube.com/watch?v=OiOPwpYV5YQ` |

## Confirmation that the video is on the channel

The upload API returned `id: OiOPwpYV5YQ` for channel **Wealth Secrets 1970**
(`CONFIG["channel_name"]`), with `privacyStatus: public`. This matches the
previous successful run (2026-07-19, Video ID `vFp8xPP8P_c`) using the same
`token.pickle` — confirming the credentials are valid and the pipeline is
functionally identical end-to-end.

> Live web verification of the YouTube watch page was not performed (would
> require browser auth / scraping); success is asserted from the API's own
> returned Video ID + the prior confirmed-good run pattern. If you want a live
> `youtube.list` sanity check, say so and I'll query the Data API.

## Credential safety (unchanged, still safe)

- `token.pickle` and `client_secret.json` both remain in `.gitignore` and are
  **not** tracked by git. No credential was touched, committed, or exposed.
- The run refreshed `token.pickle` in place (token refresh on the existing
  credential); it remains gitignored.

## Gate status for Task 2

**Task 1 succeeded → Task 2 (launchd scheduler) is now UNLOCKED.**

Task 2 preconditions are met:
1. Full successful upload confirmed. ✅
2. When setting up the scheduler, inference calls (none in the core pipeline,
   but any future script-generation step) must be pinned to `qwen3:6`;
   `openrouter/auto` stays excluded. ✅ (constraint noted for Task 2)
3. Awaiting your go-ahead (or a follow-up inbox task) before proceeding to
   Task 2 — per the gate, it runs only on Task 1 success, which is now proven.

## Result

Task 1 is **complete**: video generated and uploaded end-to-end with no errors,
verified against `agent.log`. Report tagged `finance-bot-test` and written to
`loop/`.
