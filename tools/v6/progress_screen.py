"""Render actual offline research inventory; never invent a performance percentage."""
import json
import os
import tempfile
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR",str(Path(tempfile.gettempdir())/"investedia-matplotlib"))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tools.v6.evaluate import inventory, ROOT
from tools.v6.exhibits import metadata


def main():
    base=ROOT/'research/v6'; stats=inventory(base);meta=metadata(base)
    legacy_excerpt_ids=set()
    for path in (base/'exhibits').glob('????-??.jsonl'):
        for line in path.read_text().splitlines():
            record=json.loads(line)
            if record.get('legacy_excerpt_chars'):legacy_excerpt_ids.add(record['adsh'])
    stats['archived_excerpts']=len(legacy_excerpt_ids)
    stats['cached_release_excerpts']=len(list((base/'text').glob('**/*.txt.gz')))
    stats['verified_exhibit_entries']=sum(len(r.get('docs',[])) for r in meta.values() if r.get('status')=='complete')
    stats['judged_v6_calls']=0
    metrics=base/'evaluation/metrics.json'
    if metrics.exists():
        m=json.loads(metrics.read_text())
        stats['judged_v6_calls']=sum(v.get('raw',{}).get('judged',0) for k,v in m.get('splits',{}).items() if k in ('TRAIN','VALIDATION'))
    runs=base/'exhibits/runs.jsonl'
    latest=json.loads(runs.read_text().splitlines()[-1]) if runs.exists() else {}
    out=base/'progress';out.mkdir(exist_ok=True)
    validation_path=out/'validation-run.json'
    validation=json.loads(validation_path.read_text()) if validation_path.exists() else None
    report={'inventory':stats,'latest_discovery_run':latest,'validation_run':validation,'performance_claim':'Unavailable: no validated holdout result'}
    (out/'status.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    fig=plt.figure(figsize=(14.4,9),facecolor='#101114')
    fig.text(.055,.94,'INVESTEDIA  /  ENGINE v6',color='#ff7a1a',fontsize=16,weight='bold')
    fig.text(.055,.885,'Historical research: current results',color='white',fontsize=28,weight='bold')
    fig.text(.055,.84,'OFFLINE RESEARCH  •  ACTUAL CACHED DATA  •  NOT INVESTMENT ADVICE',color='#a6a9b0',fontsize=11)
    cards=[('SEC filings indexed',stats['sec_filings']),('Acceptance timestamps recovered',stats['filings_with_acceptance_timestamp']),
           ('Stock / benchmark price histories',stats['price_files']),('Release text excerpts cached',stats['cached_release_excerpts']),
           ('New verified Exhibit 99 filings',stats['filings_with_exhibit99']),('Judged v6 research calls',stats['judged_v6_calls'])]
    for i,(label,n) in enumerate(cards):
        x=.055+(i%3)*.31;y=.68-(i//3)*.22
        fig.text(x,y,f'{n:,}',color='white',fontsize=36,weight='bold')
        fig.text(x,y-.047,label,color='#bfc1c8',fontsize=12)
    fig.text(.055,.34,'Holdout success rate: UNAVAILABLE',color='#ff7a1a',fontsize=20,weight='bold')
    fig.text(.055,.295,f"{stats['verified_exhibit_entries']} Exhibit 99 documents verified across {stats['filings_with_exhibit99']} filings. These are data, not judged predictions.",color='white',fontsize=12)
    error=(latest.get('last_error') or {}).get('error')
    status=(f"SEC DATA SAVED ON engine-v6 — {latest.get('errors',0)} discovery errors await review" if latest.get('indexes_cached',0)>0 else
            'SEC DOWNLOAD BLOCKED — proxy returned 403' if error and '403' in error else
            'See status.json for the latest download attempt')
    if validation:
        test=validation['tests']
        fig.text(.055,.258,f"Run executed: {test['passed']}/{test['total']} code tests pass | Model fit: {validation['model_training']['status']} | Dataset: {validation['dataset_rows']} calls",color='#bfc1c8',fontsize=11)
    fig.text(.055,.22,status,color='#e6e6e8',fontsize=13,weight='bold')
    fig.text(.055,.178,f"Latest discovery: {latest.get('attempts',0)} attempted / {latest.get('indexes_cached',0)} cached / {latest.get('exhibit_entries_added',0)} exhibit entries added",color='#bfc1c8',fontsize=12)
    fig.text(.055,.135,f"Run: {latest.get('at','unknown')}  |  Claude spending for discovery: $0",color='#a6a9b0',fontsize=10)
    fig.text(.055,.078,'Cached release excerpts are limited to 6,000 characters. Historical and live records stay separate.',color='#a6a9b0',fontsize=10)
    fig.savefig(out/'status.png',dpi=120,facecolor=fig.get_facecolor())
    plt.close(fig)
    phone=plt.figure(figsize=(3.9,8.1),facecolor='#101114')
    phone.text(.07,.95,'INVESTEDIA / v6',color='#ff7a1a',fontsize=11,weight='bold')
    phone.text(.07,.855,'Verified SEC\ndata collected',color='white',fontsize=22,weight='bold',linespacing=1.15)
    phone.text(.07,.805,'Actual cached results · engine-v6',color='#bfc1c8',fontsize=10)
    items=[(stats['filing_indexes_discovered'],'Verified filing\nindexes'),
           (stats['verified_exhibit_entries'],'Exhibit 99\ndocuments'),
           (stats['cached_release_excerpts'],'Release excerpts\ncached'),
           ('$0','Model API\nspending'),
           (latest.get('errors',0),'Discovery errors\nawaiting review'),
           (stats['judged_v6_calls'],'Judged v6\npredictions')]
    for i,(number,label) in enumerate(items):
        x=.07+(i%2)*.49;y=.69-(i//2)*.18
        phone.text(x,y,f'{number:,}' if isinstance(number,int) else number,color='white',fontsize=30,weight='bold')
        phone.text(x,y-.06,label,color='#bfc1c8',fontsize=10,linespacing=1.3)
    phone.text(.07,.17,'Performance not validated',color='#ff7a1a',fontsize=12,weight='bold')
    phone.text(.07,.115,'No accuracy percentage supported yet.\nNo deployment. No Claude calls.',color='#bfc1c8',fontsize=9,linespacing=1.4)
    phone.text(.07,.035,'Research only · Not investment advice',color='#a6a9b0',fontsize=8)
    phone.savefig(out/'status-phone.png',dpi=200,facecolor=phone.get_facecolor())
    plt.close(phone)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
