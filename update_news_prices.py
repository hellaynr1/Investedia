"""Prices for every asset the news mentions that the main price list does not carry.

Reads assets/globe/news-live.json, finds tickers in story impacts that are missing from assets/globe/markets.json,
fetches month/week/day moves from Yahoo Finance and writes assets/globe/news-prices.json (same shape as markets.json assets).
Run after update_globe.py. Failures keep the previous file.
"""
import json, os, time, urllib.parse, urllib.request, concurrent.futures as cf
from datetime import datetime, timezone

G = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'globe')
UA = {'User-Agent': 'Mozilla/5.0'}
CRYPTO = ('-USD',)

def fetch(sym):
    for i in range(2):
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=1mo&interval=1d'
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))['chart']['result'][0]
            c = [x for x in r['indicators']['quote'][0]['close'] if x is not None]
            live = r['meta'].get('regularMarketPrice')
            if live: c[-1] = live
            if len(c) >= 6 and c[-1]: return c
        except Exception:
            time.sleep(1 + i)
    return None

def alias_known(t, known):
    return t in known or t.replace('-USD', '') in known or t.replace('=X', '') in known

def main():
    news = json.load(open(os.path.join(G, 'news-live.json'), encoding='utf-8'))['stories']
    mk = {a['s'] for a in json.load(open(os.path.join(G, 'markets.json'), encoding='utf-8'))['assets']}
    want = {}
    for s in news:
        for i in s.get('impacts') or []:
            t = (i.get('ticker') or '').strip()
            if t and i.get('kind') != 'country' and not alias_known(t, mk): want.setdefault(t, i.get('name') or t)
    path = os.path.join(G, 'news-prices.json')
    old = {}
    try: old = json.load(open(path, encoding='utf-8')).get('assets', {})
    except Exception: pass
    syms = list(want)
    with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(fetch, syms))
    out = {}
    for t, c in zip(syms, res):
        if not c: 
            if t in old: out[t] = old[t]
            continue
        out[t] = {'s': t, 'n': want[t], 't': 'crypto' if t.endswith(CRYPTO) else 'fx' if t.endswith('=X') else 'stocks',
                  'p': round(c[-1], 6), 'd': round((c[-1] / c[-2] - 1) * 100, 2), 'w': round((c[-1] / c[-6] - 1) * 100, 2), 'sp': [round(x, 6) for x in c[-22:]]}
    print(f'news prices: {len([t for t in syms if t in out])}/{len(syms)} tickers')
    doc = json.dumps({'asof': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'assets': out}, separators=(',', ':'), ensure_ascii=False)
    for d in (G, G.replace(os.sep + 'assets' + os.sep, os.sep + 'docs' + os.sep + 'assets' + os.sep)):
        if os.path.isdir(d): open(os.path.join(d, 'news-prices.json'), 'w', encoding='utf-8').write(doc)

if __name__ == '__main__':
    main()
