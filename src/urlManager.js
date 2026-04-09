const { isBlockedUrl, toAbsoluteUrl, isSameDomain, pathDepth } = require('./utils');
const { scoreUrl } = require('./scoringEngine');

class UrlManager {
  constructor(seedUrl) {
    this.seedUrl = seedUrl;
    this.discovered = new Set();
  }

  filterAndScore(urls) {
    const unique = [];
    for (const raw of urls) {
      const abs = toAbsoluteUrl(this.seedUrl, raw);
      if (!abs) continue;
      if (!isSameDomain(this.seedUrl, abs)) continue;
      if (this.discovered.has(abs)) continue;
      if (isBlockedUrl(abs)) continue;
      const score = scoreUrl(abs);
      if (score <= -10) continue;
      this.discovered.add(abs);
      unique.push({ url: abs, score, depth: pathDepth(abs) });
    }
    unique.sort((a, b) => b.score - a.score || b.depth - a.depth);
    return unique;
  }

  deepest(count = 10) {
    return [...this.discovered]
      .map((url) => ({ url, depth: pathDepth(url) }))
      .sort((a, b) => b.depth - a.depth)
      .slice(0, count)
      .map((x) => x.url);
  }
}

module.exports = UrlManager;
