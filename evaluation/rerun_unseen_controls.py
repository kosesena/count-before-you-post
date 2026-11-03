"""Freeze fixed-code regression against the unchanged 15 original inputs; keep first run intact."""
import json
from pathlib import Path
from datetime import datetime
from evaluation import run_unseen_controls as runner

def main():
 old=Path('evaluation/inputs/unseen-single-2026-11-03/manifest.json')
 manifest=json.loads(old.read_text())
 root=Path('evaluation/private/unseen-regression-frozen-2026-11-03');root.mkdir(exist_ok=False)
 protected=[old,Path('evaluation/private/unseen-single-2026-11-03/results.json'),Path('evaluation/unseen-controls-2026-11-03.json'),Path('site/unseen-validation/results.json'),Path('site/unseen-validation/index.html')]
 manifest['previous_run']={'manifest_sha256':runner.digest(old),'protected_files':{str(p):runner.digest(p) for p in protected},'original_code_sha256':manifest['code_sha256']}
 manifest['frozen_at']=datetime.now().astimezone().isoformat()
 manifest['code_sha256']={str(p):runner.digest(p) for p in sorted(Path('cbyp').glob('*.py'))}
 manifest['scope']='POST-HOC REGRESSION, not a new holdout. Same 15 input files/orders and expected labels as the first run. Frame boundary guard and independent confirmation of document mismatch added. '+manifest['scope']
 runner.write(root/'manifest.json',manifest)
 runner.ROOT=root;runner.OUT=Path('evaluation/private/unseen-regression-2026-11-03')
 runner.run()
 for p,h in manifest['previous_run']['protected_files'].items():
  if runner.digest(p)!=h:raise ValueError('Historical file changed: '+p)
 print('Historical evidence hashes unchanged',flush=True)
if __name__=='__main__':main()
