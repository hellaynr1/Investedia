"""SEC 8-K history for engine research (v5 vs v6 comparison): every 8-K of the US companies in our registry, 2021 onward, with the
exact SEC acceptance time, the 8-K items and the start of the press release (exhibit 99.x). Resumable, one gzip JSONL per quarter in
research/sec/. Fair access: <= 8 requests a second, contact address in the User-Agent (SEC rule).
  python3 tools/sec/harvest.py [--from 2021Q1] [--to 2026Q4] [--minutes 280]"""
import argparse, gzip, html, json, os, re, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import registry

UA = 'InvestediaResearch/1.0 (+https://investedia.com; info@investedia.com)'
OUT = os.path.join(ROOT, 'research', 'sec')
KEEP_ITEMS = {'1.01', '1.02', '2.01', '2.02', '2.05', '2.06', '3.01', '4.02', '5.02', '7.01', '8.01'}  # market-relevant items
_last = [0.0]


def get(url, limit=None, tries=4):
    for k in range(tries):
        wait = 0.13 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'}), timeout=30) as r:
                return r.read(limit).decode('latin-1') if limit else r.read().decode('latin-1')
        except Exception as e:
            if '404' in str(e): return None
            time.sleep(2 * (k + 1))
    return None


def quarters(a, b):
    y, q = int(a[:4]), int(a[-1]); y2, q2 = int(b[:4]), int(b[-1])
    while (y, q) <= (y2, q2):
        yield f'{y}Q{q}'; q += 1
        if q == 5: y, q = y + 1, 1


def companies():
    """CIK -> ticker for the US-listed equities of the registry (the ones the site can call live)."""
    R = registry.get()
    us = {a['px'] for a in R.assets.values() if a.get('class') == 'equity' and a.get('px') and not re.search(r'[.^=]', a['px'])}
    tk = json.loads(get('https://www.sec.gov/files/company_tickers.json'))
    return {str(v['cik_str']): v['ticker'] for v in tk.values() if v['ticker'] in us}


def parse(txt):
    """Acceptance time, items and the press-release text from the start of a full submission file."""
    acc = re.search(r'<ACCEPTANCE-DATETIME>(\d{14})', txt)
    items = sorted(set(re.findall(r'ITEM INFORMATION:\s*(?:Item\s*)?([0-9]\.[0-9]{2})', txt, re.I)))
    if not items: items = sorted(set(re.findall(r'\bItem\s+([0-9]\.[0-9]{2})', txt[:60000])))
    ex = re.search(r'<TYPE>EX-99[.0-9]*\s.*?<TEXT>(.*?)</TEXT>', txt, re.S | re.I)
    body = ex.group(1) if ex else ''
    body = html.unescape(re.sub(r'<[^>]+>', ' ', body)); body = re.sub(r'\s+', ' ', body).strip()
    return (acc.group(1) if acc else None), items, body[:3000]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--from', dest='a', default='2021Q1'); ap.add_argument('--to', dest='b', default='2026Q4')
    ap.add_argument('--minutes', type=float, default=280); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); t_end = time.time() + a.minutes * 60
    cos = companies(); print(len(cos), 'companies', flush=True)
    for q in quarters(a.a, a.b):
        path = os.path.join(OUT, f'8k-{q}.jsonl.gz'); done_flag = path + '.done'
        if os.path.exists(done_flag): continue
        have = set()
        if os.path.exists(path):
            with gzip.open(path, 'rt') as f: have = {json.loads(l)['acc'] for l in f}
        idx = get(f'https://www.sec.gov/Archives/edgar/full-index/{q[:4]}/QTR{q[-1]}/form.idx')
        if not idx: print(q, 'no index yet'); continue
        rows = []
        for line in idx.splitlines():
            if not line.startswith('8-K '): continue
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) < 5: continue
            form, name, cik, date, fn = parts[0], parts[1], parts[2], parts[3], parts[4]
            if cik in cos: rows.append((cik, name, date, fn))
        n0 = len(have)
        with gzip.open(path, 'at') as out:
            for cik, name, date, fn in rows:
                accno = fn.rsplit('/', 1)[-1].replace('.txt', '')
                if accno in have: continue
                if time.time() > t_end: print('time budget used; next run resumes', flush=True); return
                txt = get('https://www.sec.gov/Archives/' + fn, limit=600_000)
                if not txt: continue
                acc, items, body = parse(txt)
                rec = {'acc': accno, 'cik': cik, 'ticker': cos[cik], 'name': name, 'filed': date, 'accepted': acc, 'items': items,
                       'keep': bool(set(items) & KEEP_ITEMS), 'text': body if set(items) & KEEP_ITEMS else ''}
                out.write(json.dumps(rec, separators=(',', ':')) + '\n'); have.add(accno)
        open(done_flag, 'w').write(str(len(have)))
        print(q, len(rows), 'filings,', len(have) - n0, 'new', flush=True)
    print('all quarters done', flush=True)


if __name__ == '__main__':
    main()
