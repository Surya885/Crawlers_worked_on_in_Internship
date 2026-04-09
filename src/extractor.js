const { normalizeText } = require('./utils');

async function extractPageData(page, url) {
  const data = await page.evaluate(() => {
    const text = document.body ? document.body.innerText || '' : '';
    const title = document.title || '';
    const headings = Array.from(document.querySelectorAll('h1, h2')).map((h) => h.textContent || '').slice(0, 20);
    const links = Array.from(document.querySelectorAll('a[href]')).map((a) => a.getAttribute('href')).filter(Boolean);
    return { text, title, headings, links };
  });

  return {
    url,
    title: data.title,
    text: data.text,
    normalizedText: normalizeText(data.text),
    headings: data.headings,
    links: data.links
  };
}

async function maybeInteract(page) {
  const clicked = await page.evaluate(async () => {
    const triggerLabels = ['load more', 'show more', 'ver más', 'mostrar más', 'next', 'siguiente', 'expand'];
    const candidates = Array.from(document.querySelectorAll('button, a, [role="button"]'));

    const action = async (el) => {
      try {
        el.scrollIntoView({ block: 'center' });
        el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        return true;
      } catch {
        return false;
      }
    };

    for (const el of candidates.slice(0, 40)) {
      const t = (el.innerText || el.textContent || '').toLowerCase().trim();
      if (!t) continue;
      if (triggerLabels.some((key) => t.includes(key))) {
        const ok = await action(el);
        if (ok) return true;
      }
    }
    return false;
  });

  await page.mouse.wheel(0, 2200);
  return clicked;
}

module.exports = {
  extractPageData,
  maybeInteract
};
