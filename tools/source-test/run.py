"""48-hour SOURCE TEST (measurement only). Nothing here is published, ranked or written to the production feeds.
Each pass fetches the candidate feeds, records latency/failures, and for every item first seen during the test window records:
usefulness, duplicate of an existing Investedia story, novelty, event family, country, explicitly named verified assets and
whether any would draw a verified Globe line. Production stories come from origin/main (news-live, news-archive, event archive).
  python3 tools/source-test/run.py          one pass (hourly)
  python3 tools/source-test/report.py       summary + keep/reject"""
import html, json, os, re, subprocess, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import news_core as core, events as EV, registry as R

DATA = os.path.join(HERE, 'data')
NOISE = re.compile(r'\b(stock to buy|stocks to buy|price target|horoscope|celebrity|football|soccer)\b', re.I)  # same junk filter as update_globe_news.NOISE
START = '2026-10-30T07:27:00Z'  # test window start: the first pass (items published or first seen before it are backlog, not counted)
END = '2026-11-01T07:30:00Z'
UA = {'User-Agent': 'Mozilla/5.0 (Investedia source test; measurement only)'}
SOURCES = [
    {'id': 'pib', 'name': 'PIB India', 'country': 'India', 'url': 'https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3&reg=3'},
    {'id': 'eurostat-releases', 'name': 'Eurostat news releases', 'country': 'European Union',
     'url': 'https://ec.europa.eu/eurostat/en/search?p_p_id=estatsearchportlet_WAR_estatsearchportlet&p_p_lifecycle=2&p_p_state=maximized&p_p_mode=view&p_p_resource_id=atom&_estatsearchportlet_WAR_estatsearchportlet_collection=CAT_PREREL'},
    {'id': 'eurostat-news', 'name': 'Eurostat news', 'country': 'European Union',
     'url': 'https://ec.europa.eu/eurostat/en/search?p_p_id=estatsearchportlet_WAR_estatsearchportlet&p_p_lifecycle=2&p_p_state=maximized&p_p_mode=view&p_p_resource_id=atom&_estatsearchportlet_WAR_estatsearchportlet_collection=CAT_EURNEW'},
    {'id': 'ons', 'name': 'UK ONS releases', 'country': 'United Kingdom', 'url': 'https://www.ons.gov.uk/releasecalendar?rss'},
    {'id': 'statcan', 'name': 'Statistics Canada The Daily', 'country': 'Canada', 'url': 'https://www150.statcan.gc.ca/n1/rss/dai-quo/0-eng.atom'},
]
A = '{http://www.w3.org/2005/Atom}'

def iso(d): return d.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def fetch(src):
    t0 = time.time()
    try:
        raw = urllib.request.urlopen(urllib.request.Request(src['url'], headers=UA), timeout=40).read()
        ms = int((time.time() - t0) * 1000)
        root = ET.fromstring(raw.lstrip(b'\xef\xbb\xbf'))
        out = []
        for it in root.iter('item'):
            g = lambda k: (it.findtext(k) or '').strip()
            pub = None
            try: pub = iso(parsedate_to_datetime(g('pubDate'))) if g('pubDate') else None
            except Exception: pass
            out.append({'title': html.unescape(g('title')), 'url': g('link'), 'desc': re.sub(r'<[^>]+>', ' ', html.unescape(g('description')))[:300].strip(), 'published': pub})
        for e in root.iter(A + 'entry'):
            link = next((l.get('href') for l in e.findall(A + 'link') if l.get('rel', 'alternate') == 'alternate'), None) or (e.find(A + 'link').get('href') if e.find(A + 'link') is not None else '')
            title = ''.join(e.find(A + 'title').itertext()).strip() if e.find(A + 'title') is not None else ''
            summ = e.find(A + 'summary') if e.find(A + 'summary') is not None else e.find(A + 'content')
            pub = (e.findtext(A + 'published') or e.findtext(A + 'updated') or '').strip()
            try: pub = iso(datetime.fromisoformat(pub.replace('Z', '+00:00'))) if pub else None
            except Exception: pub = None
            out.append({'title': html.unescape(re.sub(r'\s+', ' ', title)), 'url': link, 'desc': re.sub(r'\s+', ' ', ''.join(summ.itertext()) if summ is not None else '')[:300].strip(), 'published': pub})
        return {'ok': True, 'ms': ms, 'items': out, 'http': 200}
    except urllib.error.HTTPError as e:
        return {'ok': False, 'ms': int((time.time() - t0) * 1000), 'items': [], 'http': e.code, 'error': str(e)[:120]}
    except Exception as e:
        return {'ok': False, 'ms': int((time.time() - t0) * 1000), 'items': [], 'http': None, 'error': str(e)[:120]}

def production():
    """Stories Investedia already has (origin/main): title, time, country, family, verified assets."""
    subprocess.run(['git', 'fetch', '-q', 'origin', 'main'], cwd=ROOT)
    show = lambda p: subprocess.run(['git', 'show', f'origin/main:{p}'], capture_output=True, text=True, cwd=ROOT).stdout
    out = {}
    for p in ('assets/globe/news-live.json', 'assets/globe/news-archive.json'):
        try:
            for s in json.loads(show(p)).get('stories', []):
                out[s['id']] = {'title': s['headline'], 'at': s['published_at'], 'country': (s.get('location') or {}).get('country'),
                                'urls': [core.canon(x.get('url', '')) for x in s.get('sources', [])]}
        except Exception: pass
    names = subprocess.run(['git', 'ls-tree', '--name-only', 'origin/main', 'assets/globe/events/'], capture_output=True, text=True, cwd=ROOT).stdout.split()
    for p in names[-4:]:
        try:
            for e in json.loads(show(p)).get('events', []):
                out.setdefault(e['id'], {'title': e['title'], 'at': e['at'], 'country': (e.get('loc') or {}).get('country'), 'urls': [core.canon(e.get('url') or '')]})
        except Exception: pass
    return list(out.values())

