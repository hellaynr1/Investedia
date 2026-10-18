"""Data correctness checks: currency units, yield units, provenance and failed feeds."""
import unittest
from unittest.mock import patch
import update_market as market


class MarketDataTests(unittest.TestCase):
    def quote(self, symbol, currency, closes):
        rows = [[i, p, p, p, p, 10] for i, p in enumerate(closes)]
        meta = {'currency': currency, 'regularMarketPrice': closes[-1], 'regularMarketTime': 100,
                'regularMarketDayHigh': closes[-1], 'regularMarketDayLow': closes[-1]}
        with patch.object(market, 'QUICK', True), patch.object(market, 'yahoo', return_value=(meta, rows)):
            return market.from_yahoo(symbol)[0]

    def test_pence_are_converted_once(self):
        q = self.quote('HSBA', 'GBp', [1000, 1100])
        self.assertEqual(q['p'], 11)
        self.assertEqual(q['cur'], 'GBP')
        self.assertEqual(q['d'], 10)
        self.assertEqual(q['prev'], 10)
        self.assertEqual(q['open'], 11)

    def test_yield_changes_are_basis_points(self):
        q = self.quote('US10Y', 'USD', [4.0, 4.1])
        self.assertEqual(q['p'], 4.1)
        self.assertEqual(q['d'], 10)

    def test_equity_changes_are_percent(self):
        q = self.quote('AAPL', 'USD', [100, 105])
        self.assertEqual(q['d'], 5)
        self.assertEqual(q['source'], 'Yahoo Finance')
        self.assertEqual(q['symbol'], 'AAPL')
        self.assertEqual(q['t'], 100)

    def test_failed_feed_does_not_manufacture_quote(self):
        with patch.object(market, 'from_yahoo', side_effect=ValueError('missing symbol')):
            s, q, intra, history, error = market.one('MISSING')
        self.assertIsNone(q)
        self.assertIn('missing symbol', error)


if __name__ == '__main__':
    unittest.main()
