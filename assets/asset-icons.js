// One place for asset logos: local logo file -> Brandfetch -> flag -> clean glyph/initial tile. Never a white box.
(() => {
  const BASE = (() => { try { return new URL('.', document.currentScript.src).href; } catch { return ''; } })() || 'assets/';
  const BFID = typeof BF !== 'undefined' ? BF : '1idNJqyfpKbma454ae4';
  let LOGOS = {}; const ready = fetch(BASE + 'globe/logos.json').then(r => r.json()).then(j => { LOGOS = j; }).catch(() => {});
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const svg = d => `<svg viewBox="0 0 24 24" width="62%" height="62%" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const G = {
    barrel: svg("<path d=\"M7.278 4h9.444a2 2 0 0 1 1.841 1.22c.958 2.26 1.437 4.52 1.437 6.78c0 2.26 -.479 4.52 -1.437 6.78a2 2 0 0 1 -1.841 1.22h-9.444a2 2 0 0 1 -1.841 -1.22c-.958 -2.26 -1.437 -4.52 -1.437 -6.78c0 -2.26 .479 -4.52 1.437 -6.78a2 2 0 0 1 1.841 -1.22z\" /> <path d=\"M14 4c.667 2.667 1 5.333 1 8s-.333 5.333 -1 8\" /> <path d=\"M10 4c-.667 2.667 -1 5.333 -1 8s.333 5.333 1 8\" /> <path d=\"M4.5 16h15\" /> <path d=\"M19.5 8h-15\" />"),
    flame: svg("<path d=\"M12 12c2 -2.96 0 -7 -1 -8c0 3.038 -1.773 4.741 -3 6c-1.226 1.26 -2 3.24 -2 5a6 6 0 1 0 12 0c0 -1.532 -1.056 -3.94 -2 -5c-1.786 3 -2.791 3 -4 2z\" />"),
    fuel: svg("<path d=\"M14 11h1a2 2 0 0 1 2 2v3a1.5 1.5 0 0 0 3 0v-7l-3 -3\" /> <path d=\"M4 20v-14a2 2 0 0 1 2 -2h6a2 2 0 0 1 2 2v14\" /> <path d=\"M3 20l12 0\" /> <path d=\"M18 7v1a1 1 0 0 0 1 1h1\" /> <path d=\"M4 11l10 0\" />"),
    coin: svg("<path d=\"M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0\" /> <path d=\"M14.8 9a2 2 0 0 0 -1.8 -1h-2a2 2 0 1 0 0 4h2a2 2 0 1 1 0 4h-2a2 2 0 0 1 -1.8 -1\" /> <path d=\"M12 7v10\" />"),
    box: svg("<path d=\"m21.12 6.4-6.05-4.06a2 2 0 0 0-2.17-.05L2.95 8.41a2 2 0 0 0-.95 1.7v5.82a2 2 0 0 0 .88 1.66l6.05 4.07a2 2 0 0 0 2.17.05l9.95-6.12a2 2 0 0 0 .95-1.7V8.06a2 2 0 0 0-.88-1.66Z\" /> <path d=\"M10 22v-8L2.25 9.15\" /> <path d=\"m10 14 11.77-6.87\" />"),
    wheat: svg("<path d=\"M2 22 16 8\" /> <path d=\"M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z\" /> <path d=\"M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z\" /> <path d=\"M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94Z\" /> <path d=\"M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4Z\" /> <path d=\"M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z\" /> <path d=\"M15.47 13.47 17 15l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L9 15l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z\" /> <path d=\"M19.47 9.47 21 11l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L13 11l1.53-1.53a3.5 3.5 0 0 1 4.94 0Z\" />"),
    cup: svg("<path d=\"M3 14c.83 .642 2.077 1.017 3.5 1c1.423 .017 2.67 -.358 3.5 -1c.83 -.642 2.077 -1.017 3.5 -1c1.423 -.017 2.67 .358 3.5 1\" /> <path d=\"M8 3a2.4 2.4 0 0 0 -1 2a2.4 2.4 0 0 0 1 2\" /> <path d=\"M12 3a2.4 2.4 0 0 0 -1 2a2.4 2.4 0 0 0 1 2\" /> <path d=\"M3 10h14v5a6 6 0 0 1 -6 6h-2a6 6 0 0 1 -6 -6v-5z\" /> <path d=\"M16.746 16.726a3 3 0 1 0 .252 -5.555\" />"),
    beef: svg("<circle cx=\"12.5\" cy=\"8.5\" r=\"2.5\" /> <path d=\"M12.5 2a6.5 6.5 0 0 0-6.22 4.6c-1.1 3.13-.78 3.9-3.18 6.08A3 3 0 0 0 5 18c4 0 8.4-1.8 11.4-4.3A6.5 6.5 0 0 0 12.5 2Z\" /> <path d=\"m18.5 6 2.19 4.5a6.48 6.48 0 0 1 .31 2 6.49 6.49 0 0 1-2.6 5.2C15.4 20.2 11 22 7 22a3 3 0 0 1-2.68-1.66L2.4 16.5\" />"),
    drop: svg("<path d=\"M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z\" />")
  };
  const COMM = { 'GC=F': 'coin', 'SI=F': 'coin', 'PL=F': 'coin', 'PA=F': 'coin', 'HG=F': 'box', 'ALI=F': 'box', 'CL=F': 'barrel', 'BZ=F': 'barrel', 'NG=F': 'flame', 'HO=F': 'fuel', 'RB=F': 'fuel',
    'ZW=F': 'wheat', 'ZC=F': 'wheat', 'ZS=F': 'wheat', 'ZO=F': 'wheat', 'ZR=F': 'wheat', 'KC=F': 'cup', 'CC=F': 'cup', 'SB=F': 'box', 'CT=F': 'wheat', 'OJ=F': 'drop', 'LE=F': 'beef', 'HE=F': 'beef', 'GF=F': 'beef' };
  const tile = (inner, style = '') => `<span class="ai-t" style="${style}">${inner}</span>`;
  const initial = n => tile(`<b>${esc((n || '?').trim()[0].toUpperCase())}</b>`);
  // sym: site symbol, name, type, cc (country code) -> HTML (26px tile; size set by CSS .ai-t / .ai-i)
  function icon(a) {
    const sym = a.s || a.ticker || '', n = a.n || a.name || '', c = COMM[sym];
    if (c) return tile(G[c], 'color:#c8c8cf');
    const base = sym.replace(/-USD$/, '');
    const srcs = [];
    if (LOGOS[base]) srcs.push(BASE + 'globe/' + LOGOS[base]);
    if (a.t === 'crypto' || /-USD$/.test(sym)) srcs.push(`https://cdn.brandfetch.io/crypto/${encodeURIComponent(base)}/w/96/h/96/fallback/404?c=${BFID}`);
    else if (!/[\^=]/.test(sym) && a.t !== 'fx') srcs.push(`https://cdn.brandfetch.io/ticker/${encodeURIComponent(sym)}/w/96/h/96/fallback/404?c=${BFID}`);
    const flag = a.cc ? `${BASE}globe/flags/${String(a.cc).toLowerCase()}.svg` : '';
    if (flag) srcs.push(flag);
    if (!srcs.length) return initial(n);
    return `<img class="ai-i" src="${esc(srcs[0])}" alt="" data-q="${esc(JSON.stringify(srcs.slice(1)))}" data-f="${esc(initial(n))}" onerror="window.AssetIcons.next(this)">`;
  }
  function next(img) { let q = []; try { q = JSON.parse(img.dataset.q || '[]'); } catch {} if (q.length) { img.dataset.q = JSON.stringify(q.slice(1)); img.src = q[0]; } else img.outerHTML = img.dataset.f; }
  window.AssetIcons = { icon, next, ready };
})();
