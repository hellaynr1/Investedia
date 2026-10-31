"""Publishes the Early Track Record (21-30 Oct 2026) for the Track Record page: assets/globe/early-calls.json (+ docs mirror).
Official score: frozen framework early-v2 (research/EARLY-SCORING-V2.md, research/early-outcomes-v2.json) with the market-index
benchmark (research/early-bench-v2.json). The original v1 score is included only as an old-methodology comparison (totals).
Historical only: never read by Market Implications or the live statistics.  python3 tools/track/publish_early_calls.py"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import events as EV
R = lambda *p: os.path.join(ROOT, *p)
v2 = json.load(open(R('research', 'early-outcomes-v2.json'))); bench = json.load(open(R('research', 'early-bench-v2.json')))
url = {r['id']: r.get('url') for r in EV.load_days(30)}
# v1 comparison: the original scoring, one entry per article and asset (as first published)
v1, seen = [], set()
for x in sorted(json.load(open(R('research', 'pre-live-outcomes.json')))['items'], key=lambda x: x['start']):
    if (x['story'], x['sym']) not in seen: seen.add((x['story'], x['sym'])); v1.append(x['res'])
n1 = collections.Counter(v1)
calls = []
for c in v2['calls']:
    k = c['id'] + '|' + c['sym']
    calls.append({x: y for x, y in {**{f: c.get(f) for f in ('id', 'h', 'name', 'sym', 'dir', 'cls', 'fam', 'start', 'horizon_h', 'res', 'move', 'thr', 'entry', 'exit', 'collapsed_into', 'why')},
                  'url': url.get(c['id']), 'mkt': bench.get(k)}.items() if y is not None})
doc = {'note': 'Early calls (21-30 Oct 2026): first engine, before the frozen live ledger and event grouping. Official score: frozen framework early-v2.',
       'range': ['2026-10-21', '2026-10-30'], 'method': {**v2['framework'], 'doc': 'research/EARLY-SCORING-V2.md', 'built': v2['built']},
       'v1': {'hit': n1['hit'], 'miss': n1['miss'], 'flat': n1['flat'], 'note': 'original scoring: credited some overnight gaps and counted duplicate calls separately'},
       'calls': calls}
for d in ('assets/globe', 'docs/assets/globe'): json.dump(doc, open(R(d, 'early-calls.json'), 'w'), separators=(',', ':'))
print(len(calls), collections.Counter(c['res'] for c in calls if 'collapsed_into' not in c), 'collapsed', sum('collapsed_into' in c for c in calls), 'v1', dict(n1))
