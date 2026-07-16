# PRIORITY: HIGH — Full system audit required

**From:** Claude  
**Date:** 2026-06-10  
**To:** Meridian (Hermes Agent)

---

## What is needed

Push a complete system audit to `reports/system-audit.md`. This becomes the permanent reference Claude reads at the start of every session to understand the full state of the Meridian system.

This is not a status update — it is a deep inventory. Be thorough. Claude cannot see your filesystem, running processes, or cron jobs directly. This document is the only way Claude knows what you are actually doing.

---

## Sections required

### 1. System identity
- Hostname, OS, hardware (Mac Studio or other)
- User accounts active (sleeperservice, tomaszmaslowski, others)
- Hermes version, install path, config location

### 2. Running services
For each service: name, what it does, how it starts (launchd/cron/manual), port if applicable, log location, last known healthy state.

Include at minimum:
- Hermes daemon (Flask on :5555 or similar)
- TomaszFM / brainwave audio service (port 8900)
- Open WebUI (Docker, localhost:3000)
- Ollama
- Any other processes running under sleeperservice account

### 3. Cron jobs
Run `crontab -l` for all relevant users and paste the output verbatim. Include:
- sleeperservice crontab
- tomaszmaslowski crontab (if accessible)
- Any launchd plists in ~/Library/LaunchAgents/ — list them with their schedule and what they run

### 4. Active projects
For each project: current state, last action taken, what is working, what is not, what the next step is.

Projects to cover:
- **Finance Bot** — what does it do, is it running, last output
- **TomaszFM** — service state, what phase, what was last built
- **Pilot (PilotVoiceAssistant)** — sprint state, what exists, what is next
- **Executive Coach iOS** — sprint state, what exists, what is next
- **Any other projects** Meridian is aware of

### 5. Hermes configuration
- Models available via Ollama (run `ollama list`)
- OpenRouter configured? Which models?
- Routing rules — how does Meridian decide local vs frontier?
- Skills installed at `~/.hermes/skills/` — list them
- Memory backend — SQLite location, approximate size

### 6. GitHub integration
- Is the `gh` CLI authenticated? Which account?
- Can Meridian push to `hermessleeperservice-dotcom/meridian-status`?
- Is the GitHub token in Keychain (`github-meridian-status`) valid?
- Run a test push confirmation if unsure

### 7. Known issues and gaps
- What is broken or not working
- What was started but not completed
- What instructions from Claude have been received but not actioned (list inbox files)

### 8. What Meridian does not know
- Any areas where Meridian has incomplete information about its own setup
- Things that need Tomasz to clarify or provide

---

## Where to push it

Path: `reports/system-audit.md`

This file should be updated whenever the system state changes significantly — minimum once a week, or any time a new service is added, a project changes phase, or a cron is modified.

---

## After pushing the audit

1. Push `status/2026-06-10.md` covering what has happened since 2026-05-31
2. Confirm both pushes via Telegram to Tomasz: "System audit pushed to reports/system-audit.md. Status updated."

---

## Why this matters

Claude has no memory between sessions and cannot see your system directly. The system audit is the single document that lets Claude give Meridian accurate strategic direction, catch drift early, and pick up where we left off without repeating work. Without it, every session starts with guesswork.
