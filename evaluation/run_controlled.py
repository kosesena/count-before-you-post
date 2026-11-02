"""Run authored integration cases on public real images; never a field-validation claim.
python -m evaluation.run_controlled manifest.json output-directory
"""
import concurrent.futures
import hashlib
import json
import sys
import time
from pathlib import Path
from cbyp.workflow import verify


def run(source, destination):
    source = Path(source)
    manifest = json.loads(source.read_text())
    for case in manifest['cases']:
        for info in case['files'].values():
            if hashlib.sha256(Path(info['path']).read_bytes()).hexdigest() != info['sha256']:
                raise ValueError('Input changed: ' + case['id'])
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=False)
    (out/'manifest.json').write_bytes(source.read_bytes())
    def one(case):
        t = time.perf_counter()
        row = {'id':case['id'], 'scenario':case['scenario'], 'expected_constraint':case['expected_constraint'],
               'source_image_id':case['source_image_id'], 'total_cost_usd':None, 'steps_started':[]}
        try:
            f = case['files']
            result = verify(*(f[k]['path'] for k in ('note','camera','audio')), case['order'], 'English',
                            progress=lambda name: row['steps_started'].append(name))
            row['evidence'] = result
            row['action'] = (result['decision'] or {}).get('action','error')
            row['rule'] = (result['decision'] or {}).get('rule')
        except Exception as exc:
            row['action'] = 'error'
            row['error_type'] = type(exc).__name__
        row['seconds'] = round(time.perf_counter()-t,3)
        (out/(case['id']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2))
        print(json.dumps({k:row[k] for k in ('id','scenario','action','rule','error_type') if k in row}),flush=True)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(one,manifest['cases']))
    constrained = [r for r in rows if r['expected_constraint']=='not_post']
    summary = {'cases':len(rows),'expected_no_post_cases':len(constrained),
               'unsafe_posts_in_constrained_cases':sum(r['action']=='post' for r in constrained),
               'completed_nonposts_in_constrained_cases':sum(r['action'] in ('human','block') for r in constrained),
               'technical_failures':sum(r['action']=='error' for r in rows),
               'scope':manifest['scope'], 'total_cost_usd':None,
               'caveat':'An earlier rule can mask the injected fault. Baseline outcomes have no independent action truth.'}
    (out/'results.json').write_text(json.dumps({'summary':summary,'rows':rows},ensure_ascii=False,indent=2))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':run(*sys.argv[1:])
