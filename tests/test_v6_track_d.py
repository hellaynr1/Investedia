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
