"""Early calls, scoring framework v2 (research/EARLY-SCORING-V2.md). Frozen parameters below; changing them = a new version.
Reads research/pre-live-implications.json; writes research/early-outcomes-v2.json. Never touches the live ledger or the site.
python3 tools/track/score_early_v2.py"""
import json, math, os, sys, urllib.parse, urllib.request, concurrent.futures as cf, statistics as st
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import registry, events as EV, update_news_track as T

FROZEN = {'version': 'early-v2', 'k_sigma': 0.5, 'min_move_pct': 0.3, 'vol_days': 20, 'max_wait_h': 96,
          'h24': ['earnings', 'guidance', 'm&a', 'capital', 'regulation', 'rates', 'macro-data', 'labor', 'crypto', 'other'],
          'h72': ['commodity-prices', 'energy-supply', 'geopolitics', 'trade'], 'session_gap_h': 2}
H = 3600
P = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def daily(sym):
    """Daily closes (epoch, close) for the last 6 months; None on failure."""
    if len(sym) == 6 and sym.isalpha() and sym.isupper(): sym += '=X'
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=6mo&interval=1d'
    for _ in range(2):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=T.UA), timeout=20))['chart']['result'][0]
            return [(t, c) for t, c in zip(r['timestamp'], r['indicators']['quote'][0]['close']) if c]
        except Exception: pass
    return None


def sigma(dc, t):
    px = [c for ts, c in dc if ts < t][-(FROZEN['vol_days'] + 1):]
    if len(px) < 10: return None
    return st.pstdev([math.log(b / a) for a, b in zip(px, px[1:])]) * 100


def session_close(bars, t, crypto):
    """Exit price: crypto = first bar at or after t; others = last bar of the session (a run of bars without a gap of
    session_gap_h hours) that contains or follows t."""
    i = next((k for k, b in enumerate(bars) if b[0] >= t), None)
    if i is None: return None
    if crypto: return bars[i]
    j = i
    while j + 1 < len(bars) and bars[j + 1][0] - bars[j][0] < FROZEN['session_gap_h'] * H: j += 1
    return bars[j] if j + 1 < len(bars) else None  # the session must have ended (a later bar exists)


def wilson(h, n, z=1.96):
    if not n: return None
    p = h / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - w), 1), round(100 * (c + w), 1)]


def binom_p(h, n):
    if not n: return None
    pr = lambda k: math.comb(n, k) / 2 ** n
    obs = pr(h); return round(min(1.0, sum(pr(k) for k in range(n + 1) if pr(k) <= obs + 1e-15)), 5)


def main():
    R = registry.get(); now = datetime.now(timezone.utc).timestamp()
    fam = {r['id']: r.get('fam') for r in EV.load_days(30)}
    items = [x for x in json.load(open(os.path.join(ROOT, 'research', 'pre-live-implications.json')))['items'] if x.get('kind') in ('company', 'asset')]
    for x in items:
        a = R.assets.get(x.get('asset_id')) or {}; x['px'] = a.get('px') or x['sym']; x['cls'] = a.get('class') or '?'
        x['fam'] = fam.get(x['story']) or 'other'; x['T'] = P(x['first_seen'][:19] + 'Z')
    seen, calls = set(), []
    for x in sorted(items, key=lambda x: x['T']):  # one entry per article and asset (as in the published v1 file)
        if (x['story'], x['px']) in seen: continue
        seen.add((x['story'], x['px'])); calls.append(x)
    syms = sorted({c['px'] for c in calls}); t0 = min(c['T'] for c in calls) - 2 * 86400
    with cf.ThreadPoolExecutor(8) as ex:
        bars = dict(zip(syms, ex.map(lambda s: T.bars(s, t0, now), syms)))
        dly = dict(zip(syms, ex.map(daily, syms)))
    out = []
    for c in calls:
        b = bars.get(c['px']); hh = 72 if c['fam'] in FROZEN['h72'] else 24; crypto = c['px'].endswith('-USD')
        r = {'id': c['story'], 'h': (c.get('h') or '')[:140], 'name': (c.get('name') or c['px'])[:60], 'sym': c['px'], 'dir': c['dir'], 'cls': c['cls'], 'fam': c['fam'],
             'start': c['first_seen'][:19] + 'Z', 'horizon_h': hh}
        if not b:
            r.update(res='unresolved', why='no price data'); out.append(r); continue
        e = next((p for p in b if c['T'] <= p[0] <= c['T'] + FROZEN['max_wait_h'] * H), None)
        if not e:
            r.update(res='pending' if now < c['T'] + FROZEN['max_wait_h'] * H else 'unresolved', why='no traded price after the call'); out.append(r); continue
        x = session_close(b, e[0] + hh * H, crypto)
        if not x or x[0] > e[0] + (hh + FROZEN['max_wait_h']) * H:
            r.update(res='pending' if now < e[0] + (hh + FROZEN['max_wait_h']) * H else 'unresolved', entry=[int(e[0] // 60), round(e[1], 6)], why='exit not reached'); out.append(r); continue
        mv = (x[1] / e[1] - 1) * 100; s = sigma(dly.get(c['px']) or [], c['T']); thr = max(FROZEN['min_move_pct'], FROZEN['k_sigma'] * s * math.sqrt(hh / 24)) if s else None
        if thr is None:
            r.update(res='unresolved', why='no volatility history'); out.append(r); continue
        res = 'void' if abs(mv) > 50 else 'flat' if abs(mv) < thr else 'hit' if (mv > 0) == (c['dir'] == 'up') else 'miss'
        r.update(res=res, move=round(mv, 2), thr=round(thr, 2), sigma=round(s, 2), entry=[int(e[0] // 60), round(e[1], 6)], exit=[int(x[0] // 60), round(x[1], 6)])
        out.append(r)
    kept = {}  # one outcome per correlated cluster: same asset + same direction, overlapping windows
    for r in sorted(out, key=lambda r: (r.get('entry') or [P(r['start']) // 60])[0]):
        if 'entry' not in r: continue
        k = (r['sym'], r['dir']); s0 = r['entry'][0]; s1 = (r.get('exit') or [s0 + r['horizon_h'] * 60])[0]
        if k in kept and s0 < kept[k][1]: r['collapsed_into'] = kept[k][0]
        else: kept[k] = (r['id'], s1)
    json.dump({'framework': FROZEN, 'built': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'calls': out},
              open(os.path.join(ROOT, 'research', 'early-outcomes-v2.json'), 'w'), separators=(',', ':'))
    print('scored', len(out))


if __name__ == '__main__':
    main()
