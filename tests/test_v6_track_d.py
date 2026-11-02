"""Track D research contracts; all prices/documents below are test fixtures only."""
import copy
import unittest
from tools.v6.outcomes import calculate_daily, calculate_trades, timestamp
from tools.v6.evaluate import guard, split, summary, candidate, bucket, metrics


def call(**kw):
    t='2024-01-12T20:00:00Z'
    return dict(event_id='e',cluster_id='c',asset='A',event_type='guidance',tier='standard',
                direction='long',horizon='S1',information_public_at=t,prediction_generated_at=t,
                public_call_at=t,frozen_at=t,publication_proof='original SEC header hash',policy_id='test',features={},**kw)


def prices():
    # Friday, Tuesday after MLK holiday, Wednesday, Thursday.
    return {'split_adjusted':True,'d':[[d,100,102,99,p,10] for d,p in
            [('2024-01-12',99),('2024-01-16',101),('2024-01-17',102),('2024-01-18',103)]]}


class TrackD(unittest.TestCase):
    def test_timezone_required(self):
        with self.assertRaises(ValueError):timestamp('2024-01-01T12:00:00')

    def test_weekend_holiday_and_full_session(self):
        p=prices(); r=calculate_daily(call(),p,p,{},'2024-01-18T22:00:00Z')
        self.assertEqual(r['entry'][0],'2024-01-16T14:30:00+00:00')
        self.assertEqual(r['exit'][0],'2024-01-17T21:00:00+00:00')
        self.assertEqual(r['res'],'hit');self.assertIsNone(r['relative_res'])

    def test_pending_not_flat(self):
        p=prices(); r=calculate_daily(call(),p,p,{},'2024-01-16T22:00:00Z')
        self.assertEqual(r['res'],'pending')

    def test_missing_session_not_loss(self):
        p=prices(); q=copy.deepcopy(p);q['d'].pop(1)
        self.assertEqual(calculate_daily(call(),q,p,{},'2024-01-18T22:00:00Z')['res'],'unresolved')

    def test_split_unadjusted(self):
        p=prices();q={**p,'split_adjusted':False,'splits':[['2024-01-17',2]]}
        self.assertEqual(calculate_daily(call(),q,p,{},'2024-01-18T22:00:00Z')['res'],'unresolved')

    def test_flat_and_short(self):
        p=prices();p['d'][2][4]=100.1
        self.assertEqual(calculate_daily(call(),p,p,{},'2024-01-18T22:00:00Z')['res'],'flat')
        p['d'][2][4]=102;c=call();c['direction']='short'
        self.assertEqual(calculate_daily(c,p,p,{},'2024-01-18T22:00:00Z')['res'],'miss')

    def test_exact_trade_entry_and_clock(self):
        c=call();c['horizon']='24h';t=timestamp(c['public_call_at']).timestamp()
        r=calculate_trades(c,[(t-1,50),(t,100),(t+86400,102)],'2024-01-14T00:00:00Z')
        self.assertEqual(r['entry'][1],100);self.assertEqual(r['res'],'hit')
        r=calculate_trades(c,[(t,100),(t+86400,102)],'2024-01-12T22:00:00Z')
        self.assertEqual(r['res'],'pending')

    def test_feature_leakage(self):
        c=call();f=dict(value='raised',available_at=c['public_call_at'],source_published_at=c['public_call_at'],
                        source_updated_at=c['public_call_at'],source_kind='original-release')
        c['features']={'guidance_direction':f};guard(c)
        for k in ('available_at','source_published_at','source_updated_at'):
            bad=copy.deepcopy(c);bad['features']['guidance_direction'][k]='2024-01-13T00:00:00Z'
            with self.assertRaises(ValueError):guard(bad)
        for name in ('future_return','outcome','one_line','stock_price_after'):
            c['features']={name:f}
            with self.assertRaises(ValueError):guard(c)
        c['features']={'guidance_direction':{**f,'source_kind':'retrospective-news'}}
        with self.assertRaises(ValueError):guard(c)

    def test_freeze_guard(self):
        c=call();c['frozen_at']='2024-01-13T00:00:00Z'
        with self.assertRaises(ValueError):guard(c)

    def test_splits_purge_embargo_exclusion(self):
        c=call(); sessions=['2024-01-02','2024-01-03','2024-01-04','2024-01-05','2024-01-08','2024-01-12']
        self.assertEqual(split(c,{'label_end_at':'2024-01-17T21:00:00Z'},sessions),'VALIDATION')
        self.assertEqual(split(c,{'label_end_at':'2025-01-02T21:00:00Z'},sessions),'PURGED')
        c['public_call_at']='2026-10-21T00:00:00Z'
        self.assertEqual(split(c,{},sessions),'EXCLUDED')
        c=call()
        for k in ('public_call_at','prediction_generated_at','information_public_at'):c[k]='2024-01-03T00:00:00Z'
        self.assertEqual(split(c,{},sessions),'PURGED')

    def test_counts_include_flats_but_not_pending(self):
        s=summary([{'outcome':{'res':r}} for r in ['hit','miss','flat','pending','unresolved']])
        self.assertEqual(s['judged'],3);self.assertEqual(s['confirmed_rate']['denominator'],3)
        self.assertEqual(s['pending'],1)

    def test_abstention_conflicts_and_ablation(self):
        f={'guidance_direction':{'value':'raised'}}
        self.assertEqual(candidate(f),('long',1));self.assertEqual(candidate(f,{'guidance_direction'}),('none',0))
        f['financing_type']={'value':'equity'};self.assertEqual(candidate(f),('none',0))
        self.assertEqual(candidate({}),('none',0))

    def test_coverage_and_calibration(self):
        c=call();c['confidence']=62
        m=metrics([{'call':c,'outcome':{'res':'hit'}}])
        self.assertEqual(m['calibration']['60–65']['judged'],1)
        self.assertEqual(m['coverage_quality'][-1]['accepted'],0)
        self.assertEqual(bucket(None),'unscored')
        with self.assertRaises(ValueError):bucket(101)


