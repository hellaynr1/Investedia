"""Before/after: how many published stories can draw verified financial connections.
  python3 tools/registry/measure.py stories.json [--json out.json]
BEFORE = the live Globe's rule (raw ticker looked up in markets.json: exact, +'-USD', or without '=X'; no identity check).
AFTER  = canonical registry (registry.resolve on name + ticker, impacts and named entities; drawable = verified + has a place).
Both use the same stories, so the difference is the entity/asset infrastructure alone (no new sources, no new prompt)."""
import json, os, sys, copy, argparse
from collections import Counter, defaultdict
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import registry as R, events as E

ISO = json.load(open(os.path.join(ROOT, 'assets/globe/iso.json'), encoding='utf-8'))
MK = {a['s']: a for a in json.load(open(os.path.join(ROOT, 'assets/globe/markets.json'), encoding='utf-8'))['assets']}

def before_assets(s):
    """page.html assetsNamed(): [(asset symbol, impact or None)]"""
    out = {}
    def find(t):
        t = t.upper(); return MK.get(t) or MK.get(t + '-USD') or MK.get(t.replace('=X', ''))
    for i in s.get('impacts') or []:
        if not (isinstance(i, dict) and i.get('kind') in ('country', 'company', 'asset', 'sector') and isinstance(i.get('name'), str) and isinstance(i.get('why'), str)
                and i.get('country') in ISO.values() and i.get('direction') in ('up', 'down', 'mixed', 'unclear') and i.get('ticker')): continue
        a = find(i['ticker'])
        if a: out[a['s']] = i
    for e in s.get('entities') or []:
        t = e.get('ticker') or e.get('sym')
        a = find(t) if t else None
        if a and a['s'] not in out: out[a['s']] = None
    return list(out.items())

def after_assets(s, reg):
    out = {}
    for i in s.get('impacts') or []:
        if not isinstance(i, dict): continue
        r = copy.deepcopy(i); R.stamp(r, reg)
        a = r.get('asset')
        if a and a.get('la') is not None and a['id'] not in out: out[a['id']] = (r, a)
    for e in s.get('entities') or []:
        r = {'name': e.get('name'), 'ticker': e.get('ticker'), 'kind': 'company'}; R.stamp(r, reg)
        a = r.get('asset')
        if a and a.get('la') is not None and a['id'] not in out: out[a['id']] = (None, a)
    return out

def stats(stories, reg):
    B, A = Counter(), Counter()
    tick, b_syms, a_ids = set(), set(), set()
    b_cty, a_cty, b_cls, a_cls = set(), set(), Counter(), Counter()
    b_ev, a_ev = [], []
    unres = Counter(); unres_arts = defaultdict(set); wrong = []
    reasons = Counter()
    for s in stories:
        for i in (s.get('impacts') or []) + (s.get('entities') or []):
            if i.get('ticker'): tick.add(R.norm_ticker(i['ticker']))
        b = before_assets(s); a = after_assets(s, reg)
        loc = (s.get('location') or {}).get('country')
        for k, (lst, C, syms, cty, cls) in {'b': (b, B, b_syms, b_cty, b_cls), 'a': (list(a.items()), A, a_ids, a_cty, a_cls)}.items():
            C['articles'] += 1
            if lst: C['drawable'] += 1; cty.add(loc)
            if len(lst) >= 2: C['2plus'] += 1
            C['edges'] += len(lst)
            dirs = [x for x in lst[1:] if (x[1][0] if k == 'a' else x[1]) and ((x[1][0] if k == 'a' else x[1]) or {}).get('direction') in ('up', 'down')]
            if len(lst) >= 2 and dirs: C['ripple'] += 1
            for sym, v in lst:
                syms.add(sym)
                cls[(v[1]['c'] if k == 'a' else {'stocks': 'equity/index', 'fx': 'fx', 'cmd': 'commodity', 'crypto': 'crypto'}.get(MK[sym]['t']))] += 1
        rec_b = {'id': s['id'], 'at': s['published_at'], 'fam': E.family(s.get('headline'), s.get('category')), 'cluster': s['id'], 'assets': [{'id': x} for x, _ in b]}
        rec_a = {**rec_b, 'assets': [{'id': x} for x in a]}
        b_ev.append(rec_b); a_ev.append(rec_a)
        # what the registry did with each ticker the Globe matched before
        for sym, i in b:
            if i is None: continue
            r = R.Registry.resolve(reg, i.get('name'), i.get('ticker'), i.get('kind'))
            if not r['id']: wrong.append((i.get('ticker'), i.get('name'), r['reason'], MK[sym]['n']))
        for i in (s.get('impacts') or []) + [dict(e, kind='company') for e in s.get('entities') or []]:
            r = copy.deepcopy(i); R.stamp(r, reg)
            if r.get('unresolved'):
                reasons[r['unresolved'].split(':')[0]] += 1
                if i.get('ticker'): unres_arts[R.norm_ticker(i['ticker'])].add(s['id'])
            elif not r['asset'].get('la') is not None:
                reasons['verified-no-place'] += 1
    tb, ta = E.threads(b_ev), E.threads(a_ev)
    loose_b = len(E.threads([{**e, 'fam': 'x'} for e in b_ev])); loose_a = len(E.threads([{**e, 'fam': 'x'} for e in a_ev]))
    return {'stories': len(stories), 'tickers_discovered': len(tick),
            'before': {**B, 'assets': len(b_syms), 'countries': len(b_cty - {None}), 'classes': dict(b_cls), 'story_threads': len(tb), 'threads_any_family': loose_b},
            'after': {**A, 'assets': len(a_ids), 'countries': len(a_cty - {None}), 'classes': dict(a_cls), 'story_threads': len(ta), 'threads_any_family': loose_a},
            'before_matches_rejected': wrong, 'unresolved_reasons': dict(reasons.most_common()),
            'missing_ranked': sorted(((t, len(v)) for t, v in unres_arts.items()), key=lambda x: -x[1])}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('stories'); ap.add_argument('--json'); a = ap.parse_args()
    st = json.load(open(a.stories)); st = st if isinstance(st, list) else st['stories']
    res = stats(st, R.Registry())
    for k in ('before', 'after'):
        x = res[k]; print(k.upper(), {kk: x.get(kk) for kk in ('articles', 'drawable', '2plus', 'ripple', 'edges', 'assets', 'countries', 'story_threads', 'threads_any_family')},
                                 f"{100 * x.get('drawable', 0) / max(1, x['articles']):.1f}% drawable", x['classes'])
    print('tickers discovered', res['tickers_discovered']); print('before-matches the registry rejects:', len(res['before_matches_rejected']))
    for w in res['before_matches_rejected'][:25]: print('  ', w)
    print('unresolved reasons', res['unresolved_reasons']); print('missing ranked', res['missing_ranked'][:40])
    if a.json: json.dump(res, open(a.json, 'w'), indent=1, ensure_ascii=False)
