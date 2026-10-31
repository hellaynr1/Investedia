"""Official/reference data for the registry builder, cached in tools/registry/cache (not committed).
  SEC company_tickers_exchange.json  ticker, CIK, registrant name, exchange (public domain; SEC fair access: <=10 req/s, named User-Agent)
  SEC submissions/CIK##########.json business address (headquarters city) for listings the globe has no place for
  SEC EDGAR state/country codes      address codes -> country
  Yahoo Finance chart meta           official security name, exchange, instrument type, currency (unofficial; the site already prices from it)
  GeoNames cities15000 + admin1      city -> coordinates (CC BY 4.0, credit GeoNames)"""
import io, json, os, re, threading, time, urllib.parse, urllib.request, zipfile

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
SEC_UA = {'User-Agent': 'Investedia research contact@investedia.com', 'Accept-Encoding': 'identity'}
YUA = {'User-Agent': 'Mozilla/5.0'}
_lock = threading.Lock(); _last = [0.0]

def _get(url, headers, gap=.15, tries=3):
    for k in range(tries):
        with _lock:
            w = gap - (time.time() - _last[0])
            if w > 0: time.sleep(w)
            _last[0] = time.time()
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(1 + 2 * k)
        except Exception: time.sleep(1 + 2 * k)
    return None

def _cached(name, url, headers, refresh=False):
    p = os.path.join(CACHE, name)
    if os.path.exists(p) and not refresh: return open(p, 'rb').read()
    b = _get(url, headers)
    if b is not None:
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(b)
    return b

def sec_tickers(refresh=False):
    """[{cik, name, ticker, exchange}] in SEC order (a company's first ticker is its primary listing)."""
    d = json.loads(_cached('sec-tickers-exchange.json', 'https://www.sec.gov/files/company_tickers_exchange.json', SEC_UA, refresh))
    return [dict(zip(d['fields'], r)) for r in d['data']]

def sec_submission(cik):
    b = _cached(f'sec/{int(cik):010d}.json', f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json', SEC_UA)
    try: return json.loads(b) if b else None
    except Exception: return None

def edgar_codes():
    b = _cached('edgar-codes.html', 'https://www.sec.gov/submit-filings/filer-support-resources/edgar-state-country-codes', SEC_UA)
    t = (b or b'').decode('utf-8', 'replace')
    return {c: re.sub(r'<[^>]+>', '', n).strip() for c, n in re.findall(r'<td[^>]*>\s*([A-Z0-9]{2})\s*</td>\s*<td[^>]*>(.*?)</td>', t, re.S)}

def yahoo_meta(sym, refresh=False):
    """Official security record or None (unknown symbol). Cached per symbol, including misses."""
    p = os.path.join(CACHE, 'yahoo', re.sub(r'[^A-Za-z0-9._=^-]', '_', sym) + '.json')
    if os.path.exists(p) and not refresh:
        try: return json.load(open(p))
        except Exception: pass
    b = _get(f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=5d&interval=1d', YUA, gap=.12, tries=2)
    meta = None
    if b:
        try:
            m = json.loads(b)['chart']['result'][0]['meta']
            meta = {k: m.get(k) for k in ('symbol', 'longName', 'shortName', 'exchangeName', 'fullExchangeName', 'instrumentType', 'currency', 'exchangeTimezoneName')}
        except Exception: meta = None
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(meta, open(p, 'w'))
    return meta

_GEO = None
def geonames():
    """{(ISO2, admin1, city key): (lat, lon, population)} and {(ISO2, city key): best} from GeoNames cities15000."""
    global _GEO
    if _GEO: return _GEO
    b = _cached('cities1000.zip', 'https://download.geonames.org/export/dump/cities1000.zip', YUA)
    z = zipfile.ZipFile(io.BytesIO(b)); rows = z.read('cities1000.txt').decode('utf-8').split('\n')
    by_admin, by_country, world = {}, {}, {}
    key = lambda s: re.sub(r'[^a-z0-9]', '', __import__('unicodedata').normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())
    for r in rows:
        f = r.split('\t')
        if len(f) < 15: continue
        names = {f[1], f[2]} | ({x for x in f[3].split(',') if x} if int(f[14] or 0) > 100000 else set())
        lat, lon, pop, cc, a1 = float(f[4]), float(f[5]), int(f[14] or 0), f[8], f[10]
        for n in names:
            k = key(n)
            if not k: continue
            for d, kk in ((by_admin, (cc, a1, k)), (by_country, (cc, k)), (world, k)):
                if kk not in d or d[kk][2] < pop: d[kk] = (round(lat, 3), round(lon, 3), pop, cc)
    _GEO = (by_admin, by_country, world, key)
    return _GEO

def geocode(city, iso2=None, admin1=None):
    """(lat, lon, ISO2) for an address city. Tries the whole string, then shorter word runs ("CAMACARI BAHIA BRAZI" -> "Camacari");
    without a country only a city of 1M+ people is accepted (London, Zurich)."""
    by_admin, by_country, world, key = geonames()
    ws = re.sub(r'[0-9]+', ' ', city or '').replace(',', ' ').split()
    ws = [w for w in ws if len(w) > 1 or not w.isalpha()]
    runs = [ws[i:j] for n in range(len(ws), 0, -1) for i in range(0, len(ws) - n + 1) for j in [i + n]]
    for r in runs:
        k = key(' '.join(r))
        if not k: continue
        if iso2:
            hit = by_admin.get((iso2, admin1, k)) if admin1 else by_country.get((iso2, k))
        else:
            hit = world.get(k); hit = hit if hit and hit[2] >= 1000000 else None
        if hit: return hit[0], hit[1], hit[3]
    return None
