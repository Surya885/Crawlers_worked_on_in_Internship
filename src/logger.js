const path = require('path');
const winston = require('winston');
const { ensureDir, nowIso } = require('./utils');

ensureDir(path.join(process.cwd(), 'logs'));

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, domain = null, stage = null, ...rest }) => JSON.stringify({
      timestamp: timestamp || nowIso(),
      level,
      domain,
      stage,
      message,
      ...rest
    }))
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/crawler.log' }),
    new winston.transports.Console()
  ]
});

module.exports = logger;
