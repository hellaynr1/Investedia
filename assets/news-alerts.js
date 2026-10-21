// Quiet in-page headline alerts. No browser notification permission or provider calls.
(() => {
  const assetsURL = new URL('.', document.currentScript.src);
  let seen = null, timer, current;
  const style = document.createElement('style');
  style.textContent = `
  .news-alert{position:fixed;right:28px;bottom:28px;z-index:1200;width:min(390px,calc(100vw - 32px));padding:20px 44px 19px 20px;background:#111113;color:#fafafa;border:1px solid #343438;border-left:3px solid #FF7A1A;border-radius:12px;box-shadow:0 16px 50px #0008;font:14px/1.5 Inter,Arial,sans-serif;text-align:left}
  .news-alert[hidden]{display:none}.news-alert-label{font:10px/1.5 'Geist Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#FF7A1A;margin-bottom:9px}.news-alert h3{font-size:16px;line-height:1.4;letter-spacing:-.02em;margin:0 0 10px;font-weight:550}.news-alert p{font-size:12px;color:#a1a1aa;margin:0 0 12px}.news-alert a{color:#fafafa;font-size:12px;text-decoration:none;border-bottom:1px solid #555;padding-bottom:3px}.news-alert button{position:absolute;right:10px;top:10px;width:30px;height:30px;border:0;border-radius:6px;color:#a1a1aa;background:transparent;font:22px Arial;cursor:pointer}.news-alert button:hover{background:#27272a;color:white}.news-alert :focus-visible{outline:2px solid #FF7A1A;outline-offset:4px}
  @media(max-width:600px){.news-alert{right:16px;bottom:calc(18px + env(safe-area-inset-bottom));padding:17px 40px 17px 17px}.news-alert h3{font-size:15px}}
  `;
  document.head.append(style);
  function close() { if (current) current.hidden = true; clearTimeout(timer); }
  function show(story, count = 1, href) {
    close();
    if (!current) {
      current = document.createElement('aside'); current.className = 'news-alert';
      current.setAttribute('aria-label', 'New headlines');
      current.innerHTML = '<div class="news-alert-label" role="status" aria-live="polite"></div><button type="button" aria-label="Dismiss headline notification">×</button><h3></h3><p></p><a>Explore the story ↗</a>';
      current.querySelector('button').onclick = close;
      current.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
      document.body.append(current);
    }
    current.hidden = false;
    current.querySelector('.news-alert-label').textContent = count > 1 ? `${count} new headlines` : 'New headline';
    current.querySelector('h3').textContent = story.headline;
    const names = (story.impacts || []).slice(0, 3).map(i => i.name).filter(Boolean);
    current.querySelector('p').textContent = names.length ? 'Potentially affected: ' + names.join(' · ') : 'Potential impact unclear';
    current.querySelector('a').href = href || new URL('assets/globe/news.html?story=' + encodeURIComponent(story.id), location.origin + '/').href;
    // Keep the alert available until dismissed or replaced; no focus stealing.
  }
  function observe(stories, hrefFor) {
    if (!seen) { seen = new Set(stories.map(s => s.id)); return; }
    const fresh = stories.filter(s => !seen.has(s.id));
    for (const s of stories) seen.add(s.id);
    if (fresh.length) {
      fresh.sort((a,b) => b.importance - a.importance || Date.parse(b.published_at) - Date.parse(a.published_at));
      show(fresh[0], fresh.length, hrefFor?.(fresh[0]));
    }
  }
  window.NewsAlerts = { observe, show, close };
  // Other site pages get the same alerts; news views already poll their feed.
  if (!/(?:\/news\.html|\/index\.html|\/)$/.test(location.pathname)) {
    let polling = false;
    async function check() {
      if (document.hidden || polling) return;
      polling = true;
      try {
        const response = await fetch(new URL('globe/news-live.json', assetsURL), { cache: 'no-cache' });
        if (!response.ok) return;
        const data = await response.json();
        if (Array.isArray(data.stories)) observe(data.stories);
      } catch { /* Quiet retry while offline. */ }
      finally { polling = false; }
    }
    check(); setInterval(check, 30000);
  }
})();
