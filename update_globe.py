"""Refresh the world-globe prices (assets/globe/index.html) from Yahoo Finance.

The globe page carries its data inline between /*MK*/ markers; this rewrites price, day and week change and the
one-month sparkline for every asset, keeping names and places. Assets Yahoo fails to return keep their last values.
"""
import json, re, time, urllib.request, urllib.parse, concurrent.futures as cf
from datetime import datetime, timezone

PAGES = ['assets/globe/index.html', 'docs/assets/globe/index.html']
UA = {'User-Agent': 'Mozilla/5.0'}

def ysym(m):
    return m['s'] + '=X' if m['t'] == 'fx' else m['s'] + '-USD' if m['t'] == 'crypto' else m['s']

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

def main():
    html = open(PAGES[0], encoding='utf-8').read()
    mk = json.loads(re.search(r'/\*MK\*/(.*?)/\*MK\*/', html, re.S).group(1))
    with cf.ThreadPoolExecutor(16) as ex:
        res = list(ex.map(lambda m: fetch(ysym(m)), mk))
    ok = 0
    for m, c in zip(mk, res):
        if not c: continue
        sign = -1 if m.get('inv') else 1
        m['p'] = round(c[-1], 6); m['d'] = round(sign * (c[-1] / c[-2] - 1) * 100, 2); m['w'] = round(sign * (c[-1] / c[-6] - 1) * 100, 2)
        m['sp'] = [round(x, 6) for x in c[-22:]]; ok += 1
    print(f'globe: {ok}/{len(mk)} assets refreshed')
    if ok < len(mk) * .5: raise SystemExit('Too many failures; keeping the previous data')
    data = json.dumps(mk, separators=(',', ':'), ensure_ascii=False)
    asof = "'" + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + "'"
    for p in PAGES:
        h = open(p, encoding='utf-8').read()
        h = re.sub(r'/\*MK\*/.*?/\*MK\*/', lambda _: '/*MK*/' + data + '/*MK*/', h, count=1, flags=re.S)
        h = re.sub(r'/\*ASOF\*/.*?/\*ASOF\*/', lambda _: '/*ASOF*/' + asof + '/*ASOF*/', h, count=1)
        open(p, 'w', encoding='utf-8').write(h)

if __name__ == '__main__':
    main()
