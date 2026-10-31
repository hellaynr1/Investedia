"""Stable event ids: code finds candidates (72 h, same family, shared registry asset), the model only picks among them, results are frozen."""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import event_ids as E, events as EV


def st(sid, at, head, aid='CR:BTC', fam='crypto'):
    return {'id': sid, 'published_at': at, 'headline': head, 'event_type': fam, 'category': 'crypto',
            'impacts': [{'name': 'x', 'direction': 'down', 'asset': {'id': aid}}], 'entities': []}


def rec(sid, at, head, aid='CR:BTC', fam='crypto', cluster=None):
    return {'id': sid, 'at': at, 'title': head, 'fam': fam, 'cluster': cluster or sid, 'assets': [{'id': aid}]}


class EventIds(unittest.TestCase):
    def test_joins_same_incident(self):
        pool = [rec('a', '2026-10-30T01:00:00Z', 'Binance hit by $6bn hack')]
        s = st('b', '2026-10-30T05:00:00Z', 'Binance pledges to cover hack losses')
        out = E.assign([s], pool, lambda p: [{'story': 1, 'event': 1, 'why': 'same hack'}])
        self.assertEqual(s['cluster'], 'a'); self.assertEqual(out['joined'], 1)

    def test_model_null_keeps_separate(self):
        pool = [rec('a', '2026-10-30T01:00:00Z', 'Binance hit by $6bn hack')]
        s = st('b', '2026-10-31T01:00:00Z', 'Binance fined by regulator')
        E.assign([s], pool, lambda p: [{'story': 1, 'event': None}]); self.assertEqual(s['cluster'], 'b')

    def test_no_candidate_without_shared_asset_family_or_window(self):
        pool = [rec('a', '2026-10-30T01:00:00Z', 'x', aid='CR:ETH'), rec('c', '2026-10-30T01:00:00Z', 'y', fam='regulation'),
                rec('d', '2026-10-25T01:00:00Z', 'z')]
        s = st('b', '2026-10-30T05:00:00Z', 'Binance hack')
        asked = []
        E.assign([s], pool, lambda p: asked.append(p) or []); self.assertEqual(asked, []); self.assertEqual(s['cluster'], 'b')

    def test_invalid_answer_rejected(self):
        pool = [rec('a', '2026-10-30T01:00:00Z', 'Binance hack')]
        s = st('b', '2026-10-30T05:00:00Z', 'Binance hack follow-up')
        E.assign([s], pool, lambda p: [{'story': 1, 'event': 7}]); self.assertEqual(s['cluster'], 'b')
        s2 = st('c', '2026-10-30T05:00:00Z', 'Binance hack follow-up')
        E.assign([s2], pool, lambda p: (_ for _ in ()).throw(RuntimeError('down'))); self.assertEqual(s2['cluster'], 'c')

    def test_joins_existing_event_root_and_same_batch(self):
        pool = [rec('a', '2026-10-30T01:00:00Z', 'Binance hack'), rec('b', '2026-10-30T02:00:00Z', 'Binance hack 2', cluster='a')]
        s1, s2 = st('c', '2026-10-30T03:00:00Z', 'h3'), st('d', '2026-10-30T04:00:00Z', 'h4')
        E.assign([s2, s1], pool, lambda p: [{'story': 1, 'event': 1}, {'story': 2, 'event': 1}])
        self.assertEqual((s1['cluster'], s2['cluster']), ('a', 'a'))

    def test_assigned_cluster_is_frozen_in_archive(self):
        d = tempfile.mkdtemp()
        s = st('b', '2026-10-30T05:00:00Z', 'Binance hack follow-up'); s['location'] = {}; s['source'] = {}
        s['cluster'] = 'a'; s['cluster_why'] = 'same hack'; EV.upsert([s], base=d)
        s2 = dict(s); s2.pop('cluster'); s2.pop('cluster_why'); EV.upsert([s2], base=d)
        r = EV.load_days(3, now=EV._t({'at': '2026-10-31T00:00:00Z'}), base=d)[0]
        self.assertEqual((r['cluster'], r.get('cluster_why')), ('a', 'same hack'))


if __name__ == '__main__':
    unittest.main()
