"""Same 21 frozen inputs and targets; all failures retained, no ERP writer."""
import concurrent.futures, hashlib, json, time, sys, os
from datetime import datetime
from pathlib import Path
ROOT=Path('evaluation/inputs/preregistered-mixed-transport-2026-11-04')
OUT=Path('evaluation/private/preregistered-mixed-regression-2026-11-03')
runtime=(ROOT/'runtime').resolve()
sys.path.insert(0,str(runtime))
for line in Path('.env').read_text().splitlines():
 k,sep,v=line.partition('=')
 if sep and k.strip() and k.strip() not in os.environ:os.environ[k.strip()]=v.strip()
from cbyp.workflow import VerificationRun
import cbyp.workflow
assert Path(cbyp.workflow.__file__).is_relative_to(runtime)
def digest(p):
 p=Path(p)
 if not p.is_absolute() and p.parts[0]=='cbyp':p=runtime/p
 return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def error_chain(e):
 out=[]
 while e is not None and len(out)<8:
  out.append(type(e).__name__)
  e=e.__cause__ or e.__context__
 return out
def run():
 source=ROOT/'manifest.json';manifest=json.loads(source.read_text());OUT.mkdir(parents=True,exist_ok=False)
 for c in manifest['cases']:
  for f in c['files'].values():
   if digest(f['path'])!=f['sha256']:raise ValueError('Input changed')
 for p,h in manifest['code_sha256'].items():
  if digest(p)!=h:raise ValueError('Workflow changed before run')
 write(OUT/'manifest.json',manifest)
 def one(c):
  start=time.monotonic();r={k:c[k] for k in ['id','source_image_id','scenario','expected_action','acceptable_actions']};r['started_at']=datetime.now().astimezone().isoformat();run=None
  try:
   for p,h in manifest['code_sha256'].items():
    if digest(p)!=h:raise ValueError('Workflow changed during run')
   f=c['files'];run=VerificationRun(*(f[k]['path'] for k in ['note','camera','audio']),c['order'],'English')
   def progress(step):
    write(OUT/(c['id']+'-progress.json'),{'id':c['id'],'step':step,'elapsed_seconds':round(time.monotonic()-start,1)})
   r['evidence']=run.run(progress);r['action']=r['evidence']['decision']['action'];r['rule']=r['evidence']['decision']['rule']
  except Exception as e:
   r.update(action='error',error_type=type(e).__name__,error_chain=error_chain(e))
   if run:r['partial']={'failed_step':run.failed_step,'timings':run.timings,'note':run.session.note,'camera':run.session.look,'trace':run.session.trace}
  r['seconds']=round(time.monotonic()-start,3);r['exact_target_met']=r['action']==c['expected_action'];r['acceptable_action_met']=r['action'] in c['acceptable_actions']
  write(OUT/(c['id']+'.json'),r)
  print(json.dumps({k:v for k,v in r.items() if k not in ('evidence','partial')},ensure_ascii=False),flush=True)
  return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,manifest['cases']))
 write(OUT/'results.json',{'manifest_sha256':digest(source),'rows':rows})
 print('ALL CASES FINISHED',flush=True)

def preflight():
 # Check the official, unauthenticated endpoint before starting 21 model calls.
 # Keep TLS certificate verification enabled and never log credentials.
 import urllib.request
 try:
  with urllib.request.urlopen('https://api.meta.ai/v1/status', timeout=10) as response:
   status=response.status
   response.read(65536)
  if status != 200:
   raise RuntimeError('Unexpected health status')
 except Exception as exc:
  print(json.dumps({'preflight':'failed','stage':'official_status',
                    'error_chain':error_chain(exc),'tests_started':False}),flush=True)
  return False
 from cbyp.meta import client
 try:
  # A reachable status endpoint alone does not establish API authorization.
  client().with_options(max_retries=0).models.list()
 except Exception as exc:
  print(json.dumps({'preflight':'failed','stage':'authenticated_models',
                    'error_chain':error_chain(exc),'tests_started':False}),flush=True)
  return False
 print(json.dumps({'preflight':'passed','status':200}),flush=True)
 return True

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--check-only',action='store_true')
 parser.add_argument('--output',type=Path,help='New output directory; existing results are never overwritten')
 args=parser.parse_args()
 if not preflight():sys.exit(2)
 if not args.check_only:
  OUT=args.output or Path('evaluation/private')/('preregistered-mixed-recovery-'+datetime.now().strftime('%Y%m%dT%H%M%S'))
  run()
