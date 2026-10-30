"""Stamp the current feed files with canonical assets (run once at merge time, so the Globe has verified lines before the next robot run).
Only resolution metadata is added (asset / unresolved); no implication is changed.  python3 tools/registry/stamp_feeds.py"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import registry as R, news_core as core

for name in ('news-live.json', 'news-archive.json'):
    for d in ('assets/globe', 'docs/assets/globe'):
        p = os.path.join(ROOT, d, name)
        if not os.path.exists(p): continue
        with open(p, encoding='utf-8') as f: obj = json.load(f)
        n = 0
        for s in obj.get('stories', []):
            for row in s.get('impacts') or []: R.stamp(row); n += 1
            for row in s.get('entities') or []: row.setdefault('kind', 'company'); R.stamp(row); n += 1
        core.atomic_write(p, obj, core.validate_feed)
        print(p, n, 'rows stamped')
