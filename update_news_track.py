"""Price recorder for "since the news".

Every time the price robot runs, this appends one price point for each asset that a recent story names (story impacts, last 72 hours)
to assets/globe/news-track.json. The site draws the since-the-news chart from it: price when the article appeared, and every run after.
Prices come from files the price robot has just written (markets.json, news-prices.json), so no extra network calls are made.
A point is added only when those files carry a new "asof" time, so a failed price run never adds a fake flat line. Failures keep the previous file.
Format: {"schema":1,"updated":"...","asof":"...","s":{"BZ=F":[[epoch_minute, price], ...]}}

Track record: once an article is at least 24 hours old, each priced asset it names gets ONE judged call, kept for good in
assets/globe/news-ledger.json (the 72-hour price series is trimmed, the ledger is not). The call is the direction the article implied
(up or down; mixed and unclear are not calls). The move is measured from the first price recorded after the article to the first
price recorded at least 24 hours after it (and within 48 hours). "hit" = the asset moved the implied way by at least 0.3%, "miss" =
it moved the other way by at least 0.3%, "flat" = it moved less than 0.3% either way (not counted in the hit rate).
Format: {"schema":1,"since":"...","horizon_h":24,"calls":[{"id","h","sym","name","dir","pub":epoch_min,"move":pct,"res":"hit|miss|flat"}]}
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(ROOT, 'assets', 'globe')
KEEP = timedelta(hours=72)
HORIZON = timedelta(hours=24)
MAX_AGE = timedelta(hours=48)
FLAT = 0.3
LATE = timedelta(minutes=90)


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


def judge(stories, series, ledger, now):
    """Append newly judged calls to the ledger (a dict). Returns how many were added."""
    done = {(c.get('id'), c.get('sym')) for c in ledger.get('calls', [])}
    known = set(series)
    added = 0
    for s in stories:
        try:
            pub = parse(s['published_at'])
        except Exception:
            continue
        if now - pub < HORIZON:
            continue
        for i in s.get('impacts') or []:
            d = (i or {}).get('direction')
            sym = resolve((i or {}).get('ticker'), known)
            if d not in ('up', 'down') or not sym or (s.get('id'), sym) in done:
                continue
            pts = sorted((p[0] * 60, p[1]) for p in series[sym] if isinstance(p, list) and len(p) == 2 and p[1] and p[1] > 0)
            pt = pub.timestamp()
            after = [p for p in pts if p[0] >= pt]
            if not after:
                continue
            before = [p for p in pts if pt - 3 * 3600 <= p[0] < pt]
            if after[0][0] - pt > LATE.total_seconds() and not before:
                continue
            end = [p for p in after if p[0] >= pt + HORIZON.total_seconds()]
            if not end or end[0][0] > pt + MAX_AGE.total_seconds() or end[0][0] == after[0][0]:
                continue
            move = (end[0][1] / after[0][1] - 1) * 100
            res = 'flat' if abs(move) < FLAT else 'hit' if (move > 0) == (d == 'up') else 'miss'
            ledger.setdefault('calls', []).append({'id': s.get('id'), 'sym': sym, 'name': (i.get('name') or sym)[:60], 'dir': d, 'pub': int(pt // 60), 'move': round(move, 2), 'res': res, 'cat': s.get('category'), 'h': str(s.get('headline') or '')[:140]})
            done.add((s.get('id'), sym))
            added += 1
    return added


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
    out = {'schema': 1, 'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'asof': asof.isoformat(), 'every_min': 15, 's': series}
    ledger = load('news-ledger.json', {})
    if not isinstance(ledger, dict) or ledger.get('schema') != 1:
        ledger = {'schema': 1, 'since': now.strftime('%Y-%m-%d'), 'horizon_h': 24, 'calls': []}
    judged = judge(stories, series, ledger, now)
    out['_ledger'] = ledger if judged else None
    return out, f'{len(syms)} assets, {added} new points, {judged} calls judged'


def main():
    try:
        data, note = update()
        if data is None:
            print('news track:', note); return 0
        ledger = data.pop('_ledger', None)
        if ledger:
            for d in (G, os.path.join(ROOT, 'docs', 'assets', 'globe')):
                if os.path.isdir(d):
                    lp = os.path.join(d, 'news-ledger.json'); lt = lp + '.tmp'
                    with open(lt, 'w', encoding='utf-8') as f:
                        json.dump(ledger, f, separators=(',', ':'))
                    os.replace(lt, lp)
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
