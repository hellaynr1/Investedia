"""Stable event identity for news stories (the archive's `cluster` field).

A new story either joins an open event (an earlier story about the SAME specific incident) or starts its own; the event id is the id of the
event's first story, written once and never recomputed, so a rebuild cannot regroup anything. Used for presentation (one card per event);
the call ledger and Track Record statistics never read it.

Rules (all must hold; the model is only asked when code finds candidates):
- candidate events: published in the 72 hours before the story, same event family (events.family), at least one shared registry asset id;
- Gemini then answers per story: the number of the candidate that is the same specific occurrence (the same hack, earnings release, deal,
  decision...), or null. Follow-ups of that occurrence count as the same; another occurrence involving the same company does not. Unsure = null;
- the answer is accepted only if it names one of that story's own candidates. Failure of any step = the story starts its own event.
"""
from datetime import datetime, timedelta
import json

import events as EV

WINDOW = timedelta(hours=72)

PROMPT = """You group financial news stories into events. For each NEW story below, decide whether it reports the SAME specific occurrence as one
of its numbered candidate events: the same hack, the same earnings release, the same deal, the same court ruling, the same policy decision,
the same outage. Follow-ups and new developments of that same occurrence count as the same event. A DIFFERENT occurrence involving the same
company or asset (another quarter's results, another deal, another lawsuit, a separate incident) is NOT the same event. Sharing a company,
a sector or a market move is not enough. If you are not sure, answer null.

Return ONLY a JSON array: [{{"story": <story number>, "event": <candidate number or null>, "why": "<max 15 words>"}}] with one object per new story.

New stories and their candidates:
{items}"""


def _t(s):
    return datetime.fromisoformat(str(s).replace('Z', '+00:00'))


def asset_ids(rec):
    """Registry asset ids of an archive record (record['assets'][].id) or of a story (impacts/entities[].asset.id)."""
    if 'assets' in rec and isinstance(rec['assets'], list):
        return {a['id'] for a in rec['assets'] if a.get('id')}
    return {((r or {}).get('asset') or {}).get('id') for r in (rec.get('impacts') or []) + (rec.get('entities') or [])} - {None}


def _key(rec):
    """(id, time, family, assets, title) for an archive record or a story."""
    if 'at' in rec:
        return rec['id'], _t(rec['at']), rec.get('fam'), asset_ids(rec), rec.get('title') or ''
    return rec['id'], _t(rec['published_at']), EV.family(rec.get('headline'), rec.get('category'), rec.get('event_type')), asset_ids(rec), rec.get('headline') or ''


def candidates(story, pool):
    """Events (one per cluster, newest member shown) a story may belong to: earlier, within 72 h, same family, a shared registry asset."""
    sid, st, fam, ids, _ = _key(story)
    if not ids or not fam or fam == 'other':
        return []
    by = {}
    for r in pool:
        rid, rt, rfam, rids, title = _key(r)
        if rid == sid or rfam != fam or not (ids & rids) or not (st - WINDOW <= rt <= st):
            continue
        c = r.get('cluster') or rid
        e = by.setdefault(c, {'cluster': c, 'titles': [], 'last': rt, 'n': 0})
        e['n'] += 1; e['titles'].append((rt, title)); e['last'] = max(e['last'], rt)
    out = sorted(by.values(), key=lambda e: (-e['last'].timestamp(), e['cluster']))[:6]  # deterministic order
    for e in out:
        e['titles'] = [t for _, t in sorted(e['titles'], key=lambda x: x[0])][-3:]
    return out


def assign(stories, pool, ask):
    """Sets story['cluster'] (and 'cluster_why' when joined) for each new story, oldest first; earlier new stories join the pool.
    ask(prompt) -> parsed JSON. Returns {'asked': n_with_candidates, 'joined': n}."""
    pool = list(pool); todo = []
    for s in sorted(stories, key=lambda s: (s['published_at'], s['id'])):
        if s.get('cluster'):
            pool.append(s); continue
        cs = candidates(s, pool)
        if cs: todo.append((s, cs))
        s['cluster'] = s['id']  # default: its own event (replaced below only by a valid answer)
        pool.append(s)
    if not todo:
        return {'asked': 0, 'joined': 0}
    items = []
    for k, (s, cs) in enumerate(todo, 1):
        items.append(f"Story {k} ({s['published_at'][:16]}Z): {s.get('headline')} — {(s.get('summary') or '')[:200]}")
        for j, e in enumerate(cs, 1):
            items.append(f"  candidate {j} ({e['n']} article{'s' if e['n'] > 1 else ''}, latest {e['last']:%Y-%m-%d %H:%M}Z): " + ' | '.join(e['titles']))
    try:
        ans = ask(PROMPT.format(items='\n'.join(items)))
    except Exception:
        return {'asked': len(todo), 'joined': 0, 'error': True}
    joined = 0
    for a in ans if isinstance(ans, list) else []:
        try:
            k, j = int(a.get('story')), a.get('event')
            if j is None or not (1 <= k <= len(todo)): continue
            s, cs = todo[k - 1]; j = int(j)
            if 1 <= j <= len(cs):
                s['cluster'] = cs[j - 1]['cluster']; s['cluster_why'] = str(a.get('why') or '')[:120]; joined += 1
        except Exception:
            continue
    # a story that others joined keeps pointing at the root event (no chains)
    root = {s['id']: s['cluster'] for s, _ in todo}
    for s, _ in todo:
        while root.get(s['cluster'], s['cluster']) != s['cluster']: s['cluster'] = root[s['cluster']]
    return {'asked': len(todo), 'joined': joined}
