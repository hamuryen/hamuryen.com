// Run with Playwright available: node tests/navigation.cjs
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true,
    ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
  try {
    for (const width of [1440, 900, 760, 390, 320]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.goto(pathToFileURL(path.resolve(__dirname, '../index.html')).href + '#about');
      await page.waitForTimeout(400);
      for (const id of ['about', 'experience', 'projects', 'skills', 'education', 'writing']) {
        const link = page.locator(`.navigation a[href="#${id}"]`);
        await link.click();
        await page.waitForTimeout(100);
        assert.equal(await page.locator('.content section:visible').count(), 1);
        assert.equal(await page.locator(`#${id}`).isVisible(), true);
        // Keep the active panel scrolled on desktop; repeat clicks must not reset it.
        await page.locator('.content').evaluate(el => { el.scrollTop = 100; });
        const before = await page.evaluate(() => [scrollX, scrollY, document.querySelector('.content').scrollTop]);
        await link.click();
        await page.waitForTimeout(200);
        const after = await page.evaluate(() => [scrollX, scrollY, document.querySelector('.content').scrollTop]);
        assert.deepEqual(after, before, `Repeated ${id} click moved viewport at ${width}px`);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      }
      await page.goBack();
      assert.equal(await page.locator('#education').isVisible(), true);
      await page.goForward();
      assert.equal(await page.locator('#writing').isVisible(), true);
      await page.close();
      console.log(`PASS ${width}px: all panels, repeat-click scroll, history, no overflow`);
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
