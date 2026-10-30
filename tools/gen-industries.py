"""Writes assets/globe/industries.json: the official SEC industry (SIC code) of every stock in markets.json that files with the SEC
(US companies and foreign companies with US listings). Public-domain data, no key, cached; run occasionally.
Used by the Globe's Sector Spread: peers must share an industry, not only a broad sector. Stocks without an SEC filing get no entry
(no guessed industries). Run: python3 tools/gen-industries.py"""
import json, os, re, time, unicodedata, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'Investedia research contact@investedia.com'}
def get(url):
    for k in range(3):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read())
        except Exception: time.sleep(2)
tk = get('https://www.sec.gov/files/company_tickers_exchange.json')
cik = {r[2].upper(): r[0] for r in tk['data']}
names = {r[0]: r[1] for r in tk['data']}
assets = json.load(open(os.path.join(ROOT, 'assets/globe/markets.json')))['assets']
out, seen, wrong = {}, {}, []
def norm(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower()
    return [w for w in re.sub(r'[^a-z0-9 ]', ' ', x).split() if w not in {'inc', 'corp', 'corporation', 'co', 'company', 'ltd', 'limited', 'plc', 'holdings', 'holding', 'group', 'the', 'sa', 'nv', 'ag', 'se', 'de'}]
CHECKED = {'GE': 'GE Aerospace files as General Electric Co', 'FMX': 'FEMSA = Fomento Economico Mexicano (Mexican Economic Development)'}  # verified exceptions
def same_company(asset_name, registrant):  # the ticker must really belong to this company (some bare US tickers belong to others)
    a, r = norm(asset_name), norm(registrant)
    return bool(a and r and (a[0] == r[0] or a[0][:5] == r[0][:5] or ' '.join(a) in ' '.join(r) or ' '.join(r) in ' '.join(a)))
for a in assets:
    if a.get('t') != 'stocks' or a.get('g') in ('Index', 'Country ETF'): continue
    c = cik.get(a['s'].upper()) or cik.get(a['s'].upper().replace('-', '.'))
    if not c: continue
    if c not in seen:
        d = get(f'https://data.sec.gov/submissions/CIK{int(c):010d}.json') or {}; time.sleep(.15)
        seen[c] = (d.get('sic'), d.get('sicDescription'), names.get(c))
    sic, desc, reg = seen[c]
    if a['s'] not in CHECKED and not same_company(a.get('n'), reg): wrong.append(f"{a['s']} {a.get('n')} != {reg}"); continue
    if sic: out[a['s']] = {'sic': sic, 'industry': desc, 'registrant': reg}
data = {'source': 'SEC EDGAR submissions (SIC code)', 'count': len(out), 'by': out}
for d in ('assets/globe', 'docs/assets/globe'): json.dump(data, open(os.path.join(ROOT, d, 'industries.json'), 'w'), separators=(',', ':'))
print(len(out), 'stocks with an SEC industry; skipped (ticker belongs to another company):', *wrong, sep='\n  ')
