"""Live news for the Globe News page -> assets/globe/news-live.json (+ photos, + news-status.json)
Runs every 30 minutes in GitHub Actions (update-globe-news.yml). Free sources only:
  - GDELT DOC 2.0 (open, no key): business / economy headlines from around the world
  - Official press releases (ECB, Federal Reserve, Bank of England RSS)
  - Gemini (GEMINI_API_KEY): picks the financially relevant stories, merges duplicates, finds the place, category,
    companies and importance, and writes a short neutral summary from the headline + description only
  - Pixabay (PIXABAY_KEY): one topic photo per theme, downloaded once and reused (Pixabay Content License)
We never copy articles: each story keeps its headline (rewritten neutrally), our short summary, the source name, original link and times.
Without keys or when a source fails, the previous news stays online."""
import html, json, os, re, sys, time, hashlib, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(ROOT, 'assets/globe'); D = os.path.join(ROOT, 'docs/assets/globe')
OUT = 'news-live.json'; STATUS = 'news-status.json'; PH = 'photos'
UA = 'InvestediaNews/1.0 (+https://investedia.com; info@investedia.com)'
NOW = datetime.now(timezone.utc); ISO_NOW = NOW.strftime('%Y-%m-%dT%H:%M:%SZ')
KEEP_DAYS, MAX_STORIES, MAX_NEW = 7, 160, 30
GEMINI = os.environ.get('GEMINI_API_KEY', '').strip(); PIXABAY = os.environ.get('PIXABAY_KEY', '').strip()
status = {'ran_at': ISO_NOW, 'errors': []}
CATS = ['markets', 'companies', 'economy', 'technology', 'crypto', 'commodities', 'geopolitics']
REGION = {}  # iso2 -> region key, filled from the World Bank country list
PHOTO_TOPICS = ['oil refinery', 'oil tanker ship', 'container port', 'semiconductor chip', 'data center servers', 'bank building', 'stock market trading screen',
                'banknotes money', 'gold bars', 'copper mine', 'wheat field harvest', 'coffee beans', 'electric car charging', 'car factory', 'airplane airport',
                'smartphone', 'solar panels', 'wind turbines', 'gas pipeline', 'bitcoin cryptocurrency', 'housing construction', 'shopping retail store',
                'pharmaceutical laboratory', 'steel factory', 'mining truck', 'farm tractor', 'city skyline business district', 'parliament government building',
                'factory workers', 'cargo trucks highway', 'freight train', 'office meeting', 'artificial intelligence robot', 'cyber security', 'luxury fashion',
                'beer brewery', 'hotel tourism', 'telecom tower 5g', 'satellite space rocket', 'supermarket groceries']


def log(*a): print(*a, flush=True)
def err(msg): status['errors'].append(str(msg)[:300]); log('ERROR', msg)


def get(url, data=None, headers=None, timeout=40, raw=False):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read(2_000_000)
    return b if raw else b.decode('utf-8', 'replace')


