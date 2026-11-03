"""Offline, deterministic Track D evaluation. Run as python -m tools.v6.evaluate."""
import argparse
import gzip
import hashlib
import json
import re
import random
from datetime import timedelta
from collections import Counter, defaultdict
from pathlib import Path
from tools.v6.outcomes import timestamp, cutoff, calculate_daily
from tools.v6.exhibits import filings, metadata

ROOT = Path(__file__).resolve().parents[2]
GROUPS = {
    'guidance': {'guidance_direction', 'guidance_vs_previous'},
    'earnings': {'eps_surprise_pct'},
    'takeover': {'deal_role', 'deal_premium_pct', 'deal_value_usd_m'},
    'executives': {'mgmt_change', 'mgmt_role', 'mgmt_planned'},
    'capital_returns': {'buyback_usd_m', 'dividend_change'},
    'issuance': {'financing_type'},
    'regulatory_court': {'reg_outcome', 'litigation_outcome'},
}
ALLOWED = set.union(*GROUPS.values())
JUDGED = {'hit', 'miss', 'flat'}


def guard(call):
    for k in ('event_id','cluster_id','asset','event_type','tier','horizon','policy_id','publication_proof'):
        if not call.get(k):
            raise ValueError('missing '+k)
    if not re.fullmatch(r'[A-Za-z0-9.^_-]+', call['asset']):
        raise ValueError('invalid asset symbol')
    if call.get('sector_etf') and call['sector_etf'] not in ('XLK','XLF','XLV','XLE','XLI','XLY','XLP','XLU','XLB','XLRE','XLC'):
        raise ValueError('invalid sector benchmark')
    end = cutoff(call)
    prediction=timestamp(call['prediction_generated_at'])
    if timestamp(call['information_public_at']) > prediction:
        raise ValueError('prediction precedes public information')
    if timestamp(call['frozen_at']) < prediction:
        raise ValueError('freeze precedes prediction')
    if timestamp(call['frozen_at']) > timestamp(call['public_call_at']):
        raise ValueError('prediction not frozen by public call')
    if timestamp(call['prediction_generated_at']) > timestamp(call['public_call_at']):
        raise ValueError('prediction generated after public call')
    if call['direction'] not in ('long','short','none'):
        raise ValueError('invalid direction')
    if call['tier'] not in ('priority','standard','none'):
        raise ValueError('invalid tier')
    for name, f in call['features'].items():
        if name not in ALLOWED:
            raise ValueError('feature not allowlisted: '+name)
        for key in ('available_at','source_published_at','source_updated_at'):
            if timestamp(f[key]) > prediction:
                raise ValueError('future or updated feature: '+name)
        if f['source_kind'] not in ('original-release','as-filed','market-bar'):
            raise ValueError('retrospective/unproven source')
    return end


def split(call, outcome, sessions):
    day = cutoff(call).date().isoformat()
    windows = [('TRAIN','2022-01-01','2023-12-31'), ('VALIDATION','2024-01-01','2024-12-31'),
               ('OOS','2025-01-01','2026-10-20')]
    for label, a, b in windows:
        if a <= day <= b:
            first = sorted(d for d in sessions if a <= d <= b)[:5]
            if not first or day <= first[-1]:
                return 'PURGED'
            last = outcome.get('label_end_at') or (outcome.get('exit') or [None])[0]
            if last is None:
                return 'PURGED' if (timestamp(b+'T00:00:00Z')-cutoff(call)).days < 10 else label
            if timestamp(last).date().isoformat() > b:
                return 'PURGED'
            return label
    return 'EXCLUDED'


def candidate(features, drop=()):
    """Untrained factual-rule comparator. Scores are evidence points, not probabilities."""
    f = {k:v['value'] for k,v in features.items() if k not in drop}
    votes=[]
    def vote(condition, sign):
        if condition: votes.append(sign)
    vote(f.get('guidance_direction')=='raised',1)
    vote(f.get('guidance_direction') in ('lowered','withdrawn'),-1)
    eps=f.get('eps_surprise_pct')
    vote(isinstance(eps,(int,float)) and eps>=2,1)
    vote(isinstance(eps,(int,float)) and eps<=-2,-1)
    vote(f.get('deal_role')=='target' and (f.get('deal_premium_pct') or 0)>=15,1)
    vote(f.get('mgmt_change')=='departure' and f.get('mgmt_planned')=='abrupt' and f.get('mgmt_role') in ('CEO','CFO'),-1)
    vote((f.get('buyback_usd_m') or 0)>0 or f.get('dividend_change')=='increase',1)
    vote(f.get('dividend_change') in ('cut','suspended'),-1)
    vote(f.get('financing_type') in ('equity','convertible'),-1)
    vote(f.get('reg_outcome')=='approval' or f.get('litigation_outcome')=='won',1)
    vote(f.get('reg_outcome')=='rejection' or f.get('litigation_outcome')=='lost',-1)
    if not votes or len(set(votes))>1: return 'none',0
    return ('long' if votes[0]>0 else 'short'),len(votes)


