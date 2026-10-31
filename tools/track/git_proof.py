"""Proof of when each implication was first public: scans every committed version of the published news files and records, per
(story, asset), the first commit that contains it. Usage: python3 tools/track/git_proof.py out.json"""
import json, os, subprocess, collections, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
files = ['docs/assets/globe/news-live.json', 'docs/assets/globe/news-archive.json']
revs = []
for f in files:
    out = subprocess.run(['git', '-C', REPO, 'log', '--reverse', '--format=%H %cI', '--', f], capture_output=True, text=True).stdout.split('\n')
    revs += [(l.split()[1], l.split()[0], f) for l in out if l.strip()]
revs.sort()
p = subprocess.Popen(['git', '-C', REPO, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
def blob(rev, f):
    p.stdin.write(f'{rev}:{f}\n'.encode()); p.stdin.flush()
    h = p.stdout.readline().split()
    if len(h) < 3: return None
    data = p.stdout.read(int(h[2])); p.stdout.read(1); return data
seen = {}; unstamped = {}
for ct, rev, f in revs:
    raw = blob(rev, f)
    if not raw: continue
    try: d = json.loads(raw)
    except Exception: continue
    for s in d.get('stories') or []:
        for i in s.get('impacts') or []:
            if i.get('direction') not in ('up', 'down'): continue
            a = i.get('asset') or {}
            sym = (a.get('px') or i.get('ticker') or '').upper() or None
            k = (s.get('id'), (a.get('id') or sym or i.get('name')))
            if i.get('created_at'):
                if k not in seen:
                    seen[k] = dict(story=s.get('id'), h=s.get('headline'), t=s.get('t') or s.get('published_at'), created=i['created_at'], first_seen=ct, commit=rev, file=f,
                                   scorable=i.get('scorable'), ver=i.get('version'), conf=i.get('confidence'), dir=i['direction'], sym=sym,
                                   asset_id=a.get('id'), unresolved=i.get('unresolved'), kind=i.get('kind'), role=i.get('role'), fam=s.get('family') or s.get('category'))
            elif k not in unstamped:
                unstamped[k] = dict(story=s.get('id'), first_seen=ct, commit=rev, h=s.get('headline'), name=i.get('name'), kind=i.get('kind'), why=i.get('why'), sym=sym, dir=i['direction'])
json.dump({'stamped': list(seen.values()), 'unstamped': list(unstamped.values()), 'revs': len(revs)}, open(sys.argv[1], 'w'))
print('revisions', len(revs), 'stamped', len(seen), 'unstamped', len(unstamped))
