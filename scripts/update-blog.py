#!/usr/bin/env python3
"""Refresh static Medium cards: python3 scripts/update-blog.py [local-feed.xml]."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from email.utils import parsedate_to_datetime
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FEED = 'https://post.hamuryen.com/feed'
class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.src = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and not self.src:
            src = attrs.get('src', '')
            if urlsplit(src).scheme == 'https' and ((urlsplit(src).hostname or '') == 'medium.com' or (urlsplit(src).hostname or '').endswith('.medium.com')) and 'stat?' not in src:
                self.src = src

def main():
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_bytes()
    else:
        for attempt in range(3):
            try:
                with urlopen(Request(FEED, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25) as response:
                    raw = response.read()
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    feed = ET.fromstring(raw)
    cards = []
    for item in feed.findall('./channel/item'):
        title = item.findtext('title', '').strip()
        url = item.findtext('link', '').split('?')[0]
        if not title or urlsplit(url).scheme != 'https':
            continue
        parser = Images()
        parser.feed(item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', ''))
        try:
            date = parsedate_to_datetime(item.findtext('pubDate', ''))
        except (TypeError, ValueError, OverflowError):
            print('Skipping feed item with missing or invalid publication date.', file=sys.stderr)
            continue
        picture = f'<div class="blog-image"><img src="{escape(parser.src, quote=True)}" alt="" loading="lazy" width="600" height="343"></div>' if parser.src else ''
        cards.append(f'''<a class="blog-card" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{picture}<div class="blog-copy"><span class="blog-meta"><time datetime="{date.date().isoformat()}">{date.strftime('%b %d, %Y')}</time> · MEDIUM</span><h3>{escape(title)}</h3><span class="blog-read">Read story ↗<span class="sr-only"> (opens in a new tab)</span></span></div></a>''')
        if len(cards) == 6:
            break
    if not cards:
        raise SystemExit('No articles found; existing cards were preserved.')
    path = ROOT / 'index.html'
    document = path.read_text()
    start, end = '<!-- BLOG_CARDS_START -->', '<!-- BLOG_CARDS_END -->'
    before, remainder = document.split(start, 1)
    _, after = remainder.split(end, 1)
    path.write_text(before + start + '\n' + '\n'.join(cards) + '\n' + end + after)
    print(f'Updated {len(cards)} blog cards.')

if __name__ == '__main__':
    main()
