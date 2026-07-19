---
name: inbox-poll
version: 1.0.0
description: "Periodically poll ~/meridian-status/inbox/ for new instructions, execute them, and archive processed files."
platforms: [linux, macos]
metadata:
  hermes:
    tags: [inbox, meridian-status, automation]
---

# Inbox Poll — meridian-status instruction dispatcher

Periodically pull ~/meridian-status and scan inbox/ for new instructions. Execute them in discovery order, move processed ones to done/, report the outcome.

## Trigger Conditions
- Daily cron job runs this skill (recommended: every 2h during working hours)
- Explicit user request: "check meridian inbox" or "run inbox poll"
- After any system recovery / health-check completion

## Steps (MUST follow in order)

### Step 1: Git pull before every scan
```bash
cd ~/meridian-status && git pull origin main 2>&1
```
**Critical:** Never skip the pull. This is why inbox instructions go unread for days — always fetch first, even if you just pulled minutes ago.

### Step 2: Scan inbox for new files
```bash
ls -t ~/meridian-status/inbox/ 2>&1 | head -20
```
Newest files = highest priority. Read the most recent one fully before moving to the next. Skip `README.md` and any existing `*/done/` artifacts.

### Step 3: Read and execute the instruction
- Load the file with `read_file` or `cat`
- Follow instructions precisely as written — they contain recovery workflows, system audits, or project kicks
- Execute each step in order; report raw output for every command run
- Do NOT interpret instructions early or skip ahead

### Step 4: Move processed files
After executing an inbox instruction:
```bash
mkdir -p ~/meridian-status/inbox/done/2026/
mv ~/meridian-status/inbox/<filename> ~/meridian-status/inbox/done/$(date +%Y)/
```

### Step 5: Report outcome
Return a summary of what was found and executed. If no new files, report "No new inbox instructions."

## Known Bugs
- None yet — this skill was created from scratch to fill the gap where prior attempts failed because git pull was never included in the poll routine.
