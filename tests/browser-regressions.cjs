// Run with Playwright available. BROWSERS=chromium,firefox,webkit enables all engines.
const playwright = require('playwright');
const assert = require('node:assert/strict');
const { pathToFileURL } = require('node:url');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const url = name => pathToFileURL(path.join(root, name)).href;
(async () => {
  for (const name of (process.env.BROWSERS || 'chromium').split(',')) {
    const browser = await playwright[name].launch({ headless: true,
      ...(name === 'chromium' && process.env.BROWSER_EXECUTABLE
        ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
    try {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
      await context.route(/^https?:/, route => route.abort());
      await context.addInitScript(() => {
        const random = Math.random;
        let first = true;
        Math.random = () => { if (first) { first = false; return 0.1; } return random(); };
      });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(url('index.html'));
      await page.locator('.snake-preview').click();
      await page.locator('.snake-close').focus();
      await page.keyboard.press('Space');
      assert.equal(await page.locator('.snake-dialog').evaluate(el => el.open), false,
        'Space on Close must close, not start the game');
      assert.equal(await page.locator('.snake-preview').evaluate(el => el === document.activeElement), true);
      await page.locator('.snake-preview').click();
      await page.locator('.snake-start').click();
      await page.waitForFunction(() => Number(document.querySelector('#snake-score').textContent) >= 1);
      await page.locator('.snake-pause').click();
      await page.locator('.snake-start').focus();
      await page.keyboard.press('Space');
      assert.equal(await page.locator('#snake-score').textContent(), '0', 'Space on Restart resets score');
      await page.keyboard.press('Escape');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      await page.goto(url('index.html') + '#skills');
      await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
      await page.locator('.navigation a[href="#about"]').click();
      const heading = await page.locator('#about h2').boundingBox();
      assert.ok(heading.y >= 0 && heading.y < 700, 'New mobile panel heading must be visible');
      await page.locator('.navigation a[href="#experience"]').click();
      await page.locator('.skip-link').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('.content section:visible').getAttribute('id'), 'experience',
        'Skip link must preserve selected section');
      assert.equal(await page.locator('.content').evaluate(el => el === document.activeElement), true);
      await page.goto(url('index.html') + '#missing-section');
      assert.equal(await page.evaluate(() => location.hash), '#about');
      for (const section of ['writing', 'experience']) {
        const deepLink = await context.newPage();
        await deepLink.goto(url('index.html') + '#' + section);
        await deepLink.waitForFunction(id => {
          const title = document.querySelector('#' + id + ' h2').getBoundingClientRect();
          const nav = document.querySelector('.navigation').getBoundingClientRect();
          return title.top >= nav.bottom && title.top < innerHeight;
        }, section);
        const title = await deepLink.locator('#' + section + ' h2').boundingBox();
        const nav = await deepLink.locator('.navigation').boundingBox();
        assert.ok(title.y >= nav.y + nav.height && title.y < 844,
          'Fresh mobile deep link must place heading below sticky navigation');
        await deepLink.close();
      }
      assert.deepEqual(errors, []);
      await context.close();

      const lifeContext = await browser.newContext({ reducedMotion: 'reduce' });
      await lifeContext.route(/^https?:/, route => route.abort());
      await lifeContext.addInitScript(() => { Math.random = () => 0.9; });
      const lifePage = await lifeContext.newPage();
      await lifePage.goto(url('index.html'));
      const toggle = lifePage.locator('.life-panel .flow-toggle');
      const cells = () => lifePage.locator('.life-cell').evaluateAll(es => es.map(e => e.dataset.age).join(''));
      assert.equal(await toggle.isVisible(), true, 'Reduced motion must retain explicit play control');
      const initial = await cells();
      await lifePage.waitForTimeout(600);
      assert.equal(await cells(), initial);
      await toggle.click();
      await lifePage.waitForTimeout(600);
      assert.notEqual(await cells(), initial);
      await toggle.click();
      const pausedLife = await cells();
      await lifePage.emulateMedia({ reducedMotion: 'no-preference' });
      await lifePage.waitForTimeout(600);
      assert.equal(await cells(), pausedLife, 'Media changes must preserve explicit pause');
      await lifeContext.close();

      // Saved "system" must follow OS preference, and denied storage must not throw.
      for (const denyStorage of [false, true]) {
        const context = await browser.newContext({ colorScheme: 'dark' });
        await context.route(/^https?:/, route => route.abort());
        await context.addInitScript(deny => {
          if (deny) Object.defineProperty(window, 'localStorage', { get() { throw new Error('Storage denied'); } });
          else localStorage.setItem('theme', 'system');
        }, denyStorage);
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(url('404.html'));
        assert.equal(await page.locator('html').getAttribute('data-theme'), 'dark');
        await page.emulateMedia({ colorScheme: 'light' });
        await page.waitForFunction(() => document.documentElement.dataset.theme === 'light');
        assert.deepEqual(errors, []);
        await context.close();
      }
      const noScript = await browser.newContext({ javaScriptEnabled: false });
      await noScript.route(/^https?:/, route => route.abort());
      const staticPage = await noScript.newPage();
      await staticPage.goto(url('index.html'));
      assert.equal(await staticPage.locator('.profile-art').isVisible(), false,
        'Do not show dead game controls when JavaScript is unavailable');
      assert.equal(await staticPage.locator('.content section:visible').count(), 6);
      await noScript.close();
      console.log(`PASS ${name}: game keyboard, mobile navigation, skip link, motion preference, no-JS fallback, 404 theme/storage`);
    } finally { await browser.close(); }
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
