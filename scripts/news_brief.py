"""Daily brief agent.

Reads state from disk, asks Claude to search the web across standing
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
STATE_MEMORY = 120  # how many past items to remember
ITEMS = 10
MAX_SEARCHES = 18

# Threads are framed around outside thinking. The reader is a design director
# at a UK grocery retailer, so anything about his own employer arrives late and
# is worthless to him. See EXCLUSIONS.
THREADS = [
    "How large organisations are actually adopting AI - adoption evidence, "
    "failure modes, what changes about how teams work",
    "Design leadership and organisational design - how design functions are "
    "structured, levelled, funded and valued inside big companies",
    "Personalisation, loyalty and customer experience outside the UK grocery "
    "sector - other categories, other markets, other business models",
    "UK and EU regulation affecting AI, consumer data and personalisation",
    "How AI is changing user research and evaluation practice",
    "Essays that reframe a problem in technology, institutions or "
    "decision-making, rather than reporting news",
]

# Named publications, because unguided search drifts to whatever is best
# optimised for it, which is trade press and vendor announcements.
SOURCES = [
    "Stratechery",
    "One Useful Thing (Ethan Mollick)",
    "The Diff",
    "Lenny's Newsletter",
    "The Pragmatic Engineer",
    "Noahpinion",
    "Astral Codex Ten",
    "The Honest Broker",
    "Bits about Money and Complex Systems (Patrick McKenzie)",
    "Import AI",
    "Interconnects",
    "Platformer",
    "Peter Merholz on design organisations",
    "The Looking Glass (Julie Zhuo)",
]

EXCLUSIONS = [
    "Do not report Tesco announcements, press releases, product launches or "
    "results. The reader works there and knows them before they are public. "
    "Tesco may only appear when an outside analysis reframes something, and "
    "then lead with the outside argument rather than the Tesco fact.",
    "Do not include US political news.",
    "Do not include vendor marketing or press releases dressed as research.",
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
    sources = "\n".join(f"- {s}" for s in SOURCES)
    exclusions = "\n".join(f"- {e}" for e in EXCLUSIONS)

    if covered:
        seen = "\n".join(f"- {c}" for c in covered)
        avoid = (
            "\n\nYou have already covered the items below on previous days. "
            "Do not repeat them unless there is a genuine development, and if "
            "so, lead with what changed.\n\n" + seen
        )
    else:
        avoid = ""

    return f"""Search the web for the most worthwhile things published in the past few days across these threads:

{threads}

Check these publications specifically, alongside general search. They are named because unguided search drifts toward trade press and vendor announcements, which are not what is wanted:

{sources}

Exclusions:
{exclusions}

Write a brief of {ITEMS} items. For each item give a bolded one-line headline, one or two sentences of what was said or found, and one sentence starting "So what:" giving the implication for a design director who leads a group design function at a UK grocery retailer, covering app, web, loyalty and personalisation, and who is working on how design teams are structured and how AI changes research practice.

Rules:
- Favour argument over announcement. An essay that changes how the reader thinks is worth more than a funding round.
- Prioritise substance over volume. If you cannot find {ITEMS} worthwhile items, give fewer and say so plainly rather than padding.
- Give the source as a markdown link on its own line at the end of the item, formatted exactly as [Publication Name](https://the-url) - not a bare URL. Use the actual publication or outlet name, not the domain.
- Paraphrase in your own words. Do not quote at length.
- Vary the threads across the brief rather than filling it from one.
- Do not use semicolons.
- No preamble and no closing summary. Start with the first item.{avoid}

After the brief, output a line containing only ---COVERED--- followed by a plain list of the headlines you used, one per line. This is machine-read, so no formatting on those lines."""


def extract_text(message):
    return "\n".join(
        block.text for block in message.content if block.type == "text"
    ).strip()


def strip_preamble(body):
    """Drop any narration before the first bolded headline."""
    match = re.search(r"^\*\*", body, flags=re.MULTILINE)
    return body[match.start():] if match else body


def split_output(text):
    parts = re.split(r"^-{3}COVERED-{3}\s*$", text, flags=re.MULTILINE)
    body = strip_preamble(parts[0].strip())
    covered = []
    if len(parts) > 1:
        covered = [line.strip() for line in parts[1].splitlines() if line.strip()]
    return body, covered


def write_brief(body, today, ok=True):
    """Write the dated brief.

    Refuses to overwrite an existing brief with an empty body. A re-run on the
    same day sees everything as already covered and legitimately produces
    nothing, which would otherwise destroy that day's good brief.
    """
    BRIEFS_DIR.mkdir(exist_ok=True)
    path = BRIEFS_DIR / f"{today}.md"

    if ok and not body.strip() and path.exists():
        print(f"Empty result, keeping existing {path}", file=sys.stderr)
        return path

    status = "" if ok else " (FAILED)"
    content = body.strip() or "No new developments across the standing threads."
    path.write_text(f"# Brief {today}{status}\n\n{content}\n")
    return path


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state = load_state()

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": MAX_SEARCHES,
                }
            ],
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
