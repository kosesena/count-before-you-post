"""Resume only technical failures after Meta connectivity returns.
Never overwrite the original attempts or retry a completed decision.
Usage: python -m evaluation.recover_holdout20_geometry prepare|run
"""
import json,shutil
from datetime import datetime
from pathlib import Path
from evaluation.run_holdout20 import digest,write
SOURCE=Path('evaluation/inputs/holdout20-geometry-regression-v2-2026-11-03')
PREVIOUS=Path('evaluation/private/holdout20-geometry-regression-v2-2026-11-03')
ROOT=Path('evaluation/inputs/holdout20-geometry-recovery-2026-11-03')
OUT=Path('evaluation/private/holdout20-geometry-recovery-2026-11-03')
def prepare():
 ROOT.mkdir(exist_ok=False)
 m=json.loads((SOURCE/'manifest.json').read_text());r=json.loads((PREVIOUS/'results.json').read_text())
 errors={row['id'] for row in r['rows'] if row['action']=='error'}
 assert len(errors)==17
 m['cases']=[c for c in m['cases'] if c['id'] in errors]
 m['frozen_at']=datetime.now().astimezone().isoformat()
 m['scope']='Infrastructure recovery for the 17 technical failures only. The 3 completed post-fix decisions remain unchanged. Same frozen code, files, orders and targets; all failed attempts retained. Not a fresh holdout.'
 m['protocol']='One recovery application run per technical failure, only after network restoration. No completed model decision is retried. Report first-attempt errors AND recovery outcomes; never replace/hide failures.'
 m['protected_files'].update({str(PREVIOUS/'results.json'):digest(PREVIOUS/'results.json'),str(SOURCE/'manifest.json'):digest(SOURCE/'manifest.json')})
 shutil.copytree(SOURCE/'runtime',ROOT/'runtime')
 for p,h in m['code_sha256'].items():assert digest(ROOT/'runtime'/p)==h
 write(ROOT/'manifest.json',m);print('Prepared',len(m['cases']),'unchanged failed fixtures. No model calls made.')
def run():
 from evaluation import run_holdout20 as runner
 runner.ROOT=ROOT;runner.OUT=OUT;runner.run()
 m=json.loads((ROOT/'manifest.json').read_text())
 for p,h in m['protected_files'].items():assert digest(p)==h,p
 print('Recovery complete; original failed and completed attempts unchanged.')
if __name__=='__main__':
 import sys
 {'prepare':prepare,'run':run}[sys.argv[1]]()
