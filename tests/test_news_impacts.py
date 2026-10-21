"""Offline impact validation against the existing feed. Never calls Gemini or edits it."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('news_robot', ROOT / 'update_globe_news.py')
robot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(robot)
ISO = set(json.loads((ROOT / 'tools/globe-news/iso.json').read_text()).values())
FEED = json.loads((ROOT / 'assets/globe/news-live.json').read_text())
FIXTURE = json.loads((ROOT / 'tests/fixtures/impacts-response.json').read_text())

class NewsImpacts(unittest.TestCase):
    def test_typed_bounded_fields(self):
        robot.PROMPT.format(n=1, cats='markets', topics='oil', cands='[]')
        raw = copy.deepcopy(FIXTURE[0])
        raw['impacts'] = [None, {'kind': []}, {**raw['impacts'][0], 'country': 'ZZ'},
            {**raw['impacts'][0], 'direction': ['bad'], 'why': 'x' * 300, 'ticker': '<script>'}] + raw['impacts'] * 3
        result = robot.validate_analysis(raw, True, ISO)
        self.assertEqual(len(result['impacts']), 4)
        self.assertEqual(result['impacts'][0]['direction'], 'unclear')
        self.assertEqual(len(result['impacts'][0]['why']), 200)
        self.assertIsNone(result['impacts'][0]['ticker'])
        self.assertTrue(all(i['country'] in ISO for i in result['impacts']))
        self.assertIsNone(robot.validate_analysis(raw, False, ISO)['why_moved'])

    def test_missing_or_malformed_analysis(self):
        for raw in (None, [], {}, {'impacts': 'bad'}, {'impacts': [7, {}]}):
            self.assertEqual(robot.validate_analysis(raw, False, ISO), {'impacts': [], 'why_moved': None})

    def test_backfill_existing_feed_max_40_and_known_ids_only(self):
        stories = copy.deepcopy(FEED['stories'])
        for s in stories: s.pop('impacts', None)
        calls = []
        def fake(prompt):
            calls.append(prompt)
            inputs = json.loads(prompt.split('Stories:\n', 1)[1])
            rows = []
            for s in inputs:
                row = copy.deepcopy(FIXTURE[0]); row['id'] = s['id']; rows.append(row)
            return [{'id': [], 'impacts': []}, {'id': 'unknown', 'impacts': []}] + rows
        n = robot.backfill_impacts(stories, ISO, fake)
        self.assertEqual(n, min(40, len(stories)))
        self.assertEqual(len(calls), 1)
        self.assertTrue(all('impacts' not in s for s in stories[40:]))
        for before, after in zip(FEED['stories'], stories):
            self.assertEqual(before['headline'], after['headline'])
            self.assertEqual(before['summary'], after['summary'])
            self.assertEqual(before['sources'], after['sources'])
            if not after.get('market_moving'): self.assertIsNone(after.get('why_moved'))

    def test_failure_does_not_mark_stories_complete(self):
        stories = copy.deepcopy(FEED['stories'][:2]); before = copy.deepcopy(stories)
        def fail(_): raise RuntimeError('offline fixture failure')
        self.assertEqual(robot.backfill_impacts(stories, ISO, fail), 0)
        self.assertEqual(stories, before)
        self.assertEqual(robot.backfill_impacts(stories, ISO, lambda _: {'bad': True}), 0)
        self.assertEqual(stories, before)

    def test_main_pipeline_uses_fake_response_and_memory_only(self):
        writes = {}
        def fake(prompt):
            inputs = json.loads(prompt.split('Stories:\n', 1)[1])
            return [{**copy.deepcopy(FIXTURE[0]), 'id': s['id']} for s in inputs]
        latest = max(robot.datetime.fromisoformat(s['published_at'].replace('Z', '+00:00')) for s in FEED['stories'])
        before = (ROOT / 'assets/globe/news-live.json').read_bytes()
        with patch.object(robot, 'gdelt', return_value=[]), patch.object(robot, 'rss', return_value=[]), \
             patch.object(robot, 'gemini', side_effect=fake), patch.object(robot, 'save', side_effect=lambda n,v:writes.update({n:v})), \
             patch.object(robot, 'NOW', latest):
            robot.main()
        self.assertIn('news-live.json', writes)
        self.assertLessEqual(sum('impacts' in s for s in writes['news-live.json']['stories']), 40)
        self.assertEqual((ROOT / 'assets/globe/news-live.json').read_bytes(), before)

if __name__ == '__main__': unittest.main()
