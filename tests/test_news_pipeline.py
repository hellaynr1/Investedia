"""Regression tests for the two-tier news robot (update_globe_news.py). No network: every feed and every Gemini call is faked."""
import json, os, shutil, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_globe_news as u

NOW = u.NOW


def cand(i, title=None, kind='news', desc='', source='Source', published=None, url=None):
    return {'title': title or f'Story number {i}', 'url': url or f'https://news.example/a/{i}', 'source': source, 'kind': kind,
            'published': published or NOW.strftime('%Y-%m-%dT%H:%M:%SZ'), 'desc': desc}


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.g, self.d = os.path.join(self.dir, 'g'), os.path.join(self.dir, 'd')
        self._saved = (u.G, u.D, dict(u.SEEN), dict(u.status), list(u.status['errors']))
        u.G, u.D = self.g, self.d
        u.SEEN = {}
        u.status['errors'] = []

    def tearDown(self):
        u.G, u.D, u.SEEN = self._saved[0], self._saved[1], self._saved[2]
        u.status.clear(); u.status.update(self._saved[3]); u.status['errors'] = self._saved[4]
        shutil.rmtree(self.dir, ignore_errors=True)


class Normalisation(Base):
    def test_canonical_url_drops_tracking_www_and_trailing_slash(self):
        self.assertEqual(u.canon('https://www.Example.com/news/rate-cut/?utm_source=x&fbclid=y&id=7#top'),
                         u.canon('https://example.com/news/rate-cut?id=7'))
        self.assertEqual(u.canon('https://example.com/a/'), 'example.com/a')

    def test_title_words_ignore_short_words_and_stopwords(self):
        words = u.norm('The Fed says rate cut for the banks')
        self.assertIn('rate', words)
        self.assertNotIn('the', words)
        self.assertNotIn('says', words)

    def test_malformed_url_does_not_crash_canonicalisation(self):
        self.assertEqual(u.canon(''), '')


class Dedupe(Base):
    def test_same_article_with_tracking_parameters_is_one_item(self):
        a = cand(1, url='https://news.example/x?utm_campaign=a')
        b = cand(2, url='https://news.example/x?utm_campaign=b', title='Another headline entirely')
        self.assertEqual(len(u.dedupe([a, b], [])), 1)

    def test_near_identical_titles_from_different_publishers_collapse(self):
        a = cand(1, title='ECB holds rates steady as inflation cools', url='https://a.example/1')
        b = cand(2, title='ECB holds rates steady as inflation cools again', url='https://b.example/2')
        self.assertEqual(len(u.dedupe([a, b], [])), 1)

    def test_official_source_is_kept_before_news_copies(self):
        news = cand(1, title='Fed signals pause on rates', url='https://news.example/fed', kind='news')
        official = cand(2, title='Fed signals pause on rates', url='https://federalreserve.gov/fed', kind='official', source='Federal Reserve')
        kept = u.dedupe([news, official], [])
        self.assertEqual(kept[0]['kind'], 'official')

    def test_distinct_events_both_remain(self):
        a = cand(1, title='Oil prices jump after OPEC cuts output')
        b = cand(2, title='Japan bond yields hit a decade high')
        self.assertEqual(len(u.dedupe([a, b], [])), 2)

    def test_already_published_headline_is_not_repeated(self):
        a = cand(1, title='Nvidia shares fall after weak guidance')
        self.assertEqual(u.dedupe([a], ['Nvidia shares fall after weak guidance']), [])


