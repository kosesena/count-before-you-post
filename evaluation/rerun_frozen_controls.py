"""Run the unchanged 15 controls from an isolated, hashed Python snapshot.
Retains the preceding interrupted attempt in full. No secrets copied to snapshot.
"""
import hashlib,json,os,shutil,sys,subprocess
from datetime import datetime
from pathlib import Path

def main():
 repo=Path.cwd();root=repo/'evaluation/private/unseen-regression-v2-frozen-2026-11-03';root.mkdir(exist_ok=False)
 runtime=root/'runtime';shutil.copytree(repo/'cbyp',runtime/'cbyp',ignore=shutil.ignore_patterns('__pycache__'))
 # Use existing local credentials without including them in the archived snapshot or reports.
 for line in (repo/'.env').read_text().splitlines():
  key,sep,value=line.partition('=')
  if sep and key.strip() and key.strip() not in os.environ:os.environ[key.strip()]=value.strip()
 sys.path.insert(0,str(runtime))
 from evaluation import run_unseen_controls as runner
 import cbyp.workflow
 assert Path(cbyp.workflow.__file__).is_relative_to(runtime)
 original_digest=runner.digest
 def frozen_digest(p):
  p=Path(p)
  return original_digest(runtime/p if not p.is_absolute() and p.parts[0]=='cbyp' else p)
 old=repo/'evaluation/inputs/unseen-single-2026-11-03/manifest.json';m=json.loads(old.read_text())
 interrupted=repo/'evaluation/private/unseen-regression-2026-11-03/results.json'
 protected=[old,repo/'evaluation/private/unseen-single-2026-11-03/results.json',repo/'evaluation/unseen-controls-2026-11-03.json',repo/'site/unseen-validation/results.json',repo/'site/unseen-validation/index.html',interrupted]
 m['previous_run']={'manifest_sha256':original_digest(old),'protected_files':{str(p.relative_to(repo)):original_digest(p) for p in protected},'original_code_sha256':m['code_sha256']}
 m['frozen_at']=datetime.now().astimezone().isoformat();m['git_head']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 m['code_sha256']={str(p.relative_to(runtime)):original_digest(p) for p in sorted((runtime/'cbyp').glob('*.py'))}
 m['execution']='All cbyp imports resolved from archived immutable runtime snapshot. Hashes checked against snapshot for every case. No credentials in snapshot.'
 m['scope']='POST-HOC REGRESSION attempt 2, same 15 inputs and targets; not a new holdout. Attempt 1 retained: 6 completed human decisions, 9 pre-call code-drift failures after concurrent edits to agent.py and gate.py. '+m['scope']
 runner.write(root/'manifest.json',m)
 runner.digest=frozen_digest;runner.ROOT=root;runner.OUT=repo/'evaluation/private/unseen-regression-v2-2026-11-03';runner.run()
 for p,h in m['previous_run']['protected_files'].items():assert original_digest(repo/p)==h,p
 print('Original and interrupted results unchanged; frozen runtime verified',flush=True)
if __name__=='__main__':main()
