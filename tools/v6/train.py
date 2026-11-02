"""Chronological logistic research + validation calibration/ablation. Never reads OOS labels.
python -m tools.v6.train [--dataset PATH] [--output PATH]
Requires numpy/scikit-learn only for training; inference uses the standard library.
Does not freeze a policy, unlock OOS, call an API, or write a live call.
"""
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter
from engine.v6.model import encode, predict
from tools.v6.evaluate import ROOT, GROUPS, ALLOWED, guard, summary, bucket, redirect
from tools.v6.outcomes import cutoff


def validate(rows):
    selected=[];seen=set();clusters={}
    for r in rows:
        c=r['call'];guard(c)
        if r['split'] not in ('TRAIN','VALIDATION'):continue
        day=cutoff(c).date().isoformat()
        if not (('2022-01-01'<=day<='2023-12-31') if r['split']=='TRAIN' else ('2024-01-01'<=day<='2024-12-31')):
            raise ValueError('incorrect chronological stage')
        key=(c['event_id'],c['asset'],c['horizon'])
        if key in seen:raise ValueError('duplicate event')
        seen.add(key)
        if c['cluster_id'] in clusters and clusters[c['cluster_id']]!=r['split']:
            raise ValueError('cluster spans development and validation')
        clusters[c['cluster_id']]=r['split']
        o=r['outcome']
        if o.get('research_long_relative_res',o.get('relative_res')) not in ('hit','miss','flat'):continue
        if not o.get('exit') or o['exit'][0][:10] > ('2023-12-31' if r['split']=='TRAIN' else '2024-12-31'):
            raise ValueError('label crosses stage boundary')
        selected.append(r)
    return selected


def labels(rows):
    # Reconstruct underlying positive/negative target independently of frozen direction.
    return [0 if r['outcome'].get('research_long_relative_res',r['outcome'].get('relative_res'))=='flat' else
            1 if r['outcome']['relative_move_pct']>0 else -1 for r in rows]


def enough(train,val):
    a,b=Counter(labels(train)),Counter(labels(val))
    if len(train)<100 or len(val)<50 or any(a[k]<10 or b[k]<5 for k in (-1,0,1)):
        raise ValueError('insufficient cohort: need >=100 TRAIN / >=50 VALIDATION and both signs plus flats')
    if len({r['call']['cluster_id'] for r in train})<50 or len({r['call']['cluster_id'] for r in val})<25:
        raise ValueError('insufficient independent event clusters')


def fit(train,val,drop=()):
    import numpy as np
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    enough(train,val)
    vec=DictVectorizer(sparse=False)
    xt=vec.fit_transform([encode(r['call']['features'],drop) for r in train])
    xv=vec.transform([encode(r['call']['features'],drop) for r in val])
    if not xt.shape[1]:raise ValueError('no usable training features')
    scaler=StandardScaler(with_mean=False).fit(xt)
    xt,xv=scaler.transform(xt),scaler.transform(xv)
    yt,yv=np.array(labels(train)),np.array(labels(val))
    material=LogisticRegression(C=1,max_iter=2000,random_state=0).fit(xt,(yt!=0).astype(int))
    positive=LogisticRegression(C=1,max_iter=2000,random_state=0).fit(xt[yt!=0],(yt[yt!=0]>0).astype(int))
    def platt(m,x,y):
        calibration=LogisticRegression(C=1,max_iter=2000,random_state=0).fit(m.decision_function(x).reshape(-1,1),y)
        return [float(calibration.coef_[0][0]),float(calibration.intercept_[0])]
    def coefficients(m):return {'coef':m.coef_[0].tolist(),'intercept':float(m.intercept_[0])}
    return {'version':'v6-logistic-research-1','feature_names':vec.get_feature_names_out().tolist(),
            'scales':scaler.scale_.tolist(),'drop':sorted(drop), 'material':coefficients(material),'positive':coefficients(positive),
            'calibration_material':platt(material,xv,(yv!=0).astype(int)),
            'calibration_positive':platt(positive,xv[yv!=0],(yv[yv!=0]>0).astype(int)),
            'thresholds':{'material':.5,'direction':.5}}


