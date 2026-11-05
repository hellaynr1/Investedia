"""Per-asset news index for asset charts: the last 35 days of the event archive (assets/globe/events/*.json), keyed by ticker.
Writes assets/globe/asset-news.json. Small and static, so the asset sheet can place older articles on Week/Month charts."""
import json, glob, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, 'assets', 'globe')
def main():
    cut = time.strftime('%Y-%m-%d', time.gmtime(time.time() - 35 * 86400)); by = {}
    for f in sorted(glob.glob(os.path.join(G, 'events', '*.json'))):
        if os.path.basename(f)[:10] < cut: continue
        try: evs = json.load(open(f)).get('events', [])
        except Exception: continue
        for e in evs:
            for a in e.get('assets') or []:
                t = str(a.get('t') or '').upper()
                if not t or not e.get('at') or not e.get('title'): continue
                by.setdefault(t, {})[e['id']] = {'id': e['id'], 'at': e['at'], 'h': e['title'], 'src': e.get('src') or '', 'url': e.get('url') or '', 'dir': a.get('dir') or '', 'fam': e.get('fam') or ''}
    try: m = json.load(open(os.path.join(G, 'markets.json'))); tracked = {x['s'].upper() for x in m.get('assets', [])}
    except Exception: tracked = set(by)
    out = {t: sorted(v.values(), key=lambda x: x['at'], reverse=True)[:25] for t, v in by.items() if t in tracked}
    json.dump({'schema': 1, 'since': cut, 'by': out}, open(os.path.join(G, 'asset-news.json'), 'w'), separators=(',', ':'))
    print(len(out), 'assets')
if __name__ == '__main__': main()
