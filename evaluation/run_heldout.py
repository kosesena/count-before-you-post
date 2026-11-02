"""Seal: python -m evaluation.run_heldout --freeze manifest.json sealed.json
Run: python -m evaluation.run_heldout --run sealed.json results.json
Run sends the three files per case to configured Meta/Baseten services; dry run, no ERP writes.
"""
import argparse
import hashlib
import json
from pathlib import Path
from cbyp.evaluation import freeze, summarize
from cbyp.workflow import verify

def run(sealed, output):
    cases=json.loads(Path(sealed).read_text())['cases']
    if Path(output).exists():raise ValueError('Use a new results filename; trials are never overwritten.')
    # Validate ALL hashes before any API call.
    for case in cases:
        for info in case['files'].values():
            if hashlib.sha256(Path(info['path']).read_bytes()).hexdigest()!=info['sha256']:
                raise ValueError('Sealed input changed: '+case['id'])
    rows=[]
    for case in cases:
        files=case['files']
        try:
            evidence=verify(*(files[k]['path'] for k in ('note','camera','audio')),case['order'],case.get('language','Turkish'))
            decision=evidence['decision'] or {'action':'error','quantity':None}
            row={'id':case['id'],'truth':case['truth'],'result':decision,'seconds':evidence['seconds'],
                 'total_cost_usd':evidence['total_cost_usd'],'observed_count':evidence['camera'].get('cartons_visible'),'evidence':evidence}
        except Exception as e:
            row={'id':case['id'],'truth':case['truth'],'result':{'action':'error','quantity':None},'error_type':type(e).__name__}
        # Preserve independently collected baseline; unknown stays null.
        row['load_id'] = case.get('load_id', case['id'])
        row['manual_active_seconds'] = case.get('manual_active_seconds')
        row['observer'] = case.get('observer')
        rows.append(row)
        Path(output).write_text(json.dumps({'rows':rows,'summary':summarize(rows),'sealed_sha256':hashlib.sha256(Path(sealed).read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
    return summarize(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['--freeze','--run']);p.add_argument('source');p.add_argument('output')
    # positional mode is intentionally parsed directly to support the documented flags.
    import sys
    if len(sys.argv)!=4 or sys.argv[1] not in ('--freeze','--run'):p.print_help();sys.exit(2)
    print(freeze(sys.argv[2],sys.argv[3]) if sys.argv[1]=='--freeze' else run(sys.argv[2],sys.argv[3]))
