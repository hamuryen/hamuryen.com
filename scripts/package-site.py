#!/usr/bin/env python3
"""Package only explicitly public assets for GitHub Pages."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / '_site'
if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir()
for name in ['index.html', '404.html', 'CNAME', 'favicon.ico', 'favicon.svg', 'apple-touch-icon.png', 'og.png',
             'robots.txt', 'sitemap.xml', 'resume.html',
             'burak-hamuryen-resume.pdf', 'burak-hamuryen-resume.txt',
             'blog-ideas.md']:
    shutil.copy2(ROOT / name, TARGET / name)
for name in ['assets', 'drafts']:
    shutil.copytree(ROOT / name, TARGET / name)
print('Packaged public site files into _site/.')
