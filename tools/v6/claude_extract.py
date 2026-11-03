"""v6 Track C: text facts from 8-K press releases (Exhibit 99.x) that structured sources don't give: guidance direction, deal role and
terms, management changes, buybacks/financing, regulatory/litigation outcome. Claude Haiku 5.5 through the Message Batches API
(50% cheaper), structured output so every answer is schema-valid. Facts only: no direction call, no market view.
Budget guard: stops when the tracked spend reaches V6_CLAUDE_BUDGET (default $4.50). Cached per filing; resumable.
Steps per run: (1) fetch missing press-release texts (SEC, fair-access rate) -> research/v6/text/; (2) submit one batch of up to
V6_BATCH_SIZE filings not yet extracted; (3) collect finished batches -> research/v6/facts/YYYY-MM.jsonl.
Needs ANTHROPIC_API_KEY.  python3 tools/v6/claude_extract.py"""
import argparse, glob, gzip, hashlib, html, json, os, re, sys, time, urllib.request
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from tools.v6.exhibits import filings, EX99

IDX, TXT, FACTS = (os.path.join(ROOT, 'research', 'v6', d) for d in ('index', 'text', 'facts'))
MAN = os.path.join(FACTS, 'manifest.json')
MODEL, BUDGET = 'claude-haiku-5-5', float(os.environ.get('V6_CLAUDE_BUDGET', 4.5))
BATCH_SIZE, FETCH_MAX = int(os.environ.get('V6_BATCH_SIZE', 3000)), int(os.environ.get('V6_FETCH_MAX', 6000))
PRICE_IN, PRICE_OUT = 0.10 / 1e6 * 0.5, 0.50 / 1e6 * 0.5  # Haiku 5.5, batch discount
ITEMS = {'2.02', '1.01', '2.01', '5.02', '7.01', '8.01', '1.02', '2.05', '2.06', '3.01', '4.02'}
UA = 'InvestediaResearch/1.0 (+https://investedia.com; info@investedia.com)'
MAX_CHARS = 6000  # the first ~1,500 tokens of a release hold the headline facts

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "event_type", "guidance_direction", "guidance_vs_previous", "deal_role", "deal_premium_pct", "deal_value_usd_m", "mgmt_change",
    "mgmt_role", "mgmt_planned", "buyback_usd_m", "dividend_change", "financing_type", "reg_outcome", "litigation_outcome", "one_line"],
  "properties": {
    "event_type": {"type": "string", "enum": ["earnings", "guidance", "m&a", "management", "buyback-dividend", "financing", "regulatory", "litigation", "other"]},
    "guidance_direction": {"type": "string", "enum": ["raised", "lowered", "maintained", "initiated", "withdrawn", "none"]},
    "guidance_vs_previous": {"type": "string", "enum": ["above", "below", "same", "not-stated"]},
    "deal_role": {"type": "string", "enum": ["target", "acquirer", "merger-of-equals", "seller", "none"]},
    "deal_premium_pct": {"type": ["number", "null"]}, "deal_value_usd_m": {"type": ["number", "null"]},
    "mgmt_change": {"type": "string", "enum": ["departure", "appointment", "both", "none"]},
    "mgmt_role": {"type": "string", "enum": ["CEO", "CFO", "chair", "other", "none"]},
    "mgmt_planned": {"type": "string", "enum": ["planned", "abrupt", "not-stated", "none"]},
    "buyback_usd_m": {"type": ["number", "null"]},
    "dividend_change": {"type": "string", "enum": ["increase", "cut", "suspended", "special", "initiated", "none"]},
    "financing_type": {"type": "string", "enum": ["equity", "convertible", "debt", "none"]},
    "reg_outcome": {"type": "string", "enum": ["approval", "rejection", "investigation", "settlement", "none"]},
    "litigation_outcome": {"type": "string", "enum": ["won", "lost", "settled", "filed", "none"]},
    "one_line": {"type": "string"}}}
SYSTEM = ("You extract facts from a company's press release. Use only what the text states; never use outside knowledge, never infer "
          "how the stock moved or will move. If a field is not stated, use 'none', 'not-stated' or null. one_line: max 20 words, factual.")


def sec(url):
    time.sleep(0.12)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r: return r.read(800_000).decode('latin-1')
    except Exception: return None


def candidates(base=None):
    """Merge verified attachment metadata without rewriting the original SEC index."""
    for r in filings(Path(base) if base is not None else Path(ROOT)/'research/v6'):
        if not r.get('tickers') or not set(r.get('items') or []) & ITEMS or (r.get('filed') or '') > '2026-10-20': continue
        docs=[d for d in r.get('docs') or [] if EX99.fullmatch(d.get('type') or '')
              and Path(d.get('file','')).suffix.lower() in ('.htm','.html','.txt')]
        # Prefer a press release to presentation slides; deterministic tie break.
        docs.sort(key=lambda d: ('press release' not in d.get('description','').lower(),
                                 'presentation' in d.get('description','').lower(),d['file']))
        if docs:
            selected=docs[0]
            yield {**r,'exhibit_cik':selected.get('cik') or r['ciks'][0]},selected['file']


def text_path(adsh): return os.path.join(TXT, adsh[:10], adsh + '.txt.gz')


