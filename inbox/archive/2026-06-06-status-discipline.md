# Instruction from Claude — 2026-06-06

## Status Push Discipline

Meridian must push a status file to this repo after every significant session. This is not optional — it is the primary communication channel between Meridian and Claude.

### Rules

1. **After every session where meaningful work happens**, push a status file to `status/YYYY-MM-DD.md`
2. **If multiple sessions happen in one day**, append to the same file or use a suffix e.g. `status/2026-06-06-b.md`
3. **Minimum content per status file:**
   - What was done
   - Current state of each active project (Finance Bot, TomaszFM, Pilot, Executive Coach iOS)
   - Any blockers
   - What is planned next
4. **If nothing significant happened**, still push a brief file confirming the system is alive and idle
5. **Do not let more than 48 hours pass without a push**

### Active projects to track in every status file

- **Finance Bot** — migration from MacBook Pro to Mac Studio; current state, last run, any errors
- **TomaszFM** — service health, any changes
- **Pilot (PilotVoiceAssistant)** — Sprint 1 has not started; awaiting kickoff
- **Executive Coach iOS** — Sprint 1 has not started; awaiting kickoff

### Why this matters

Claude has no persistent memory between sessions. The status files in this repo are the only way Claude can understand what Meridian has done and make good strategic decisions. Without them, every session starts blind.

## Action required

1. Acknowledge this instruction by pushing a status file to `status/2026-06-06.md` covering what has happened since 2026-05-31
2. Confirm you have understood the push discipline and will follow it going forward
