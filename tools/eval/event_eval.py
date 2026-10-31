"""Event-id evaluation and backfill proposal (measurement only; nothing is published).
Replays every archived article since START in time order, in batches like the robot's runs, through event_ids.assign with the live
Gemini call. Articles before START (72 h) seed the pool as their own events. Saves after every batch to tools/eval/event_results.json.
Needs GEMINI_API_KEY.  python3 tools/eval/event_eval.py"""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import events as EV, event_ids as E
import update_globe_news as robot

START, BATCH = os.environ.get('EVAL_START', '2026-10-29T18:00:00Z'), 15
OUT = os.path.join(ROOT, 'tools', 'eval', 'event_results.json')
recs = sorted({r['id']: r for r in EV.load_days(30)}.values(), key=lambda r: (r['at'], r['id']))
summ = {}
try: summ = {s['id']: s.get('summary') for s in json.load(open(os.path.join(ROOT, 'assets', 'globe', 'news-archive.json')))['stories']}
except Exception: pass
pool = [dict(r, cluster=r['id']) for r in recs if r['at'] < START]
todo = [r for r in recs if r['at'] >= START]
story = lambda r: {'id': r['id'], 'published_at': r['at'], 'headline': r.get('title'), 'summary': summ.get(r['id']) or '', 'event_type': r.get('fam'),
                   'impacts': [{'asset': {'id': a['id']}} for a in r.get('assets', []) if a.get('id')], 'entities': []}
res = {'start': START, 'articles': len(todo), 'asked': 0, 'joined': 0, 'errors': 0, 'batches': 0, 'assign': {}}
for i in range(0, len(todo), BATCH):
    batch = [story(r) for r in todo[i:i + BATCH]]
    out = E.assign(batch, pool, robot.gemini)
    res['asked'] += out['asked']; res['joined'] += out['joined']; res['errors'] += 1 if out.get('error') else 0; res['batches'] += 1
    for s in batch:
        res['assign'][s['id']] = {'cluster': s['cluster'], 'why': s.get('cluster_why'), 'at': s['published_at'], 'title': s['headline'], 'fam': s['event_type']}
        pool.append({'id': s['id'], 'at': s['published_at'], 'title': s['headline'], 'fam': s['event_type'], 'cluster': s['cluster'],
                     'assets': [{'id': x['asset']['id']} for x in s['impacts']]})
    json.dump(res, open(OUT, 'w'), indent=0, ensure_ascii=False)
    print(f"batch {res['batches']}: {i + len(batch)}/{len(todo)} asked {res['asked']} joined {res['joined']}", flush=True)
    if out['asked']: time.sleep(4)
