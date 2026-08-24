"""Render the latest brief as a standalone HTML page.

Reads the most recent NON-EMPTY file in briefs/ and writes site/index.html.
The page is noindex so it stays out of search results.

Cards are image-led. The image is fetched from each source's own og:image
tag, the same preview every link unfurl uses. A card without an image still
renders, so a failed fetch degrades rather than breaks.

Sources are normally written by the agent as a markdown link
[Publication](https://...). Older/occasional output is a bare URL on its
own line instead — that's still parsed: the source name falls back to the
domain, and the URL still drives the image lookup and the "So what" link.
"""

import html
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BRIEFS_DIR = Path("briefs")
OUT_DIR = Path("site")
IMAGE_CACHE = BRIEFS_DIR / "images.json"

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
BARE_URL_RE = re.compile(r"https?://\S+")
TRAILING_PUNCT = ".,;:'\")]"
OG_RE = re.compile(
    rb"""<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']""", re.I
)
OG_ALT_RE = re.compile(
    rb"""<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']""", re.I
)
UA = "Mozilla/5.0 (compatible; brief-agent/1.0)"

CSS = """
*, *::before, *::after { box-sizing: border-box; }

:root {
  --paper:  #F2F4F5;
  --card:   #FFFFFF;
  --ink:    #10161B;
  --muted:  #5E6B75;
  --rule:   #DDE2E5;
  --signal: #2B4ACB;
}

@media (prefers-color-scheme: dark) {
  :root {
    --paper:  #0B0E11;
    --card:   #161C21;
    --ink:    #E8ECEF;
    --muted:  #94A2AC;
    --rule:   #262F36;
    --signal: #8FA5FF;
  }
}

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  padding: 2rem 0.875rem 4rem;
  background: var(--paper);
  color: var(--ink);
  font-family: Newsreader, Georgia, "Times New Roman", serif;
  font-size: 17px;
  line-height: 1.5;
}

.wrap { max-width: 34rem; margin: 0 auto; }

.masthead { margin: 0 0.25rem 1.5rem; }

.masthead h1 {
  font-size: 1.625rem;
  font-weight: 500;
  letter-spacing: -0.015em;
  margin: 0 0 0.375rem;
}

.stamp {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.6875rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0;
}

.stamp .sep { opacity: 0.4; padding: 0 0.4em; }

.card {
  background: var(--card);
  border: 1px solid var(--rule);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 0.875rem;
}

.shot {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  background: var(--rule);
  border-bottom: 1px solid var(--rule);
}

.body { padding: 1rem 1.125rem 1.125rem; }

.meta {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.num {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--signal);
  flex-shrink: 0;
}

.source {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.625rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.card h2 {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.008em;
  margin: 0 0 0.5rem;
}

.what {
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--muted);
  margin: 0 0 1rem;
}

.sowhat {
  font-size: 1.0625rem;
  line-height: 1.5;
  margin: 0;
  padding-left: 0.875rem;
  border-left: 2px solid var(--signal);
}

.sowhat b {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.625rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--signal);
  display: block;
  margin-bottom: 0.3125rem;
}

.card a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
.source a { text-decoration: none; }
.source a:hover { text-decoration: underline; }
a:focus-visible { outline: 2px solid var(--signal); outline-offset: 3px; }

.foot {
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.6875rem;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin-top: 2rem;
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
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("# ")
    ]


def latest_brief():
    """Most recent brief that actually has content."""
    files = sorted(p for p in BRIEFS_DIR.glob("*.md") if p.name != "README.md")
    for path in reversed(files):
        if body_lines(path):
            return path
    return None


def load_cache():
    try:
        return json.loads(IMAGE_CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def fetch_og_image(url):
    """Return the page's own preview image, or None."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            head = resp.read(300000)
    except Exception:  # noqa: BLE001 - a missing image is not a failure
        return None

    match = OG_RE.search(head) or OG_ALT_RE.search(head)
    if not match:
        return None
    # The regex reads raw HTML without a parser, so entities in the
    # attribute (some sites emit &amp; or &#x3D; inside og:image URLs)
    # are still literal text here. Decode once so esc() doesn't
    # re-escape them into garbage when the page is rendered.
    image = html.unescape(match.group(1).decode("utf-8", "ignore")).strip()
    return image if image.startswith("https://") else None


