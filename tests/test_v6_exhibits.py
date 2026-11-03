"""Synthetic SEC index fixtures only; no requests or model API calls in tests."""
import copy
import gzip
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
from tools.v6.exhibits import parse_index,index_url,acceptance,run,filings,import_legacy,metadata
from tools.v6.claude_extract import candidates,fetch_texts

ROW={'adsh':'0000000001-24-000001','filed':'2024-03-12','ciks':['0000000001'],
     'tickers':['TEST'],'items':['2.02'],'docs':[{'file':'main.htm','type':'8-K'}]}
PAGE='''<html><h1>0000000001-24-000001</h1><div>Accepted</div><div>2024-03-12 16:05:00</div>
<table><tr><th>Seq</th><th>Description</th><th>Document</th><th>Type</th><th>Size</th></tr>
<tr><td>1</td><td>Main</td><td><a href="main.htm">main.htm</a></td><td>8-K</td><td>100</td></tr>
<tr><td>2</td><td>Investor presentation</td><td><a href="slides.htm">slides.htm</a></td><td>EX-99.2</td><td>100</td></tr>
<tr><td>3</td><td>Press release</td><td><a href="release.htm">release.htm</a></td><td>EX-99.1</td><td>100</td></tr>
</table></html>'''.encode()


def prepare(base):
    (base/'index').mkdir()
    with gzip.open(base/'index/8k-2024-03.jsonl.gz','wt') as f:f.write(json.dumps(ROW)+'\n')


class Exhibits(unittest.TestCase):
    def test_verified_docs_and_acceptance_dst(self):
        r=parse_index(PAGE,ROW,index_url(ROW))
        self.assertEqual(len(r['docs']),2)
        self.assertEqual(r['filing_accepted_at'],'2024-03-12T20:05:00+00:00')
        self.assertEqual(acceptance('20240112160500'),'2024-01-12T21:05:00+00:00')
        self.assertEqual(len(r['source_sha256']),64)

    def test_access_denial_not_successful_no_exhibits(self):
        for page in (b'Access denied',b'<html>SEC.gov rate limit</html>',PAGE.replace(b'0000000001-24-000001',b'0000000002-24-000001')):
            with self.assertRaises(ValueError):parse_index(page,ROW,index_url(ROW))

    def test_no_exhibit_is_valid_only_with_primary_document(self):
        text=PAGE.decode();text=text[:text.index('<tr><td>2')]+ '</table></html>'
        self.assertEqual(parse_index(text.encode(),ROW,index_url(ROW))['docs'],[])
        with self.assertRaises(ValueError):parse_index(PAGE.replace(b'>8-K<',b'>other<'),ROW,index_url(ROW))

    def test_external_or_wrong_accession_link_rejected(self):
        for target in (b'https://evil.example/release.htm',b'/Archives/edgar/data/2/other/release.htm',b'../release.htm'):
            with self.assertRaises(ValueError):parse_index(PAGE.replace(b'href="release.htm"',b'href="'+target+b'"'),ROW,index_url(ROW))

    def test_sec_inline_viewer_link_resolves_to_verified_attachment(self):
        path=index_url(ROW).rsplit('/',1)[0].replace('https://www.sec.gov','')+'/release.htm'
        wrapped=PAGE.replace(b'href="release.htm"',f'href="/ix?doc={path}"'.encode())
        self.assertEqual(parse_index(wrapped,ROW,index_url(ROW))['docs'][-1]['file'],'release.htm')

    def test_sec_viewer_cannot_escape_host_or_accession(self):
        for target in ('https://evil.example/release.htm','/Archives/edgar/data/2/other/release.htm'):
            wrapped=PAGE.replace(b'href="release.htm"',f'href="/ix?doc={target}"'.encode())
            with self.assertRaises(ValueError):parse_index(wrapped,ROW,index_url(ROW))

    def test_sec_cross_filer_cik_keeps_exact_accession(self):
        accession=ROW['adsh'].replace('-','')
        link=f'/Archives/edgar/data/4515/{accession}/release.htm'
        page=PAGE.replace(b'href="release.htm"',f'href="{link}"'.encode())
        doc=parse_index(page,ROW,index_url(ROW))['docs'][-1]
        self.assertEqual(doc['cik'],'4515')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);prepare(base)
            self.assertEqual(run(base,1,1,fetcher=lambda url:page)['indexes_cached'],1)
            selected=list(candidates(base))[0][0]
            self.assertEqual(selected['exhibit_cik'],'4515')
            urls=[]
            def fake_sec(url):urls.append(url);return '<p>Original release</p>'
            with patch('tools.v6.claude_extract.sec',side_effect=fake_sec),patch('tools.v6.claude_extract.text_path',return_value=str(base/'release.txt.gz')):
                self.assertEqual(fetch_texts([(selected,'release.htm')]),1)
            self.assertIn('/data/4515/'+accession+'/release.htm',urls[0])
        wrong=link.replace(accession,'000000000124000002')
        with self.assertRaises(ValueError):parse_index(PAGE.replace(b'href="release.htm"',f'href="{wrong}"'.encode()),ROW,index_url(ROW))

    def test_cache_resume_and_original_index_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);prepare(base);original=(base/'index/8k-2024-03.jsonl.gz').read_bytes()
            calls=[]
            def fetch(url):calls.append(url);return PAGE
            first=run(base,1,1,fetcher=fetch);second=run(base,1,1,fetcher=fetch)
            self.assertEqual(first['exhibit_entries_added'],2);self.assertEqual(second['attempts'],0)
            self.assertEqual(len(calls),1)
            self.assertEqual((base/'index/8k-2024-03.jsonl.gz').read_bytes(),original)
            self.assertEqual(len(list(filings(base))[0]['docs']),3)
            self.assertEqual(list(candidates(base))[0][1],'release.htm')

    def test_network_error_does_not_mark_accession_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);prepare(base)
            def blocked(url):raise urllib.error.HTTPError(url,403,'Forbidden',{},None)
            r=run(base,1,1,fetcher=blocked)
            self.assertEqual(r['errors'],1);self.assertEqual(metadata(base),{})
            self.assertEqual(run(base,1,1,fetcher=lambda url:PAGE)['indexes_cached'],1)

    def test_legacy_acceptance_import_does_not_invent_exhibit_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/'v6';base.mkdir();prepare(base);legacy=Path(tmp)/'legacy';legacy.mkdir()
            r={'acc':ROW['adsh'],'accepted':'20240312160500','text':'Truncated old excerpt'}
            with gzip.open(legacy/'8k-2024Q1.jsonl.gz','wt') as f:f.write(json.dumps(r)+'\n')
            self.assertEqual(import_legacy(base,legacy)['acceptance_timestamps_imported'],1)
            self.assertEqual(import_legacy(base,legacy)['acceptance_timestamps_imported'],0)
            self.assertEqual(list(candidates(base)),[])
            self.assertEqual(metadata(base)[ROW['adsh']]['status'],'acceptance-only')
            self.assertEqual(run(base,1,1,fetcher=lambda url:PAGE)['indexes_cached'],1)
            self.assertEqual(len(list(candidates(base))),1)

    def test_fetch_only_never_imports_anthropic(self):
        import sys
        from tools.v6 import claude_extract
        with patch.object(sys,'argv',['claude_extract','--fetch-only']),patch.object(claude_extract,'candidates',return_value=iter([])),patch.object(claude_extract,'fetch_texts',return_value=0):
            with patch.dict(sys.modules,{'anthropic':None}):claude_extract.main()


if __name__=='__main__':unittest.main()
