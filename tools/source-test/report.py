"""Summary of the 48-hour source test and a keep/reject recommendation per source (measurement only)."""
import json, os, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data')
sys.path.insert(0, HERE)
import run as T

def load(n):
    p = os.path.join(D, n)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

runs, items = load('runs.jsonl'), load('items.jsonl')
by_r, by_i = defaultdict(list), defaultdict(list)
for r in runs: by_r[r['source']].append(r)
for i in items: by_i[i['source']].append(i)
hours = max(1, len({r['at'][:13] for r in runs}))
print(f"window {T.START} -> {T.END}; passes {len({r['at'] for r in runs})} over ~{hours} h; items {len(items)}")
rows = []
for src in T.SOURCES:
    rr, ii = by_r[src['id']], by_i[src['id']]
    ok = [r for r in rr if r['ok']]
    days = max(1 / 24, hours / 24)
    useful = [i for i in ii if i['useful']]; novel = [i for i in ii if i['novel']]
    lat = sorted(i['latency_min'] for i in ii if i.get('latency_min') is not None)
    row = {'source': src['name'], 'passes': len(rr), 'failure_rate': round(1 - len(ok) / max(1, len(rr)), 3),
           'fetch_ms_median': sorted(r['ms'] for r in ok)[len(ok) // 2] if ok else None,
           'new_items': len(ii), 'useful': len(useful), 'useful_per_day': round(len(useful) / days, 1),
           'duplicates_of_existing': sum(bool(i['duplicate_of']) for i in ii), 'covered_already': sum(bool(i['covered_by']) for i in ii),
           'novel_useful': len(novel), 'novel_per_day': round(len(novel) / days, 1), 'macro_headlines': sum(i.get('macro_headline', False) for i in ii),
           'with_verified_asset': sum(bool(i['assets']) for i in ii), 'would_draw_line_pct': round(100 * sum(bool(i['drawable']) for i in useful) / max(1, len(useful)), 1),
           'families': dict(Counter(i['family'] for i in useful).most_common(6)), 'countries': dict(Counter(i['country'] for i in useful)),
           'assets': dict(Counter(a for i in ii for a in i['assets']).most_common(6)),
           'latency_min_median': lat[len(lat) // 2] if lat else None, 'english_share': round(sum(i.get('english', True) for i in ii) / max(1, len(ii)), 2)}
    # recommendation: keep when it reliably adds useful, novel market-relevant stories at low failure; otherwise reject
    keep = row['failure_rate'] <= .1 and row['novel_per_day'] >= 2 and (row['macro_headlines'] >= 1 or row['useful_per_day'] >= 4)
    row['recommendation'] = 'KEEP' if keep else 'REJECT'
    rows.append(row)
print(json.dumps(rows, indent=1, ensure_ascii=False))
json.dump(rows, open(os.path.join(D, 'summary.json'), 'w'), indent=1, ensure_ascii=False)
