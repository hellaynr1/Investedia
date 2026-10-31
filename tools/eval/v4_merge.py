"""Merge the parallel v4 re-run parts (research/v4-replay-<n>.json) into research/v4-replay.json. One Market View per event x asset x
horizon across parts (the earliest wins; later duplicates become No View 'duplicate-view'), the same rule the single run applies."""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parts = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(ROOT, 'research', 'v4-replay-*.json')))]
out = {k: parts[0].get(k) for k in ('note', 'from', 'policy_id', 'prompt_id')} if parts else {}
recs = sorted((r for p in parts for r in p['records']), key=lambda r: r.get('start_ts') or 0)
seen = set()
for r in recs:
    if r.get('view_tier') in ('standard', 'priority'):
        key = (r.get('event_id'), r.get('asset_id'), r.get('horizon'))
        if key in seen: r.update(view_tier='none', decision='none', tier_reasons=['duplicate-view'], outcome=None)
        seen.add(key)
out.update(parts=len(parts), stories=sum(p['stories'] for p in parts), done=[i for p in parts for i in p['done']], errors=sum(p.get('errors', 0) for p in parts), records=recs)
json.dump(out, open(os.path.join(ROOT, 'research', 'v4-replay.json'), 'w'), separators=(',', ':'))
print(len(parts), 'parts;', len(out['done']), '/', out['stories'], 'stories;', len(recs), 'records')
