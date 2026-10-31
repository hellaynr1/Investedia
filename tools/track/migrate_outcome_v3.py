"""One-off move of the live ledger to outcome-v3 (approved 2026-10-31; see research/LIVE-OUTCOME-RULES.md). Idempotent.
outcome-v3 changes the entry: the first traded price AT OR AFTER the call's proven public time (v2 used the last price before it, which could
credit an overnight move that happened before publication). One live record uses one rule, so v3 re-scores every live call: an earlier v2
verdict is kept under 'prev_v2'; prediction fields (direction, asset, times, version, confidence) are never touched. The wrong-asset void stays.
python3 tools/track/migrate_outcome_v3.py && (the next robot run, or update_news_track.judge) re-judges the reset calls."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = ('move', 'base', 'end', 'judged', 'why', 'mkt')
for path in (os.path.join(ROOT, 'assets', 'globe', 'news-ledger.json'), os.path.join(ROOT, 'docs', 'assets', 'globe', 'news-ledger.json')):
    L = json.load(open(path)); n = 0
    for c in L['calls']:
        if c.get('legacy') or c.get('rule') == 'outcome-v3': continue
        if c.get('res') == 'void' and 'wrong asset' in (c.get('why') or ''): c['rule'] = 'outcome-v3'; continue
        if c.get('res') != 'pending':
            c['prev_v2'] = {k: c[k] for k in ('res',) + OUT if k in c}; c['prev_v2']['rule'] = c.get('rule', 'outcome-v2')
            for k in OUT: c.pop(k, None)
            c['res'] = 'pending'; n += 1
        c['rule'] = 'outcome-v3'
    L['outcome_rule'] = {'id': 'outcome-v3', 'since': '2026-10-31', 'start': 'max(created_at, first provable public time)',
                         'entry': 'first traded price at or after start (exchange session bars); nothing before publication is credited',
                         'end': 'first traded price >= 24 h after the entry, within 4 calendar days, else unresolved', 'flat_pct': 0.3,
                         'benchmark': 'market index move over the same window (mkt), where a relevant index exists',
                         'history': 'outcome-v1 (2026-10-29): first recorded price after creation; outcome-v2 (2026-10-31 09:16 UTC): prevailing price at start'}
    json.dump(L, open(path, 'w'), separators=(',', ':')); print(os.path.relpath(path, ROOT), 'reset for re-scoring:', n)