def evaluate(model,rows,mt=.5,dt=.5):
    accepted=[]; profits=[]; buckets={}
    for row in rows:
        p=predict(model,row['call']['features'],mt,dt)
        if p['direction']=='none':continue
        r=redirect(row,p['direction'])
        # Primary target is sector-relative; preserve raw metrics separately elsewhere.
        r={**r,'outcome':{**r['outcome'],'res':r['outcome']['relative_res']}}
        accepted.append(r)
        profits.append(row['outcome']['relative_move_pct']*(1 if p['direction']=='long' else -1))
        buckets.setdefault(bucket(p['confidence']),[]).append(r)
    return {'accepted':len(accepted),'eligible':len(rows),'coverage_pct':100*len(accepted)/len(rows) if rows else None,
            'mean_signed_abnormal_return_pct':sum(profits)/len(profits) if profits else None,
            'outcomes':summary(accepted),'score_buckets':{k:summary(v) for k,v in buckets.items()}}


def research(rows):
    rows=validate(rows)
    train=[r for r in rows if r['split']=='TRAIN'];val=[r for r in rows if r['split']=='VALIDATION']
    enough(train,val)
    model=fit(train,val)
    table=[]
    for mt in (.5,.55,.6,.65,.7):
        for dt in (.5,.55,.6,.65,.7):
            table.append({'material_threshold':mt,'direction_threshold':dt,**evaluate(model,val,mt,dt)})
    # Coverage + minimum judged count are fixed engineering gates, not a headline hit-rate objective.
    feasible=[r for r in table if r['coverage_pct']>=20 and r['accepted']>=30]
    if not feasible:raise ValueError('no threshold meets 20% coverage and >=30 validation calls')
    chosen=max(feasible,key=lambda r:(r['mean_signed_abnormal_return_pct'],r['accepted']))
    model['thresholds']={'material':chosen['material_threshold'],'direction':chosen['direction_threshold']}
    full_train=evaluate(model,train);full_val=evaluate(model,val)
    ablation={}
    for name,drop in {**GROUPS,**{k:{k} for k in sorted(ALLOWED)}}.items():
        try:
            m=fit(train,val,drop);a=evaluate(m,train);b=evaluate(m,val)
            gain_train=(full_train['mean_signed_abnormal_return_pct']-a['mean_signed_abnormal_return_pct']) if a['mean_signed_abnormal_return_pct'] is not None and full_train['mean_signed_abnormal_return_pct'] is not None else None
            gain_val=(full_val['mean_signed_abnormal_return_pct']-b['mean_signed_abnormal_return_pct']) if b['mean_signed_abnormal_return_pct'] is not None and full_val['mean_signed_abnormal_return_pct'] is not None else None
            ablation[name]={'TRAIN':a,'VALIDATION':b,
                            'feature_incremental_return_TRAIN':gain_train,'feature_incremental_return_VALIDATION':gain_val,
                            'feature_training_only_warning':gain_train is not None and gain_train>0 and (gain_val is None or gain_val<=0),
                            'training_only_warning':a['mean_signed_abnormal_return_pct'] is not None and a['mean_signed_abnormal_return_pct']>0 and
                            (b['mean_signed_abnormal_return_pct'] is None or b['mean_signed_abnormal_return_pct']<=0)}
        except ValueError as exc:ablation[name]={'unavailable':str(exc)}
    return {'model':model,'threshold_selection':chosen,'coverage_quality':table,
            'TRAIN':evaluate(model,train,**{'mt':model['thresholds']['material'],'dt':model['thresholds']['direction']}),
            'VALIDATION':evaluate(model,val,**{'mt':model['thresholds']['material'],'dt':model['thresholds']['direction']}),
            'ablation':ablation, 'OOS':'LOCKED',
            'limitations':['Calibration and threshold selection share 2024: validation results are selection-biased.',
                           'No OOS improvement claim. Model remains a candidate; no live wiring or frozen policy.',
                           '20% coverage floor and 30-call minimum are safeguards, not empirically validated thresholds.']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,default=ROOT/'research/v6/evaluation/dataset.jsonl')
    ap.add_argument('--output',type=Path,default=ROOT/'research/v6/evaluation/training.json');a=ap.parse_args()
    data=a.dataset.read_bytes()
    rows=[json.loads(line) for line in data.decode().splitlines()]
    try: result=research(rows)
    except ValueError as exc:result={'status':'BLOCKED','reason':str(exc),'OOS':'LOCKED'}
    result['dataset_sha256']=hashlib.sha256(data).hexdigest()
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','reason','OOS')}))


if __name__=='__main__':main()
