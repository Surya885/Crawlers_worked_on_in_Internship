const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

class Dashboard {
  constructor() {
    this.state = {
      totalDomains: 0,
      completed: 0,
      failed: 0,
      remaining: 0,
      activeDomains: [],
      avgTimePerDomainMs: 0,
      estimatedRemainingMs: 0,
      lastLogs: [],
      failedDomains: []
    };
    this.startTimes = new Map();

    this.app = express();
    this.server = http.createServer(this.app);
    this.io = new Server(this.server);

    this.app.get('/', (_, res) => res.send(this.renderHtml()));
    this.io.on('connection', (socket) => socket.emit('state', this.state));
  }

  start(port = 3000) {
    this.server.listen(port, () => {
      // eslint-disable-next-line no-console
      console.log(`Dashboard running at http://localhost:${port}`);
    });
  }

  update(patch) {
    this.state = { ...this.state, ...patch };
    this.io.emit('state', this.state);
  }

  markDomainActive(domain) {
    this.startTimes.set(domain, Date.now());
    if (!this.state.activeDomains.includes(domain)) {
      this.state.activeDomains.push(domain);
      this.io.emit('state', this.state);
    }
  }

  markDomainDone(domain, failed = false) {
    const started = this.startTimes.get(domain) || Date.now();
    const duration = Date.now() - started;
    const newCompleted = this.state.completed + (failed ? 0 : 1);
    const totalFinished = this.state.completed + this.state.failed + 1;
    const avg = ((this.state.avgTimePerDomainMs * (totalFinished - 1)) + duration) / totalFinished;

    this.state.activeDomains = this.state.activeDomains.filter((d) => d !== domain);
    this.state.completed = newCompleted;
    this.state.failed += failed ? 1 : 0;
    this.state.remaining = Math.max(0, this.state.totalDomains - (this.state.completed + this.state.failed));
    this.state.avgTimePerDomainMs = Math.round(avg);
    this.state.estimatedRemainingMs = this.state.avgTimePerDomainMs * this.state.remaining;
    this.io.emit('state', this.state);
  }

  log(line) {
    this.state.lastLogs.unshift(line);
    this.state.lastLogs = this.state.lastLogs.slice(0, 10);
    this.io.emit('state', this.state);
  }

  addFailedDomain(domain) {
    if (!this.state.failedDomains.includes(domain)) {
      this.state.failedDomains.unshift(domain);
      this.state.failedDomains = this.state.failedDomains.slice(0, 200);
      this.io.emit('state', this.state);
    }
  }

  renderHtml() {
    return `<!doctype html>
<html><head><meta charset="utf-8"/><title>Crawler Dashboard</title>
<style>body{font-family:Arial;margin:20px} .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px} .card{padding:12px;border:1px solid #ddd;border-radius:8px} ul{max-height:220px;overflow:auto} pre{max-height:300px;overflow:auto;background:#111;color:#0f0;padding:10px;border-radius:8px}</style>
</head><body>
<h1>Crawler Dashboard</h1><div class="grid" id="cards"></div>
<h2>Active Domains</h2><ul id="active"></ul>
<h2>Failed Domains</h2><ul id="failed"></ul>
<h2>Last 10 Logs</h2><pre id="logs"></pre>
<script src="/socket.io/socket.io.js"></script>
<script>
const socket = io();
socket.on('state', s => {
  document.getElementById('cards').innerHTML = [
    ['Total Domains', s.totalDomains],['Completed', s.completed],['Failed', s.failed],['Remaining', s.remaining],
    ['Avg Time (s)', (s.avgTimePerDomainMs/1000).toFixed(1)],['ETA (min)', (s.estimatedRemainingMs/60000).toFixed(1)]
  ].map(([k,v])=>"<div class='card'><b>"+k+"</b><div>"+v+"</div></div>").join('');
  document.getElementById('active').innerHTML = (s.activeDomains || []).map(d=>"<li>"+d+"</li>").join('');
  document.getElementById('failed').innerHTML = (s.failedDomains || []).map(d=>"<li>"+d+"</li>").join('');
  document.getElementById('logs').textContent = (s.lastLogs || []).map(l=>JSON.stringify(l)).join('\n');
});
</script></body></html>`;
  }
}

module.exports = Dashboard;
