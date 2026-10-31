"""Benchmark for the early v2 scores (does not change any verdict): the asset's market index over each call's own entry -> exit window,
using the same index map as the live robot (update_news_track.bench_of). Writes research/early-bench-v2.json {id|sym: {sym, move}}.
python3 tools/track/bench_early_v2.py"""
import json, os, sys, concurrent.futures as cf
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import update_news_track as T
V = json.load(open(os.path.join(ROOT, 'research', 'early-outcomes-v2.json')))['calls']
J = [c for c in V if c.get('entry') and c.get('exit')]
ix = sorted({T.bench_of(c['sym']) for c in J} - {None}); now = datetime.now(timezone.utc).timestamp()
t0 = min(c['entry'][0] for c in J) * 60 - 4 * 86400
with cf.ThreadPoolExecutor(8) as ex: bars = dict(zip(ix, ex.map(lambda s: T.bars(s, t0, now), ix)))
out = {}
for c in J:
    b = bars.get(T.bench_of(c['sym']) or '') or []
    b0 = [p for p in b if p[0] <= c['entry'][0] * 60]; b1 = [p for p in b if p[0] <= c['exit'][0] * 60]
    if b0 and b1 and b1[-1][0] > b0[-1][0]: out[c['id'] + '|' + c['sym']] = {'sym': T.bench_of(c['sym']), 'move': round((b1[-1][1] / b0[-1][1] - 1) * 100, 2)}
json.dump(out, open(os.path.join(ROOT, 'research', 'early-bench-v2.json'), 'w'), separators=(',', ':'))
print('benchmarked', len(out), 'of', len(J), 'indices', ix)
