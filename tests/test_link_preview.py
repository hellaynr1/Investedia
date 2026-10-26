import os, re, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LinkPreview(unittest.TestCase):
    def test_every_page_has_a_large_absolute_preview_image(self):
        pages = [f for f in os.listdir(ROOT) if re.fullmatch(r'[a-z0-9-]+\.html', f) and not f.startswith('google')]
        self.assertGreater(len(pages), 20)
        for f in pages:
            h = open(os.path.join(ROOT, f), encoding='utf-8').read()
            if 'http-equiv="refresh"' in h[:2000] and 'og:image' not in h:
                continue
            self.assertIn('property="og:image" content="https://investedia.com/assets/og-default.png"', h, f)
            self.assertIn('twitter:card" content="summary_large_image"', h, f)
            self.assertIn('og:image:width" content="1200"', h, f)

    def test_homepage_url_is_the_bare_domain(self):
        h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
        self.assertIn('property="og:url" content="https://investedia.com/"', h)

    def test_image_is_1200_by_630(self):
        from PIL import Image
        self.assertEqual(Image.open(os.path.join(ROOT, 'assets', 'og-default.png')).size, (1200, 630))


if __name__ == '__main__':
    unittest.main()
