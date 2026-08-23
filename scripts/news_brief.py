"""Weekly news brief agent.

Reads state from disk, asks Claude to search the web across three standing
threads, writes a dated markdown brief, and records what it covered so the
next run does not repeat itself.

Runs unattended via .github/workflows/news-brief.yml
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic

MODEL = "claude-sonnet-5"
BRIEFS_DIR = Path("briefs")
STATE_PATH = BRIEFS_DIR / "state.json"
STATE_MEMORY = 40  # how many past items to remember

THREADS = [
    "UK AI regulation, especially the Regulating for Growth Bill",
    "Tesco news of strategic significance",
    "Retail AI and personalisation trends",
]


def load_state():
    if not STATE_PATH.exists():
        return {"runs": 0, "covered": []}
    try:
        return json.loads(STATE_PATH.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"State unreadable, starting fresh: {exc}", file=sys.stderr)
        return {"runs": 0, "covered": []}


def save_state(state):
    state["covered"] = state["covered"][-STATE_MEMORY:]
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def build_prompt(covered):
    threads = "\n".join(f"- {t}" for t in THREADS)
    if covered:
        seen = "\n".join(f"- {c}" for c in covered)
        avoid = (
            "\n\nYou have already covered the items below in previous weeks. "
            "Do not repeat them unless there is a genuine development, and if "
            "so, lead with what changed.\n\n" + seen
        )
    else:
        avoid = ""

    return f"""Search the web for the most significant developments over the past seven days across these threads:

{threads}

Write a brief of six to eight items. For each item give a bolded one-line headline, one sentence of what happened, and one sentence starting "So what:" giving the implication for a design director working on loyalty and personalisation at a UK grocery retailer.

Rules:
- Prioritise substance over volume. Fewer, better items beat padding.
- Link the source for each item.
- Say plainly if a thread had nothing worth reporting this week rather than inventing filler.
- Do not use semicolons.
- No preamble and no closing summary. Start with the first item.{avoid}

After the brief, output a line containing only ---COVERED--- followed by a plain list of the headlines you used, one per line. This is machine-read, so no formatting on those lines."""


def extract_text(message):
    return "\n".join(
        block.text for block in message.content if block.type == "text"
    ).strip()


def split_output(text):
    parts = re.split(r"^-{3}COVERED-{3}\s*$", text, flags=re.MULTILINE)
    body = parts[0].strip()
    covered = []
    if len(parts) > 1:
        covered = [line.strip() for line in parts[1].splitlines() if line.strip()]
    return body, covered


def write_brief(body, today, ok=True):
    BRIEFS_DIR.mkdir(exist_ok=True)
    status = "" if ok else " (FAILED)"
    path = BRIEFS_DIR / f"{today}.md"
    path.write_text(f"# Brief {today}{status}\n\n{body}\n")
    return path


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state = load_state()

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}],
            messages=[{"role": "user", "content": build_prompt(state["covered"])}],
        )
    except Exception as exc:  # noqa: BLE001 - always leave an artefact
        write_brief(f"Run failed.\n\n```\n{exc}\n```", today, ok=False)
        state["runs"] += 1
        save_state(state)
        raise

    body, covered = split_output(extract_text(message))
    path = write_brief(body, today)

    state["runs"] += 1
    state["covered"].extend(covered)
    save_state(state)

    print(f"Wrote {path} with {len(covered)} items. Run {state['runs']}.")


if __name__ == "__main__":
    main()
