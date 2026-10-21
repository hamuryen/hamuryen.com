"""RSS refresh regressions; uses local fixtures and never modifies the real page."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update_blog', ROOT / 'scripts/update-blog.py')
update_blog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_blog)


def item(name, date='Sat, 10 Oct 2026 08:00:00 GMT'):
    pub = '' if date is None else f'<pubDate>{date}</pubDate>'
    return f'<item><title>{name}</title><link>https://post.hamuryen.com/{name}</link>{pub}</item>'


class FeedTests(unittest.TestCase):
    def refresh(self, items, fail=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = '<!-- BLOG_CARDS_START -->saved cards<!-- BLOG_CARDS_END -->'
            (root / 'index.html').write_text(original)
            feed = root / 'feed.xml'
            feed.write_text('<rss><channel>' + ''.join(items) + '</channel></rss>')
            with patch.object(update_blog, 'ROOT', root), patch.object(sys, 'argv', ['update-blog.py', str(feed)]):
                if fail:
                    with self.assertRaises(SystemExit):
                        update_blog.main()
                    self.assertEqual((root / 'index.html').read_text(), original)
                else:
                    update_blog.main()
                return (root / 'index.html').read_text()

    def test_invalid_dates_do_not_block_later_valid_items(self):
        page = self.refresh([item('missing', None), item('bad', 'invalid-date')] + [item(f'valid-{i}') for i in range(8)])
        self.assertEqual(page.count('class="blog-card"'), 6)
        self.assertIn('valid-5', page)
        self.assertNotIn('valid-6', page)
        self.assertNotIn('>missing<', page)

    def test_all_invalid_items_preserve_saved_cards(self):
        self.refresh([item('bad', None)], fail=True)

    def test_feed_titles_remain_escaped(self):
        page = self.refresh([item('&lt;script&gt;')])
        self.assertIn('<h3>&lt;script&gt;</h3>', page)
        self.assertNotIn('<h3><script>', page)


if __name__ == '__main__':
    unittest.main()