def fetch_texts(todo):
    n = 0
    for r, ex in todo:
        p = text_path(r['adsh'])
        if os.path.exists(p): continue
        if n >= FETCH_MAX: break
        cik = str(int(r.get('exhibit_cik') or r['ciks'][0])) if r.get('ciks') else None
        raw = sec(f"https://www.sec.gov/Archives/edgar/data/{cik}/{r['adsh'].replace('-', '')}/{ex}") if cik else None
        if not raw: continue
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', raw))).strip()[:MAX_CHARS]
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with gzip.open(p, 'wt') as f: f.write(t)
        proof={'adsh':r['adsh'],'file':ex,'source_url':f"https://www.sec.gov/Archives/edgar/data/{cik}/{r['adsh'].replace('-', '')}/{ex}",
               'filing_accepted_at':r.get('filing_accepted_at'),
               'source_sha256':hashlib.sha256(raw.encode('latin-1')).hexdigest(),
               'source_capture_limit_bytes':800000,'source_capture_may_be_truncated':len(raw.encode('latin-1'))>=800000,
               'excerpt_sha256':hashlib.sha256(t.encode()).hexdigest(),
               'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
               'truncated':True,'max_chars':MAX_CHARS}
        with open(p+'.json','w') as f:json.dump(proof,f,sort_keys=True)
        n += 1
    return n


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fetch-only',action='store_true',help='SEC text caching only; never imports or calls Anthropic')
    args=ap.parse_args()
    if args.fetch_only:
        todo=sorted(candidates(),key=lambda x:('2.02' not in x[0]['items'],x[0]['filed']))
        print('eligible filings',len(todo),'new texts',fetch_texts(todo));return
    import anthropic
    os.makedirs(FACTS, exist_ok=True)
    man = json.load(open(MAN)) if os.path.exists(MAN) else {'spent_usd': 0.0, 'batches': {}, 'done': []}
    done = set(man['done']); pending = {a for b in man['batches'].values() if b['state'] != 'collected' for a in b['ids']}
    client = anthropic.Anthropic()
    # 1) collect finished batches
    for bid, b in man['batches'].items():
        if b['state'] == 'collected': continue
        st = client.messages.batches.retrieve(bid)
        if st.processing_status != 'ended': continue
        rows = []
        for res in client.messages.batches.results(bid):
            if res.result.type != 'succeeded': continue
            m = res.result.message
            man['spent_usd'] += m.usage.input_tokens * PRICE_IN + m.usage.output_tokens * PRICE_OUT
            txt = next((c.text for c in m.content if c.type == 'text'), None)
            try: rows.append({'adsh': res.custom_id, 'model': MODEL, **json.loads(txt)})
            except Exception: continue
        for r in rows:
            with open(os.path.join(FACTS, f"{b['months'].get(r['adsh'], 'unknown')}.jsonl"), 'a') as f: f.write(json.dumps(r, separators=(',', ':')) + '\n')
            done.add(r['adsh'])
        b['state'] = 'collected'; b['got'] = len(rows)
        print('collected', bid, len(rows), 'facts; spent so far $%.2f' % man['spent_usd'], flush=True)
    man['done'] = sorted(done); json.dump(man, open(MAN, 'w'))
    # 2) fetch press-release texts (earnings first: they matter most)
    todo = sorted(candidates(), key=lambda x: ('2.02' not in x[0]['items'], x[0]['filed']))
    print('fetched', fetch_texts([x for x in todo if x[0]['adsh'] not in done]), 'new texts', flush=True)
    # 3) submit the next batch within budget
    if man['spent_usd'] >= BUDGET: print('budget reached: no new batch'); return
    reqs, months = [], {}
    for r, _ in todo:
        a = r['adsh']
        if a in done or a in pending or not os.path.exists(text_path(a)): continue
        with gzip.open(text_path(a), 'rt') as f: t = f.read()
        reqs.append({'custom_id': a, 'params': {'model': MODEL, 'max_tokens': 600, 'system': SYSTEM, 'output_config': {'effort': 'low', 'format': {'type': 'json_schema', 'schema': SCHEMA}},
                     'messages': [{'role': 'user', 'content': f"Company: {', '.join(r['tickers'][:2])} | 8-K items {', '.join(r['items'])} | filed {r['filed']}\n\n{t}"}]}})
        months[a] = r['filed'][:7]
        if len(reqs) >= BATCH_SIZE: break
    est = len(reqs) * (1700 * PRICE_IN + 200 * PRICE_OUT)
    if not reqs: print('nothing to submit'); return
    if man['spent_usd'] + est > BUDGET: reqs = reqs[:max(0, int((BUDGET - man['spent_usd']) / (1700 * PRICE_IN + 200 * PRICE_OUT)))]
    if not reqs: print('budget reached'); return
    b = client.messages.batches.create(requests=reqs)
    man['batches'][b.id] = {'state': 'submitted', 'ids': [q['custom_id'] for q in reqs], 'months': months, 'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    json.dump(man, open(MAN, 'w'))
    print('submitted batch', b.id, len(reqs), 'filings, est $%.2f' % est, flush=True)


if __name__ == '__main__':
    main()