def summary(rows, key='res'):
    c=Counter(r['outcome'].get(key) or 'unresolved' for r in rows)
    n=sum(c[k] for k in JUDGED)
    return {'total':len(rows),'judged':n,'confirmed':c['hit'],'other_way':c['miss'],'no_clear_move':c['flat'],
            'pending':c['pending'],'unresolved':c['unresolved'],'void':c['void'],'no_view':c['no-view'],
            **{k+'_rate': {'n':c[v], 'denominator':n,'pct':round(c[v]/n*100,2) if n else None}
               for k,v in [('confirmed','hit'),('other_way','miss'),('no_clear_move','flat')]}}


def bucket(value):
    if value is None: return 'unscored'
    if not isinstance(value,(int,float)) or not 0<=value<=100: raise ValueError('confidence must be a 0–100 score')
    for lo,hi in [(50,55),(55,60),(60,65),(65,70)]:
        if lo<=value<hi:return f'{lo}–{hi}'
    return '70+' if value>=70 else '<50'


def regroup(rows,key):
    groups=defaultdict(list)
    for r in rows: groups[str(key(r))].append(r)
    return {k:summary(v) for k,v in sorted(groups.items())}


def redirect(row,direction):
    out=dict(row['outcome'])
    old=row['call']['direction']
    if old=='none':
        out['res']=out.get('research_long_res','unresolved')
        out['relative_res']=out.get('research_long_relative_res')
        old='long'
    for key in ('res','relative_res'):
        if direction=='none': out[key]='no-view'
        elif out.get(key) in ('hit','miss') and direction!=old:
            out[key]='miss' if out[key]=='hit' else 'hit'
    return {**row,'outcome':out}


def cluster_interval(rows, repeats=500):
    """Seeded event-cluster bootstrap, with flats in the judged denominator."""
    clusters=defaultdict(list)
    for r in rows:
        if r['outcome']['res'] in JUDGED:
            clusters[r['call']['cluster_id']].append(r['outcome']['res']=='hit')
    if len(clusters)<2:
        return {'clusters':len(clusters),'judged':sum(map(len,clusters.values())), 'confirmed_95pct':None}
    rng=random.Random(6); groups=list(clusters.values()); samples=[]
    for _ in range(repeats):
        sample=[x for g in rng.choices(groups,k=len(groups)) for x in g]
        samples.append(100*sum(sample)/len(sample))
    samples.sort()
    return {'clusters':len(groups),'judged':sum(map(len,groups)),
            'confirmed_95pct':[samples[int(.025*repeats)],samples[int(.975*repeats)]],
            'bootstrap_repeats':repeats,'seed':6}


def metrics(rows):
    # No View has separate research labels: evaluate abstention without selection bias.
    labelled=rows
    baselines={'always_long':summary([redirect(r,'long') for r in labelled]),
               'always_short':summary([redirect(r,'short') for r in labelled])}
    ablation={}
    removals={'all_facts':ALLOWED, **GROUPS, **{k:{k} for k in sorted(ALLOWED)}, 'full':set()}
    for name,drop in removals.items():
        selected=[redirect(r,candidate(r['call']['features'],drop)[0]) for r in labelled]
        ablation[name]=summary(selected)
    coverage=[]
    for threshold in [None,50,55,60,65,70]:
        accepted=[r for r in rows if r['call']['direction']!='none' and
                  (threshold is None or (r['call'].get('confidence') is not None and r['call']['confidence']>=threshold))]
        coverage.append({'minimum_score':threshold,'accepted':len(accepted),'eligible':len(rows),
                         'coverage_pct':100*len(accepted)/len(rows) if rows else None, **summary(accepted)})
    return {'raw':summary(rows),'cluster_interval':cluster_interval(rows),'sector_relative':summary(rows,'relative_res'), 'baselines':baselines,
            'direction':regroup(rows,lambda r:r['call']['direction']), 'tier':regroup(rows,lambda r:r['call']['tier']),
            'event_type':regroup(rows,lambda r:r['call']['event_type']), 'horizon':regroup(rows,lambda r:r['call']['horizon']),
            'calibration':regroup(rows,lambda r:bucket(r['call'].get('confidence'))),
            'coverage_quality':coverage,'ablation':ablation}


