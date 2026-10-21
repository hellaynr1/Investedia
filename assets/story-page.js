// Story page: ?id=STORY_ID. Chain of cause and effect, how the story developed, and next steps.
(() => {
  const root = document.getElementById('sp'), id = new URLSearchParams(location.search).get('id');
  const arr = d => `<span class="sp-dir ${d}">${d === 'up' ? '↑' : d === 'down' ? '↓' : d === 'mixed' ? '↔' : '–'}</span>`;
  const fl = c => c ? `<img class="sp-fl" src="assets/globe/flags/${c.toLowerCase()}.svg" alt="" onerror="this.remove()">` : '';
  const lg = t => t && !/[\^=]/.test(t) ? `<img class="sp-lg" src="https://cdn.brandfetch.io/${/-USD$/.test(t) ? 'crypto/' + encodeURIComponent(t.split('-')[0]) : 'ticker/' + encodeURIComponent(t)}/w/96/h/96/fallback/404?c=${BF}" alt="" onerror="this.remove()">` : '';
  const ic = i => i.kind === 'country' || !i.ticker ? fl(i.country) : lg(i.ticker) || fl(i.country);
  const link = s => `story.html?id=${encodeURIComponent(s.id)}`;
  const FKEY = 'inv-follow-items';
  const followed = () => { try { return JSON.parse(localStorage.getItem(FKEY)) || []; } catch { return []; } };
  const toggle = n => { const f = followed(), i = f.indexOf(n); i < 0 ? f.push(n) : f.splice(i, 1); try { localStorage.setItem(FKEY, JSON.stringify(f)); } catch {} return i < 0; };
  loadNews().then(d => {
    const all = d.stories, s = all.find(x => x.id === id);
    if (!s) { root.innerHTML = '<div class="sp-none">We couldn’t find that story. It may be older than 7 days. <a href="news.html">Back to the news</a></div>'; return; }
    document.title = s.headline + ' · Investedia';
    const names = new Set([...(s.entities || []).map(e => e.name), ...(s.impacts || []).map(i => i.name)].filter(Boolean));
    const rel = all.filter(x => x.id !== s.id && ([...(x.entities || []).map(e => e.name), ...(x.impacts || []).map(i => i.name)].some(n => names.has(n))));
    const thread = [s, ...rel].sort((a, b) => Date.parse(a.published_at) - Date.parse(b.published_at)).slice(-6);
    const others = i => all.filter(x => x.id !== s.id && (x.impacts || []).some(z => z.name === i.name)).slice(0, 2).map(x => ({ x, z: x.impacts.find(z => z.name === i.name) }));
    const imp = s.impacts || [], e0 = imp[0], follow = (s.entities?.[0]?.name) || (e0 && e0.name) || nm(s.location.country);
    const photo = s.image ? `<div class="sp-im"><img class="ph" src="assets/globe/${esc(s.image.file)}" alt="${esc(s.image.alt || '')}"><span class="cr">${s.image.kind === 'place' ? 'Photo' : 'Illustration'} · ${esc(s.image.credit || '')} · ${esc(s.image.source || '')}</span></div>` : '';
    root.innerHTML = `<a class="sp-back" href="news.html">← News</a>
    <div class="sp-pg"><div><div class="sp-m">${fl(ISO[s.location.country])}<b>${esc(s.location.place.split(',')[0])}</b><span>· ${esc(CAT[s.category] || '')} · ${ago(s.published_at)}</span></div><h1>${esc(s.headline)}</h1>${photo}<p class="sp-sum">${esc(s.summary)}</p>
    <section class="sp-sec"><h2>The chain of cause and effect</h2><p>What happened, why it matters, and who it touches.</p><div class="sp-chain">
     <div class="sp-step"><span class="n">1</span><div class="sp-lab">What happened</div><div class="sp-box"><p>${esc(s.summary)}</p></div></div>
     <div class="sp-step"><span class="n">2</span><div class="sp-lab">Why it matters</div><div class="sp-box"><p>${esc(s.why_moved || s.why || '')}</p></div></div>
     <div class="sp-step"><span class="n">3</span><div class="sp-lab">Who it touches, and which way</div>${imp.length ? imp.slice(0, 4).map(i => { const o = others(i); return `<div class="sp-fi"><div class="hd">${ic(i)}<b>${esc(i.name)}</b><small>${esc(i.kind)}</small>${arr(i.direction)}</div><p>${esc(i.why)}</p>${o.length ? `<div class="sp-also"><div class="t">Also pushing on ${esc(i.name)} this week</div>${o.map(({ x, z }) => `<a href="${link(x)}">${arr(z.direction)}<span>${esc(x.headline)}</span></a>`).join('')}</div>` : ''}</div>`; }).join('') : '<div class="sp-box"><p>No direct knock-on effects identified for this story yet.</p></div>'}</div>
    </div></section>
    ${thread.length > 1 ? `<section class="sp-sec"><h2>How this story developed</h2><p>Reports on the same thread, oldest first.</p><div class="sp-tl">${thread.map((x, n) => `<div class="sp-ev${x.id === s.id ? ' now' : ''}"><div class="d">${new Date(x.published_at).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })} · ${new Date(x.published_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</div><a href="${link(x)}">${esc(x.headline)}</a><p>${esc(x.summary)}</p>${(x.impacts || []).length ? `<div class="eff">${x.impacts.slice(0, 3).map(i => `<span>${ic(i)}${esc(i.name)} ${arr(i.direction)}</span>`).join('')}</div>` : ''}</div>`).join('')}</div></section>` : ''}
    <div class="sp-src"><span>Source: ${(s.sources || [s.source]).slice(0, 3).map(x => x ? `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.name)}</a>` : '').join(', ')}</span><span><a href="assets/globe/news.html?story=${encodeURIComponent(s.id)}">Open on the globe →</a></span></div></div>
    <aside class="sp-side"><div class="sp-card"><h3>What you can do next</h3>
      <div class="sp-act"><span class="ic">◉</span><span><b>Follow ${esc(follow)}</b><small>Keep an eye on new stories that touch it</small></span><button class="sp-b p" type="button" id="sp-f"></button></div>
      <div class="sp-act"><span class="ic">☰</span><span><b>Add to my morning briefing</b><small>This thread, summarised each morning</small></span><button class="sp-b" type="button" data-auth="up">Add</button></div>
      <div class="sp-act"><span class="ic">?</span><span><b>Learn the basics</b><small>How news moves markets</small></span><a class="sp-b" href="education.html">Read</a></div></div>
    ${e0 ? `<div class="sp-card"><h3>Two scenarios to watch</h3><div class="sp-sc"><div><b>${arr('up')} If it continues</b>More stories like this keep pushing ${esc(e0.name)} ${e0.direction === 'down' ? 'down' : e0.direction === 'up' ? 'up' : 'both ways'}; watch ${esc((imp[1] || e0).name)} next.</div><div><b>${arr('down')} If it fades</b>The effect on ${esc(e0.name)} usually eases once the news stops repeating.</div></div><p class="sp-note">Scenarios describe what could happen, not what you should do. Investedia is media, not advice: nothing here is a recommendation to buy or sell.</p></div>` : ''}
    <p class="sp-note">Summaries are written with the help of AI from each source's own reporting. Every story links to its source.</p></aside></div>`;
    const b = document.getElementById('sp-f'), paint = () => { const on = followed().includes(follow); b.textContent = on ? 'Following' : 'Follow'; b.classList.toggle('on', on); b.classList.toggle('p', !on); };
    paint(); b.onclick = () => { toggle(follow); paint(); };
  }).catch(() => { root.innerHTML = '<div class="sp-none">News could not load. Please refresh.</div>'; });
})();
