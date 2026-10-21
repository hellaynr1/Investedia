// One place for asset logos: local logo file -> Brandfetch -> flag -> clean glyph/initial tile. Never a white box.
(() => {
  const BFID = typeof BF !== 'undefined' ? BF : '1idNJqyfpKbma454ae4';
  let LOGOS = {}; const ready = fetch('assets/globe/logos.json').then(r => r.json()).then(j => { LOGOS = j; }).catch(() => {});
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const svg = d => `<svg viewBox="0 0 24 24" width="62%" height="62%" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const G = {
    barrel: svg('<ellipse cx="12" cy="5.5" rx="6" ry="2.5"/><path d="M6 5.5v13c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5v-13M6 10c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5M6 15c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5"/>'),
    flame: svg('<path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 .5 1.500 1.500 2 2 2 0-3-.5-5 1-8z"/>'),
    drop: svg('<path d="M12 3s6 6.500 6 11a6 6 0 0 1-12 0c0-4.500 6-11 6-11z"/>'),
    wheat: svg('<path d="M12 21V8M12 8c-2.500 0-4-1.500-4-4 2.500 0 4 1.500 4 4zM12 8c2.500 0 4-1.500 4-4-2.500 0-4 1.500-4 4zM12 13c-2.500 0-4-1.500-4-4M12 13c2.500 0 4-1.500 4-4M12 18c-2.500 0-4-1.500-4-4M12 18c2.500 0 4-1.500 4-4"/>'),
    cup: svg('<path d="M5 9h11v5a5 5 0 0 1-5 5H10a5 5 0 0 1-5-5zM16 10h1.500a2.500 2.500 0 0 1 0 5H16M8 3v3M12 3v3"/>'),
    bean: svg('<path d="M7 17c-3-3-2-9 3-11s10 2 8 7-8 7-11 4z"/><path d="M8 16c3-1 5-5 7-8"/>'),
    cube: svg('<path d="M12 3l8 4v10l-8 4-8-4V7zM4 7l8 4 8-4M12 11v10"/>'),
    leaf: svg('<path d="M5 19c0-8 5-14 14-14 0 9-6 14-14 14zM5 19l8-8"/>'),
    cow: svg('<path d="M4 8h16M6 8v3a6 6 0 0 0 12 0V8M9 14v3M15 14v3M5 8L3 5M19 8l2-3"/>'),
    chart: svg('<path d="M4 18l5-6 4 3 7-9M4 21h16"/>')
  };
  const COMM = { 'GC=F': ['el', 'Au', '#f5c542'], 'SI=F': ['el', 'Ag', '#c9ced6'], 'PL=F': ['el', 'Pt', '#b9c2d0'], 'PA=F': ['el', 'Pd', '#aab4c4'], 'HG=F': ['el', 'Cu', '#e08a5a'], 'ALI=F': ['el', 'Al', '#9fb3c8'],
    'CL=F': ['g', 'barrel'], 'BZ=F': ['g', 'barrel'], 'NG=F': ['g', 'flame'], 'HO=F': ['g', 'drop'], 'RB=F': ['g', 'drop'],
    'ZW=F': ['g', 'wheat'], 'ZC=F': ['g', 'wheat'], 'ZS=F': ['g', 'bean'], 'ZO=F': ['g', 'wheat'], 'ZR=F': ['g', 'wheat'], 'KC=F': ['g', 'cup'], 'CC=F': ['g', 'bean'], 'SB=F': ['g', 'cube'], 'CT=F': ['g', 'leaf'], 'OJ=F': ['g', 'drop'], 'LE=F': ['g', 'cow'], 'HE=F': ['g', 'cow'], 'GF=F': ['g', 'cow'] };
  const tile = (inner, style = '') => `<span class="ai-t" style="${style}">${inner}</span>`;
  const initial = n => tile(`<b>${esc((n || '?').trim()[0].toUpperCase())}</b>`);
  // sym: site symbol, name, type, cc (country code) -> HTML (26px tile; size set by CSS .ai-t / .ai-i)
  function icon(a) {
    const sym = a.s || a.ticker || '', n = a.n || a.name || '', c = COMM[sym];
    if (c) return c[0] === 'el' ? tile(`<b>${c[1]}</b>`, `color:${c[2]};background:${c[2]}22`) : tile(G[c[1]], 'color:#c8c8cf');
    const base = sym.replace(/-USD$/, '');
    const srcs = [];
    if (LOGOS[base]) srcs.push('assets/globe/' + LOGOS[base]);
    if (a.t === 'crypto' || /-USD$/.test(sym)) srcs.push(`https://cdn.brandfetch.io/crypto/${encodeURIComponent(base)}/w/96/h/96/fallback/404?c=${BFID}`);
    else if (!/[\^=]/.test(sym) && a.t !== 'fx') srcs.push(`https://cdn.brandfetch.io/ticker/${encodeURIComponent(sym)}/w/96/h/96/fallback/404?c=${BFID}`);
    const flag = a.cc ? `assets/globe/flags/${String(a.cc).toLowerCase()}.svg` : '';
    if (flag) srcs.push(flag);
    if (!srcs.length) return initial(n);
    return `<img class="ai-i" src="${esc(srcs[0])}" alt="" data-q="${esc(JSON.stringify(srcs.slice(1)))}" data-f="${esc(initial(n))}" onerror="window.AssetIcons.next(this)">`;
  }
  function next(img) { let q = []; try { q = JSON.parse(img.dataset.q || '[]'); } catch {} if (q.length) { img.dataset.q = JSON.stringify(q.slice(1)); img.src = q[0]; } else img.outerHTML = img.dataset.f; }
  window.AssetIcons = { icon, next, ready };
})();
