"""v6 earnings engine: point-in-time and split integrity checks (synthetic data, no network)."""
import math, unittest
from tools.v6.earnings_dataset import features, idx_after, money


def series(n, start=100.0, step=0.001):
    d = [f'2024-{1 + k // 28:02d}-{1 + k % 28:02d}' for k in range(n)]
    c = [start * math.exp(step * k + 0.01 * math.sin(k)) for k in range(n)]
    return {'dates': d, 'o': [x * 0.999 for x in c], 'c': c, 'v': [1e6] * n}


class T(unittest.TestCase):
    def test_features_ignore_future_bars(self):
        P, S = series(120), series(120, 400)
        e = {'eps': 1.1, 'est': 1.0, 'n_est': 5}
        f1, _ = features(P, S, None, 90, 90, e, None)
        P2 = {k: v[:] for k, v in P.items()}
        for k in range(90, 120): P2['c'][k] *= 3  # change the close of the entry session and everything after
        for k in range(91, 120): P2['o'][k] *= 3
        f2, _ = features(P2, S, None, 90, 90, e, None)
        self.assertEqual(f1, f2)

    def test_entry_strictly_after_report_day(self):
        d = ['2025-01-02', '2025-01-03', '2025-01-06']
        self.assertEqual(idx_after(d, '2025-01-03'), 2)
        self.assertEqual(idx_after(d, '2025-01-04'), 2)

    def test_money(self):
        self.assertEqual(money('$(0.12)'), -0.12); self.assertEqual(money('$1,234.5'), 1234.5); self.assertIsNone(money('N/A'))

    def test_splits_are_chronological(self):
        from tools.v6.earnings_model import load
        try: rows = load()
        except FileNotFoundError: self.skipTest('dataset not built')
        tr = max(r['entry_day'] for r in rows if r['split'] == 'train'); va = [r['entry_day'] for r in rows if r['split'] == 'val']; te = min(r['entry_day'] for r in rows if r['split'] == 'test')
        self.assertLess(tr, min(va)); self.assertLess(max(va), te)
        for r in rows[:2000]: self.assertLess(r['report_day'], r['entry_day']); self.assertLess(r['entry_day'], r['exit_day'])


if __name__ == '__main__': unittest.main()
