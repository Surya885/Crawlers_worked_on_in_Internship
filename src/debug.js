const fs = require('fs');
const path = require('path');
const { ensureDir, safeDomain, nowIso } = require('./utils');

async function saveDebugArtifacts({ domain, page, url, error, stage }) {
  const dir = path.join(process.cwd(), 'debug', safeDomain(domain));
  ensureDir(dir);
  const stamp = Date.now();
  const htmlPath = path.join(dir, `${stamp}.html`);
  const screenshotPath = path.join(dir, `${stamp}.png`);
  const metaPath = path.join(dir, `${stamp}.json`);

  try {
    if (page) {
      const html = await page.content();
      fs.writeFileSync(htmlPath, html);
      await page.screenshot({ path: screenshotPath, fullPage: true });
    }
  } catch (_) {
    // noop
  }

  fs.writeFileSync(metaPath, JSON.stringify({
    timestamp: nowIso(),
    url,
    error: String(error || ''),
    stage,
    htmlPath,
    screenshotPath
  }, null, 2));
}

module.exports = {
  saveDebugArtifacts
};
