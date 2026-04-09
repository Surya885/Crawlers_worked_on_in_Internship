const fs = require('fs');
const path = require('path');

const BLOCKED_PATH_SEGMENTS = [
  'blog', 'news', 'article', 'post', 'insights', 'media', 'press', 'stories', 'updates', 'events',
  'privacy', 'terms', 'policy', 'login', 'signup', 'cart', 'checkout', 'faq'
];

const TARGET_URL_KEYWORDS = {
  product: ['product', 'products', 'producto', 'productos', 'item', 'sku'],
  shop: ['shop', 'store', 'catalog', 'catalogo', 'tienda'],
  category: ['category', 'categories', 'collection', 'collections', 'categoria', 'categorias'],
  about: ['about', 'about-us', 'company', 'empresa', 'nosotros', 'quienes-somos'],
  contact: ['contact', 'support', 'help', 'contacto', 'soporte', 'atencion']
};

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function safeDomain(domain) {
  return domain.replace(/^https?:\/\//i, '').replace(/[^a-zA-Z0-9.-]/g, '_');
}

function normalizeDomain(input) {
  const cleaned = input.trim();
  if (!cleaned) return null;
  if (/^https?:\/\//i.test(cleaned)) return cleaned;
  return `https://${cleaned}`;
}

function normalizeText(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isBlockedUrl(url) {
  const normalized = normalizeText(url);
  return BLOCKED_PATH_SEGMENTS.some((token) => normalized.includes(`/${token}`) || normalized.includes(`-${token}`) || normalized.includes(`${token}/`));
}

function toAbsoluteUrl(base, href) {
  try {
    return new URL(href, base).toString();
  } catch {
    return null;
  }
}

function isSameDomain(seedUrl, candidateUrl) {
  try {
    const a = new URL(seedUrl);
    const b = new URL(candidateUrl);
    return a.hostname === b.hostname;
  } catch {
    return false;
  }
}

function pathDepth(url) {
  try {
    const p = new URL(url).pathname.split('/').filter(Boolean);
    return p.length;
  } catch {
    return 0;
  }
}

function hasNumbers(value) {
  return /\d/.test(value);
}

function nowIso() {
  return new Date().toISOString();
}

function readJsonIfExists(filePath, fallback = null) {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJson(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

module.exports = {
  BLOCKED_PATH_SEGMENTS,
  TARGET_URL_KEYWORDS,
  ensureDir,
  safeDomain,
  normalizeDomain,
  normalizeText,
  sleep,
  isBlockedUrl,
  toAbsoluteUrl,
  isSameDomain,
  pathDepth,
  hasNumbers,
  nowIso,
  readJsonIfExists,
  writeJson
};
