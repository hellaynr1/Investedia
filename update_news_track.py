"""Price recorder for "since the news".

Every time the price robot runs, this appends one price point for each asset that a recent story names (story impacts, last 72 hours)
to assets/globe/news-track.json. The site draws the since-the-news chart from it: price when the article appeared, and every run after.
Prices come from files the price robot has just written (markets.json, news-prices.json), so no extra network calls are made.
A point is added only when those files carry a new "asof" time, so a failed price run never adds a fake flat line. Failures keep the previous file.
Format: {"schema":1,"updated":"...","asof":"...","s":{"BZ=F":[[epoch_minute, price], ...]}}
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(ROOT, 'assets', 'globe')
KEEP = timedelta(hours=72)


def load(name, default):
    try:
        with open(os.path.join(G, name), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def parse(ts):
    return datetime.fromisoformat(str(ts).replace('Z', '+00:00')).astimezone(timezone.utc)


def resolve(ticker, known):
    """Same aliasing as the site: SYMBOL, SYMBOL-USD, or SYMBOL without =X."""
    t = str(ticker or '').upper()
    for c in (t, t + '-USD', t[:-2] if t.endswith('=X') else None):
        if c and c in known:
            return c
    return None


def tracked_symbols(stories, known, now):
    out = set()
    for s in stories:
        try:
            if now - parse(s['published_at']) > KEEP:
                continue
        except Exception:
            continue
        for i in s.get('impacts') or []:
            sym = resolve((i or {}).get('ticker'), known)
            if sym:
                out.add(sym)
    return out


def update(now=None):
    now = now or datetime.now(timezone.utc)
    markets = load('markets.json', {})
    extra = load('news-prices.json', {})
    prices = {}
    for src in (extra.get('assets') or {}, ):
        for k, a in (src.items() if isinstance(src, dict) else []):
            if isinstance(a, dict) and isinstance(a.get('p'), (int, float)):
                prices[k] = a['p']
    for a in markets.get('assets') or []:
        if isinstance(a, dict) and isinstance(a.get('p'), (int, float)):
            prices[a['s']] = a['p']
    asof_raw = markets.get('asof') or extra.get('asof')
    if not prices or not asof_raw:
        return None, 'no prices'
    asof = parse(asof_raw)
    stories = (load('news-live.json', {}).get('stories')) or []
    syms = tracked_symbols(stories, set(prices), now)
    old = load('news-track.json', {})
    series = {k: v for k, v in (old.get('s') or {}).items() if k in syms and isinstance(v, list)}
    minute = int(asof.timestamp() // 60)
    if old.get('asof') == asof.isoformat() and set(series) == set(syms):
        return old, 'unchanged'
    cutoff = int((now - KEEP).timestamp() // 60)
    added = 0
    for sym in sorted(syms):
        pts = [p for p in series.get(sym, []) if isinstance(p, list) and len(p) == 2 and p[0] >= cutoff]
        if old.get('asof') != asof.isoformat() and (not pts or pts[-1][0] < minute):
            pts.append([minute, float(f'{prices[sym]:.6g}')])
            added += 1
        series[sym] = pts
    return {'schema': 1, 'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'asof': asof.isoformat(), 'every_min': 15, 's': series}, f'{len(syms)} assets, {added} new points'


def main():
    try:
        data, note = update()
        if data is None:
            print('news track:', note); return 0
        path = os.path.join(G, 'news-track.json')
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))
        os.replace(tmp, path)
        print('news track:', note)
    except Exception as e:
        print('news track failed, keeping the previous file:', type(e).__name__, e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
