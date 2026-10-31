"""Scores the pre-live research implications (research/pre-live-implications.json) with the live outcome-v2 rule, for the separate
Historical/research record. Never writes the live ledger. start = first public commit time (git proof); baseline = prevailing traded
price at start; end = first traded price >= 24 h later within 4 calendar days, else unresolved. Prices: the canonical registry asset's
own exchange bars. Writes research/pre-live-outcomes.json.  python3 tools/track/score_research.py"""
import json, os, sys, concurrent.futures as cf
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import registry, update_news_track as T
P = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
R = registry.get(); now = datetime.now(timezone.utc).timestamp()
items = [x for x in json.load(open(os.path.join(ROOT, 'research', 'pre-live-implications.json')))['items'] if x.get('kind') in ('company', 'asset')]
px = lambda x: ((R.assets.get(x['asset_id']) or {}).get('px')) or x['sym']
syms = sorted({px(x) for x in items}); t0 = min(P(x['first_seen']) for x in items) - 5 * 86400
with cf.ThreadPoolExecutor(8) as ex: bars = dict(zip(syms, ex.map(lambda s: T.bars(s, t0, now), syms)))
out = []
for x in items:
    s = px(x); L = {'calls': [{'id': x['story'], 'sym': s, 'dir': x['dir'], 'start': x['first_seen'][:19] + 'Z', 'created': x['first_seen'][:19] + 'Z', 'res': 'pending'}]}
    T.judge({}, L, datetime.now(timezone.utc), None, fetch=lambda sym, a, b, s=s: [p for p in (bars.get(s) or []) if a <= p[0] <= b] if bars.get(s) is not None else None)
    c = L['calls'][0]
    out.append({**{k: x[k] for k in ('story', 'h', 'name', 'kind', 'dir', 'asset_id', 'commit')}, 'sym': s, 'start': c['start'],
                **{k: c[k] for k in ('res', 'move', 'base', 'end', 'why') if k in c}})
json.dump({'note': 'Pre-live research calls scored with outcome-v2. Historical/research only: never part of the Live Track Record.',
           'built': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'items': out}, open(os.path.join(ROOT, 'research', 'pre-live-outcomes.json'), 'w'), separators=(',', ':'))
from collections import Counter
print(len(out), Counter(o['res'] for o in out), 'no data symbols', sum(1 for s in syms if not bars.get(s)))