def save(name, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    for d in (G, D):
        os.makedirs(d, exist_ok=True); open(os.path.join(d, name), 'w', encoding='utf-8').write(s)


# ---------- reference data: map countries, codes, bounding boxes, price symbols ----------
def load_ref():
    rows = json.load(open(os.path.join(G, 'countries-50m.json')))
    box = {}
    for r in rows:
        b = [180, 90, -180, -90]
        for f in r[3:]:
            x = y = 0
            for i in range(0, len(f), 2):
                x += f[i]; y += f[i + 1]; lo, la = x / 50, y / 50
                b = [min(b[0], lo), min(b[1], la), max(b[2], lo), max(b[3], la)]
        box[r[0]] = (b, (r[1] / 50, r[2] / 50))
    iso = json.load(open(os.path.join(ROOT, 'tools/globe-news/iso.json')))  # map name -> ISO2 (written by tools/globe-news/build.py)
    by_iso = {}
    for name, c in iso.items(): by_iso.setdefault(c, name)
    by_iso['US'] = 'United States of America'
    reg = {'North America': 'na', 'Europe & Central Asia': 'eu', 'East Asia & Pacific': 'asia', 'South Asia': 'asia', 'Middle East & North Africa': 'me',
           'Middle East, North Africa, Afghanistan & Pakistan': 'me', 'Sub-Saharan Africa': 'af', 'Latin America & Caribbean': 'latam'}
    for c in json.load(open(os.path.join(ROOT, 'tools/globe-news/wb-countries.json')))[1]:
        r = reg.get(c['region']['value'].strip())
        if r: REGION[c['iso2Code']] = r
    for c in ('AU', 'NZ', 'FJ', 'PG', 'NC', 'SB', 'VU', 'WS', 'TO', 'PF'): REGION[c] = 'oc'
    for c in ('EG', 'LY', 'TN', 'DZ', 'MA'): REGION[c] = 'af'
    for c in ('KZ', 'UZ', 'TM', 'KG', 'TJ', 'AF', 'PK'): REGION[c] = 'asia'
    sym = {}
    try:
        for a in json.load(open(os.path.join(G, 'markets.json')))['assets']:
            if a.get('site'): sym[a['s'].upper()] = a['site']
    except Exception as e: err(f'markets.json: {e}')
    try:
        q = json.loads(re.sub(r'^window\.QUOTES=', '', open(os.path.join(ROOT, 'assets/quotes.js')).read().strip().rstrip(';')))['q']
        for k in q: sym.setdefault(k.upper(), k)
    except Exception as e: err(f'quotes.js: {e}')
    return box, by_iso, sym


# ---------- sources ----------
GDELT_QUERIES = [
    '("central bank" OR "interest rate" OR inflation OR GDP OR recession OR tariffs OR "trade deal") sourcelang:english',
    '(earnings OR "shares rose" OR "shares fell" OR "stock market" OR IPO OR merger OR acquisition OR bankruptcy) sourcelang:english',
    '(oil OR OPEC OR gas OR gold OR copper OR wheat OR bitcoin OR semiconductor OR "artificial intelligence") (prices OR market OR company) sourcelang:english',
]


def gdelt():
    out = []
    for i, q in enumerate(GDELT_QUERIES):
        url = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode({'query': q, 'mode': 'ArtList', 'format': 'json', 'maxrecords': 75, 'timespan': '3h', 'sort': 'HybridRel'})
        for t in range(3):
            time.sleep(6)  # GDELT asks for one request every 5 seconds
            try:
                txt = get(url, timeout=60)
                if txt.lstrip().startswith('{'):
                    for a in json.loads(txt).get('articles', []):
                        if a.get('language', 'English') != 'English': continue
                        ts = datetime.strptime(a['seendate'], '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
                        out.append({'title': html.unescape(a['title']).strip(), 'url': a['url'], 'source': a.get('domain', ''), 'published': ts.strftime('%Y-%m-%dT%H:%M:%SZ'), 'kind': 'news'})
                    break
                log('GDELT busy:', txt[:80])
            except Exception as e:
                if t == 2: err(f'GDELT query {i}: {e}')
    return out


FEEDS = [  # official press releases: (url, source name, hint)
    ('https://www.ecb.europa.eu/rss/press.html', 'European Central Bank', 'ECB press release, Frankfurt, Germany'),
    ('https://www.federalreserve.gov/feeds/press_all.xml', 'Federal Reserve', 'US Federal Reserve press release, Washington DC'),
    ('https://www.bankofengland.co.uk/rss/news', 'Bank of England', 'Bank of England news, London, United Kingdom'),
]


def rss():
    out = []
    for url, name, hint in FEEDS:
        try:
            root = ET.fromstring(get(url).encode('utf-8'))
            for it in root.iter('item'):
                t, l = (it.findtext('title') or '').strip(), (it.findtext('link') or '').strip()
                if not t or not l: continue
                pd = it.findtext('pubDate') or it.findtext('{http://purl.org/dc/elements/1.1/}date') or ''
                try: ts = datetime.strptime(pd.strip()[:25].strip(), '%a, %d %b %Y %H:%M:%S').replace(tzinfo=timezone.utc)
                except ValueError:
                    try: ts = datetime.fromisoformat(pd.strip().replace('Z', '+00:00'))
                    except ValueError: ts = NOW
                if NOW - ts > timedelta(days=3): continue
                desc = re.sub(r'<[^>]+>', ' ', html.unescape(it.findtext('description') or '')).strip()
                out.append({'title': html.unescape(t), 'url': l, 'source': name, 'published': ts.strftime('%Y-%m-%dT%H:%M:%SZ'), 'kind': 'official', 'hint': hint, 'desc': desc[:400]})
        except Exception as e: err(f'RSS {name}: {e}')
    return out


def describe(c):  # the article's own short description (meta tag), used only as input for our summary
    if c.get('desc'): return c
    try:
        h = get(c['url'], timeout=10)[:300_000]
        m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:description|description)["\'][^>]+content=["\']([^"\']{20,600})', h, re.I) \
            or re.search(r'<meta[^>]+content=["\']([^"\']{20,600})["\'][^>]+(?:property|name)=["\'](?:og:description|description)', h, re.I)
        if m: c['desc'] = html.unescape(m.group(1)).strip()[:400]
    except Exception: pass
    return c


def norm(t): return set(w for w in re.sub(r'[^a-z0-9 ]', ' ', t.lower()).split() if len(w) > 2)


def dedupe(items, known_titles):
    out, seen = [], [norm(t) for t in known_titles]
    for c in sorted(items, key=lambda c: c['kind'] != 'official'):
        w = norm(c['title'])
        if len(w) < 3: continue
        if any(len(w & s) / max(1, len(w | s)) > .55 for s in seen): continue
        seen.append(w); out.append(c)
    return out


# ---------- Gemini ----------
PROMPT = """You are the news editor of Investedia, a financial news globe for beginner investors. Below are candidate headlines (JSON) with their source and, when available, the article's own short description.

Pick at most {n} stories that are genuinely about business, finance, markets, companies, the economy, commodities, crypto, technology business, or politics/geopolitics WITH a clear economic impact. Skip: sports, celebrity, crime, lifestyle, opinion columns, press-release spam, "stock to buy" tips, price-target listicles, and anything you cannot place.
Merge candidates that report the same event into one story (list all their indexes in "members").

For each story return:
- "members": candidate indexes (numbers) of the same event, most important source first
- "headline": a neutral, factual headline in plain English, max 90 characters, no clickbait, no exclamation marks
- "summary": 1-2 short sentences (max 45 words) using ONLY facts present in the candidates' titles/descriptions. Never invent numbers, names, quotes or reasons.
- "why": 1-2 sentences of general, well-established background explaining why this matters for investors (e.g. what the company or institution is). No claims about the event itself beyond the input.
- "category": one of {cats}
- "importance": 3 = major global market story, 2 = notable, 1 = minor
- "market_moving": true only if the event itself clearly moves markets
- "place": city or area where it happens (company: headquarters city), "country": ISO 3166-1 alpha-2 code, "lat", "lon": coordinates of that place
- "entities": up to 3 companies or assets involved: {{"name": ..., "ticker": Yahoo Finance symbol if you are sure (e.g. NVDA, ASML, 7203.T, BZ=F, EURUSD=X, ^GSPC, BTC-USD) else null}}
- "photo": one of {topics} that fits the subject, or null
- "leads_to": index (in your output list) of another selected story this one directly causes or strongly affects, else null. Use rarely.

Return ONLY a JSON array of story objects.

Candidates:
{cands}"""


def gemini(prompt):
    if not GEMINI: raise RuntimeError('GEMINI_API_KEY is not set')
    body = json.dumps({'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json'}}).encode()
    last = None
    for model in ('gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash'):
        for t in range(2):
            try:
                r = json.loads(get(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', data=body,
                                   headers={'Content-Type': 'application/json', 'x-goog-api-key': GEMINI}, timeout=180))
                txt = r['candidates'][0]['content']['parts'][0]['text']
                status['gemini_model'] = model
                return json.loads(re.sub(r'^```(json)?|```$', '', txt.strip()))
            except urllib.error.HTTPError as e:
                last = f'{model}: HTTP {e.code} {e.read()[:200]!r}'
                if e.code in (400, 401, 403): raise RuntimeError(last)
                time.sleep(10)
            except Exception as e:
                last = f'{model}: {e}'; time.sleep(5)
    raise RuntimeError(last)


