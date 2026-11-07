"""Verify real historical outputs, source identity and generator reproducibility."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class HistoryConnections(unittest.TestCase):
    def test_provenance_and_reproduction(self):
        live = (ROOT / 'assets/globe/connections.json').read_bytes()
        files = sorted((ROOT / 'assets/globe/connections-history').glob('*.json'))
        self.assertTrue(files)
        hashes = {p: hashlib.sha256(p.read_bytes()).digest() for p in files}
        for path in files:
            data = json.loads(path.read_text())
            ids = {e['id'] for e in json.loads((ROOT / 'assets/globe/events' / path.name).read_text())['events']}
            self.assertEqual(data['day'], path.stem)
            self.assertEqual(path.read_bytes(), (ROOT / 'docs' / path.relative_to(ROOT)).read_bytes())
            for conn in data['connections']:
                self.assertIn(conn['event'], ids)
                self.assertGreaterEqual(conn['km'], 100)
                self.assertGreaterEqual(conn['confidence'], .25)
                self.assertNotEqual(conn['type'], 'sector')
                self.assertTrue(conn['evidence']['source'])
                self.assertTrue(conn['explanation'])
        subprocess.run(['python3', 'tools/globe-news/connections.py'], cwd=ROOT,
                       env={**os.environ, 'CONN_HISTORY': '1', 'PYTHONHASHSEED': '103'}, check=True, capture_output=True)
        self.assertEqual(live, (ROOT / 'assets/globe/connections.json').read_bytes())
        self.assertEqual(hashes, {p: hashlib.sha256(p.read_bytes()).digest() for p in files})

if __name__ == '__main__': unittest.main()
