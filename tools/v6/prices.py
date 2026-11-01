"""v6 Track B (part 1): daily price histories for every ticker in the point-in-time 8-K index that has a relevant event, plus
market/sector ETFs and VIX. Yahoo first (still-listed companies, no quota); Tiingo for tickers Yahoo no longer has (delisted, acquired,
renamed), within the free plan (<= 480 new symbols a month, <= 45 requests an hour). Cached per ticker (never re-downloaded once
complete), resumable, manifest with source and coverage. Output research/v6/prices/<TICKER>.json.gz:
  {"t": ticker, "src": "yahoo"|"tiingo", "d": [[YYYY-MM-DD, open, high, low, close, volume], ...], "splits": [[date, ratio], ...]}
Yahoo prices come split-adjusted, Tiingo prices raw: each file says which (split_adjusted) and lists split events, so labels
correct returns across a split explicitly.
  python3 tools/v6/prices.py [--minutes 270]"""
import argparse, glob, gzip, json, os, time, urllib.request
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IDX, OUT = os.path.join(ROOT, 'research', 'v6', 'index'), os.path.join(ROOT, 'research', 'v6', 'prices')
ITEMS = {'1.01', '2.01', '2.02', '2.05', '2.06', '3.01', '4.02', '5.02', '7.01', '8.01'}
ETFS = ['SPY', 'QQQ', 'IWM', 'XLK', 'XLF', 'XLV', 'XLE', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE', 'XLC', '^VIX']
P1, P2 = int(datetime(2021, 10, 1, tzinfo=timezone.utc).timestamp()), int(datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())


def tickers():
    out = {}
    for p in sorted(glob.glob(os.path.join(IDX, '8k-*.jsonl.gz'))):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if not set(r.get('items') or []) & ITEMS: continue
                common = [t for t in r.get('tickers') or [] if t.isalpha() and not (len(t) == 5 and t[-1] in 'WURZ')]  # skip warrants/units/rights/preferreds
                for t in common[:1]: out[t] = out.get(t, 0) + 1  # one listing per company: the first common share
    return out


def yahoo(t):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(t)}?period1={P1}&period2={P2}&interval=1d&events=split'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=25) as r: res = json.load(r)['chart']['result']
    except Exception: return None
    if not res or not res[0].get('timestamp'): return None
    r = res[0]; q = r['indicators']['quote'][0]
    d = [[datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d'), o, h, l, c, v] for ts, o, h, l, c, v in zip(r['timestamp'], q['open'], q['high'], q['low'], q['close'], q['volume']) if c]
    sp = [[datetime.fromtimestamp(int(k), timezone.utc).strftime('%Y-%m-%d'), round(e['numerator'] / e['denominator'], 6)] for k, e in ((r.get('events') or {}).get('splits') or {}).items()]
    return {'t': t, 'src': 'yahoo', 'split_adjusted': True, 'd': d, 'splits': sorted(sp)}


def tiingo(t, key):
    url = f'https://api.tiingo.com/tiingo/daily/{urllib.request.quote(t)}/prices?startDate=2021-10-01&endDate=2026-11-15&token={key}'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Content-Type': 'application/json'}), timeout=30) as r: rows = json.load(r)
    except Exception as e:
        return 'quota' if '429' in str(e) else None
    if not isinstance(rows, list) or not rows: return None
    d = [[x['date'][:10], x.get('open'), x.get('high'), x.get('low'), x.get('close'), x.get('volume')] for x in rows if x.get('close')]
    sp = [[x['date'][:10], x['splitFactor']] for x in rows if x.get('splitFactor') not in (None, 1, 1.0)]
    return {'t': t, 'src': 'tiingo', 'split_adjusted': False, 'd': d, 'splits': sp}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--minutes', type=float, default=270); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); mp = os.path.join(OUT, 'manifest.json')
    man = json.load(open(mp)) if os.path.exists(mp) else {'done': {}, 'missing': {}, 'tiingo_month': {}}
    key, month, t_end = os.environ.get('TIINGO_KEY', '').strip(), datetime.now(timezone.utc).strftime('%Y-%m'), time.time() + a.minutes * 60
    tk = tickers(); order = ETFS + sorted(tk, key=lambda t: -tk[t])
    print(len(tk), 'tickers with relevant events;', len(man['done']), 'already cached', flush=True)
    t_req = []
    for t in order:
        if time.time() > t_end: break
        if t in man['done'] or (t in man['missing'] and man['missing'][t] == 'none'): continue
        r = yahoo(t) if t not in man['missing'] else None; time.sleep(0.25)
        if not r and key:
            used = man['tiingo_month'].get(month, 0)
            if used >= 480: man['missing'][t] = 'tiingo-month-cap'; continue
            t_req = [x for x in t_req if time.time() - x < 3600]
            if len(t_req) >= 45: time.sleep(max(0, 3600 - (time.time() - t_req[0])) + 1); t_req = t_req[1:]
            r = tiingo(t, key); t_req.append(time.time())
            if r == 'quota': man['missing'][t] = 'tiingo-quota'; time.sleep(60); continue
            man['tiingo_month'][month] = used + 1
        if not r: man['missing'][t] = 'none'; continue
        with gzip.open(os.path.join(OUT, t.replace('^', '_') + '.json.gz'), 'wt') as f: json.dump(r, f, separators=(',', ':'))
        man['done'][t] = {'src': r['src'], 'n': len(r['d']), 'first': r['d'][0][0], 'last': r['d'][-1][0], 'splits': len(r['splits'])}
        man['missing'].pop(t, None)
        if len(man['done']) % 100 == 0: json.dump(man, open(mp, 'w')); print(len(man['done']), 'cached', flush=True)
    json.dump(man, open(mp, 'w'))
    src = {}; [src.__setitem__(v['src'], src.get(v['src'], 0) + 1) for v in man['done'].values()]
    print('cached', len(man['done']), src, '| missing', len(man['missing']), flush=True)


if __name__ == '__main__':
    main()
