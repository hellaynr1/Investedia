import json, os, tempfile, unittest
from datetime import datetime, timezone, timedelta
import update_news_track as t

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def story(ticker, hours_ago):
    return {'published_at': (NOW - timedelta(hours=hours_ago)).strftime('%Y-%m-%dT%H:%M:%SZ'), 'impacts': [{'ticker': ticker}]}


class Track(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        t.G = self.dir

    def write(self, name, obj):
        with open(os.path.join(self.dir, name), 'w') as f:
            json.dump(obj, f)

    def test_resolve_uses_site_aliases(self):
        known = {'BTC-USD', 'EURUSD', 'META'}
        self.assertEqual(t.resolve('btc', known), 'BTC-USD')
        self.assertEqual(t.resolve('EURUSD=X', known), 'EURUSD')
        self.assertEqual(t.resolve('meta', known), 'META')
        self.assertIsNone(t.resolve('NOPE', known))
        self.assertIsNone(t.resolve(None, known))

    def test_only_recent_stories_count(self):
        known = {'A', 'B'}
        self.assertEqual(t.tracked_symbols([story('A', 5), story('B', 100)], known, NOW), {'A'})

    def test_adds_one_point_per_new_asof_and_not_twice(self):
        self.write('markets.json', {'asof': '2026-10-26T11:50:00+00:00', 'assets': [{'s': 'A', 'p': 10.123456789}]})
        self.write('news-live.json', {'stories': [story('A', 2)]})
        data, note = t.update(NOW)
        self.assertEqual(list(data['s']), ['A'])
        self.assertEqual(len(data['s']['A']), 1)
        self.assertEqual(data['s']['A'][0][1], 10.1235)
        self.write('news-track.json', data)
        data2, note2 = t.update(NOW)
        self.assertEqual(note2, 'unchanged')
        self.assertEqual(len(data2['s']['A']), 1)
        self.write('markets.json', {'asof': '2026-10-26T12:05:00+00:00', 'assets': [{'s': 'A', 'p': 10.5}]})
        data3, _ = t.update(NOW + timedelta(minutes=6))
        self.assertEqual([p[1] for p in data3['s']['A']], [10.1235, 10.5])

    def test_drops_old_points_and_unreferenced_assets(self):
        self.write('markets.json', {'asof': '2026-10-26T12:00:00+00:00', 'assets': [{'s': 'A', 'p': 1.0}, {'s': 'B', 'p': 2.0}]})
        self.write('news-live.json', {'stories': [story('A', 1)]})
        old_min = int((NOW - timedelta(hours=80)).timestamp() // 60)
        self.write('news-track.json', {'asof': 'x', 's': {'A': [[old_min, 0.9]], 'B': [[old_min, 2.0]]}})
        data, _ = t.update(NOW)
        self.assertEqual(list(data['s']), ['A'])
        self.assertEqual([p[1] for p in data['s']['A']], [1.0])

    def test_no_prices_keeps_previous(self):
        self.write('news-live.json', {'stories': [story('A', 1)]})
        data, note = t.update(NOW)
        self.assertIsNone(data)

    def test_news_prices_file_is_used_for_assets_missing_from_markets(self):
        self.write('markets.json', {'asof': '2026-10-26T12:00:00+00:00', 'assets': [{'s': 'A', 'p': 1.0}]})
        self.write('news-prices.json', {'assets': {'EB5.SI': {'p': 3.64}}})
        self.write('news-live.json', {'stories': [story('EB5.SI', 1)]})
        data, _ = t.update(NOW)
        self.assertEqual(data['s']['EB5.SI'][0][1], 3.64)


if __name__ == '__main__':
    unittest.main()
