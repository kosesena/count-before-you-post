"""Single post-fix regression on the exact 20 valid first-run fixtures.
Original rows/inputs/targets remain protected; code is isolated before calls.
"""
import json,shutil,subprocess
from datetime import datetime
from pathlib import Path
from evaluation.run_holdout20 import digest,write
ROOT=Path('evaluation/inputs/holdout20-geometry-regression-v2-2026-11-03')
OUT=Path('evaluation/private/holdout20-geometry-regression-v2-2026-11-03')
BEFORE=Path('evaluation/holdout20-final-2026-11-03.json')
def prepare():
 ROOT.mkdir(exist_ok=False)
 initial=Path('evaluation/inputs/holdout20-2026-11-03/manifest.json')
 addendum=Path('evaluation/inputs/holdout20-input-addendum-2026-11-03/manifest.json')
 m=json.loads(initial.read_text());a=json.loads(addendum.read_text());before=json.loads(BEFORE.read_text())
 cases={c['id']:c for c in m['cases']+a['cases']}
 chosen=[cases[r['id']] for r in before['valid_first_model_runs']]
 assert len(chosen)==20 and len({c['source_image_id'] for c in chosen})==20
 for c in chosen:
  for f in c['files'].values():assert digest(f['path'])==f['sha256']
 runtime=ROOT/'runtime';shutil.copytree('cbyp',runtime/'cbyp',ignore=shutil.ignore_patterns('__pycache__'))
 protected=[Path("evaluation/private/holdout20-geometry-regression-2026-11-03/interrupted-results.json"),initial,addendum,BEFORE,Path('evaluation/private/holdout20-2026-11-03/results.json'),Path('evaluation/private/holdout20-input-addendum-2026-11-03/results.json')]
 m.update(frozen_at=datetime.now().astimezone().isoformat(),cases=chosen,
  scope='POST-HOC geometry regression on the same 20 previously tested photos and exact valid fixtures, including the three already-frozen wrong-product addendum fixtures. Not a new holdout.',
  protocol='Exactly one new application run per unchanged valid fixture; same targets, orders, note/photo/audio bytes. No model-outcome edits or retries. Provider SDK transport retries unchanged. Every outcome retained. No ERP writer.',
  git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  code_sha256={str(p.relative_to(runtime)):digest(p) for p in sorted((runtime/'cbyp').glob('*.py'))},
  before_code_sha256=json.loads(initial.read_text())['code_sha256'],
  protected_files={str(p):digest(p) for p in protected},
  changes=['All Spark and SAM image requests use EXIF-oriented, metadata-free lossless PNG pixels. Original files and their hashes remain unchanged. Corrects ambiguous encoded-vs-oriented image coordinates.',
           'Spark point prompt no longer assumes ceiling view or regular grid; requires one interior-face point per actual carton.',
           'Invalid point coordinates fail closed; ambiguous carton matches and duplicate probe IDs are not arbitrarily selected. Probe mask must contain its prompt point. Existing 80% containment / 1.5 growth / confidence thresholds unchanged.',
           'Frame uses occupied mask extents instead of bounding-box padding. Empty/malformed/out-of-frame masks fail closed. Every actual boundary mask >=0.7, even tiny/doubtful, still requires review. 1% guard band unchanged.',
           'Trace records point coordinates and per-point/probe associations for audit. No product, count, speech, visibility, audit, signoff or ERP policy relaxed.'],
  interrupted_attempt={'path':'evaluation/private/holdout20-geometry-regression-2026-11-03/interrupted-results.json','reason':'Prompt-only attempt stopped after EXIF mismatch discovered. 3 completed, 3 interrupted, 14 not started; all records retained.'},
  diagnostic='One baseline geometry-only diagnostic on 541 used to inspect failure; not counted in regression or accuracy. It showed three-column/two-row points on a two-column/three-row load. No delivery decision made.')
 write(ROOT/'manifest.json',m);print('FROZEN',len(chosen),'cases',digest(ROOT/'manifest.json'),flush=True)
def run():
 from evaluation import run_holdout20 as runner
 runner.ROOT=ROOT;runner.OUT=OUT;runner.run()
 m=json.loads((ROOT/'manifest.json').read_text())
 for p,h in m['protected_files'].items():assert digest(p)==h,p
 print('All previous inputs/results unchanged.',flush=True)
if __name__=='__main__':
 import sys
 {'prepare':prepare,'run':run}[sys.argv[1]]()
