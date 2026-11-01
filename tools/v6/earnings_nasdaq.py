"""v6 Track C: historical earnings surprises from Nasdaq's public earnings calendar, one call per trading day 2022-01 -> 2026-10-20:
symbol, EPS actual, EPS forecast (consensus before the release), surprise %, number of estimates, time (pre-market/after-hours/not
supplied), fiscal quarter. marketCap in the response is TODAY's value: dropped (look-ahead). Cached per month, resumable.
Output research/v6/earnings/YYYY-MM.json  ->  {"YYYY-MM-DD": [rows...]}"""
import json, os, time, urllib.request
from datetime import date, timedelta
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'research', 'v6', 'earnings')
KEEP = ('symbol', 'name', 'eps', 'epsForecast', 'surprise', 'noOfEsts', 'time', 'fiscalQuarterEnding', 'lastYearEPS', 'lastYearRptDt')


def get(d):
    for k in range(5):
        try:
            req = urllib.request.Request(f'https://api.nasdaq.com/api/calendar/earnings?date={d}', headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as r: j = json.load(r)
            return [{k2: x.get(k2) for k2 in KEEP} for x in ((j.get('data') or {}).get('rows') or [])]
        except Exception: time.sleep(5 * (k + 1))
    return None


def main(a='2022-01-01', b='2026-10-20'):
    os.makedirs(OUT, exist_ok=True); d, end, n = date.fromisoformat(a), date.fromisoformat(b), 0
    while d <= end:
        p = os.path.join(OUT, f'{d.isoformat()[:7]}.json'); cur = json.load(open(p)) if os.path.exists(p) else {}
        if d.weekday() < 5 and d.isoformat() not in cur:
            rows = get(d.isoformat()); time.sleep(0.4)
            if rows is not None: cur[d.isoformat()] = rows; n += len(rows); json.dump(cur, open(p, 'w'), separators=(',', ':'))
        d += timedelta(days=1)
    tot = sum(len(v) for f in os.listdir(OUT) for v in json.load(open(os.path.join(OUT, f))).values())
    print('new rows', n, '| total rows', tot, flush=True)


if __name__ == '__main__':
    main()
