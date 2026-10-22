// First-party consent. Optional storage and remote media are off until chosen.
(() => {
  'use strict';
  const VERSION = 1, KEY = 'inv-consent', YEAR = 365 * 24 * 60 * 60 * 1000;
  const root = new URL('../', document.currentScript.src);
  const nativeGet = Storage.prototype.getItem, nativeSet = Storage.prototype.setItem, nativeRemove = Storage.prototype.removeItem;
  const preferences = new Set(['inv-theme','inv-pal','inv-studio','inv-profile','inv-notif-read','inv-learn']);
  let choice = null, panel, returnFocus;
  function read() {
    try {
      const c = JSON.parse(nativeGet.call(localStorage, KEY));
      const age = Date.now() - Date.parse(c?.date);
      return c?.version === VERSION && age >= 0 && age < YEAR && typeof c.preferences === 'boolean' && typeof c.images === 'boolean' && typeof c.analytics === 'boolean' ? c : null;
    } catch { return null; }
  }
  choice = read();
  const allows = category => category === 'necessary' || !!choice?.[category];
  // Existing optional settings use the same gate on all pages. Requested account,
  // watchlist, follow and consent storage is unaffected; preferences need opt-in.
  Storage.prototype.getItem = function(k) { return preferences.has(String(k)) && !allows('preferences') ? null : nativeGet.call(this,k); };
  Storage.prototype.setItem = function(k,v) { if (!preferences.has(String(k)) || allows('preferences')) nativeSet.call(this,k,v); };
  function activate() {
    if (!allows('images')) document.getElementById('st-geist')?.remove();
    if (!allows('images')) document.querySelectorAll('img').forEach(img => { if (img.src.startsWith('https://cdn.brandfetch.io/')) { img.src = img.dataset.fb || new URL('assets/favicon.svg', root).href; delete img.dataset.fb; } });
    const fonts = document.getElementById('consent-fonts');
    if (allows('images') && !fonts) {
      const link = document.createElement('link'); link.id = 'consent-fonts'; link.rel = 'stylesheet';
      link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&family=Geist+Mono:wght@400;500;600&display=swap';
      document.head.append(link);
    } else if (!allows('images') && fonts) fonts.remove();
  }
  function save(values) {
    choice = { version: VERSION, date: new Date().toISOString(), preferences: !!values.preferences, images: !!values.images, analytics: !!values.analytics };
    try { nativeSet.call(localStorage,KEY,JSON.stringify(choice)); } catch {}
    if (!choice.preferences) for (const k of preferences) try { nativeRemove.call(localStorage,k); } catch {}
    activate(); panel.hidden = true;
    window.dispatchEvent(new CustomEvent('inv-consent-change', { detail: {...choice} }));
    if (returnFocus?.isConnected) returnFocus.focus({ preventScroll:true });
  }
  function mount() {
    if (panel || new URLSearchParams(location.search).get('embed') === '1') return;
    panel = document.createElement('section'); panel.id = 'inv-consent-panel'; panel.className = 'consent-card'; panel.hidden = true;
    panel.setAttribute('aria-labelledby','consent-title');
    panel.innerHTML = `<div class="consent-summary"><h2 id="consent-title">Your privacy choices</h2><p>Necessary storage keeps the site working. Optional preferences, third-party images and usage statistics stay off until you choose.</p><a href="${new URL('cookies.html',root)}">Read our cookie policy</a></div><div id="consent-options" hidden><label class="consent-option"><span><b>Necessary</b><small>Consent choice, sign-in and features you request.</small></span><input type="checkbox" checked disabled aria-label="Necessary, always on"></label><label class="consent-option"><span><b>Preferences</b><small>Remember theme, chart settings and learning progress.</small></span><input id="consent-preferences" type="checkbox"></label><label class="consent-option"><span><b>Third-party images & services</b><small>Brandfetch logos, Google Fonts and live Coinbase rates. Local fallbacks work without them.</small></span><input id="consent-images" type="checkbox"></label><label class="consent-option"><span><b>Analytics</b><small>Allow existing first-party usage events, stored with Supabase. No advertising trackers.</small></span><input id="consent-analytics" type="checkbox"></label><p class="consent-hint">You can change your choices at any time in Cookie settings.</p></div><div class="consent-actions"><button type="button" data-consent="accept">Accept all</button><button type="button" data-consent="reject">Reject non-essential</button><button type="button" data-consent="settings" aria-expanded="false" aria-controls="consent-options">Settings</button><button type="button" data-consent="save" hidden>Save choices</button><button type="button" data-consent="cancel" hidden>Cancel</button></div><p class="consent-message" role="status"></p>`;
    document.body.append(panel);
    panel.addEventListener('click', e => {
      const action = e.target.closest('[data-consent]')?.dataset.consent;
      if (action === 'accept' || action === 'reject') return save({preferences:action==='accept',images:action==='accept',analytics:action==='accept'});
      if (action === 'settings') return show(true);
      if (action === 'save') return save(Object.fromEntries(['preferences','images','analytics'].map(k=>[k,panel.querySelector('#consent-'+k).checked])));
      if (action === 'cancel') { if (choice) { panel.hidden=true; returnFocus?.focus(); } else show(false); }
    });
    panel.addEventListener('keydown', e => { if (e.key === 'Escape') { if (choice) { panel.hidden=true; returnFocus?.focus(); } else show(false); } });
    if (!choice) show(false);
  }
  function show(settings = false) {
    mount(); if (!panel) return;
    if (panel.hidden) returnFocus = document.activeElement;
    panel.hidden = false;
    panel.querySelector('#consent-options').hidden = !settings;
    panel.querySelector('[data-consent=settings]').hidden = settings;
    panel.querySelector('[data-consent=settings]').setAttribute('aria-expanded',String(settings));
    for(const key of ['save','cancel']) panel.querySelector('[data-consent='+key+']').hidden = !settings;
    for(const k of ['preferences','images','analytics']) panel.querySelector('#consent-'+k).checked = allows(k);
    if(settings) panel.querySelector('#consent-preferences').focus({preventScroll:true});
  }
  window.InvConsent = { allows, mount, open:()=>show(true), version:VERSION, choice:()=>choice&&({...choice}) };
  document.addEventListener('click',e=>{if(e.target.closest('[data-cookie-settings]')){e.preventDefault();show(true);}});
  addEventListener('storage',e=>{if(e.key===KEY){choice=read();activate();window.dispatchEvent(new Event('inv-consent-change'));}});
  activate();
})();
