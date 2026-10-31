"""outcome-v2: proven start, exchange-session end price, 4-day limit, ledger-driven tracking."""
import os, sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_news_track as T

D = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
E = lambda s: D(s).timestamp()


def call(**k):
    return {'id': 'n1', 'sym': 'X', 'dir': 'up', 'created': '2026-10-30T15:00:00Z', 'start': '2026-10-30T15:00:00Z', 'res': 'pending', **k}


class OutcomeV2(unittest.TestCase):
    def test_weekend_waits_for_next_session(self):
        # Friday 15:00 call; market closed Fri 20:00 -> Mon 14:30. End = first trade >= 24 h later = Monday open.
        bars = [(E('2026-10-30T14:55'), 100.0), (E('2026-10-30T19:55'), 101.0), (E('2026-11-02T14:30'), 103.0), (E('2026-11-02T15:00'), 104.0)]
        L = {'calls': [call()]}
        T.judge({}, L, D('2026-10-31T16:00'), fetch=lambda sym, t0, t1: [b for b in bars if t0 <= b[0] <= t1]); self.assertEqual(L['calls'][0]['res'], 'pending')  # Saturday: no trade yet
        T.judge({}, L, D('2026-11-02T16:00'), fetch=lambda sym, t0, t1: [b for b in bars if t0 <= b[0] <= t1])
        c = L['calls'][0]; self.assertEqual(c['res'], 'hit'); self.assertEqual(c['base'][1], 100.0); self.assertEqual(c['end'][1], 103.0); self.assertEqual(c['move'], 3.0)

    def test_unresolved_after_four_days(self):
        bars = [(E('2026-10-30T14:55'), 100.0)]
        L = {'calls': [call()]}
        T.judge({}, L, D('2026-11-04T16:00'), fetch=lambda sym, t0, t1: [b for b in bars if t0 <= b[0] <= t1]); self.assertEqual(L['calls'][0]['res'], 'unresolved')

    def test_never_scores_before_proven_start(self):
        # created 10:00 but first public 15:00: the 10:00 price must not be the baseline
        bars = [(E('2026-10-30T10:00'), 50.0), (E('2026-10-30T14:55'), 100.0), (E('2026-10-31T15:05'), 99.0)]
        L = {'calls': [call(created='2026-10-30T10:00:00Z')]}
        T.judge({}, L, D('2026-10-31T16:00'), fetch=lambda sym, t0, t1: [b for b in bars if t0 <= b[0] <= t1])
        self.assertEqual(L['calls'][0]['base'][1], 100.0); self.assertEqual(L['calls'][0]['res'], 'miss')

    def test_pending_calls_stay_tracked_without_their_article(self):
        L = {'calls': [call(sym='AAA'), call(sym='BBB', res='hit'), call(sym='CCC', legacy=True)]}
        self.assertEqual(T.pending_symbols(L, {'AAA', 'BBB', 'CCC'}), {'AAA'})


if __name__ == '__main__':
    unittest.main()
