"""Artifact verification uses synthetic SEC fixture pages, never network data."""
import copy
import gzip
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from test_v6_exhibits import ROW,PAGE,prepare
from tools.v6.exhibits import parse_index,index_url,metadata
from tools.v6.import_exhibits import merge


class ImportArtifact(unittest.TestCase):
    def archive(self,path,alter=None,raw=PAGE):
        r=parse_index(raw,ROW,index_url(ROW))
        if alter:alter(r)
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('2024-03.jsonl',json.dumps(r)+'\n')
            z.writestr(f"source/{ROW['adsh'][:10]}/{ROW['adsh']}.html.gz",gzip.compress(raw))
            z.writestr('runs.jsonl',json.dumps({'attempts':1,'indexes_cached':1,'exhibit_entries_added':2,'errors':0,'api_cost_usd':0})+'\n')

    def test_import_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'v6';base.mkdir();prepare(base);archive=Path(tmp)/'artifact.zip';self.archive(archive)
            self.assertEqual(merge(archive,base,'123')['exhibit_entries_imported'],2)
            self.assertEqual(merge(archive,base,'123')['filing_indexes_imported'],0)
            self.assertEqual(metadata(base)[ROW['adsh']]['github_run_id'],'123')

    def test_hash_tampering_is_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'v6';base.mkdir();archive=Path(tmp)/'artifact.zip'
            self.archive(archive,lambda r:r.update(source_sha256='0'*64))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):merge(archive,base,'123')
            self.assertEqual(metadata(base),{})

    def test_metadata_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'v6';base.mkdir();archive=Path(tmp)/'artifact.zip'
            self.archive(archive,lambda r:r['docs'][0].update(file='invented.htm'))
            with self.assertRaisesRegex(ValueError,'differs from source'):merge(archive,base,'123')
            self.assertEqual(metadata(base),{})

    def test_zip_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'artifact.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('../escape','invalid')
            with self.assertRaisesRegex(ValueError,'unsafe ZIP path'):merge(archive,Path(tmp)/'v6','123')


if __name__=='__main__':unittest.main()
