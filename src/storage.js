const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');
const { ensureDir, safeDomain } = require('./utils');

class Storage {
  constructor() {
    this.jsonDir = path.join(process.cwd(), 'output', 'json');
    this.zipDir = path.join(process.cwd(), 'output', 'zips');
    ensureDir(this.jsonDir);
    ensureDir(this.zipDir);
  }

  saveDomainResult(domain, payload) {
    const base = safeDomain(domain);
    const jsonPath = path.join(this.jsonDir, `${base}.json`);
    fs.writeFileSync(jsonPath, JSON.stringify(payload, null, 2));

    const zip = new AdmZip();
    zip.addLocalFile(jsonPath);
    const zipPath = path.join(this.zipDir, `${base}.zip`);
    zip.writeZip(zipPath);

    return { jsonPath, zipPath };
  }
}

module.exports = Storage;
