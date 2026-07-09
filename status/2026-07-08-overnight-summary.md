## Addendum — 2026-07-09 06:58 BST

`list_scheduled_tasks` confirms `meridian-12h-loop` still shows `enabled: true` (checked directly, not inferred), well over 8 hours past the 22:30 BST window close. This is at least the sixth Claude-side firing to hit this bug. Commits since the 04:22 addendum (03:01–05:41 BST) are all routine Meridian `inbox-poll: auto-acknowledged new files` / daily-status entries — polling continues to work correctly, no new inbox content, no change to Finance Bot OAuth (still blocked, repo not on the Mac Studio) or the `run_console` commit (still held, untouched).

No new substantive information since 04:22 BST. Making one further disable attempt as usual. Reiterating: this is a platform-side bug in the disable call's persistence, not a repo or Meridian issue — needs to be stopped manually from the Cowork scheduled-tasks UI if it keeps recurring.
