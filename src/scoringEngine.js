const { normalizeText, TARGET_URL_KEYWORDS } = require('./utils');

const STRONG_KEYWORDS = [
  'product', 'products', 'producto', 'productos', 'specifications', 'features', 'caracteristicas',
  'catalog', 'catalogo', 'category', 'collection', 'categoria', 'about us', 'sobre nosotros',
  'contact', 'contacto', 'company', 'empresa'
];

const PARTIAL_KEYWORDS = [
  'spec', 'feature', 'detail', 'modelo', 'tienda', 'shop', 'store', 'about', 'support', 'help'
];

const PHRASES = [
  'product details', 'technical specifications', 'about our company', 'contact us',
  'nuestra empresa', 'atencion al cliente', 'catalogo de productos', 'product catalog'
];

const HEADING_HINTS = ['product', 'products', 'catalog', 'category', 'about', 'contact', 'producto', 'categoria', 'contacto'];

function scoreUrl(url) {
  const lower = normalizeText(url);
  if (/(\/|\b)(blog|news|article|post)(\/|\b)/.test(lower)) return -10;

  let score = 0;
  if (TARGET_URL_KEYWORDS.product.some((k) => lower.includes(k))) score += 6;
  if (TARGET_URL_KEYWORDS.shop.some((k) => lower.includes(k))) score += 5;
  if (TARGET_URL_KEYWORDS.category.some((k) => lower.includes(k))) score += 4;
  if (TARGET_URL_KEYWORDS.about.some((k) => lower.includes(k))) score += 3;
  if (TARGET_URL_KEYWORDS.contact.some((k) => lower.includes(k))) score += 2;

  const depth = (new URL(url)).pathname.split('/').filter(Boolean).length;
  if (depth >= 2) score += 3;
  if (/\d/.test(url)) score += 2;

  return score;
}

function classifyPage({ url, text, headings = [] }) {
  const urlNorm = normalizeText(url);
  const textNorm = normalizeText(text);
  const headingNorm = normalizeText(headings.join(' '));

  const blogSignals = [
    'published', 'author', 'comments', 'read more', 'posted on', 'fecha', 'comentarios', 'by '
  ];

  if (/(\/|\b)(blog|news)(\/|\b)/.test(urlNorm) || blogSignals.filter((s) => textNorm.includes(s)).length >= 2) {
    return 'BLOG';
  }

  const productSignals = ['specification', 'features', 'sku', 'price', 'buy now', 'caracteristicas', 'modelo'];
  const categorySignals = ['category', 'collection', 'browse', 'shop all', 'catalog', 'categoria'];
  const aboutSignals = ['about us', 'our company', 'our mission', 'sobre nosotros', 'nuestra empresa'];
  const contactSignals = ['contact', 'email', 'phone', 'support', 'form', 'telefono', 'contacto'];

  const has = (arr) => arr.some((k) => textNorm.includes(k) || headingNorm.includes(k) || urlNorm.includes(k));

  if (has(productSignals)) return 'PRODUCT';
  if (has(categorySignals)) return 'CATEGORY';
  if (has(aboutSignals)) return 'ABOUT';
  if (has(contactSignals)) return 'CONTACT';
  return 'GENERIC';
}

function scoreRelevance({ url, text, headings = [] }) {
  const normalized = normalizeText(text);
  const urlNorm = normalizeText(url);
  const headingNorm = normalizeText(headings.join(' '));

  let score = 0;

  for (const kw of STRONG_KEYWORDS) {
    if (normalized.includes(kw)) score += 5;
  }
  for (const kw of PARTIAL_KEYWORDS) {
    if (normalized.includes(kw)) score += 3;
  }
  for (const phrase of PHRASES) {
    if (normalized.includes(phrase)) score += 3;
  }
  for (const h of HEADING_HINTS) {
    if (headingNorm.includes(h)) score += 2;
    if (urlNorm.includes(h)) score += 2;
  }

  const coOccurBuckets = [
    ['product', 'specification'],
    ['catalog', 'category'],
    ['about', 'company'],
    ['contact', 'support'],
    ['producto', 'caracteristicas'],
    ['contacto', 'soporte']
  ];

  for (const bucket of coOccurBuckets) {
    if (bucket.every((t) => normalized.includes(t))) score += 2;
  }

  return score;
}

function isMatch(score) {
  return score >= 6;
}

module.exports = {
  scoreUrl,
  classifyPage,
  scoreRelevance,
  isMatch
};
