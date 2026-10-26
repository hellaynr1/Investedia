import os, sys, unittest
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_track_backfill as b

ts = lambda y, m, d, h=13: int(datetime(y, m, d, h, 30, tzinfo=timezone.utc).timestamp())
BARS = [[ts(2026, 10, 19), 0, 0, 0, 100.0, 0], [ts(2026, 10, 20), 0, 0, 0, 100.0, 0], [ts(2026, 10, 21), 0, 0, 0, 103.0, 0], [ts(2026, 10, 22), 0, 0, 0, 102.0, 0]]


class Daily(unittest.TestCase):
    def test_uses_the_article_day_close_then_the_next_close(self):
        self.assertEqual(b.judge_daily(ts(2026, 10, 20, 15), 'up', BARS), (3.0, 'hit'))
        self.assertEqual(b.judge_daily(ts(2026, 10, 20, 15), 'down', BARS), (3.0, 'miss'))
        self.assertEqual(b.judge_daily(ts(2026, 10, 21, 15), 'down', BARS), (-0.97, 'hit'))

    def test_small_moves_are_no_clear_move(self):
        bars = [[ts(2026, 10, 20), 0, 0, 0, 100.0, 0], [ts(2026, 10, 21), 0, 0, 0, 100.2, 0]]
        self.assertEqual(b.judge_daily(ts(2026, 10, 20), 'up', bars)[1], 'flat')

    def test_not_judged_until_the_next_session_exists(self):
        self.assertIsNone(b.judge_daily(ts(2026, 10, 22, 15), 'up', BARS))

    def test_article_on_a_non_session_day_uses_the_last_close_before_it(self):
        sat = ts(2026, 10, 24, 10)
        bars = BARS + [[ts(2026, 10, 26), 0, 0, 0, 110.0, 0]]
        self.assertEqual(b.judge_daily(sat, 'up', bars), (7.84, 'hit'))

    def test_run_skips_young_articles_and_never_adds_twice(self):
        import json, tempfile
        d = tempfile.mkdtemp(); g = os.path.join(d, 'g'); h = os.path.join(d, 'h'); os.makedirs(g); os.makedirs(h)
        json.dump({'assets': [{'s': 'AAA', 'site': 'AAA', 'n': 'Aaa'}]}, open(os.path.join(g, 'markets.json'), 'w'))
        json.dump({'daily': BARS}, open(os.path.join(h, 'AAA.json'), 'w'))
        st = lambda i, t: {'id': i, 'published_at': t, 'headline': 'x', 'impacts': [{'ticker': 'AAA', 'name': 'Aaa', 'direction': 'up'}]}
        json.dump({'stories': [st('old', '2026-10-20T15:00:00Z'), st('young', '2026-10-24T10:00:00Z')]}, open(os.path.join(g, 'news-archive.json'), 'w'))
        b.G, b.HIST = g, h
        now = datetime(2026, 10, 22, 16, tzinfo=timezone.utc)  # 'old' is 49 h old: still the live recorder's
        self.assertEqual(b.run(False, now)[0], 0)
        now = datetime(2026, 10, 24, 16, tzinfo=timezone.utc)
        n, led = b.run(True, now)
        self.assertEqual(n, 1)
        self.assertEqual(led['calls'][0]['basis'], 'daily')
        self.assertEqual(b.run(True, now)[0], 0)


if __name__ == '__main__':
    unittest.main()
