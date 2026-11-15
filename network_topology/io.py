"""Bounded strict JSON, exclusive review bundles, deterministic recomputation."""
import hashlib
import json
from html import escape
from pathlib import Path
import platform
import shutil
from .analysis import analyze

LIMIT=4*1024*1024
FILES={'input.json','report.json','review.html','manifest.json'}

def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False,ensure_ascii=True)+'\n').encode()

def load(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>LIMIT:raise ValueError('bounded regular JSON file required')
    raw=path.read_bytes()
    if len(raw)>LIMIT:raise ValueError('input exceeds size limit')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    value=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
    pending=[(value,0)]
    while pending:
        v,d=pending.pop()
        if d>32:raise ValueError('JSON nesting limit')
        if isinstance(v,dict):pending.extend((x,d+1) for x in v.values())
        elif isinstance(v,list):pending.extend((x,d+1) for x in v)
    canonical(value)
    return value

def contents(data):
    report=analyze(data)
    report['engine_version']='0.1.0'
    report['python_version']=platform.python_version()
    report['input_sha256']=hashlib.sha256(canonical(data)).hexdigest()
    html=('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Research review</title><h1>Scoped offline research review</h1><p>Local consistency is not independent scientific validation or execution authority.</p><pre>'+escape(canonical(report).decode())+'</pre></html>\n').encode()
    files={'input.json':canonical(data),'report.json':canonical(report),'review.html':html}
    files['manifest.json']=canonical({'schema_version':1,'files':{n:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for n,v in sorted(files.items())}})
    if any(len(v)>LIMIT for v in files.values()):raise ValueError('output too large')
    return files,report

def create(path,data):
    files,report=contents(data);path=Path(path);path.mkdir(mode=0o700)
    try:
        for n,v in files.items():
            with (path/n).open('xb') as f:f.write(v)
    except (OSError,ValueError):shutil.rmtree(path);raise
    return report

def verify(path):
    path=Path(path)
    if path.is_symlink() or not path.is_dir() or {p.name for p in path.iterdir()}!=FILES:raise ValueError('exact bundle directory required')
    for p in path.iterdir():
        if p.is_symlink() or not p.is_file() or p.stat().st_size>LIMIT:raise ValueError('bounded regular bundle files required')
    files,report=contents(load(path/'input.json'))
    if any((path/n).read_bytes()!=v for n,v in files.items()):raise ValueError('bundle differs from recomputed analysis')
    return report
