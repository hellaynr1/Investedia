"""v6 Track A: point-in-time 8-K event index from SEC full-text search (efts). Every 8-K filed by any company, with the items, industry
codes and the ticker(s) the company had AT FILING TIME (from the display name), so delisted, acquired and renamed companies are included
(no survivorship bias). One request per 100 documents; resumable per day; output research/v6/index/8k-YYYY-MM.jsonl.gz (one row per filing).
  python3 tools/v6/efts_index.py --from 2022-01-01 --to 2026-10-20 [--minutes 270]"""
import argparse, gzip, json, os, re, time, urllib.request
from datetime import date, timedelta
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'research', 'v6', 'index')
UA = 'InvestediaResearch/1.0 (+https://investedia.com; info@investedia.com)'
_last = [0.0]


def get(url, tries=8):
    for k in range(tries):
        w = 0.12 - (time.time() - _last[0])
        if w > 0: time.sleep(w)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r: j = json.load(r)
            if 'hits' in j: return j  # an error answer (rate limit, timeout) has no hits: wait and retry
        except Exception: pass
        time.sleep(10 * (k + 1))
    raise RuntimeError('efts failed: ' + url)


def day(d):
    """All 8-K filings of one day, merged by accession number."""
    rows, frm = {}, 0
    while True:
        j = get(f'https://efts.sec.gov/LATEST/search-index?forms=8-K&startdt={d}&enddt={d}&from={frm}')
        hs = j['hits']['hits']
        for h in hs:
            s = h['_source']; adsh = s.get('adsh') or h['_id'].split(':')[0]
            if '8-K' not in (s.get('root_forms') or [s.get('form')]): continue
            r = rows.setdefault(adsh, {'adsh': adsh, 'filed': s.get('file_date'), 'form': s.get('form'), 'ciks': s.get('ciks') or [], 'names': s.get('display_names') or [],
                                       'sics': s.get('sics') or [], 'items': sorted(set(s.get('items') or [])), 'docs': []})
            r['items'] = sorted(set(r['items']) | set(s.get('items') or []))
            r['docs'].append({'file': h['_id'].split(':', 1)[-1], 'type': s.get('file_type')})
        frm += len(hs)
        if not hs or frm >= j['hits']['total']['value'] or frm >= 9900: break
    for r in rows.values():  # point-in-time tickers from the display name, e.g. "KIORA PHARMACEUTICALS INC  (KPRX, KPHMW)  (CIK 0001372514)"
        r['tickers'] = sorted({t.strip() for n in r['names'] for m in re.findall(r'\(([A-Z0-9.\-, ]+)\)\s*\(CIK', n) for t in m.split(',') if t.strip()})
    return list(rows.values())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--from', dest='a', default='2022-01-01'); ap.add_argument('--to', dest='b', default='2026-10-20')
    ap.add_argument('--minutes', type=float, default=270); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); man_p = os.path.join(OUT, 'manifest.json')
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    t_end, d, end = time.time() + a.minutes * 60, date.fromisoformat(a.a), date.fromisoformat(a.b)
    while d <= end:
        k = d.isoformat()
        if k not in man and d.weekday() < 5:
            if time.time() > t_end: print('time budget used; resume next run', flush=True); break
            try: rows = day(k)
            except RuntimeError as e: print('skip for now:', e, flush=True); d += timedelta(days=1); continue
            with gzip.open(os.path.join(OUT, f'8k-{k[:7]}.jsonl.gz'), 'at') as f:
                for r in rows: f.write(json.dumps(r, separators=(',', ':')) + '\n')
            man[k] = len(rows); json.dump(man, open(man_p, 'w'))
            if d.day == 1 or len(man) % 20 == 0: print(k, len(rows), 'filings', flush=True)
        d += timedelta(days=1)
    print('days done:', len(man), flush=True)


if __name__ == '__main__':
    main()
