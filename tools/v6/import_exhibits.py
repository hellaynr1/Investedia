"""Import verified SEC discovery artifacts without refetching SEC or invoking a model.
python -m tools.v6.import_exhibits /path/to/v6-sec-exhibits.zip --run-id ID
"""
import argparse
import gzip
import hashlib
import json
import io
import re
import zipfile
from pathlib import Path
from tools.v6.exhibits import BASE,append_record,metadata,parse_index,index_url


def merge(archive,base=BASE,run_id=None):
    have=metadata(base);added=0;docs=0
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('duplicate ZIP paths')
        if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):raise ValueError('unsafe ZIP path')
        if sum(i.file_size for i in z.infolist())>100_000_000:raise ValueError('artifact exceeds import size limit')
        pending=[]
        for name in names:
            if not re.fullmatch(r'\d{4}-\d{2}\.jsonl',name):continue
            for line in z.read(name).decode().splitlines():
                r=json.loads(line)
                if r.get('status')!='complete':continue
                source_name=f"source/{r['adsh'][:10]}/{r['adsh']}.html.gz"
                if source_name not in names:raise ValueError('source evidence missing')
                packed=z.read(source_name)
                with gzip.GzipFile(fileobj=io.BytesIO(packed)) as f:raw=f.read(2_000_001)
                if len(raw)>2_000_000:raise ValueError('source exceeds capture limit')
                if hashlib.sha256(raw).hexdigest()!=r['source_sha256']:raise ValueError('source evidence hash mismatch')
                url=r['source_url'];parts=url.split('/');cik=parts[6]
                row={'adsh':r['adsh'],'filed':r['filed'],'ciks':[cik]}
                if index_url(row)!=url:raise ValueError('source URL does not match accession')
                verified=parse_index(raw,row,url)
                for key in ('docs','filing_accepted_at'):
                    if verified[key]!=r[key]:raise ValueError('artifact metadata differs from source evidence')
                old=have.get(r['adsh'])
                if old and old['status']=='complete':
                    if old['source_sha256']!=r['source_sha256']:raise ValueError('conflicting previously verified source')
                    continue
                pending.append((r,source_name,packed));have[r['adsh']]=r
        # Validate the complete archive before any cache writes.
        for r,name,packed in pending:
            path=base/'exhibits'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(packed)
            append_record(base,{**r,'github_run_id':run_id});added+=1;docs+=len(r['docs'])
        if 'runs.jsonl' in names:
            result=json.loads(z.read('runs.jsonl').decode().splitlines()[-1])
            result['github_run_id']=run_id
            path=base/'exhibits/runs.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('a') as f:f.write(json.dumps(result,sort_keys=True)+'\n')
    return {'filing_indexes_imported':added,'exhibit_entries_imported':docs,'github_run_id':run_id}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('archive',type=Path);ap.add_argument('--run-id',required=True)
    a=ap.parse_args();print(json.dumps(merge(a.archive,run_id=a.run_id)))


if __name__=='__main__':main()
