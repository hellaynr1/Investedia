"""Free SEC Exhibit 99 discovery, separate from paid fact extraction.
python3 -m tools.v6.exhibits --import-legacy --minutes 10 --max-filings 500
Raw index files stay untouched. Successful accession metadata is cached and reused.
"""
import argparse
import gzip
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/v6'
UA = 'InvestediaResearch/1.0 (+https://investedia.com; info@investedia.com)'
ITEMS = {'2.02','1.01','2.01','5.02','7.01','8.01','1.02','2.05','2.06','3.01','4.02'}
EX99 = re.compile(r'^EX-99(?:[.\-]\d+)*$',re.I)


def now():return datetime.now(timezone.utc).isoformat()


def acceptance(value):
    """SEC displayed acceptance clocks are America/New_York, not UTC."""
    dt=datetime.strptime(value,'%Y%m%d%H%M%S' if value.isdigit() else '%Y-%m-%d %H:%M:%S')
    return dt.replace(tzinfo=ZoneInfo('America/New_York')).astimezone(timezone.utc).isoformat()


class IndexParser(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=None;self.cell=None;self.text=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='tr':self.row=[]
        if tag in ('td','th') and self.row is not None:self.cell={'text':'','links':[]}
        if tag=='a' and self.cell is not None and attrs.get('href'):self.cell['links'].append(attrs['href'])
    def handle_data(self,data):
        self.text.append(data)
        if self.cell is not None:self.cell['text']+=data
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.cell['text']=' '.join(self.cell['text'].split())
            self.row.append(self.cell);self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row);self.row=None


def index_url(row):
    adsh=row['adsh']
    if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',adsh):raise ValueError('invalid accession')
    cik=str(int(row['ciks'][0]))
    return f'https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace("-","")}/{adsh}-index.html'


def parse_index(raw,row,url):
    text=raw.decode('utf-8',errors='replace');p=IndexParser();p.feed(text)
    all_text=' '.join(' '.join(p.text).split())
    match=re.search(r'Accepted\s+(\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d)',all_text)
    if row['adsh'] not in text or not match:
        raise ValueError('not the expected SEC filing index or acceptance time absent')
    docs=[];primary=False
    for cells in p.rows:
        if len(cells)<4:continue
        kind=cells[3]['text'].upper()
        if kind in ('8-K','8-K/A'):primary=True
        if not EX99.fullmatch(kind):continue
        for link in cells[2]['links']:
            target=urllib.parse.urlparse(urllib.parse.urljoin(url,link))
            # SEC sometimes wraps an inline exhibit link in its own iXBRL viewer.
            # Resolve only the SEC viewer's document parameter, then apply the same
            # host/accession checks as direct attachment links.
            if target.hostname=='www.sec.gov' and target.path.rstrip('/') in ('/ix','/ixviewer/doc/action'):
                documents=urllib.parse.parse_qs(target.query).get('doc',[])
                if len(documents)!=1:raise ValueError('ambiguous SEC viewer document')
                target=urllib.parse.urlparse(urllib.parse.urljoin(url,documents[0]))
            path=urllib.parse.unquote(target.path)
            attachment=re.fullmatch(r'/Archives/edgar/data/(\d+)/('+row['adsh'].replace('-','')+r')/([A-Za-z0-9_.\-]+)',path)
            if target.hostname!='www.sec.gov' or not attachment or target.query or target.fragment:
                # Preserve the link shape for review when an official index uses
                # an unexpected wrapper. Never follow an unverified target.
                raise ValueError('attachment outside expected SEC accession: '+link[:300])
            filename=attachment.group(3)
            doc={'file':filename,'type':kind,'description':cells[1]['text']}
            if int(attachment.group(1))!=int(row['ciks'][0]):doc['cik']=attachment.group(1)
            if doc not in docs:docs.append(doc)
    if not primary:raise ValueError('primary 8-K document table absent')
    return {'adsh':row['adsh'],'filed':row['filed'],'status':'complete',
            'filing_accepted_at':acceptance(match.group(1)), 'docs':docs,
            'source_url':url,'source_sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':now()}


def metadata(base=BASE):
    result={}
    for path in sorted((base/'exhibits').glob('????-??.jsonl')):
        for line in path.read_text().splitlines():
            r=json.loads(line);old=result.get(r['adsh'])
            if old is None or old['status']!='complete':result[r['adsh']]=r
    return result


