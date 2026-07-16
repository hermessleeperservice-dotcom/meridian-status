#!/usr/bin/env python3
"""Meridian inbox poll worker — called by launchd every 20 minutes.

Closes the loop: git pull → scan inbox → process new files → push results to loop/.
"""
import glob, os, datetime, subprocess, re

INBOX = os.path.expanduser("~/meridian-status/inbox")
LOOP_DIR = os.path.expanduser("~/meridian-status/loop")
GIT_REPO = os.path.expanduser("~/meridian-status")
LOG = "/tmp/meridian-worker.log"

# Run-prefix stamped on every generated loop/ ack filename: YYYY-MM-DD-HHMM-
_RUNPREFIX = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{4}-')
# Generator prefixes we add when naming acks (e.g. "...-inbox-<src>", "...-followup-<src>",
# "...-kickoff-<src>"). All acks embed the source token so they can be deduped.
_GENPREFIX = re.compile(r'^(?:inbox-|followup-|kickoff-)')
# A recovered source token must look like it came from a dated inbox file,
# otherwise it's a non-embedding ack (e.g. kickoff "inbox-processing") and is ignored.
_DATEISH = re.compile(r'\d{4}-\d{2}-\d{2}')

def _norm(name):
    """Strip a trailing .md for extension-insensitive comparison (legacy acks truncated)."""
    return name[:-3] if name.endswith('.md') else name

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="", flush=True)
    with open(LOG, "a") as fp:
        fp.write(line)

def run(cmd, cwd=None):
    """Run a command and return (returncode, stdout, stderr)."""
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

def _strip_run_prefix(name):
    """Drop a single leading YYYY-MM-DD-HHMM- run-prefix if present."""
    return _RUNPREFIX.sub('', name, count=1)

def _source_token(loop_basename):
    """Recover the embedded *source* inbox token from a generated loop/ ack filename.

    Acks embed the original inbox name after a run-prefix and an optional
    generator prefix (inbox-/followup-). Reversing those yields the source token
    used for dedup, e.g.:
      loop/2026-07-08-1759-2026-07-08-1106-foll... -> 2026-07-08-1106-followup
      2026-07-08-1759-inbox-2026-07-09-finance-bot-clone-r... -> 2026-07-09-finance-bot-clone-r
    """
    s = _strip_run_prefix(loop_basename)      # drop outer run-prefix
    s = _GENPREFIX.sub('', s)                 # drop generator prefix
    return s

def main():
    import fcntl
    lock_path = os.path.expanduser("~/meridian-status/.poll-worker.lock")
    with open(lock_path, "a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            log("Worker starts.")

            # Step 1: git pull — ALWAYS fetch latest state BEFORE scanning.
            # A stale local inbox/loop copy would miss new instructions pushed from
            # the other end and could re-ack already-processed items.
            log("Running git pull...")
            rc, out, err = run("git pull origin main 2>&1", GIT_REPO)
            if rc == 0 and out:
                log(f"Pull output: {out[:200]}...")
            elif rc != 0 and err:
                error_msg = f"Pull FAILED (rc={rc}): {err[:200]}"
                log(error_msg)
                log("Aborting — cannot process stale data from a failed pull.")
                return

            # Step 2: scan inbox for files — AFTER the pull (state may have changed).
            files = glob.glob(os.path.join(INBOX, "*.md"))
            files = [f for f in files if os.path.basename(f) != "README.md"]

            # Dedup: key off the *source* inbox token embedded in each loop/ ack,
            # not the full generated ack name. Stripping the run-prefix (and any
            # generator prefix) from both sides lets us recognize that an inbox
            # file was already acknowledged in a previous run — regardless of this
            # run's own timestamp prefix or truncation to a fixed length.
            _acked_sources = set()
            if os.path.isdir(LOOP_DIR):
                # NOTE: glob '*' not '*.md' — legacy acks for long source names were
                # truncated and may lack a .md extension. Compare on the date-intact
                # source token (extension-normalized) so truncation doesn't defeat dedup.
                for lp in glob.glob(os.path.join(LOOP_DIR, '*')):
                    tok = _norm(_source_token(os.path.basename(lp)))
                    if tok and _DATEISH.search(tok):
                        _acked_sources.add(tok)

            def _already_acked(inbox_basename):
                s = _norm(inbox_basename)
                for tok in _acked_sources:
                    # match either direction to tolerate one-sided truncation
                    if s.startswith(tok) or tok.startswith(s):
                        return True
                return False

            new_files = [f for f in files if not _already_acked(os.path.basename(f))]

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
                    ack_name = f"{now}-kickoff-{info['filename'][:20]}"
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
            else:
                log("No new inbox files to process — nothing to commit.")

            log("Worker complete.")
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

if __name__ == "__main__":
    main()
