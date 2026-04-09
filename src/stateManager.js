const path = require('path');
const { ensureDir, readJsonIfExists, writeJson } = require('./utils');

class StateManager {
  constructor() {
    this.dir = path.join(process.cwd(), 'state');
    this.progressFile = path.join(this.dir, 'progress.json');
    this.failedFile = path.join(this.dir, 'failed.json');
    ensureDir(this.dir);

    this.progress = readJsonIfExists(this.progressFile, { completed: [], timestamps: {} });
    this.failed = readJsonIfExists(this.failedFile, []);
  }

  isCompleted(domain) {
    return this.progress.completed.includes(domain);
  }

  markCompleted(domain) {
    if (!this.progress.completed.includes(domain)) {
      this.progress.completed.push(domain);
    }
    this.progress.timestamps[domain] = new Date().toISOString();
    writeJson(this.progressFile, this.progress);
  }

  markFailed(domain, reason) {
    const existing = this.failed.find((f) => f.domain === domain);
    if (existing) {
      existing.reason = reason;
      existing.timestamp = new Date().toISOString();
    } else {
      this.failed.push({ domain, reason, timestamp: new Date().toISOString() });
    }
    writeJson(this.failedFile, this.failed);
  }
}

module.exports = StateManager;
