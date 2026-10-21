# hamuryen.com

Static personal website and résumé. Open `index.html` directly, or serve this
directory with `python3 -m http.server 8000` and visit http://localhost:8000.

## Files

- `index.html`: profile, experience, projects, skills, and Medium cards.
- `assets/site.css` and `assets/site.js`: responsive styling, themes, and section navigation.
- `resume.html`, `burak-hamuryen-resume.pdf`, and `burak-hamuryen-resume.txt`: public résumé formats.
- `robots.txt` and `sitemap.xml`: crawler configuration.
- `scripts/` and `tests/`: maintenance utilities and local checks; not required by visitors.

All sections remain readable without JavaScript and are visible when printing.

## Automatic publishing and Medium updates

GitHub Actions publishes on every push to `master` and refreshes the latest six
Medium articles daily at 06:23 UTC. No local script is required. The Actions tab
also offers a manual run. Refreshed cards are included in the deployed artifact;
automation does not commit changes back to the repository. If Medium cannot be
reached after three attempts, the saved cards are published with a workflow warning.
GitHub may delay scheduled jobs and disables schedules in public repositories
after 60 days without repository activity; re-enable the workflow if that happens.

`package-site.py` packages explicitly public site files and the intentionally public
drafts. Planning notes, tests, scripts, and local development files are excluded
from the deployment artifact.

## Optional local refresh

```sh
python3 scripts/update-blog.py
python3 scripts/update-seo.py
```

Reads the public RSS feed and replaces the marked blog-card region in `index.html`.
A downloaded XML file can be passed as the first argument. Cards open the original
article in a new tab. Publish the updated HTML to make refreshed cards visible.

`update-seo.py` derives publication titles, dates, images, and author references
from those same visible cards. CI runs it even when the feed refresh fails, using
the saved cards. It never labels an unpublished draft as a published article.

## Search and AI discovery

The home page identifies the person and website with stable JSON-LD IDs; the
résumé and published articles refer to that same identity. All content and article
links are present in the initial HTML, without requiring a bot to click tabs.
The Writing section includes topic links that remain useful when recent cards rotate.

`robots.txt` permits search crawlers, including OAI-SearchBot. The content audit
checks this policy. Hosting/CDN bot restrictions must also be checked separately.
The sitemap lists canonical HTML pages only. Optional `lastmod` dates are omitted:
the scheduled feed changes the deployed page independently of Git, so a fixed
date would become inaccurate. Do not replace it with the date of every build.

After publishing, submit `https://hamuryen.com/sitemap.xml` in Google Search
Console and Bing Webmaster Tools, inspect the two canonical URLs, and track
queries, impressions, clicks, and referral traffic. Repository checks cannot
verify account ownership, indexing, rankings, or AI citations.

Guidance: [Google AI features](https://developers.google.com/search/docs/appearance/ai-features),
[OpenAI search crawlers](https://developers.openai.com/api/docs/bots), and
[Google sitemap dates](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
There is no special AI schema or `llms.txt` requirement for Google's AI features.

## Update the résumé

After editing experience or skills:

```sh
python3 scripts/build-resume.py
```

This regenerates the HTML and plain-text résumé. Open `resume.html` and save to
PDF as `burak-hamuryen-resume.pdf` using A4 paper with browser headers and footers
disabled. Regenerate the PDF whenever résumé content changes.

## Checks

```sh
python3 tests/content_audit.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --check assets/site.js
node --check assets/snake.js
node --check assets/life.js
```

The content audit checks links, anchors, metadata, skill consistency, structured
data, employer records, and the sitemap. With Playwright installed in your local
development environment, run `node tests/navigation.cjs` for navigation checks
at five screen widths. Run `node tests/browser-regressions.cjs` for game keyboard
controls, mobile deep links, skip links, motion preferences, no-JavaScript fallback,
and 404 theme/storage regressions. Set `BROWSERS=chromium,firefox,webkit`
to run the latter against all three installed Playwright engines. Optionally set
`BROWSER_EXECUTABLE` to a Chromium binary.

After deployment, use Search Console to inspect indexing and rendered content.
Local checks do not guarantee search rankings or compatibility with every ATS.