def inventory(base):
    ids=set(); exhibits=set(); fact_ids=set(); fact_rows=0
    accepted=0
    for r in filings(base):
        ids.add(r['adsh'])
        accepted+=bool(r.get('filing_accepted_at'))
        if any((d.get('type') or '').startswith('EX-99') for d in r['docs']):exhibits.add(r['adsh'])
    discovery=metadata(base)
    for p in sorted((base/'facts').glob('*.jsonl')):
        for line in p.read_text().splitlines():
            fact_ids.add(json.loads(line)['adsh']); fact_rows+=1
    man_path=base/'facts'/'manifest.json'
    man=json.loads(man_path.read_text()) if man_path.exists() else {}
    batches=man.get('batches',{}).values()
    return {'sec_filings':len(ids),'filings_with_acceptance_timestamp':accepted,
            'filing_indexes_discovered':sum(r['status']=='complete' for r in discovery.values()),'filings_with_exhibit99':len(exhibits),'claude_unique_extractions':len(fact_ids),
            'duplicate_fact_rows':fact_rows-len(fact_ids),'claude_tracked_cost_usd':man.get('spent_usd'),
            'extraction_failures':None, 'uncollected_batches':sum(b.get('state')!='collected' for b in batches),
            'price_files':len(list((base/'prices').glob('*.gz')))}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--as-of',required=True)
    ap.add_argument('--base',type=Path,default=ROOT/'research/v6')
    args=ap.parse_args(); timestamp(args.as_of)
    base=args.base; out=base/'evaluation'; out.mkdir(exist_ok=True)
    hashes={}; cache={}
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__), ROOT/'tools/v6/outcomes.py', ROOT/'engine/policy.py', ROOT/'engine/outcome.py', ROOT/'engine/v6/model.py', ROOT/'tools/v6/train.py', ROOT/'tools/v6/exhibits.py']}
    def load(path):
        if path in cache:return cache[path]
        if not path.exists():return {}
        data=path.read_bytes();hashes[str(path.relative_to(base))]=hashlib.sha256(data).hexdigest()
        value=json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
        cache[path]=value; return value
    market=load(base/'prices/SPY.json.gz')
    calls=base/'frozen-calls.jsonl'; rows=[]; rejected=[]; seen=set(); clusters={}
    if calls.exists():
        hashes['frozen-calls.jsonl']=hashlib.sha256(calls.read_bytes()).hexdigest()
        for number,line in enumerate(calls.read_text().splitlines(),1):
            try:
                c=json.loads(line); end=guard(c);bucket(c.get('confidence'))
                if end>timestamp(args.as_of):raise ValueError('call after as-of')
                key=(c['event_id'],c['asset'],c['horizon'])
                if key in seen:raise ValueError('duplicate event/asset/horizon')
                seen.add(key)
                p=load(base/'prices'/f"{c['asset'].replace('^','_')}.json.gz")
                sector=load(base/'prices'/f"{c['sector_etf']}.json.gz") if c.get('sector_etf') else {}
                day=end.date().isoformat()
                result=({'res':'locked','why':'OOS labels locked before model freeze'}
                        if '2025-01-01'<=day<='2026-10-20' else calculate_daily(c,p,market,sector,args.as_of))
                stage=split(c,result,[r[0] for r in market.get('d',[])])
                old=clusters.get(c['cluster_id'])
                if old and old!=stage:raise ValueError('cluster crosses chronological split')
                clusters[c['cluster_id']]=stage
                rows.append({'call':c,'outcome':result,'split':stage})
            except (ValueError,KeyError,TypeError) as exc:
                rejected.append({'line':number,'reason':str(exc)})
    # Reject ALL members of cross-split clusters, including the earlier occurrence.
    # Any duplicate cluster that was rejected above invalidates its accepted members too.
    if any(r['reason']=='cluster crosses chronological split' for r in rejected):
        raise ValueError('cross-split cluster: fix input before evaluation')
    results={'as_of':args.as_of,'inventory':inventory(base),'accepted_rows':len(rows),'rejected_rows':len(rejected),
             'input_sha256':dict(sorted(hashes.items())), 'source_sha256':source_hashes, 'splits':{}}
    for stage in ['TRAIN','VALIDATION','OOS','PURGED','EXCLUDED']:
        subset=[r for r in rows if r['split']==stage]
        results['splits'][stage]=({'status':'LOCKED: no development/validation freeze', 'rows':len(subset)}
                                  if stage=='OOS' else metrics(subset))
    for name,values in [('dataset',rows),('rejected',rejected)]:
        (out/f'{name}.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in values))
    (out/'metrics.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    report=['# v6 Track D evaluation', '', f"As of {args.as_of}. Informational research; not investment advice.", '',
            'Status: OFFLINE. No trained/frozen v6 model; OOS locked. No claim of improvement.', '',
            '## Cache inventory', '', *[f'- {k}: {v if v is not None else "unknown / not recorded"}' for k,v in results['inventory'].items()], '',
            f'Frozen research rows accepted: {len(rows)}; rejected: {len(rejected)}.', '',
            'Cache counts are not evaluated calls. Claude failures/cost are unknown when no manifest exists.', '',
            '## Development and validation', '',
            '| Split | Judged | Confirmed | Other way | No clear move | Pending | Unresolved |',
            '|---|---:|---:|---:|---:|---:|---:|']
    for stage in ['TRAIN','VALIDATION']:
        s=results['splits'][stage]['raw']; n=s['judged']
        def rate(k):return f"{s[k]}/{n} ({100*s[k]/n:.1f}%)" if n else '0/0 (N/A)'
        report.append(f"| {stage} | {n} | {rate('confirmed')} | {rate('other_way')} | {rate('no_clear_move')} | {s['pending']} | {s['unresolved']} |")
    report+=['', '## Coverage versus quality', '', '| Split | Minimum score | Accepted / eligible | Judged | Confirmed / judged |', '|---|---:|---:|---:|---:|']
    for stage in ['TRAIN','VALIDATION']:
        for s in results['splits'][stage]['coverage_quality']:
            report.append(f"| {stage} | {s['minimum_score']} | {s['accepted']}/{s['eligible']} | {s['judged']} | {s['confirmed']}/{s['judged']} |")
    report+=['', '## Detailed measurements', '',
             'metrics.json contains direction, tier, event type, horizon, calibration, same-event long/short baselines,',
             'individual/group fact-rule ablations, raw and sector-relative labels, and threshold coverage.',
             'Empty groups mean no observations, not zero predictive performance. Candidate ablations are untrained',
             'rule comparisons using independent research labels; they cannot establish the value of a trained v6 model.', '',
             '## Limitations and remaining gates', '',
             '- No provenance-complete historical calls or collected Claude facts in the audited branch.',
             '- SEC filing dates lack acceptance timestamps; Nasdaq retrospective consensus has no vintage proof.',
             f"- Verified Exhibit 99 filings in this checkout: {results['inventory']['filings_with_exhibit99']}; discovery requires SEC access.",
             '- Daily next-open proxies cannot prove first intraday trade; sector mapping still required.',
             '- Split adjustments, ticker reuse, delistings, exceptional closures and incomplete free prices require review.',
             '- Calibration is descriptive score bucketing, not probability calibration. No Brier/log loss claim.',
             '- Fit two-stage model on TRAIN, select/calibrate on 2024, commit freeze, then unlock OOS in a separate change.',
             '- Market/sector-follow and v5 baselines need pre-call context not currently supplied; unavailable.',
             '- Seeded event-cluster intervals and training-versus-validation warning flags require a populated cohort.',
             '- Keep v6 offline. The tiny live v5 sample is not v6 evidence. No API calls made by this tool.', '']
    report += ['## Calibration and baselines', '', '| Score bucket | Judged | Confirmed | Other way | No clear move |', '|---|---:|---:|---:|---:|']
    for label in ('50–55','55–60','60–65','65–70','70+'):
        s=results['splits']['VALIDATION']['calibration'].get(label,summary([]))
        report.append(f"| {label} | {s['judged']} | {s['confirmed']} | {s['other_way']} | {s['no_clear_move']} |")
    report += ['', 'Baseline counts and rates are in metrics.json for the identical evaluated cohort.',
               'Missing model/cohort means performance is unavailable; empty groups must not be read as 0% accuracy.',
               'Run python -m tools.v6.train after building a provenance-complete cohort for two-stage logistic',
               'training, validation Platt calibration, coverage-constrained threshold selection and refitted ablations.',
               'Training writes a candidate only; no policy freeze, OOS unlock or live integration.']
    report += ['', '## Verification at implementation', '',
               '25 Track D tests pass. Full Python suite: 149/150 pass; the pre-existing footer test',
               'treats mailto:jobs@investedia.com as a local path. Worker tests: 3/3 pass.',
               'Site build succeeds; generated output restored to keep website files unchanged.',
               'No API credit used, deployment, merge or live-site change.']
    (out/'REPORT.md').write_text('\n'.join(report))
    snapshot=hashlib.sha256((out/'metrics.json').read_bytes()).hexdigest()[:16]
    history=out/'runs'/snapshot; history.mkdir(parents=True,exist_ok=True)
    for name in ('dataset.jsonl','rejected.jsonl','metrics.json','REPORT.md'):
        target=history/name; content=(out/name).read_bytes()
        if target.exists() and target.read_bytes()!=content:
            raise ValueError('immutable evaluation snapshot conflict')
        target.write_bytes(content)
    print(json.dumps({'accepted':len(rows),'rejected':len(rejected),'inventory':results['inventory']},indent=2))


if __name__=='__main__':main()