if __name__=='__main__':unittest.main()


class ModelResearch(unittest.TestCase):
    def test_unpopulated_cohort_blocks_training(self):
        from tools.v6.train import research
        with self.assertRaisesRegex(ValueError,'insufficient cohort'):research([])

    def test_json_inference_and_unknown_feature(self):
        from engine.v6.model import predict,encode
        model={'feature_names':['guidance_direction=raised'],'scales':[1], 'drop':[],
               'material':{'coef':[1],'intercept':1},'positive':{'coef':[1],'intercept':1},
               'calibration_material':[1,0],'calibration_positive':[1,0],
               'thresholds':{'material':.5,'direction':.5}}
        p=predict(model,{'guidance_direction':{'value':'raised'}})
        self.assertEqual(p['direction'],'long');self.assertFalse(p['score_is_probability'])
        with self.assertRaises(ValueError):encode({'future_return':{'value':10}})
        with self.assertRaises(ValueError):encode({'eps_surprise_pct':{'value':float('nan')}})

    def test_bootstrap_reproducible(self):
        from tools.v6.evaluate import cluster_interval
        rows=[{'call':{'cluster_id':str(i)},'outcome':{'res':'hit' if i%2 else 'miss'}} for i in range(10)]
        self.assertEqual(cluster_interval(rows),cluster_interval(rows))
        self.assertEqual(cluster_interval(rows)['clusters'],10)

    def test_material_and_sign_training_roundtrip(self):
        from tools.v6.train import fit,evaluate
        from engine.v6.model import predict
        def cohort(year,n):
            result=[]
            for i in range(n):
                t=f'{year}-03-12T20:00:00Z'; c=call()
                for k in ('information_public_at','prediction_generated_at','public_call_at','frozen_at'):c[k]=t
                c.update(event_id=f'{year}-{i}',cluster_id=f'{year}-{i}')
                v=[-5,0,5][i%3]
                c['features']={'eps_surprise_pct':{'value':v,'available_at':t,'source_published_at':t,
                                                   'source_updated_at':t,'source_kind':'as-filed'}}
                result.append({'call':c,'split':'TRAIN' if year==2023 else 'VALIDATION',
                               'outcome':{'relative_res':'flat' if v==0 else 'hit' if v>0 else 'miss',
                                          'relative_move_pct':v,'exit':[f'{year}-03-14T20:00:00Z',100]}})
            return result
        tr,va=cohort(2023,120),cohort(2024,60)
        m=fit(tr,va)
        self.assertEqual(m['feature_names'],['eps_surprise_pct'])
        self.assertEqual(evaluate(m,va)['eligible'],60)
        self.assertEqual(predict(m,{'eps_surprise_pct':{'value':5}})['direction'],'long')


