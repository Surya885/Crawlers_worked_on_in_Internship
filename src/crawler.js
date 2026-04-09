const PriorityQueue = require('./queue');
const UrlManager = require('./urlManager');
const logger = require('./logger');
const { extractPageData, maybeInteract } = require('./extractor');
const { scoreRelevance, isMatch, classifyPage } = require('./scoringEngine');
const { isBlockedUrl, sleep } = require('./utils');
const { saveDebugArtifacts } = require('./debug');

class Crawler {
  constructor({ domain, seedUrl, browserPool, maxPages = 200, maxDepth = 4 }) {
    this.domain = domain;
    this.seedUrl = seedUrl;
    this.browserPool = browserPool;
    this.maxPages = Math.min(300, Math.max(150, maxPages));
    this.maxDepth = Math.min(5, Math.max(3, maxDepth));
    this.urlManager = new UrlManager(seedUrl);

    this.resultPages = [];
    this.noSignalWindow = [];
    this.consecutiveFailures = 0;
    this.antiBotHits = 0;
  }

  async createPage(context) {
    const page = await context.newPage();
    await page.route('**/*', (route) => {
      const type = route.request().resourceType();
      if (['image', 'font', 'media'].includes(type)) {
        route.abort();
      } else {
        route.continue();
      }
    });
    return page;
  }

  detectAntiBot(text) {
    const lower = String(text || '').toLowerCase();
    return lower.includes('access denied') || lower.includes('captcha') || lower.includes('verify you are human');
  }

  async fetchAndAnalyze(context, url, depth, stage, retry = 0) {
    let page;
    try {
      page = await this.createPage(context);
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 12000 });
      await sleep(1000);

      if (await page.locator('button, a').count() > 0) {
        await maybeInteract(page);
        await sleep(500);
      }

      const extracted = await extractPageData(page, url);
      if (this.detectAntiBot(extracted.text)) {
        this.antiBotHits += 1;
        throw new Error('ANTI_BOT_DETECTED');
      }

      if ((extracted.text || '').length < 300) {
        if (retry < 1) {
          await page.close();
          return this.fetchAndAnalyze(context, url, depth, stage, retry + 1);
        }
        throw new Error('CONTENT_TOO_SHORT');
      }

      const type = classifyPage(extracted);
      if (type === 'BLOG') {
        return { skip: true, reason: 'BLOG' };
      }

      const relevanceScore = scoreRelevance(extracted);
      const matched = isMatch(relevanceScore);

      const candidates = this.urlManager.filterAndScore(extracted.links);
      return {
        skip: false,
        url,
        depth,
        type,
        relevanceScore,
        matched,
        title: extracted.title,
        headings: extracted.headings,
        text: extracted.text,
        links: candidates
      };
    } catch (err) {
      if (retry < 1) {
        if (page) await saveDebugArtifacts({ domain: this.domain, page, url, error: err, stage });
        if (page) await page.close();
        return this.fetchAndAnalyze(context, url, depth, stage, retry + 1);
      }
      if (page) await saveDebugArtifacts({ domain: this.domain, page, url, error: err, stage });
      throw err;
    } finally {
      if (page) {
        try { await page.close(); } catch (_) { /* noop */ }
      }
    }
  }

  async runPrecheck(context) {
    const home = this.seedUrl;

    const homeData = await this.fetchAndAnalyze(context, home, 0, 'PRECHECK_HOME').catch((e) => {
      throw new Error(`HOMEPAGE_FAIL:${e.message}`);
    });

    const initialLinks = homeData.links || [];
    const top100 = initialLinks.slice(0, 100);

    const ranges = [
      top100.slice(0, 20),
      top100.slice(20, 50),
      top100.slice(50, 100)
    ];

    for (const group of ranges) {
      for (const item of group) {
        const r = await this.fetchAndAnalyze(context, item.url, 1, 'PRECHECK').catch(() => null);
        if (!r || r.skip) continue;
        if (['PRODUCT', 'CATEGORY', 'ABOUT'].includes(r.type) && r.matched) {
          return { pass: true, seeds: initialLinks };
        }
      }
    }

    const fallback = [home, ...this.urlManager.deepest(10)];
    for (const f of fallback) {
      if (isBlockedUrl(f)) continue;
      const r = await this.fetchAndAnalyze(context, f, 1, 'PRECHECK_FALLBACK').catch(() => null);
      if (!r || r.skip) continue;
      if (['PRODUCT', 'CATEGORY', 'ABOUT'].includes(r.type) && r.matched) {
        return { pass: true, seeds: initialLinks };
      }
    }

    return { pass: false, seeds: initialLinks };
  }

  async crawlFull(context, seedCandidates = []) {
    const pq = new PriorityQueue();
    const visited = new Set();

    pq.push({ url: this.seedUrl, score: 50, depth: 0 });
    for (const c of seedCandidates.slice(0, 120)) {
      if (!isBlockedUrl(c.url)) pq.push({ url: c.url, score: c.score, depth: 1 });
    }

    while (pq.size > 0 && visited.size < this.maxPages) {
      if (this.consecutiveFailures >= 3 || this.antiBotHits >= 2) break;
      const next = pq.pop();
      if (!next || visited.has(next.url) || next.depth > this.maxDepth || isBlockedUrl(next.url)) continue;
      visited.add(next.url);

      try {
        const result = await this.fetchAndAnalyze(context, next.url, next.depth, 'CRAWL');
        if (!result || result.skip) continue;

        this.consecutiveFailures = 0;
        this.noSignalWindow.push(result.matched ? 1 : 0);
        if (this.noSignalWindow.length > 20) this.noSignalWindow.shift();

        if (['PRODUCT', 'CATEGORY', 'ABOUT', 'CONTACT'].includes(result.type)) {
          this.resultPages.push(result);
        }

        logger.info('PAGE_SUCCESS', { domain: this.domain, stage: 'CRAWL', url: next.url, type: result.type, relevance: result.relevanceScore });

        for (const link of result.links) {
          if (!visited.has(link.url) && link.depth <= this.maxDepth) {
            pq.push(link);
          }
        }

        const enoughRelevant = this.resultPages.filter((p) => p.matched).length >= 30;
        const noSignal = this.noSignalWindow.length >= 20 && this.noSignalWindow.every((x) => x === 0);
        if (enoughRelevant || noSignal) break;
      } catch (err) {
        this.consecutiveFailures += 1;
        logger.error('PAGE_FAIL', { domain: this.domain, stage: 'CRAWL', url: next.url, error: err.message });
      }
    }

    return {
      totalVisited: visited.size,
      relevantPages: this.resultPages,
      terminatedBy: this.consecutiveFailures >= 3 ? 'THREE_CONSECUTIVE_FAILURES' : (this.antiBotHits >= 2 ? 'ANTI_BOT' : 'NORMAL')
    };
  }
}

module.exports = Crawler;
