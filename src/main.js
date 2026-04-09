const fs = require('fs');
const path = require('path');
const BrowserPool = require('./browserPool');
const StateManager = require('./stateManager');
const Dashboard = require('./dashboard');
const Worker = require('./worker');
const logger = require('./logger');

async function runBatch(items, limit, handler) {
  const ret = [];
  let idx = 0;

  async function worker() {
    while (idx < items.length) {
      const current = idx;
      idx += 1;
      ret[current] = await handler(items[current]);
    }
  }

  const workers = Array.from({ length: Math.min(limit, items.length) }, () => worker());
  await Promise.all(workers);
  return ret;
}

async function main() {
  const domainsFile = path.join(process.cwd(), 'input', 'domains.json');
  if (!fs.existsSync(domainsFile)) {
    throw new Error('Missing input/domains.json');
  }

  const rawDomains = JSON.parse(fs.readFileSync(domainsFile, 'utf8'));
  const domains = rawDomains.filter((d) => typeof d === 'string' && d.trim().length > 0);

  const state = new StateManager();
  const remaining = domains.filter((d) => !state.isCompleted(new URL(d.startsWith('http') ? d : `https://${d}`).hostname));

  const dashboard = new Dashboard();
  dashboard.update({
    totalDomains: remaining.length,
    completed: 0,
    failed: 0,
    remaining: remaining.length
  });
  dashboard.start(3000);

  const pool = new BrowserPool({ size: 3 });
  await pool.init();

  const worker = new Worker({ browserPool: pool, stateManager: state, dashboard });
  logger.info('SYSTEM_START', { stage: 'SYSTEM', message: `Domains loaded: ${domains.length}, remaining: ${remaining.length}` });

  await runBatch(remaining, 5, async (domain) => worker.processDomain(domain));
  await pool.close();

  logger.info('SYSTEM_COMPLETE', { stage: 'SYSTEM', message: 'All domains processed' });
  setTimeout(() => process.exit(0), 1000);
}

main().catch((err) => {
  logger.error('SYSTEM_FAIL', { stage: 'SYSTEM', message: err.message });
  process.exit(1);
});
