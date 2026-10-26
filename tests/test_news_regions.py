import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import update_globe_news as u


def c(i, region=None):
    return {'title': f't{i}', 'url': f'https://x/{i}', 'source': 's', 'published': '2026-10-26T00:00:00Z', 'kind': 'news', **({'region': region} if region else {})}


class Balance(unittest.TestCase):
    def test_reserved_slots_mix_regions_and_keep_the_limit(self):
        cands = [c(i) for i in range(200)] + [c(1000 + i, 'af') for i in range(30)] + [c(2000 + i, 'latam') for i in range(30)] + [c(3000 + i, 'me') for i in range(30)]
        out = u.balance(cands, 140)
        self.assertEqual(len(out), 140)
        regs = [x.get('region') for x in out]
        for r in ('af', 'latam', 'me'):
            self.assertEqual(regs.count(r), 14)

    def test_a_thin_region_does_not_block_the_others(self):
        cands = [c(i) for i in range(50)] + [c(900, 'af')] + [c(910 + i, 'latam') for i in range(40)]
        out = u.balance(cands, 60)
        regs = [x.get('region') for x in out]
        self.assertEqual(regs.count('af'), 1)
        self.assertEqual(regs.count('latam'), u.REGION_EACH)
        self.assertEqual(len(out), 60)

    def test_without_regional_candidates_nothing_changes(self):
        cands = [c(i) for i in range(30)]
        self.assertEqual(u.balance(cands, 20), cands[:20])

    def test_every_regional_feed_names_a_known_region(self):
        self.assertTrue(all(r in ('af', 'latam', 'me') for _, _, r in u.REGION_FEEDS))
        self.assertTrue(all(r in ('af', 'latam', 'me') for _, r in u.REGION_GDELT))


if __name__ == '__main__':
    unittest.main()
