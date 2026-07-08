#!/usr/bin/env python3
"""Meridian inbox poll worker — called by launchd every 20 minutes."""
import glob, os, datetime

INBOX = os.path.expanduser("~/meridian-status/inbox")
LOG = "/tmp/meridian-worker.log"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    with open(LOG, "a") as fp:
        fp.write(line)

log("Worker starts. New files:")
files = glob.glob(os.path.join(INBOX, "*.md"))
for f in sorted(files):
    fname = os.path.basename(f)
    if fname != "README.md":
        log(f"  {fname}")
log("Worker complete.")
