#!/usr/bin/env python3
"""Keep profile publication metadata in sync with the visible, saved blog cards."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PERSON = 'https://hamuryen.com/#person'
SCHEMA = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


class Publications(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current = None
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'blog-card' in attrs.get('class', '').split():
            self.current = {'@type': 'BlogPosting', 'url': attrs['href'],
                            'headline': '', 'author': {'@id': PERSON}}
        if self.current is not None:
            if tag == 'h3':
                self.in_title = True
            elif tag == 'time':
                self.current['datePublished'] = attrs['datetime']
            elif tag == 'img':
                self.current['image'] = attrs['src']

    def handle_data(self, data):
        if self.in_title:
            self.current['headline'] += data

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_title = False
        elif tag == 'a' and self.current is not None:
            self.current['headline'] = self.current['headline'].strip()
            self.articles.append(self.current)
            self.current = None


def update(document):
    cards = document.split('<!-- BLOG_CARDS_START -->', 1)[1].split('<!-- BLOG_CARDS_END -->', 1)[0]
    parser = Publications()
    parser.feed(cards)
    if not parser.articles:
        raise ValueError('No visible publications; refusing to replace metadata')
    match = SCHEMA.search(document)
    profile = json.loads(match[2])
    profile['hasPart'] = parser.articles
    # HTML entities are decoded by HTMLParser. JSON encoding alone does not stop
    # an article title containing </script> from ending a JSON-LD script element.
    encoded = json.dumps(profile, ensure_ascii=False, indent=2).replace('<', r'\u003c')
    return document[:match.start(2)] + '\n' + encoded + '\n' + document[match.end(2):]


def main():
    path = ROOT / 'index.html'
    original = path.read_text()
    updated = update(original)
    if updated != original:
        path.write_text(updated)
    print('Publication metadata matches visible blog cards.')


if __name__ == '__main__':
    main()
