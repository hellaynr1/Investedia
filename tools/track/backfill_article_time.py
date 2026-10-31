"""One-off (2026-10-31): give every live ledger call its article's original publish time ('art'), as the robot now stores at freeze.
Source: the first committed news file that contained the call (tools/track/git_proof.py), so the time is the article's original one,
not the archive's, which moves when sources merge. Only adds 'art' where it is missing; prediction and outcome fields are untouched.
Usage: python3 tools/track/git_proof.py /tmp/proof.json && python3 tools/track/backfill_article_time.py /tmp/proof.json"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
first = {}
for x in sorted(json.load(open(sys.argv[1]))['stamped'], key=lambda y: y['first_seen']):
    if x.get('t'): first.setdefault(x['story'], x['t'])
for path in (os.path.join(ROOT, 'assets', 'globe', 'news-ledger.json'), os.path.join(ROOT, 'docs', 'assets', 'globe', 'news-ledger.json')):
    L = json.load(open(path)); n = 0
    for c in L['calls']:
        if not c.get('legacy') and not c.get('art') and c['id'] in first: c['art'] = first[c['id']]; n += 1
    json.dump(L, open(path, 'w'), separators=(',', ':')); print(os.path.relpath(path, ROOT), 'article times added', n)