def resolve_images(urls):
    """Fetch preview images, reusing anything already cached."""
    cache = load_cache()
    missing = [u for u in dict.fromkeys(urls) if u not in cache]

    if missing:
        with ThreadPoolExecutor(max_workers=6) as pool:
            for url, image in zip(missing, pool.map(fetch_og_image, missing)):
                cache[url] = image
        try:
            IMAGE_CACHE.write_text(json.dumps(cache, indent=2) + "\n")
        except OSError:
            pass

    return cache


def esc(text):
    return html.escape(text)


def linkify(text):
    return LINK_RE.sub(r'<a href="\2" rel="noopener">\1</a>', esc(text))


def clean_url(url):
    return url.rstrip(TRAILING_PUNCT)


def domain_name(url):
    host = re.sub(r"^https?://", "", url).split("/")[0]
    return re.sub(r"^www\.", "", host)


def parse_items(lines):
    """Group lines into items keyed off bolded headline lines."""
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


def split_item(item):
    body = " ".join(item["body"]).strip()

    sources = LINK_RE.findall(body)
    body = LINK_RE.sub("", body).strip(" /").strip()

    if not sources:
        # Fall back to bare URLs (e.g. "https://example.com/story") — the
        # agent doesn't always wrap the source in markdown link syntax.
        bare = [clean_url(u) for u in BARE_URL_RE.findall(body)]
        if bare:
            sources = [(domain_name(u), u) for u in bare]
            body = BARE_URL_RE.sub("", body).strip()

    what, sowhat = body, ""
    match = re.search(r"\bSo what:\s*", body)
    if match:
        what = body[: match.start()].strip()
        sowhat = body[match.end():].strip()

    return sources, what, sowhat


def render_card(item, sources, what, sowhat, images, index=None):
    image = next((images.get(url) for _, url in sources if images.get(url)), None)
    first_url = sources[0][1] if sources else None

    parts = ['<article class="card">']

    if image:
        alt = esc(item["headline"] or "")
        shot = f'<img class="shot" src="{esc(image)}" alt="{alt}" loading="lazy">'
        parts.append(
            f'<a href="{esc(first_url)}" rel="noopener">{shot}</a>'
            if first_url
            else shot
        )

    parts.append('<div class="body">')

    meta = []
    if index is not None:
        meta.append(f'<span class="num">{index:02d}</span>')
    if sources:
        links = " / ".join(
            f'<a href="{esc(url)}" rel="noopener">{esc(name)}</a>'
            for name, url in sources
        )
        meta.append(f'<span class="source">{links}</span>')
    if meta:
        parts.append(f'<div class="meta">{"".join(meta)}</div>')

    if item["headline"]:
        parts.append(f"<h2>{linkify(item['headline'])}</h2>")
    if what:
        parts.append(f'<p class="what">{linkify(what)}</p>')
    if sowhat:
        parts.append(f'<p class="sowhat"><b>So what</b>{linkify(sowhat)}</p>')

    parts.append("</div></article>")
    return "\n".join(parts)


def to_html(path, date):
    items = parse_items(body_lines(path))
    parsed = [(item, *split_item(item)) for item in items]

    urls = [url for _, sources, _, _ in parsed for _, url in sources]
    images = resolve_images(urls)

    cards, story_index = [], 0
    for item, sources, what, sowhat in parsed:
        if item["headline"]:
            story_index += 1
            idx = story_index
        else:
            idx = None
        cards.append(render_card(item, sources, what, sowhat, images, idx))
    cards = "\n".join(cards)
    count = story_index

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<title>Brief {date}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
<h1>Your brief</h1>
<p class="stamp">{date}<span class="sep">/</span>{count} items</p>
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
