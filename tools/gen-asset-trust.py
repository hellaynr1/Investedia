"""Writes assets/globe/asset-trust.json: which stock symbols may take part in Globe relationships (Main impact, Ripple, Sector spread,
Story threads). A symbol must resolve to the company we say it is:
  verified-sec       bare US ticker whose SEC registrant name matches the company name
  verified-yahoo     ticker whose Yahoo Finance security name (longName/shortName) matches the company name
  verified-exchange  exchange-suffixed symbol (unique on that exchange) with an official name; the official name becomes canonical
  verified-checked   hand-checked exception with a reason (CHECKED below)
  known-bad          the official name belongs to ANOTHER company (e.g. AIR = AAR Corp, not Airbus)
  unverified         no official name could be retrieved
Only verified-* symbols are used for relationships; known-bad and unverified are excluded (no guessing). Indices, commodities,
currencies and crypto use fixed symbols and are always allowed. Run: python3 tools/gen-asset-trust.py"""
import json, os, re, time, unicodedata, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC_UA = {'User-Agent': 'Investedia research contact@investedia.com'}; YUA = {'User-Agent': 'Mozilla/5.0'}
CHECKED = {'GE': 'GE Aerospace files with the SEC as General Electric Co', 'FMX': 'FEMSA = Fomento Economico Mexicano (SEC: Mexican Economic Development)'}
STOP = {'inc', 'corp', 'corporation', 'co', 'company', 'ltd', 'limited', 'plc', 'holdings', 'holding', 'group', 'the', 'sa', 'nv', 'ag', 'se', 'de', 'spa', 'adr', 'ads', 'class', 'a', 'b', 'shares', 'common', 'stock', 'and', 'of', 'cl', 'sponsored', 'unsponsored', 'each', 'rep', 'ord', 'tbk', 'pt', 'bhd', 'pcl', 'asa', 'ab', 'oyj'}
def get(url, h):
    for k in range(3):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40).read())
        except Exception: time.sleep(1.5)
def words(x):
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower().replace('&', ' ')
    return [w for w in re.sub(r'[^a-z0-9 ]', ' ', x).split() if w not in STOP]
def same(a, b):
    a, b = words(a), words(b)
    if not a or not b: return False
    A, B = ' '.join(a), ' '.join(b)
    return a[0] == b[0] or a[0][:5] == b[0][:5] or A in B or B in A or bool(set(a) & set(b) - {'bank', 'energy', 'international', 'industries', 'financial', 'motor', 'motors', 'resources', 'technology', 'technologies', 'global', 'national', 'first', 'american', 'new'})
assets = json.load(open(os.path.join(ROOT, 'assets/globe/markets.json')))['assets']
tk = get('https://www.sec.gov/files/company_tickers_exchange.json', SEC_UA)
sec = {r[2].upper(): r[1] for r in tk['data']}
out = {}
for a in assets:
    if a.get('t') != 'stocks' or a.get('g') in ('Index', 'Country ETF'): continue
    s, n = a['s'], a.get('n', '')
    if s in CHECKED: out[s] = {'status': 'verified-checked', 'official': CHECKED[s]}; continue
    reg = sec.get(s.upper()) if '.' not in s else None
    if reg:
        out[s] = {'status': 'verified-sec' if same(n, reg) else 'known-bad', 'official': reg}; continue
    m = (get(f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}?range=1d&interval=1d', YUA) or {}).get('chart', {}).get('result') or [{}]
    meta = m[0].get('meta', {}) if m else {}; off = meta.get('longName') or meta.get('shortName'); time.sleep(.2)
    if not off: out[s] = {'status': 'unverified', 'official': None}
    elif same(n, off): out[s] = {'status': 'verified-yahoo', 'official': off}
    elif '.' in s: out[s] = {'status': 'verified-exchange', 'official': off, 'note': 'exchange-unique symbol; our display name is a short form of the official name'}
    else: out[s] = {'status': 'known-bad', 'official': off}  # a bare US-style ticker whose security is another company
data = {'about': __doc__.split('\n')[0], 'by': out}
for d in ('assets/globe', 'docs/assets/globe'): json.dump(data, open(os.path.join(ROOT, d, 'asset-trust.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
from collections import Counter
print(Counter(v['status'] for v in out.values()))
for s, v in out.items():
    if v['status'] in ('known-bad', 'unverified'): print(' ', v['status'], s, '|', next(a['n'] for a in assets if a['s'] == s), '| official:', v['official'])
