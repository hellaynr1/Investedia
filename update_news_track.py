"""Price recorder for "since the news".

Every time the price robot runs, this appends one price point for each asset that a recent story names (story impacts, last 72 hours)
to assets/globe/news-track.json. The site draws the since-the-news chart from it: price when the article appeared, and every run after.
Prices come from files the price robot has just written (markets.json, news-prices.json), so no extra network calls are made.
A point is added only when those files carry a new "asof" time, so a failed price run never adds a fake flat line. Failures keep the previous file.
Format: {"schema":1,"updated":"...","asof":"...","s":{"BZ=F":[[epoch_minute, price], ...]}}

Track record (schema 2): every implication stamped at creation (created_at, version, confidence, horizon, scorable) is copied into
assets/globe/news-ledger.json as a frozen "pending" call the first time a run sees it; later runs judge that frozen copy, never the current
story, so a call cannot be changed after the outcome. Back-filled implications are not scorable. Schema-1 calls are kept and marked legacy.
The call is the direction the article implied (up or down; mixed and unclear are not calls). The move is measured from the first price recorded after the article to the first
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


def resolve_row(row, known):
    """Price symbol of an implication's CANONICAL asset (registry stamp). A row the registry could not resolve is never priced:
    a raw ticker string can name another company (e.g. MC = Moelis & Company, not LVMH). Rows written before the registry
    (no stamp at all) keep the old symbol aliasing so already-frozen behaviour does not change."""
    row = row or {}
    a = row.get('asset')
    if a: return a.get('px') if a.get('px') in known and a.get('freq') != 'monthly' else None
    if 'unresolved' in row: return None
    return resolve(row.get('ticker'), known)


def tracked_symbols(stories, known, now):
    out = set()
    for s in stories:
        try:
            if now - parse(s['published_at']) > KEEP:
                continue
        except Exception:
            continue
        for i in s.get('impacts') or []:
            sym = resolve_row(i, known)
            if sym:
                out.add(sym)
    return out


def freeze(stories, series, ledger, now):
    """Copy every new scorable implication into the ledger as a frozen, pending call, the first time it is seen.
    Only implications stamped at creation (created_at, scorable) qualify; back-filled ones never do. Returns how many were frozen."""
    done = {(c.get('id'), c.get('sym')) for c in ledger.get('calls', [])}
    known, added = set(series), 0
    for s in stories:
        for i in s.get('impacts') or []:
            i = i or {}
            if not i.get('scorable') or not i.get('created_at') or i.get('direction') not in ('up', 'down'):
                continue
            sym = resolve_row(i, known)
            if not sym or (s.get('id'), sym) in done:
                continue
            try:
                created = parse(i['created_at'])
            except Exception:
                continue
            ledger.setdefault('calls', []).append({'id': s.get('id'), 'sym': sym, **({'aid': i['asset']['id']} if i.get('asset') else {}), 'name': (i.get('name') or sym)[:60], 'dir': i['direction'], 'conf': i.get('confidence'),
                                                   'created': i['created_at'], 'ver': i.get('version'), 'model': i.get('model'), 'horizon': i.get('horizon'),
                                                   'baseline_rule': i.get('baseline_rule'), 'pub': int(created.timestamp() // 60), 'res': 'pending',
                                                   'frozen': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'cat': s.get('category'), 'h': str(s.get('headline') or '')[:140]})
            done.add((s.get('id'), sym))
            added += 1
    return added


def judge(series, ledger, now):
    """Judge pending calls from their FROZEN fields (direction, symbol, creation time), never from the current story.
    Only the outcome fields (move, res, base, end, judged) are written; prediction fields are never edited. Returns how many were judged."""
    judged = 0
    for c in ledger.get('calls', []):
        if c.get('res') != 'pending' or c.get('sym') not in series:
            continue
        created = parse(c['created'])
        if now - created < HORIZON:
            continue
        pts = sorted((p[0] * 60, p[1]) for p in series[c['sym']] if isinstance(p, list) and len(p) == 2 and p[1] and p[1] > 0)
        pt = created.timestamp()
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
        if abs(move) > 50:  # a price-series break (unit change such as pence -> pounds, split, wrong instrument), never a real 24 h move
            c.update(res='void', why='price series break (|move| > 50%)', base=[int(after[0][0] // 60), after[0][1]], end=[int(end[0][0] // 60), end[0][1]],
                     judged=now.strftime('%Y-%m-%dT%H:%M:%SZ'))
            judged += 1
            continue
        c.update(move=round(move, 2), res='flat' if abs(move) < FLAT else 'hit' if (move > 0) == (c['dir'] == 'up') else 'miss',
                 base=[int(after[0][0] // 60), after[0][1]], end=[int(end[0][0] // 60), end[0][1]], judged=now.strftime('%Y-%m-%dT%H:%M:%SZ'))
        judged += 1
    return judged


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
    if not isinstance(ledger, dict) or ledger.get('schema') not in (1, 2):
        ledger = {'schema': 2, 'since': now.strftime('%Y-%m-%d'), 'horizon_h': 24, 'calls': []}
    if ledger.get('schema') == 1:  # schema 2: calls are frozen when first seen; schema-1 calls stay as they were (marked legacy)
        for c in ledger.get('calls', []): c.setdefault('legacy', True)
        ledger.update(schema=2, live_since=now.strftime('%Y-%m-%dT%H:%M:%SZ'))
    frozen = freeze(stories, series, ledger, now)
    judged = judge(series, ledger, now)
    out['_ledger'] = ledger if frozen or judged else None
    return out, f'{len(syms)} assets, {added} new points, {frozen} calls frozen, {judged} calls judged'


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
