const Crawler = require('./crawler');
const Storage = require('./storage');
const logger = require('./logger');
const { normalizeDomain, nowIso } = require('./utils');

class Worker {
  constructor({ browserPool, stateManager, dashboard }) {
    this.browserPool = browserPool;
    this.stateManager = stateManager;
    this.dashboard = dashboard;
    this.storage = new Storage();
  }

  async processDomain(rawDomain) {
    const seedUrl = normalizeDomain(rawDomain);
    if (!seedUrl) return { status: 'skipped', reason: 'INVALID_DOMAIN' };
    const domain = new URL(seedUrl).hostname;

    this.dashboard.markDomainActive(domain);
    logger.info('DOMAIN_START', { domain, stage: 'DOMAIN', message: 'Domain processing started' });
    this.dashboard.log({ timestamp: nowIso(), domain, stage: 'DOMAIN', message: 'DOMAIN_START' });

    const context = await this.browserPool.newContext();
    const crawler = new Crawler({ domain, seedUrl, browserPool: this.browserPool });

    try {
      const pre = await crawler.runPrecheck(context);
      if (!pre.pass) {
        logger.info('PRECHECK_FAIL', { domain, stage: 'PRECHECK', message: 'No signal after adaptive precheck' });
        this.dashboard.log({ timestamp: nowIso(), domain, stage: 'PRECHECK', message: 'PRECHECK_FAIL' });
        this.stateManager.markFailed(domain, 'PRECHECK_FAIL');
        this.dashboard.addFailedDomain(domain);
        this.dashboard.markDomainDone(domain, true);
        return { status: 'skipped', reason: 'PRECHECK_FAIL' };
      }

      logger.info('PRECHECK_MATCH', { domain, stage: 'PRECHECK', message: 'Domain passed precheck' });
      logger.info('CRAWL_START', { domain, stage: 'CRAWL', message: 'Starting full crawl' });
      this.dashboard.log({ timestamp: nowIso(), domain, stage: 'PRECHECK', message: 'PRECHECK_MATCH' });

      const crawlResult = await crawler.crawlFull(context, pre.seeds);
      const payload = {
        domain,
        seedUrl,
        crawledAt: nowIso(),
        stats: {
          totalVisited: crawlResult.totalVisited,
          relevantCount: crawlResult.relevantPages.length,
          termination: crawlResult.terminatedBy
        },
        pages: crawlResult.relevantPages.map((p) => ({
          url: p.url,
          type: p.type,
          relevanceScore: p.relevanceScore,
          title: p.title,
          headings: p.headings,
          text: p.text
        }))
      };

      const out = this.storage.saveDomainResult(domain, payload);
      this.stateManager.markCompleted(domain);
      logger.info('DOMAIN_COMPLETE', { domain, stage: 'DOMAIN', message: 'Completed', jsonPath: out.jsonPath, zipPath: out.zipPath });
      this.dashboard.log({ timestamp: nowIso(), domain, stage: 'DOMAIN', message: 'DOMAIN_COMPLETE' });
      this.dashboard.markDomainDone(domain, false);
      return { status: 'completed', domain, out };
    } catch (err) {
      this.stateManager.markFailed(domain, err.message);
      logger.error('DOMAIN_FAIL', { domain, stage: 'DOMAIN', message: err.message });
      this.dashboard.log({ timestamp: nowIso(), domain, stage: 'DOMAIN', message: 'DOMAIN_FAIL', error: err.message });
      this.dashboard.addFailedDomain(domain);
      this.dashboard.markDomainDone(domain, true);
      return { status: 'failed', reason: err.message };
    } finally {
      try { await context.close(); } catch (_) { /* noop */ }
      await this.browserPool.markDomainDoneAndMaybeRecycle();
    }
  }
}

module.exports = Worker;
