"""DEVELOPMENT REPLAY of Prediction Engine v4 on current archived stories (research/ENGINE-V4.md §11). Not evidence: replay results are
for development only; real evidence starts with forward shadow predictions. Uses the frozen policy, the v4 extraction prompt (Gemini),
the economic calendar for expectations and exchange prices up to each story's publication time for context.
Writes research/v4-replay.json after every batch (resumable). Needs GEMINI_API_KEY.  python3 tools/eval/v4_replay.py"""
import json, os, sys, time
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import registry, events as EV, update_globe_news as robot
from engine import extract as X, run as RUN, context as C, prices as PX

OUT = os.path.join(ROOT, 'research', 'v4-replay.json'); BATCH = int(os.environ.get('V4_BATCH', 10)); N = int(os.environ.get('V4_N', 600))
P = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
R = registry.get(); IND = json.load(open(os.path.join(ROOT, 'docs', 'assets', 'globe', 'industries.json'))).get('by', {})
cal = json.load(open(os.path.join(ROOT, 'docs', 'assets', 'calendar-live.json')))
cluster = {r['id']: r.get('cluster') or r['id'] for r in EV.load_days(30)}
stories = sorted(json.load(open(os.path.join(ROOT, 'docs', 'assets', 'globe', 'news-archive.json')))['stories'], key=lambda s: s['published_at'])[-N:]
res = {'note': 'DEVELOPMENT REPLAY: not performance evidence', 'stories': len(stories), 'done': [], 'records': [], 'errors': 0}
try:
    old = json.load(open(OUT))
    if old.get('stories') == len(stories): res = old
except Exception: pass


def resolve(a):
    ids = R.ids_for_ticker(a['ticker']) if a.get('ticker') else []
    aid = ids[0] if ids else (R.resolve(name=a['name'], ticker=a.get('ticker'), kind='company') or {}).get('id')
    return dict(R.assets[aid], id=aid) if aid and aid in R.assets else None


BARS, DAILY = {}, {}
def series(sym, t):
    if sym not in BARS: BARS[sym] = PX.bars(sym, t - 6 * 86400, datetime.now(timezone.utc).timestamp()) or []
    if sym not in DAILY: DAILY[sym] = PX.daily(sym) or []
    return [b for b in BARS[sym] if b[0] <= t], [d for d in DAILY[sym] if d[0] < t]  # nothing after publication is read


def context_of(reg, t):
    px = reg.get('px'); b, d = series(px, t)
    ix = PX.bench_of(px) if reg.get('class') in ('equity', 'crypto') else None
    sec = C.sector_etf((IND.get(px) or {}).get('sic')) if ix == '^GSPC' else None
    ib, idd = series(ix, t) if ix else (None, None); sb, sd = series(sec, t) if sec else (None, None)
    f = C.features(t, b, d, ib, idd, sb, sd); f['benchmark'] = {'index': ix, 'sector': sec}
    return f


seen = set()  # one View per event x asset x horizon across the whole replay
for i in range(0, len(stories), BATCH):
    batch = [s for s in stories[i:i + BATCH] if s['id'] not in res['done']]
    if not batch: continue
    try: ex = X.validate(robot.gemini(X.build_prompt(batch, cal)), len(batch))
    except Exception as e: res['errors'] += 1; print('batch error', e, flush=True); time.sleep(10); continue
    for k, s in enumerate(batch, 1):
        res['done'].append(s['id'])
        if k not in ex: continue
        _, src = X.calendar_expectations(s, cal)
        res['records'] += RUN.records(s, ex[k], resolve, context_of, cluster.get(s['id'], s['id']), s['published_at'], P(s['published_at']), seen,
                                      model=robot.status.get('gemini_model'), calendar_sources=src)
    json.dump(res, open(OUT, 'w'), separators=(',', ':'))
    print(f"{len(res['done'])}/{len(stories)} stories, {len(res['records'])} records", flush=True)