class RelevanceGate(Base):
    def test_central_bank_and_macro_items_score_high(self):
        self.assertGreaterEqual(u.relevance(cand(1, title='Federal Reserve weighs rate cut as inflation eases')), u.PRIORITY_MIN_SCORE)

    def test_official_source_gets_a_bonus(self):
        plain = u.relevance(cand(1, title='Speech on the economy'))
        official = u.relevance(cand(2, title='Speech on the economy', kind='official'))
        self.assertEqual(official - plain, 2)

    def test_junk_scores_zero_and_never_reaches_the_editor(self):
        self.assertEqual(u.relevance(cand(1, title='Top stock to buy this week before the price target')), 0)

    def test_lifestyle_item_stays_below_the_gate(self):
        self.assertLess(u.relevance(cand(1, title='Best beaches to visit this summer')), u.PRIORITY_MIN_SCORE)


class FeedParsing(Base):
    RSS = """<rss><channel>
      <item><title>Fed holds rates</title><link>https://www.federalreserve.gov/x</link><pubDate>Tue, 27 Oct 2026 10:00:00 +0200</pubDate><description>&lt;p&gt;Holds at 4%&lt;/p&gt;</description></item>
      <item><title></title><link>https://no-title.example</link><pubDate>Tue, 27 Oct 2026 10:00:00 GMT</pubDate></item>
      <item><title>Future item</title><link>https://future.example/x</link><pubDate>Wed, 01 Jan 2031 00:00:00 GMT</pubDate></item>
      <item><title>Too old</title><link>https://old.example/x</link><pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate></item>
    </channel></rss>"""

    def fake_get(self, calls, body):
        def g(url, *a, **k):
            calls.append(url)
            if isinstance(body, Exception): raise body
            return body if isinstance(body, str) else body.decode()
        return g

    def test_timezone_offset_is_converted_and_bad_rows_are_skipped(self):
        real, calls = u.get, []
        u.get = self.fake_get(calls, self.RSS)
        try:
            out = [c for c in u.rss(priority=True) if c['title'] == 'Fed holds rates'][:1]
        finally:
            u.get = real
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['published'], '2026-10-27T08:00:00Z')  # +0200 converted to UTC
        self.assertEqual(out[0]['desc'], 'Holds at 4%')

    def test_stale_items_are_dropped_and_future_timestamps_are_clamped_to_now(self):
        real = u.get
        u.get = self.fake_get([], self.RSS)
        try:
            items = u.rss(priority=True)
        finally:
            u.get = real
        self.assertFalse(any(c['title'] == 'Too old' for c in items))
        future = [c for c in items if c['title'] == 'Future item']
        self.assertTrue(all(c['published'] <= NOW.strftime('%Y-%m-%dT%H:%M:%SZ') for c in items))
        self.assertTrue(future)  # the same fixture comes back from every feed, so one row per feed
        self.assertTrue(all(c['published'] == NOW.strftime('%Y-%m-%dT%H:%M:%SZ') for c in future))

    def test_priority_tier_requests_only_official_feeds_and_marketwatch(self):
        real, calls = u.get, []
        u.get = self.fake_get(calls, '<rss><channel/></rss>')
        try:
            u.rss(priority=True)
        finally:
            u.get = real
        allowed = {f[0] for f in u.FEEDS} | u.PRIORITY_NEWS
        self.assertTrue(calls)
        self.assertTrue(set(calls) <= allowed, set(calls) - allowed)
        self.assertNotIn('https://www.theguardian.com/business/rss', calls)

    def test_failed_source_is_logged_and_does_not_stop_the_run(self):
        real = u.get
        u.get = self.fake_get([], TimeoutError('feed down'))
        try:
            items = u.rss(priority=True)
        finally:
            u.get = real
        self.assertEqual(items, [])
        self.assertTrue(any('feed down' in e for e in u.status['errors']))


