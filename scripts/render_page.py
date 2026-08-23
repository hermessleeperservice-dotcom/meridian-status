"""Render the latest brief as a standalone HTML page.

Reads the most recent NON-EMPTY file in briefs/ and writes site/index.html.
The page is noindex so it stays out of search results.
"""

import html
import re
import sys
from pathlib import Path

BRIEFS_DIR = Path("briefs")
OUT_DIR = Path("site")

CSS = """
:root { color-scheme: light dark; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  max-width: 40rem;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
  line-height: 1.55;
  font-size: 1.05rem;
}
h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
.meta { color: #888; font-size: 0.85rem; margin-bottom: 2.5rem; }
.item { margin-bottom: 2.25rem; }
.headline { font-weight: 600; margin-bottom: 0.4rem; }
a { color: #0066cc; }
.foot { margin-top: 3rem; font-size: 0.85rem; color: #888; }
"""


def body_lines(path):
    """Content lines only, excluding the '# Brief ...' heading and blanks."""
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("# ")
    ]


def latest_brief():
    """Most recent brief that actually has content.

    A run can legitimately produce nothing (everything already covered).
    Rendering that would blank the page, so walk backwards to the last
    brief with a body.
    """
    files = sorted(p for p in BRIEFS_DIR.glob("*.md") if p.name != "README.md")
    for path in reversed(files):
        if body_lines(path):
            return path
    return None


def inline_markdown(text):
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a href="\2" rel="noopener">\1</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def to_html(path, date):
    """Render generically.

    Every non-heading line becomes a paragraph. Lines that are entirely bold
    are treated as headlines. Nothing is dropped for failing to match a
    pattern, so a formatting change upstream degrades the look rather than
    silently emptying the page.
    """
    body = []
    for line in body_lines(path):
        if line.startswith("**") and line.endswith("**"):
            body.append(f'<p class="headline">{inline_markdown(line)}</p>')
        else:
            body.append(f"<p>{inline_markdown(line)}</p>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<title>Brief {date}</title>
<style>{CSS}</style>
</head>
<body>
<h1>Weekly brief</h1>
<div class="meta">{date} &middot; UK AI regulation, Tesco, retail personalisation</div>
{chr(10).join(body)}
<p class="foot">Past briefs live in the meridian-status repo.</p>
</body>
</html>
"""


def main():
    source = latest_brief()
    if source is None:
        print("No brief with content found, leaving page untouched", file=sys.stderr)
        sys.exit(0)

    date = source.stem
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(to_html(source, date))
    print(f"Rendered {source} to {OUT_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
