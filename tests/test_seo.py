"""Publication metadata must match the visible content and remain inert HTML."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update_seo', ROOT / 'scripts/update-seo.py')
seo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)


class PublicationTests(unittest.TestCase):
    def test_metadata_matches_visible_cards_and_is_idempotent(self):
        page = (ROOT / 'index.html').read_text()
        updated = seo.update(page)
        self.assertEqual(seo.update(updated), updated)
        schema = json.loads(seo.SCHEMA.search(updated)[2])
        articles = schema['hasPart']
        self.assertEqual(len(articles), page.count('class="blog-card"'))
        for article in articles:
            self.assertIn('href="' + article['url'] + '"', page)
            self.assertIn('datetime="' + article['datePublished'] + '"', page)
            self.assertEqual(article['author']['@id'], schema['mainEntity']['@id'])

    def test_encoded_title_cannot_break_out_of_script(self):
        page = '''<script type="application/ld+json">{"mainEntity":{}}</script>
<!-- BLOG_CARDS_START --><a class="blog-card" href="https://example.com/article">
<time datetime="2026-10-10"></time><h3>&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;</h3>
</a><!-- BLOG_CARDS_END -->'''
        updated = seo.update(page)
        self.assertEqual(updated.count('</script>'), 1)
        article = json.loads(seo.SCHEMA.search(updated)[2])['hasPart'][0]
        self.assertEqual(article['headline'], '</script><script>alert(1)</script>')

    def test_empty_cards_fail_without_silent_metadata_loss(self):
        with self.assertRaises(ValueError):
            seo.update('<script type="application/ld+json">{}</script><!-- BLOG_CARDS_START --><!-- BLOG_CARDS_END -->')


if __name__ == '__main__':
    unittest.main()