class AtomicSave(Base):
    def test_save_writes_valid_json_and_leaves_no_temporary_file(self):
        u.save('news-live.json', {'stories': [{'id': 'n1'}]})
        with open(os.path.join(self.g, 'news-live.json')) as f: self.assertEqual(json.load(f), {'stories': [{'id': 'n1'}]})
        self.assertFalse([n for n in os.listdir(self.g) if n.endswith('.tmp')])
        self.assertTrue(os.path.exists(os.path.join(self.d, 'news-live.json')))

    def test_empty_feed_never_replaces_working_news(self):
        u.save('news-live.json', {'stories': [{'id': 'keep'}]})
        u.save('news-live.json', {'stories': []})
        with open(os.path.join(self.g, 'news-live.json')) as f: self.assertEqual(json.load(f)['stories'][0]['id'], 'keep')

    def test_unserialisable_data_leaves_the_previous_file_intact(self):
        u.save('news-live.json', {'stories': [{'id': 'keep'}]})
        with self.assertRaises(TypeError): u.save('news-live.json', {'stories': [{'bad': object()}]})
        with open(os.path.join(self.g, 'news-live.json')) as f: self.assertEqual(json.load(f)['stories'][0]['id'], 'keep')


class SeenLedger(Base):
    def test_rejected_candidates_are_remembered_and_old_entries_expire(self):
        fresh = (NOW - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        old = (NOW - timedelta(days=u.SEEN_DAYS + 1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        u.save(u.SEEN_FILE, {'seen': {'recent': fresh, 'stale': old}})
        u.load_seen()
        self.assertIn('recent', u.SEEN)
        self.assertNotIn('stale', u.SEEN)

    def test_seen_key_is_stable_for_the_same_article(self):
        self.assertEqual(u.seen_key('https://www.x.example/a?utm_source=1'), u.seen_key('https://x.example/a'))

    def test_missing_ledger_starts_empty(self):
        u.load_seen()
        self.assertEqual(u.SEEN, {})


class EditorStep(Base):
    def test_failed_gemini_call_does_not_mark_items_seen(self):
        real = u.gemini
        u.gemini = lambda prompt: (_ for _ in ()).throw(RuntimeError('quota'))
        try:
            new = u.pick_stories([cand(1, desc='x' * 30)], {}, {}, {}, set(), 3, [])
        finally:
            u.gemini = real
        self.assertEqual(new, [])
        self.assertEqual(u.SEEN, {})
        self.assertTrue(any('quota' in e for e in u.status['errors']))

    def test_successful_call_marks_every_sent_candidate_seen(self):
        real = u.gemini
        u.gemini = lambda prompt: []  # editor ran and rejected everything
        try:
            u.pick_stories([cand(1, desc='x' * 30), cand(2, desc='y' * 30)], {}, {}, {}, set(), 3, [])
        finally:
            u.gemini = real
        self.assertEqual(len(u.SEEN), 2)

    def test_malformed_editor_output_is_dropped_safely(self):
        real = u.gemini
        u.gemini = lambda prompt: [None, {'members': 'nope'}, {'members': [0], 'country': 'ZZ', 'category': 'markets', 'lat': 1, 'lon': 1}]
        try:
            new = u.pick_stories([cand(1, desc='x' * 30)], {}, {}, {}, set(), 3, [])
        finally:
            u.gemini = real
        self.assertEqual(new, [])

    def test_impact_analysis_keeps_only_bounded_typed_rows(self):
        raw = {'impacts': [{'kind': 'country', 'name': 'Japan', 'country': 'JP', 'ticker': '^N225', 'direction': 'sideways', 'why': 'Yen moves.'},
                           {'kind': 'planet', 'name': 'Mars', 'country': 'XX', 'why': 'bad'}] + [{'kind': 'asset', 'name': f'a{i}', 'country': 'US', 'why': 'w'} for i in range(9)]}
        out = u.validate_analysis(raw, False, {'JP', 'US'})
        self.assertEqual(len(out['impacts']), 4)
        self.assertEqual(out['impacts'][0]['direction'], 'unclear')
        self.assertIsNone(out['why_moved'])


class Balance(Base):
    def test_balance_handles_empty_input(self):
        self.assertEqual(u.balance([]), [])


if __name__ == '__main__':
    unittest.main()
