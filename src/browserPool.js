const { chromium } = require('playwright');

class BrowserPool {
  constructor({ size = 3 } = {}) {
    this.size = size;
    this.browsers = [];
    this.pointer = 0;
    this.domainCounter = 0;
  }

  async init() {
    for (let i = 0; i < this.size; i += 1) {
      const browser = await chromium.launch({ headless: true });
      this.browsers.push(browser);
    }
  }

  async getBrowser() {
    const browser = this.browsers[this.pointer];
    this.pointer = (this.pointer + 1) % this.browsers.length;
    return browser;
  }

  async newContext() {
    const browser = await this.getBrowser();
    return browser.newContext({
      userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      viewport: { width: 1440, height: 900 }
    });
  }

  async markDomainDoneAndMaybeRecycle() {
    this.domainCounter += 1;
    if (this.domainCounter % 20 === 0) {
      await this.close();
      this.browsers = [];
      await this.init();
    }
  }

  async close() {
    for (const b of this.browsers) {
      try { await b.close(); } catch (_) { /* noop */ }
    }
  }
}

module.exports = BrowserPool;
