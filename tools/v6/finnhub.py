"""v6 Track C: Finnhub structured features (free plan), cached and resumable.
- Earnings calendar month by month 2022-01 -> 2026-10: date, hour (bmo/amc/dmh), EPS actual/estimate, revenue actual/estimate.
- Analyst upgrades/downgrades (if the free plan allows it): date, firm, from/to grade, action.
First run prints a coverage probe so we know what the free plan really returns. Output research/v6/finnhub/.
  python3 tools/v6/finnhub.py   (needs FINNHUB_KEY)"""
import json, os, sys, time, urllib.request
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'research', 'v6', 'finnhub')
KEY = os.environ.get('FINNHUB_KEY', '').strip()
_t = []


def get(path):
    global _t
    _t = [x for x in _t if time.time() - x < 60]
    if len(_t) >= 50: time.sleep(61 - (time.time() - _t[0]))
    _t.append(time.time())
    url = f'https://finnhub.io/api/v1/{path}{"&" if "?" in path else "?"}token={KEY}'
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=30) as r: return json.load(r)
        except Exception as e:
            if '403' in str(e): return {'_error': 'not in free plan'}
            if '429' in str(e): time.sleep(30); continue
            time.sleep(5)
    return {'_error': 'failed'}


def months():
    y, m = 2022, 1
    while (y, m) <= (2026, 10):
        a = date(y, m, 1); b = date(y + (m == 12), m % 12 + 1, 1)
        yield a.isoformat(), (date.fromordinal(b.toordinal() - 1)).isoformat()
        y, m = y + (m == 12), m % 12 + 1


def main():
    if not KEY: print('FINNHUB_KEY missing'); sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    probe = {}
    for a, b in [('2022-02-01', '2022-02-28'), ('2024-02-01', '2024-02-29'), ('2026-08-01', '2026-08-31')]:
        j = get(f'calendar/earnings?from={a}&to={b}')
        ec = j.get('earningsCalendar') or []
        probe[a[:7]] = {'rows': len(ec), 'with_actual': sum(1 for x in ec if x.get('epsActual') is not None), 'with_rev': sum(1 for x in ec if x.get('revenueActual') is not None), 'error': j.get('_error')}
    ud = get('stock/upgrade-downgrade?symbol=AAPL&from=2022-01-01&to=2026-10-20')
    probe['upgrade_downgrade_AAPL'] = ud.get('_error') or (len(ud) if isinstance(ud, list) else str(ud)[:80])
    rec = get('stock/recommendation?symbol=AAPL')
    probe['recommendation_trends_AAPL'] = rec.get('_error') if isinstance(rec, dict) else len(rec)
    print('PROBE', json.dumps(probe), flush=True)
    json.dump(probe, open(os.path.join(OUT, 'probe.json'), 'w'), indent=1)
    # earnings calendar, one file per month, never re-downloaded once saved
    for a, b in months():
        p = os.path.join(OUT, f'earnings-{a[:7]}.json')
        if os.path.exists(p): continue
        j = get(f'calendar/earnings?from={a}&to={b}')
        if j.get('_error'): print(a[:7], j['_error'], flush=True); continue
        json.dump(j.get('earningsCalendar') or [], open(p, 'w'), separators=(',', ':'))
    n = sum(len(json.load(open(os.path.join(OUT, f)))) for f in os.listdir(OUT) if f.startswith('earnings-'))
    print('earnings rows cached:', n, flush=True)


if __name__ == '__main__':
    main()
