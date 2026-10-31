"""Prediction Engine v4: frozen tables and the decision policy (research/ENGINE-V4.md)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import policy as P

A = lambda **k: {'id': 'EQ:X', 'cls': 'equity', 'relation': 'subject', 'stance': 1, **k}


class Policy(unittest.TestCase):
    def test_horizons(self):
        self.assertEqual(P.horizon('earnings', 'equity'), 'S1'); self.assertEqual(P.horizon('macro-data', 'fx'), '6h')
        self.assertEqual(P.horizon('m&a', 'equity', 'acquirer'), 'S2'); self.assertIsNone(P.horizon('earnings', 'crypto'))

    CTX = {'pre_move_sigma': 0.2, 'index_pre_sigma': 0.1, 'sector_pre_sigma': 0.0, 'expected_move_sigma': 1.4}

    def test_earnings_follow_surprise_not_tone_and_reach_priority(self):
        ev = {'event_type': 'earnings', 'event_id': 'e1', 'expectations': {'eps_actual': 1.10, 'eps_expected': 1.00}}
        d = P.decide(ev, A(stance=-1), self.CTX)
        self.assertEqual((d['decision'], d['tier']), ('long', 'priority'))  # beat by 10 % = long even if the article sounds negative

    def test_no_expectations_is_an_outlook_not_priority(self):
        d = P.decide({'event_type': 'earnings', 'expectations': {}}, A(), self.CTX)
        self.assertEqual((d['decision'], d['tier']), ('long', 'outlook')); self.assertIn('evidence', d['priority_missing'])

    def test_conflict_without_guidance_is_no_call(self):
        ev = {'event_type': 'earnings', 'expectations': {'eps_actual': 1.1, 'eps_expected': 1, 'revenue_actual': 90, 'revenue_expected': 100}}
        self.assertEqual(P.decide(ev, A(), self.CTX)['tier'], 'none')
        ev['expectations'].update(guidance_actual=105, guidance_expected=100)
        self.assertEqual(P.decide(ev, A(), self.CTX)['decision'], 'long')  # guidance breaks the tie

    def test_hard_no_calls(self):
        for ev, a, ctx, why in [({'event_type': 'product', 'flags': ['commentary']}, A(), {}, 'commentary'),
                                ({'event_type': 'product'}, A(relation='competitor'), {}, 'indirect'),
                                ({'event_type': 'product'}, A(), {'pre_move_sigma': 3.2}, 'priced-in'),
                                ({'event_type': 'crypto'}, A(), {}, 'unsupported-combination')]:
            d = P.decide(ev, a, ctx); self.assertEqual(d['tier'], 'none'); self.assertIn(why, d['reasons'])
        self.assertIn('duplicate-event', P.decide({'event_type': 'product', 'event_id': 'e'}, A(), {}, seen={('e', 'EQ:X', 'S1')})['reasons'])

    def test_priority_gates_from_structured_features_only(self):
        ev = {'event_type': 'm&a', 'catalyst': {'premium_pct': 30}}
        self.assertEqual(P.decide(ev, A(relation='target'), self.CTX)['tier'], 'priority')
        moved = P.decide(ev, A(relation='target'), {**self.CTX, 'pre_move_sigma': 2.0})
        self.assertEqual(moved['tier'], 'outlook'); self.assertIn('not-priced-in', moved['priority_missing'])  # 1.5-3 sigma: Outlook only
        against = P.decide(ev, A(relation='target'), {**self.CTX, 'index_pre_sigma': -1.5}); self.assertIn('context-supports', against['priority_missing'])
        small = P.decide({'event_type': 'm&a', 'catalyst': {'premium_pct': 5}}, A(relation='target'), self.CTX); self.assertIn('evidence', small['priority_missing'])
        self.assertEqual(P.decide({'event_type': 'm&a', 'catalyst': {'premium_pct': None}}, A(relation='target'), self.CTX)['tier'], 'outlook')  # missing stays missing

    def test_thresholds_after_validation(self):
        cal = lambda raw, t: .55
        d = P.decide({'event_type': 'product'}, A(), self.CTX, th={'outlook': .6, 'priority': .7}, calibrate=cal); self.assertEqual(d['reasons'], ['below-outlook-threshold'])
        d = P.decide({'event_type': 'm&a', 'catalyst': {'premium_pct': 30}}, A(relation='target'), self.CTX, th={'outlook': .5, 'priority': .7}, calibrate=cal)
        self.assertEqual(d['tier'], 'outlook'); self.assertIn('priority-confidence', d['priority_missing'])

    def test_policy_id_is_stable(self):
        self.assertEqual(len(P.POLICY_ID), 12)


if __name__ == '__main__':
    unittest.main()
