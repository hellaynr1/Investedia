"""One-off ledger migration to outcome-v2 (approved 2026-10-31). Idempotent: running it twice changes nothing.
1. Proof time: every live call gets 'public' (first provable public appearance: the first git commit of a published news file that
   contains it) and 'start' = max(created, public). Nothing is scored from an earlier time than we can prove.
2. Outcomes are re-judged under outcome-v2; an earlier verdict is kept under 'prev' for audit.
3. Wrong-asset call: the Colombian peso call frozen as COP (ConocoPhillips) by old ticker aliasing is voided, never deleted.
4. Recovery: valid calls that git proves existed but that were never frozen (their article left the live feed first) are added with
   provenance (recovered: true). Calls whose ticker failed the registry are added only when the identity is verified (registry_repair).
5. The older pre-stamping implications go to data/research/pre-live-implications.json: research data, never the Live Track Record.
Usage: python3 tools/track/git_proof.py /tmp/proof.json && python3 tools/track/migrate_outcome_v2.py /tmp/proof.json"""
import json, os, sys, collections
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
import registry
P = lambda s: datetime.fromisoformat(str(s).replace('Z', '+00:00')).astimezone(timezone.utc)
F = lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')
NOW = datetime.now(timezone.utc)
# verified identity repairs (checked 2026-10-31 against the registry and the exchange listing)
REPAIR = {'CAPP.PA': ('CAP.PA', 'EQ:XPAR:CAP', 'Capgemini SE', 'CAPP.PA is not a listed symbol; exact registry name match Capgemini -> CAP.PA (Euronext Paris)'),
          'ACBR.AT': ('ALPHA.AT', 'EQ:XATH:ALPHA', 'Alpha Bank S.A.', 'ACBR.AT is a retired symbol; exact registry name match Alpha Bank -> ALPHA.AT (Athens)'),
          'SEPL.LG': ('SEPL.L', 'EQ:XLON:SEPL', 'Seplat Energy Plc', 'no Lagos (NGX) price source exists; the same company is listed in London as SEPL.L')}
WRONG = {('n79d61700bb', 'COP'): 'wrong asset: the article implied the Colombian peso (COP=X); old ticker aliasing priced ConocoPhillips (COP)'}
OUTCOME = ('move', 'base', 'end', 'judged', 'why')


def main(proof_path):
    R = registry.get()
    proof = json.load(open(proof_path))
    groups = collections.defaultdict(list)
    for x in proof['stamped']:
        if x.get('scorable') and x.get('sym'): groups[(x['story'], x['sym'])].append(x)
    first = {k: min(v, key=lambda y: y['first_seen']) for k, v in groups.items()}
    for path in (os.path.join(ROOT, 'assets', 'globe', 'news-ledger.json'), os.path.join(ROOT, 'docs', 'assets', 'globe', 'news-ledger.json')):
        L = json.load(open(path)); calls = L['calls']; have = {(c['id'], c.get('raw_sym', c['sym'])) for c in calls}
        for c in calls:
            if c.get('legacy') or c.get('rule') == 'outcome-v2': continue
            g = first.get((c['id'], c['sym']))
            public = P(g['first_seen']) if g else P(c.get('frozen') or c['created'])  # no git copy yet: the committed ledger itself is the proof
            c['public'] = F(max(public, P(c['created']))); c['start'] = F(max(P(c['created']), public))
            if g: c['proof'] = {'commit': g['commit'][:12], 'file': os.path.basename(g['file'])}
            if c.get('res') != 'pending':
                c['prev'] = {k: c[k] for k in ('res',) + OUTCOME if k in c}; c['prev']['rule'] = 'outcome-v1'
                for k in OUTCOME: c.pop(k, None)
                c['res'] = 'pending'
            c['rule'] = 'outcome-v2'
            if (c['id'], c['sym']) in WRONG:
                c.update(res='void', why=WRONG[(c['id'], c['sym'])], judged=F(NOW))
        for (story, sym), g in sorted(first.items(), key=lambda kv: kv[1]['created']):
            if (story, sym) in have: continue
            if (NOW - P(g['first_seen'])).total_seconds() < 2 * 3600: continue  # recent: the ledger robot freezes it on its next run
            rep = REPAIR.get(sym)
            aid = g.get('asset_id') or (R.ids_for_ticker(sym) or [None])[0]
            if not aid and not rep: continue  # identity not verified: stays excluded
            px, aid, name, why = (rep[0], rep[1], rep[2], rep[3]) if rep else (sym, aid, None, None)
            created = P(g['created']); public = max(P(g['first_seen']), created)
            calls.append({'id': story, 'sym': px, 'aid': aid, 'name': (name or (R.assets.get(aid) or {}).get('name') or sym)[:60], 'dir': g['dir'], 'conf': g.get('conf'),
                          'created': g['created'], 'ver': g.get('ver'), 'pub': int(created.timestamp() // 60), 'res': 'pending', 'frozen': F(NOW),
                          'public': F(public), 'start': F(public), 'rule': 'outcome-v2', 'cat': g.get('fam'), 'h': str(g.get('h') or '')[:140],
                          'recovered': True, 'recovery': {'at': F(NOW), 'commit': g['commit'][:12], 'file': os.path.basename(g['file']),
                          'reason': 'git proves the call was public before its outcome; never frozen because the article left the live feed first'},
                          **({'raw_sym': sym, 'registry_repair': why} if rep else {})})
        L['outcome_rule'] = {'id': 'outcome-v2', 'since': '2026-10-31', 'start': 'max(created_at, first provable public time)',
                             'baseline': 'prevailing traded price at start (exchange session bars)', 'end': 'first traded price >= 24 h after start, within 4 calendar days, else unresolved',
                             'flat_pct': 0.3}
        with open(path, 'w', encoding='utf-8') as f: json.dump(L, f, separators=(',', ':'))
    # research set: implications from before creation stamping (existence proven by git, never frozen calls)
    rs = [dict(x, asset_id=(R.ids_for_ticker(x['sym']) or [None])[0], commit=x['commit'][:12]) for x in proof['unstamped'] if x.get('sym') and R.ids_for_ticker(x['sym'])]
    json.dump({'note': 'Research data for the Historical Prediction Track Record and Prediction Engine development. NOT live calls: these implications were '
                       'written before creation stamping (no frozen version/confidence; some were added to older articles). first_seen = first commit that '
                       'contains them. Never mix with the Live Track Record.', 'built': F(NOW), 'items': rs},
              open(os.path.join(ROOT, 'data', 'research', 'pre-live-implications.json'), 'w'), separators=(',', ':'))
    print('ledger calls', len(calls), 'research items', len(rs))


if __name__ == '__main__':
    main(sys.argv[1])