def filings(base=BASE):
    extra=metadata(base);seen=set()
    for path in sorted((base/'index').glob('8k-*.jsonl.gz')):
        with gzip.open(path,'rt') as f:
            for line in f:
                r=json.loads(line);a=r['adsh']
                if a in seen:continue
                seen.add(a)
                if a in extra:
                    e=extra[a];r={**r,'filing_accepted_at':e['filing_accepted_at'],'exhibit_discovery':{k:v for k,v in e.items() if k!='docs'}}
                    docs=list(r.get('docs') or [])
                    for doc in e.get('docs',[]):
                        if not any(d.get('file')==doc['file'] and d.get('type')==doc['type'] for d in docs):docs.append(doc)
                    r['docs']=docs
                yield r


def append_record(base,record):
    path=base/'exhibits'/f"{record['filed'][:7]}.jsonl";path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')


def import_legacy(base=BASE,legacy=ROOT/'research/sec'):
    """Reuse acceptance clocks, but never invent filenames or promote truncated text."""
    have=metadata(base);wanted={r['adsh']:r for r in filings(base)};count=snippets=0
    for path in sorted(legacy.glob('8k-*.jsonl.gz')):
        with gzip.open(path,'rt') as f:
            for line in f:
                r=json.loads(line);a=r['acc']
                if a in have or a not in wanted or not r.get('accepted'):continue
                e={'adsh':a,'filed':wanted[a]['filed'],'status':'acceptance-only','docs':[],
                   'filing_accepted_at':acceptance(r['accepted']),
                   'source_kind':'legacy-sec-harvest','source_file':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name,
                   'source_row_sha256':hashlib.sha256(line.encode()).hexdigest(),
                   'legacy_excerpt_chars':len(r.get('text') or '')}
                append_record(base,e);have[a]=e;count+=1;snippets+=bool(r.get('text'))
    return {'acceptance_timestamps_imported':count,'legacy_truncated_excerpts_not_promoted':snippets}


def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=25) as response:
        raw=response.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError('filing index exceeds size limit')
    return raw


def run(base,minutes,max_filings,fetcher=fetch,start='2022-01-01',end='2026-10-20'):
    have=metadata(base);deadline=time.monotonic()+minutes*60;last=0;attempts=complete=exhibits=errors=0
    candidates=sorted((r for r in filings(base) if r.get('tickers') and set(r.get('items') or [])&ITEMS
                       and start<=r.get('filed','')<=end),key=lambda r:('2.02' not in r['items'],r['filed'],r['adsh']))
    failure=None;failures=[]
    for r in candidates:
        if have.get(r['adsh'],{}).get('status')=='complete':continue
        if attempts>=max_filings or time.monotonic()>=deadline:break
        # Two requests per second, well below SEC's published aggregate limit.
        delay=.5-(time.monotonic()-last)
        if delay>0:time.sleep(delay)
        last=time.monotonic();attempts+=1
        try:
            url=index_url(r);raw=fetcher(url);entry=parse_index(raw,r,url)
            source=base/'exhibits'/'source'/r['adsh'][:10]/f"{r['adsh']}.html.gz"
            source.parent.mkdir(parents=True,exist_ok=True)
            source.write_bytes(gzip.compress(raw,mtime=0))
            append_record(base,entry);have[r['adsh']]=entry;complete+=1;exhibits+=len(entry['docs'])
        except (ValueError,KeyError,IndexError,urllib.error.URLError,TimeoutError) as exc:
            errors+=1;failure={'adsh':r['adsh'],'error':str(exc),'at':now()};failures.append(failure)
            # Access denials are not successful "no exhibits" results. Stop instead of hammering SEC.
            if (isinstance(exc,urllib.error.HTTPError) and exc.code in (403,429)) or re.search(r'\b(403|429)\b',str(exc)):break
            if errors>=3:break
        if complete and complete%100==0:print(f'{complete} indexes cached; {exhibits} Exhibit 99 entries',flush=True)
    summary={'at':now(),'attempts':attempts,'indexes_cached':complete,'exhibit_entries_added':exhibits,
             'errors':errors,'last_error':failure,'failures':failures,'api_cost_usd':0}
    path=base/'exhibits'/'runs.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:f.write(json.dumps(summary,sort_keys=True)+'\n')
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base',type=Path,default=BASE);ap.add_argument('--minutes',type=float,default=10)
    ap.add_argument('--max-filings',type=int,default=500);ap.add_argument('--import-legacy',action='store_true')
    ap.add_argument('--from',dest='start',default='2022-01-01');ap.add_argument('--to',dest='end',default='2026-10-20')
    a=ap.parse_args()
    if a.minutes<0 or a.max_filings<0:ap.error('limits must be nonnegative')
    if a.import_legacy:print(json.dumps(import_legacy(a.base)),flush=True)
    print(json.dumps(run(a.base,a.minutes,a.max_filings,start=a.start,end=a.end)),flush=True)


if __name__=='__main__':main()
