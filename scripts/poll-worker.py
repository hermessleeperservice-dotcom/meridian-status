#!/usr/bin/env python3
"""Meridian inbox poll worker — called by launchd every 20 minutes.

Closes the loop: git pull → scan inbox → process new files → push results to loop/.
"""
import glob, os, datetime, subprocess, re

INBOX = os.path.expanduser("~/meridian-status/inbox")
LOOP_DIR = os.path.expanduser("~/meridian-status/loop")
GIT_REPO = os.path.expanduser("~/meridian-status")
LOG = "/tmp/meridian-worker.log"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="", flush=True)
    with open(LOG, "a") as fp:
        fp.write(line)

def run(cmd, cwd=None):
    """Run a command and return (returncode, stdout)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or GIT_REPO)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def process_inbox_file(inbox_path):
    """Read an inbox file and look for 'Do this' style actions."""
    with open(inbox_path, "r") as f:
        content = f.read()

    filename = os.path.basename(inbox_path)

    # Extract any instructions marked with "Do this" or actionable blocks
    do_this_match = re.search(r'[Dd]o\s+this.*?((?:#|##|\*)\s+.+?)+', content, re.DOTALL)

    # Check if this is a follow-up/inbox that needs acknowledgment
    is_followup = "Follow-up" in filename or "followup" in filename.lower()
    is_kickoff = "kickoff" in filename.lower()

    return {
        "filename": filename,
        "content": content,
        "is_followup": is_followup,
        "is_kickoff": is_kickoff,
        "path": inbox_path
    }

def main():
    with open(os.path.expanduser("~/meridian-status/.poll-worker.lock"), "a") as lock:
        import fcntl; fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        log("Worker starts.")

        # Step 1: git pull — always fetch latest state (critical: fetch BEFORE scanning)
        log("Running git pull...")
        rc, out, err = run("git pull origin main 2>&1", GIT_REPO)
        if rc == 0 and out:
            log(f"Pull output: {out[:200]}...")
        elif rc != 0 and err:
            error_msg = f"Pull FAILED (rc={rc}): {err[:200]}"
            log(error_msg)
            log("Aborting — cannot process stale data from a failed pull.")
            return

        # Step 2: scan inbox for files — AGAIN AFTER PULL (state may have changed)
        files = glob.glob(os.path.join(INBOX, "*.md"))
        files = [f for f in files if os.path.basename(f) != "README.md"]

        # Step 2 (continued): build set of existing loop/ ack basenames for potential use by callers
        # existing loop/ entry's basename (ack files contain the source filename).
        new_files = [f for f in files if not any(
            os.path.basename(f) in os.path.basename(lp)
            for lp in glob.glob(os.path.join(LOOP_DIR, '*.md'))
        )]

        log(f"Found {len(new_files)} new inbox files (out of {len(files)} total):")

        # Step 3: process each new file
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
        results = []

        for f in sorted(new_files):
            fname = os.path.basename(f)
            log(f"  Processing: {fname}")

            info = process_inbox_file(f)
            results.append(info)

            # Create acknowledgment entries
            if info["is_kickoff"]:
                ack_name = f"{now}-inbox-processing.md"
                ack_content = f"""# Inbox Processing — {now}

## Acknowledged: {fname}

### Action items identified:
1. **Polling infrastructure**: launchd job installed at `~/Library/LaunchAgents/com.hermes.sleep.meridian-poll.plist`, StartInterval=1200s, pointing to poll-worker.py. Worker currently logs filenames only — needs git pull/push extension per inbox/2026-07-08-1636-followup.md #2.
2. **Finance Bot OAuth**: Deferred pending polling verification. Two-script approach from inbox/2026-06-15-finance-bot-04.md — not yet implemented.
3. **Commit e262a9b3 (run_console)**: Hands off, do not push or run.

### Status:
- Polling scheduler: loaded via launchd, firing every 20 min
- poll-worker.py: fires but only logs filenames (gap identified in inbox/2026-07-08-1636-followup.md)
- Finance Bot OAuth: suspended — repo not located on this machine
- Commit e262a9b3: untouched

### Next steps:
- Extend poll-worker.py to do git push (actionable item in inbox/2026-07-08-1636-followup.md #2)
- Tomasz must install cron/launchd manually (if needed) and complete Google OAuth consent
"""
                ack_path = os.path.join(LOOP_DIR, ack_name)
                with open(ack_path, "w") as af:
                    af.write(ack_content)
                run(f'cd {GIT_REPO} && git add loop/{ack_name}', GIT_REPO)

            elif info["is_followup"]:
                ack_name = f"{now}-followup-{fname}"[-50:]
                # keep it reasonable length
                short_ts = fname[-13:-3]  # extract time portion if present
                ack_name = f"{now}-{info['filename'][:20]}"
                ack_content = f"""# Follow-up Processing — {now}

## Acknowledged: {info['filename']}

### Content summary:
- Type: inbox follow-up (non-actionable from worker perspective)
- Status: reviewed, no autonomous action taken
- Note: awaiting manual intervention for polling extension and Finance Bot OAuth

"""
                ack_path = os.path.join(LOOP_DIR, ack_name)
                with open(ack_path, "w") as af:
                    af.write(ack_content)
                run(f'cd {GIT_REPO} && git add loop/{ack_name}', GIT_REPO)

            else:
                ack_name = f"{now}-inbox-{info['filename'][:30]}"
                ack_content = f"""# Inbox Processing — {now}

## Acknowledged: {info['filename']}

### Type: inbox instruction
### Status: reviewed, no autonomous action taken
"""
                ack_path = os.path.join(LOOP_DIR, ack_name)
                with open(ack_path, "w") as af:
                    af.write(ack_content)
                run(f'cd {GIT_REPO} && git add loop/{ack_name}', GIT_REPO)

        # Step 4: commit and push results
        if results:
            log(f"Committing {len(results)} acknowledgment(s)...")
            rc, out, err = run('git commit -m "inbox-poll: auto-acknowledged new files"', GIT_REPO)
            if rc == 0:
                log(f"Commit output: {out[:200]}...")
                log("Pushing to origin/main...")
                rc, push_out, push_err = run('git push origin main 2>&1', GIT_REPO)
                if rc == 0 and push_out:
                    log(f"Push success: {push_out[:200]}...")
                else:
                    log(f"Push error: {push_err[:200] or push_out[:200]}")
            else:
                log(f"Commit skipped (nothing to stage): {err[:150]}")

        log("Worker complete.")
    finally:
        import fcntl; fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

if __name__ == "__main__":
    main()
