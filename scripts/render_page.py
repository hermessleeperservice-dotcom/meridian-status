"""Render the latest brief as a standalone HTML page.

Reads the most recent file in briefs/ and writes site/index.html.
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
.sowhat { border-left: 3px solid #ccc; padding-left: 0.85rem; margin-top: 0.5rem; }
a { color: #0066cc; }
.archive { margin-top: 3rem; font-size: 0.85rem; color: #888; }
"""


def latest_brief():
    files = sorted(p for p in BRIEFS_DIR.glob("*.md") if p.name != "README.md")
    if not files:
        return None
    return files[-1]


def inline_markdown(text):
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a href="\2" rel="noopener">\1</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def to_html(markdown, date):
    lines = markdown.splitlines()
    body = []
    open_item = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("# "):
            continue

        if stripped.startswith("**") and stripped.endswith("**"):
            if open_item:
                body.append("</div>")
            body.append('<div class="item">')
            body.append(f'<div class="headline">{inline_markdown(stripped)}</div>')
            open_item = True
        elif stripped.startswith("So what:"):
            body.append(f'<p class="sowhat">{inline_markdown(stripped)}</p>')
        else:
            body.append(f"<p>{inline_markdown(stripped)}</p>")

    if open_item:
        body.append("</div>")

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
<div class="archive">Past briefs live in the meridian-status repo.</div>
</body>
</html>
"""


def main():
    source = latest_brief()
    if source is None:
        print("No briefs found", file=sys.stderr)
        sys.exit(1)

    date = source.stem
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(to_html(source.read_text(), date))
    print(f"Rendered {source} to {OUT_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