class AdditionalGuards(unittest.TestCase):
    def test_early_close_and_dst(self):
        from tools.v6.outcomes import session_time
        self.assertEqual(session_time('2024-11-29',16).hour,18)
        self.assertEqual(session_time('2024-07-03',16).hour,17)
        self.assertEqual(session_time('2024-06-03',9,30).hour,13)
        self.assertEqual(session_time('2024-01-03',9,30).hour,14)

    def test_public_info_must_precede_prediction(self):
        c=call();c['information_public_at']='2024-01-13T00:00:00Z'
        with self.assertRaises(ValueError):guard(c)

    def test_feature_after_prediction_before_publication_is_rejected(self):
        c=call();c['public_call_at']='2024-01-12T22:00:00Z'
        c['features']={'eps_surprise_pct':{'value':10,'available_at':'2024-01-12T21:00:00Z',
                     'source_published_at':c['prediction_generated_at'],
                     'source_updated_at':c['prediction_generated_at'],'source_kind':'as-filed'}}
        with self.assertRaises(ValueError):guard(c)

    def test_no_view_and_old_missing_calendar(self):
        c=call();c['direction']='none';p=prices()
        self.assertEqual(calculate_daily(c,p,p,{},'2024-01-18T22:00:00Z')['res'],'no-view')
        c['direction']='long'
        self.assertEqual(calculate_daily(c,{}, {},{},'2024-02-18T22:00:00Z')['res'],'unresolved')

    def test_train_rejects_cluster_overlap_and_duplicate_events(self):
        from tools.v6.train import validate
        c=call();a={'call':c,'split':'VALIDATION','outcome':{}}
        with self.assertRaisesRegex(ValueError,'duplicate'):validate([a,a])
        b=copy.deepcopy(a);b['split']='TRAIN';b['call']['event_id']='earlier'
        for k in ('information_public_at','prediction_generated_at','public_call_at','frozen_at'):
            b['call'][k]='2023-03-12T20:00:00Z'
        with self.assertRaisesRegex(ValueError,'cluster'):validate([b,a])


class NoViewResearch(unittest.TestCase):
    def test_abstention_retains_independent_target(self):
        from tools.v6.evaluate import redirect
        c=call();c['direction']='none';c['tier']='none';p=prices()
        o=calculate_daily(c,p,p,{},'2024-01-18T22:00:00Z')
        self.assertEqual(o['res'],'no-view');self.assertEqual(o['research_long_res'],'hit')
        self.assertEqual(redirect({'call':c,'outcome':o},'short')['outcome']['res'],'miss')

    def test_abstention_missing_prices_has_no_guessed_label(self):
        c=call();c['direction']='none';c['tier']='none'
        o=calculate_daily(c,{}, {},{},'2024-02-18T22:00:00Z')
        self.assertEqual(o['res'],'no-view');self.assertEqual(o['research_long_res'],'unresolved')


class DatasetIntegration(unittest.TestCase):
    def run_dataset(self,base):
        import contextlib,io
        from unittest.mock import patch
        from tools.v6.evaluate import main
        with patch('sys.argv',['evaluate','--base',str(base),'--as-of','2024-01-18T22:00:00Z']),contextlib.redirect_stdout(io.StringIO()):
            main()

    def test_repeatability_and_rejection_audit(self):
        import gzip,json,tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'prices').mkdir()
            p=prices()
            for symbol in ('SPY','A'):
                with gzip.open(base/'prices'/f'{symbol}.json.gz','wt') as f:json.dump(p,f)
            # Enough observed dates to pass the boundary embargo.
            p['d'][:0]=[[f'2024-01-{d:02}',100,101,99,100,10] for d in (2,3,4,5,8)]
            with gzip.open(base/'prices/SPY.json.gz','wt') as f:json.dump(p,f)
            c=call();bad=copy.deepcopy(c);bad['event_id']='bad';bad['features']={'future_return':{'value':10}}
            (base/'frozen-calls.jsonl').write_text('\n'.join(json.dumps(r) for r in (c,c,bad)))
            self.run_dataset(base)
            metrics=(base/'evaluation/metrics.json').read_bytes()
            results=json.loads(metrics)
            self.assertEqual(results['accepted_rows'],1);self.assertEqual(results['rejected_rows'],2)
            self.assertEqual(results['splits']['VALIDATION']['raw']['judged'],1)
            self.run_dataset(base)
            self.assertEqual(metrics,(base/'evaluation/metrics.json').read_bytes())
            self.assertEqual(len(list((base/'evaluation/runs').iterdir())),1)
