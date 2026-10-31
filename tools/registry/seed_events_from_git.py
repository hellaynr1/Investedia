"""One-time seed of the event archive (assets/globe/events/) from git history: every story that was ever in news-live.json or
news-archive.json (the 160/600 caps dropped most of them from the files, not from git). The richest copy of each story is kept,
resolved through the canonical registry and written as normalised metadata (no article text).
  python3 tools/registry/seed_events_from_git.py [--ref origin/main] [--dump stories.json]"""
import argparse, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import registry as R, events as E

def history(ref):
    out = {}
    for f in ('assets/globe/news-archive.json', 'assets/globe/news-live.json'):
        for h in subprocess.run(['git', 'log', ref, '--format=%H', '--', f], capture_output=True, text=True, cwd=ROOT).stdout.split():
            try: d = json.loads(subprocess.run(['git', 'show', f'{h}:{f}'], capture_output=True, text=True, cwd=ROOT).stdout)
            except Exception: continue
            for s in d.get('stories', []):
                if s.get('demo') or not s.get('id') or not s.get('published_at'): continue
                o = out.get(s['id'])
                if not o or len(json.dumps(s)) >= len(json.dumps(o)): out[s['id']] = s
    return list(out.values())

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--ref', default='origin/main'); ap.add_argument('--dump'); a = ap.parse_args()
    st = history(a.ref)
    reg = R.get()
    for s in st:
        for row in s.get('impacts') or []: R.stamp(row, reg)
        for row in s.get('entities') or []: row.setdefault('kind', 'company'); R.stamp(row, reg)
    if a.dump: json.dump(st, open(a.dump, 'w'), ensure_ascii=False)
    print(len(st), 'stories;', E.upsert(st), 'event records written;', E.write_threads(30, reg=reg), 'story threads (last 30 days)')
