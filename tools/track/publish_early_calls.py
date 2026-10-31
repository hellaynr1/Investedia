"""Publishes the scored early calls (21-30 Oct 2026, before the frozen live ledger) for the Track Record's separate Early Track Record
section: assets/globe/early-calls.json (+ docs mirror). Historical only: never read by Market Implications or the live statistics.
Source: research/pre-live-outcomes.json (tools/track/score_research.py). One entry per article and asset.
python3 tools/track/publish_early_calls.py"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import events as EV
src = json.load(open(os.path.join(ROOT, 'research', 'pre-live-outcomes.json')))
url = {r['id']: r.get('url') for r in EV.load_days(30)}
seen, out = set(), []
for x in sorted(src['items'], key=lambda x: x['start']):
    k = (x['story'], x['sym'])
    if k in seen: continue
    seen.add(k)
    out.append({k2: v for k2, v in {'id': x['story'], 'h': (x.get('h') or '')[:140], 'name': (x.get('name') or x['sym'])[:60], 'sym': x['sym'], 'dir': x['dir'],
                'start': x['start'], 'res': x['res'], 'move': x.get('move'), 'base': x.get('base'), 'end': x.get('end'), 'url': url.get(x['story'])}.items() if v is not None})
doc = {'note': 'Early calls (21-30 Oct 2026): made by the first engine before the frozen live ledger and before event grouping. Scored with the '
               'current outcome rule from their first provable public time. Historical only; never mixed with live statistics.',
       'range': ['2026-10-21', '2026-10-30'], 'built': src['built'], 'calls': out}
for d in ('assets/globe', 'docs/assets/globe'):
    p = os.path.join(ROOT, d, 'early-calls.json'); json.dump(doc, open(p, 'w'), separators=(',', ':'))
from collections import Counter
print(len(out), Counter(c['res'] for c in out), 'with url', sum('url' in c for c in out), os.path.getsize(p) // 1024, 'KB')