# ---------- photos (Pixabay, downloaded once per topic and reused) ----------
def photo(topic, seed):
    if not topic or topic not in PHOTO_TOPICS: return None
    idx_path = os.path.join(G, PH, 'index.json')
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
    if topic not in idx and PIXABAY:
        try:
            r = json.loads(get('https://pixabay.com/api/?' + urllib.parse.urlencode({'key': PIXABAY, 'q': topic, 'image_type': 'photo', 'orientation': 'horizontal', 'safesearch': 'true', 'per_page': 20, 'min_width': 1200})))
            hits = [h for h in r.get('hits', []) if h.get('largeImageURL')][:3]
            got = []
            for h in hits:
                b = get(h['largeImageURL'], raw=True, timeout=60)
                name = f"{re.sub(r'[^a-z0-9]+', '-', topic)}-{h['id']}.jpg"
                try:
                    from PIL import Image; import io
                    im = Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((1200, 800)); bio = io.BytesIO(); im.save(bio, 'JPEG', quality=78, optimize=True, progressive=True); b = bio.getvalue()
                except Exception: pass
                for d in (G, D):
                    os.makedirs(os.path.join(d, PH), exist_ok=True); open(os.path.join(d, PH, name), 'wb').write(b)
                got.append({'file': f'{PH}/{name}', 'credit': h.get('user', 'Pixabay'), 'source_url': h.get('pageURL'), 'alt': topic})
            idx[topic] = got
            for d in (G, D): open(os.path.join(d, PH, 'index.json'), 'w').write(json.dumps(idx, indent=1))
            status['photos_downloaded'] = status.get('photos_downloaded', 0) + len(got)
        except Exception as e: err(f'Pixabay {topic}: {e}')
    opts = idx.get(topic) or []
    if not opts: return None
    p = opts[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(opts)]
    return {'kind': 'topic', 'file': p['file'], 'alt': f'{topic} (illustration)', 'credit': p['credit'], 'license': 'Pixabay Content License',
            'license_url': 'https://pixabay.com/service/license-summary/', 'source': 'Pixabay', 'source_url': p['source_url']}


