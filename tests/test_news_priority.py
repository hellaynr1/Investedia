"""Offline checks for free collection, relevance and bounded AI usage."""
import json
import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import news_rules as rules
import update_globe_news as robot

class PriorityNews(unittest.TestCase):
    def test_major_and_minor(self):
        for title in ['Fed announces rate cut', 'US CPI inflation data rises unexpectedly',
                      'NVIDIA earnings beat estimates', 'Government imposes tariffs on imported steel',
                      'Parliament approves budget tax cuts', 'Oil supply disruption closes shipping route',
                      'Stocks plunge after sanctions announcement']:
            self.assertTrue(rules.classify(title)['summary_priority'], title)
        self.assertFalse(rules.classify('Small company earnings beat estimates')['summary_priority'])
        self.assertFalse(rules.classify('Apple releases new product with revenue outlook')['summary_priority'])
        self.assertIsNone(rules.classify('Celebrity wins football election'))
        self.assertIsNone(rules.classify('Presidential election result announced'))
        self.assertEqual(rules.classify('Election results raise uncertainty for economy')['category'], 'geopolitics')

    def test_multiple_exposures_no_direction_guesses(self):
        rows = rules.rule_impacts('Oil shipping supply disruption')
        self.assertTrue({'Crude oil', 'Airlines', 'Shipping companies'} <= {r['name'] for r in rows})
        self.assertTrue(all(r['direction'] == 'unclear' and r['country'] is None for r in rows))
        self.assertEqual(rules.rule_impacts('Unclassified market story'), [])
        names = {r['name'] for r in rules.entities_for('Apple earnings beat estimates')}
        self.assertIn('Apple Inc', names)

    def test_headlines_survive_without_any_keys(self):
        box, countries, symbols = robot.load_ref()
        candidates = [{'title': 'Oil supply disruption hits markets', 'url': 'https://example.org/story',
                       'source': 'Example', 'published': robot.ISO_NOW, 'kind': 'news'}]
        with patch.object(robot, 'get', side_effect=AssertionError('no provider calls')), patch.object(robot, 'gemini', side_effect=AssertionError('no AI')):
            stories = robot.pick_stories(candidates, box, countries, symbols, set(countries), 30)
        self.assertEqual(len(stories), 1)
        self.assertFalse(stories[0]['ai_summary'])
        self.assertIsNone(stories[0]['location']['lat'])
        self.assertTrue(stories[0]['impacts'])

    def test_no_ai_without_free_project_confirmation(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(robot, 'get', side_effect=AssertionError('no API')):
            self.assertEqual(robot.enrich_major([{'summary_priority': True}]), 0)

    def test_failed_attempt_reserved_and_caps_persist(self):
        story = {'id': 'one', 'headline': 'Fed announces rate cut', 'published_at': robot.ISO_NOW, 'summary_priority': True}
        config = {'NEWS_FREE_TIER_CONFIRMED':'true', 'NEWS_FREE_MODEL':'test-flash', 'NEWS_AI_DAILY_CAP':'1'}
        with tempfile.TemporaryDirectory() as temp, patch.object(robot, 'G', temp), patch.object(robot, 'D', temp), patch.object(robot, 'GEMINI', 'test'), patch.dict(os.environ, config), patch.object(robot, 'get', side_effect=RuntimeError('offline')) as api:
            self.assertEqual(robot.enrich_major([story]), 0)
            self.assertEqual(json.loads((Path(temp)/'news-ai-usage.json').read_text())['attempts'], 1)
            self.assertEqual(robot.enrich_major([story]), 0)
            self.assertEqual(api.call_count, 1)

    def test_summary_batch_major_only_and_known_ids(self):
        stories = [{'id': str(i), 'headline': 'Headline', 'summary_priority': i != 0, 'published_at': robot.ISO_NOW, 'summary': ''} for i in range(8)]
        response = {'candidates':[{'content':{'parts':[{'text':json.dumps([{'id':'7','summary':'A short factual summary.','why':'Context.'}, {'id':'unknown','summary':'ignore'}])}]}}]}
        with tempfile.TemporaryDirectory() as temp, patch.object(robot, 'G', temp), patch.object(robot, 'D', temp), patch.object(robot, 'GEMINI', 'test'), patch.dict(os.environ, {'NEWS_FREE_TIER_CONFIRMED':'true','NEWS_FREE_MODEL':'test-flash'}), patch.object(robot, 'get', return_value=json.dumps(response)) as api:
            robot.enrich_major(stories)
            request = json.loads(api.call_args.kwargs['data'])
            inputs = json.loads(request['contents'][0]['parts'][0]['text'].split('Stories:\n')[1])
            self.assertEqual(len(inputs), 4)
            self.assertNotIn('0', [s['id'] for s in inputs])

if __name__ == '__main__': unittest.main()
