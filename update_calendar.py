"""Upcoming economic events + company earnings for the homepage -> assets/calendar-live.json
Sources (free, no key): ForexFactory weekly calendar feed (faireconomy.media) and the Nasdaq earnings calendar.
Runs with the globe-news workflow. If a source fails, the previous data stays.
Note: both are public feeds without a formal licence; check their terms before using them in a paid product."""
import json, os, time, urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = [os.path.join(ROOT, 'assets/calendar-live.json'), os.path.join(ROOT, 'docs/assets/calendar-live.json')]
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.9'}
NOW = datetime.now(timezone.utc)


def get(url):
    for t in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))
        except Exception as e:
            err = e; time.sleep(5 * (t + 1))
    raise err


prev = {}
if os.path.exists(OUT[0]):
    try: prev = json.load(open(OUT[0]))
    except Exception: pass
out = {'updated_at': NOW.strftime('%Y-%m-%dT%H:%M:%SZ'), 'events': prev.get('events', []), 'earnings': prev.get('earnings', []),
       'sources': {'events': 'ForexFactory calendar', 'earnings': 'Nasdaq earnings calendar'}}

# economic events: this week + next week, medium/high impact, still to come
try:
    ev = []
    for f in ('ff_calendar_thisweek.json', 'ff_calendar_nextweek.json'):
        try: ev += get('https://nfs.faireconomy.media/' + f)
        except Exception: pass
    keep = []
    for e in ev:
        try: d = datetime.fromisoformat(e['date'])
        except Exception: continue
        if d.astimezone(timezone.utc) < NOW - timedelta(hours=1) or e.get('impact') not in ('High', 'Medium'): continue
        keep.append({'t': e['title'], 'c': e['country'], 'at': d.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                     'imp': 3 if e['impact'] == 'High' else 2, 'fc': e.get('forecast') or '', 'prev': e.get('previous') or ''})
    keep.sort(key=lambda e: e['at'])
    if keep: out['events'] = keep[:40]
except Exception as e: print('events failed:', e)

# earnings: next 10 days, the largest companies each day
try:
    ern = []
    for i in range(0, 10):
        day = (NOW + timedelta(days=i)).date()
        if day.weekday() > 4: continue
        rows = (get(f'https://api.nasdaq.com/api/calendar/earnings?date={day.isoformat()}').get('data') or {}).get('rows') or []
        def cap(r):
            try: return float(r['marketCap'].replace('$', '').replace(',', ''))
            except Exception: return 0
        for r in sorted(rows, key=cap, reverse=True)[:6]:
            if cap(r) < 20e9: continue
            ern.append({'s': r['symbol'], 'n': r['name'].replace(' (The)', '').replace(', Inc.', '').replace(' Inc.', '').replace(' Corporation', '').replace(' Company', '').replace(' Inc', '').replace(' SE', '').replace(' plc', '').strip(),
                        'date': day.isoformat(), 'when': {'time-pre-market': 'Before open', 'time-after-hours': 'After close'}.get(r.get('time'), ''),
                        'eps': r.get('epsForecast') or '', 'cap': cap(r)})
        time.sleep(1)
    if ern: out['earnings'] = ern[:30]
except Exception as e: print('earnings failed:', e)

for p in OUT:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(json.dumps(out, separators=(',', ':')))
print('calendar:', len(out['events']), 'events,', len(out['earnings']), 'earnings')
