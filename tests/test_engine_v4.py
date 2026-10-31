"""Prediction Engine v4: frozen tables and the decision policy (research/ENGINE-V4.md)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import policy as P

A = lambda **k: {'id': 'EQ:X', 'cls': 'equity', 'relation': 'subject', 'stance': 1, **k}


class Policy(unittest.TestCase):
    def test_horizons(self):
        self.assertEqual(P.horizon('earnings', 'equity'), 'S1'); self.assertEqual(P.horizon('macro-data', 'fx'), '6h')
        self.assertEqual(P.horizon('m&a', 'equity', 'acquirer'), 'S2'); self.assertIsNone(P.horizon('earnings', 'crypto'))

    def test_earnings_follow_surprise_not_tone(self):
        ev = {'event_type': 'earnings', 'event_id': 'e1', 'expectations': {'eps_actual': 1.10, 'eps_expected': 1.00}}
        d = P.decide(ev, A(stance=-1), {'pre_move_sigma': 0.2})
        self.assertEqual(d['decision'], 'long')  # beat by 10 % = long even if the article sounds negative

    def test_no_expectations_abstains(self):
        d = P.decide({'event_type': 'earnings', 'expectations': {}}, A(), {}); self.assertEqual(d['decision'], 'none'); self.assertIn('no-expectations', d['reasons'])

    def test_conflict_without_guidance_abstains(self):
        ev = {'event_type': 'earnings', 'expectations': {'eps_actual': 1.1, 'eps_expected': 1, 'revenue_actual': 90, 'revenue_expected': 100}}
        self.assertIn('competing-catalysts', P.decide(ev, A(), {})['reasons'])
        ev['expectations'].update(guidance_actual=105, guidance_expected=100)
        self.assertEqual(P.decide(ev, A(), {})['decision'], 'long')  # guidance breaks the tie

    def test_flags_indirect_already_moved_duplicate(self):
        self.assertIn('commentary', P.decide({'event_type': 'product', 'flags': ['commentary']}, A(), {})['reasons'])
        self.assertIn('indirect', P.decide({'event_type': 'product'}, A(relation='competitor'), {})['reasons'])
        self.assertIn('already-moved', P.decide({'event_type': 'product'}, A(), {'pre_move_sigma': 2.0})['reasons'])
        self.assertIn('duplicate-event', P.decide({'event_type': 'product', 'event_id': 'e'}, A(), {}, seen={('e', 'EQ:X', 'S1')})['reasons'])
        self.assertEqual(P.decide({'event_type': 'product'}, A(), {'pre_move_sigma': -2.0})['decision'], 'long')  # context never flips

    def test_threshold_and_unsupported(self):
        d = P.decide({'event_type': 'product'}, A(), {}, threshold=.7, calibrate=lambda raw, t: .6)
        self.assertEqual(d['reasons'], ['below-threshold'])
        self.assertIn('unsupported-combination', P.decide({'event_type': 'crypto'}, A(), {})['reasons'])

    def test_policy_id_is_stable(self):
        self.assertEqual(len(P.POLICY_ID), 12)


if __name__ == '__main__':
    unittest.main()