REG = R.get()
def explicit_assets(text):
    """Verified assets NAMED in the text (no inference: an asset counts only if the release itself names it)."""
    words = re.findall(r"[A-Za-z0-9&'.-]+", text or '')
    found = {}
    for n in range(5, 0, -1):
        for i in range(len(words) - n + 1):
            ph = ' '.join(words[i:i + n])
            nxt = words[i + n].lower() if i + n < len(words) else ''
            if nxt in ('area', 'zone', 'region', 'regions', 'countries', 'member', 'medal', 'standard'): continue  # "euro area" is not the euro
            r = REG._by_name(ph, 'asset', None)
            if r.get('id') and len(R.name_key(ph)) >= 4: found[r['id']] = ph
    return found

STAT = re.compile(r'\b(gdp|inflation|consumer price|producer price|price index|prices|employment|unemployment|jobs?|payroll|labour|labor|wages?|earnings|'
                  r'trade|exports?|imports?|retail|production|output|manufacturing|construction|housing|deficit|debt|government finance|balance of payments|'
                  r'current account|investment|business|sales|turnover|income|household|consumption|economic activity)\b', re.I)
DATEWORDS = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'quarter',
             'quarterly', 'first', 'second', 'third', 'fourth', 'year', 'annual', 'monthly', 'weekly', 'week', 'provisional', 'estimates', 'statistics'}
def keywords(t): return {w for w in core.norm(t) if not w.isdigit() and w not in DATEWORDS}
def family(src, t):
    """events.family for news; for statistical releases, a data release about the economy is macro-data."""
    if src['id'] != 'pib' and STAT.search(t): return 'macro-data'
    return EV.family(t)

def analyse(src, it, prod, now):
    t = it['title']; text = f"{t} {it.get('desc', '')}"
    at = it.get('published') or iso(now)
    tt = datetime.fromisoformat(at.replace('Z', '+00:00'))
    near = [p for p in prod if abs((datetime.fromisoformat(p['at'].replace('Z', '+00:00')) - tt).total_seconds()) < 72 * 3600]
    dup = next((p['title'] for p in near if core.canon(it['url']) in p['urls'] or core.same_event(t, p['title'], abs((datetime.fromisoformat(p['at'].replace('Z', '+00:00')) - tt).total_seconds()) / 3600)), None)
    # covered: an existing story within 48 h about the same country sharing 3+ distinctive title words (same news, other wording)
    tw = keywords(t)
    cov = dup or next((p['title'] for p in near if abs((datetime.fromisoformat(p['at'].replace('Z', '+00:00')) - tt).total_seconds()) < 48 * 3600
                       and p.get('country') == src['country'] and len(tw & keywords(p['title'])) >= 3), None)
    fam = family(src, t)
    # useful = about the economy/markets/business, judged on the TITLE (descriptions of official releases mention "economic" boilerplate)
    useful = bool(not NOISE.search(t) and (core.MACRO.search(t) or core.RELEVANT.search(t) or core.EXPOSURE.search(t) or fam not in ('other',)))
    assets = explicit_assets(text)
    return {'source': src['id'], 'title': t, 'url': it['url'], 'published': it.get('published'), 'first_seen': iso(now),
            'latency_min': round((now - datetime.fromisoformat(it['published'].replace('Z', '+00:00'))).total_seconds() / 60) if it.get('published') else None,
            'country': src['country'], 'family': fam, 'useful': useful, 'duplicate_of': dup, 'covered_by': cov,
            'novel': bool(useful and not cov), 'macro_headline': bool(core.MACRO.search(t)), 'assets': sorted(assets), 'drawable': [a for a in assets if REG.drawable(a)],
            'english': t.isascii() or bool(re.search(r'[A-Za-z]{4,}', t))}

def main():
    os.makedirs(DATA, exist_ok=True)
    now = datetime.now(timezone.utc)
    if iso(now) > END: print('test window over'); return
    seen_p = os.path.join(DATA, 'seen.json')
    seen = json.load(open(seen_p)) if os.path.exists(seen_p) else {}
    prod = production()
    runs, items = [], []
    for src in SOURCES:
        r = fetch(src)
        runs.append({'at': iso(now), 'source': src['id'], 'ok': r['ok'], 'http': r.get('http'), 'ms': r['ms'], 'n': len(r['items']), 'error': r.get('error')})
        for it in r['items']:
            k = src['id'] + '|' + core.canon(it['url'] or it['title'])
            if k in seen: continue
            backlog = (it.get('published') or iso(now)) < START or not seen.get('_started_' + src['id'])
            seen[k] = iso(now)
            if backlog and not (it.get('published') and it['published'] >= START): continue  # first pass / pre-window items are not counted
            items.append(analyse(src, it, prod, now))
        seen['_started_' + src['id']] = seen.get('_started_' + src['id']) or iso(now)
    with open(os.path.join(DATA, 'runs.jsonl'), 'a') as f:
        for r in runs: f.write(json.dumps(r) + '\n')
    with open(os.path.join(DATA, 'items.jsonl'), 'a') as f:
        for i in items: f.write(json.dumps(i, ensure_ascii=False) + '\n')
    json.dump(seen, open(seen_p, 'w'))
    print(iso(now), {r['source']: (r['ok'], r['n'], r['ms']) for r in runs}, len(items), 'new items;', len(prod), 'production stories compared')

if __name__ == '__main__':
    main()