# ---------- main ----------
def main():
    box, by_iso, sym = load_ref()
    prev_path = os.path.join(G, OUT)
    prev = json.load(open(prev_path)).get('stories', []) if os.path.exists(prev_path) else []
    cutoff = NOW - timedelta(days=KEEP_DAYS)
    prev = [s for s in prev if datetime.fromisoformat(s['published_at'].replace('Z', '+00:00')) > cutoff]
    known_urls = {u['url'] for s in prev for u in s.get('sources', [])}
    raw = gdelt() + rss()
    status['fetched'] = len(raw)
    fresh = [c for c in raw if c['url'] not in known_urls]
    cands = dedupe(fresh, [s['headline'] for s in prev])[:90]
    status['candidates'] = len(cands)
    log(f'{len(raw)} fetched, {len(cands)} new candidates')
    new = []
    if cands:
        with ThreadPoolExecutor(8) as ex: cands = list(ex.map(describe, cands))
        listing = json.dumps([{'i': i, 'title': c['title'], 'source': c['source'], **({'about': c['hint']} if c.get('hint') else {}), **({'description': c['desc']} if c.get('desc') else {})} for i, c in enumerate(cands)], ensure_ascii=False)
        try:
            picked = gemini(PROMPT.format(n=MAX_NEW, cats=', '.join(CATS), topics=', '.join(PHOTO_TOPICS), cands=listing))
            status['gemini_ok'] = True
        except Exception as e:
            err(f'Gemini: {e}'); picked = []
        ids = []
        for k, p in enumerate(picked if isinstance(picked, list) else []):
            try:
                mem = [m for m in p.get('members', []) if isinstance(m, int) and 0 <= m < len(cands)]
                if not mem: ids.append(None); continue
                iso2 = str(p.get('country', '')).upper(); country = by_iso.get(iso2)
                if not country or p.get('category') not in CATS: ids.append(None); continue
                lat, lon = float(p['lat']), float(p['lon'])
                (b, centre) = box.get(country, ([-180, -90, 180, 90], (lon, lat)))
                if not (b[0] - 1 <= lon <= b[2] + 1 and b[1] - 1 <= lat <= b[3] + 1): lon, lat = centre  # place outside the country: use its centre
                srcs = [{'name': cands[m]['source'], 'url': cands[m]['url']} for m in mem]
                pub = min(cands[m]['published'] for m in mem)
                sid = 'n' + hashlib.md5(cands[mem[0]]['url'].encode()).hexdigest()[:10]
                ents = []
                for e in (p.get('entities') or [])[:3]:
                    if not isinstance(e, dict) or not e.get('name'): continue
                    t = (e.get('ticker') or '') or None
                    ents.append({'name': str(e['name'])[:60], 'ticker': t, **({'sym': sym[t.upper()]} if t and t.upper() in sym else {})})
                s = {'id': sid, 'headline': str(p['headline'])[:110], 'summary': str(p.get('summary', ''))[:400], 'why': str(p.get('why', ''))[:400],
                     'category': p['category'], 'importance': max(1, min(3, int(p.get('importance', 1)))), 'flag': None, 'market_moving': bool(p.get('market_moving')),
                     'location': {'place': str(p.get('place') or country)[:60], 'country': country, 'lat': round(lat, 3), 'lon': round(lon, 3), 'region': REGION.get(iso2, 'eu')},
                     'entities': ents, 'links': [], 'source': srcs[0], 'sources': srcs, 'published_at': pub, 'retrieved_at': ISO_NOW,
                     'official': any(cands[m]['kind'] == 'official' for m in mem), 'ai_summary': True}
                img = photo(p.get('photo'), sid) if s['importance'] >= 2 else None
                if img: s['image'] = img
                new.append(s); ids.append((s, p.get('leads_to')))
            except Exception as e:
                ids.append(None); err(f'story {k}: {e}')
        for x in ids:  # connections between the new stories
            if x and isinstance(x[1], int) and 0 <= x[1] < len(ids) and ids[x[1]] and ids[x[1]][0] is not x[0]: x[0]['links'] = [ids[x[1]][0]['id']]
    status['new_stories'] = len(new)
    stories = sorted(new + prev, key=lambda s: s['published_at'], reverse=True)[:MAX_STORIES]
    # flags, used sparingly: breaking = major and under 90 minutes old; trending = 4+ sources; market moving = flagged by the editor step
    for s in stories: s['flag'] = None
    age = lambda s: (NOW - datetime.fromisoformat(s['published_at'].replace('Z', '+00:00'))).total_seconds() / 60
    for s in [s for s in stories if s['importance'] == 3 and age(s) < 90][:2]: s['flag'] = 'breaking'
    for s in [s for s in stories if not s['flag'] and len(s.get('sources', [])) >= 4][:2]: s['flag'] = 'trending'
    for s in [s for s in stories if not s['flag'] and s.get('market_moving') and age(s) < 1440][:2]: s['flag'] = 'moving'
    if not stories:
        status['note'] = 'No stories yet: keeping the page on demo content'
    else:
        save(OUT, {'schema': 'investedia.globe.news/v1', 'demo': False, 'updated_at': ISO_NOW,
                   'notice': 'Headlines and short summaries written with AI from each source\'s own headline and description. Every story links to its original source. Not investment advice.',
                   'stories': stories})
    status['stories_online'] = len(stories)
    save(STATUS, status)
    log(json.dumps(status, indent=1))


if __name__ == '__main__':
    try: main()
    except Exception as e:
        err(f'fatal: {e}'); save(STATUS, status); sys.exit(0)  # never break the workflow: the previous news stays online
