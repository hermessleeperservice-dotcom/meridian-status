# inbox-poll

Poll the meridian-status GitHub inbox for pending instructions from Claude, process them, and push an acknowledgement status file.

## When to use

Run this skill at the **start of every session**, before doing anything else. It is how Claude leaves instructions for Meridian between sessions.

---

## Steps

### 1. Fetch the inbox listing

```bash
curl -s https://api.github.com/repos/hermessleeperservice-dotcom/meridian-status/contents/inbox
```

Parse the JSON. Collect all `.md` files except `README.md`. These are pending instructions from Claude.

### 2. For each pending file

Fetch and read its content:

```bash
curl -s https://raw.githubusercontent.com/hermessleeperservice-dotcom/meridian-status/main/inbox/FILENAME.md
```

Read the full content. Understand the instruction. Execute any actions it specifies.

### 3. Push a status file acknowledging receipt

After processing all inbox files, push `status/YYYY-MM-DD.md` to the repo using today's date.

The file must include:

```
# Meridian Status - YYYY-MM-DD

## Inbox processed
- [list each inbox file read]

## Active project state

### Finance Bot
[current state - last run, any errors, what changed]

### TomaszFM
[service health, any changes]

### Pilot (PilotVoiceAssistant)
[sprint state, what was done, what is next]

### Executive Coach iOS
[sprint state, what was done, what is next]

## Blockers
[anything blocking progress - or "None"]

## Planned next
[what Meridian will do next]
```

Push using the GitHub API with your token:

```bash
CONTENT=$(cat status-YYYY-MM-DD.md | base64)

curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
      https://api.github.com/repos/hermessleeperservice-dotcom/meridian-status/contents/status/YYYY-MM-DD.md \
        -d "{\"message\": \"status: YYYY-MM-DD\", \"content\": \"$CONTENT\"}"
        ```

        Retrieve the token from Apple Keychain:

        ```bash
        security find-generic-password -s "github-meridian-status" -w
        ```

        ### 4. Confirm

        ```bash
        curl -s https://api.github.com/repos/hermessleeperservice-dotcom/meridian-status/contents/status/YYYY-MM-DD.md | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK:', d['name'])"
        ```

        ---

        ## Frequency

        - **Always**: run at session start, every session
        - **Never skip**: even if no work happened, push a brief "alive + idle" status

        ---

        ## Token location

        GitHub PAT is in Apple Keychain on the sleeperservice account:
        - Service name: `github-meridian-status`
        - Retrieve: `security find-generic-password -s "github-meridian-status" -w`

        If the token is missing or expired, relay to Tomasz via Telegram: "GitHub token for meridian-status needs refreshing."
