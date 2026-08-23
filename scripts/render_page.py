"""Render the latest brief as a standalone HTML page.

Reads the most recent NON-EMPTY file in briefs/ and writes site/index.html.
The page is noindex so it stays out of search results.

Layout note: the "So what" line is the dominant element and the news itself
is supporting text. That inversion is deliberate. The reader does not need
to be told what happened, they need the implication.
"""

import html
import re
import sys
from pathlib import Path

BRIEFS_DIR = Path("briefs")
OUT_DIR = Path("site")

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")

CSS = """
*, *::before, *::after { box-sizing: border-box; }

:root {
  --paper:  #E9ECEE;
  --card:   #FFFFFF;
  --ink:    #10161B;
  --muted:  #5E6B75;
  --rule:   #D2D8DC;
  --signal: #2B4ACB;
}

@media (prefers-color-scheme: dark) {
  :root {
    --paper:  #0D1114;
    --card:   #161C21;
    --ink:    #E8ECEF;
    --muted:  #94A2AC;
    --rule:   #2A333A;
    --signal: #8FA5FF;
  }
}

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  padding: 2.5rem 1rem 5rem;
  background: var(--paper);
  color: var(--ink);
  font-family: Newsreader, Georgia, "Times New Roman", serif;
  font-size: 17px;
  line-height: 1.5;
}

.wrap { max-width: 38rem; margin: 0 auto; }

.masthead { margin-bottom: 2rem; }

.masthead h1 {
  font-size: 1.75rem;
  font-weight: 500;
  letter-spacing: -0.015em;
  margin: 0 0 0.5rem;
}

.stamp {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.6875rem;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0;
}

.stamp span { white-space: nowrap; }
.stamp .sep { opacity: 0.45; padding: 0 0.4em; }

.card {
  background: var(--card);
  border: 1px solid var(--rule);
  border-radius: 10px;
  padding: 1.375rem 1.25rem 1.25rem;
  margin-bottom: 1rem;
}

.card .source {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.625rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  display: block;
  margin-bottom: 0.75rem;
}

.card h2 {
  font-size: 1.0625rem;
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: -0.005em;
  margin: 0 0 0.625rem;
}

.card .what {
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--muted);
  margin: 0 0 1.125rem;
}

.card .sowhat {
  font-size: 1.0625rem;
  line-height: 1.5;
  margin: 0;
  padding-left: 0.9375rem;
  border-left: 2px solid var(--signal);
}

.card .sowhat b {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.625rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--signal);
  display: block;
  margin-bottom: 0.375rem;
}

.card a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
.card .source a { text-decoration: none; }
.card .source a:hover { text-decoration: underline; }

a:focus-visible { outline: 2px solid var(--signal); outline-offset: 3px; }

.foot {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.6875rem;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin-top: 2.5rem;
  text-align: center;
}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?'
    "family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&"
    'family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">'
)


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


def esc(text):
    return html.escape(text)


def linkify(text):
    return LINK_RE.sub(r'<a href="\2" rel="noopener">\1</a>', esc(text))


def parse_items(lines):
    """Group lines into items keyed off bolded headline lines.

    Anything before the first headline is kept as its own item so a
    formatting change upstream degrades the layout rather than silently
    dropping content.
    """
    items, current = [], None
    for line in lines:
        if line.startswith("**") and line.endswith("**"):
            if current:
                items.append(current)
            current = {"headline": line.strip("*").strip(), "body": []}
        elif current:
            current["body"].append(line)
        else:
            items.append({"headline": None, "body": [line]})
    if current:
        items.append(current)
    return items


def render_card(item):
    body = " ".join(item["body"]).strip()

    sources = LINK_RE.findall(body)
    body = LINK_RE.sub("", body).strip(" /").strip()

    what, sowhat = body, ""
    match = re.search(r"\bSo what:\s*", body)
    if match:
        what = body[: match.start()].strip()
        sowhat = body[match.end():].strip()

    parts = ['<article class="card">']

    if sources:
        links = " / ".join(
            f'<a href="{esc(url)}" rel="noopener">{esc(name)}</a>'
            for name, url in sources
        )
        parts.append(f'<span class="source">{links}</span>')

    if item["headline"]:
        parts.append(f"<h2>{linkify(item['headline'])}</h2>")
    if what:
        parts.append(f'<p class="what">{linkify(what)}</p>')
    if sowhat:
        parts.append(f'<p class="sowhat"><b>So what</b>{linkify(sowhat)}</p>')

    parts.append("</article>")
    return "\n".join(parts)


def to_html(path, date):
    items = parse_items(body_lines(path))
    cards = "\n".join(render_card(item) for item in items)
    count = sum(1 for item in items if item["headline"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="color-scheme" content="light dark">
<title>Brief {date}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
<h1>Weekly brief</h1>
<p class="stamp"><span>{date}</span><span class="sep">/</span><span>{count} items</span><span class="sep">/</span><span>UK AI regulation, Tesco, retail personalisation</span></p>
</header>
{cards}
<p class="foot">Written by an agent. Archive in meridian-status.</p>
</div>
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
