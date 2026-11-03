"""Pre-register and run every case on a fixed new-photo set. No edits or trial retries.
Usage: python -m evaluation.run_unseen_controls prepare|run
Existing product-description profile; no invented brand/model identifiers.
"""
import concurrent.futures, hashlib, json, subprocess, time
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from cbyp.workflow import VerificationRun
ROOT=Path('evaluation/inputs/unseen-single-2026-11-03')
OUT=Path('evaluation/private/unseen-single-2026-11-03')
# Visually transcribed before any verification calls; not readings from the tested models.
REFERENCES={
 37:('关节止痛膏','human','Carton fills frame with clipped edges; complete extent cannot confidently be established.'),
 93:('V88','human','Open/torn top and partly obscured markings; no verified contents or SKU.'),
 111:('川贝清肺糖浆','post','One visibly intact carton on pallet, legible product name. Candidate for description-level acceptance only.'),
 278:('WATER FILTER FOR RO Plus','human','Torn/crushed upper rim; damage calls for review.'),
 711:('苦参素葡萄糖注射液','human','Carton partly obscured by shelf and extends beyond upper/left frame; full extent uncertain.'),
}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def prepare():
 if (ROOT/'manifest.json').exists():raise ValueError('Manifest already frozen')
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32)
 cases=[]
 for source in json.loads((ROOT/'downloaded.json').read_text()):
  image_id=source['id'];product,base_action,rationale=REFERENCES[image_id]
  for variant in ['baseline','quantity_mismatch','receiver_uncertain']:
   cid=f'scd-{image_id}-{variant}';d=ROOT/cid;d.mkdir(exist_ok=False)
   qty=2 if variant=='quantity_mismatch' else 1
   note=d/'note.png';audio=d/'receiver.wav'
   lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: '+cid,'Product: '+product,'Quantity: '+str(qty)+' carton','Unit: carton']
   im=Image.new('RGB',(1600,800),'white');draw=ImageDraw.Draw(im)
   for i,line in enumerate(lines):draw.text((40,40+95*i),line,font=font,fill='black')
   im.save(note)
   spoken=('I am the receiving clerk. I am not sure how many cartons arrived. I could not complete the count. The supplier is Controlled Fixture Supplier.' if variant=='receiver_uncertain' else 'I am the receiving clerk. I counted one carton. The supplier is Controlled Fixture Supplier.')
   subprocess.run(['say','-v','Samantha','-o',str(d/'receiver.aiff'),spoken],check=True)
   subprocess.run(['afconvert','-f','WAVE','-d','LEI16@16000','-c','1',str(d/'receiver.aiff'),str(audio)],check=True)
   target='human' if variant=='receiver_uncertain' else ('block' if variant=='quantity_mismatch' and base_action=='post' else base_action)
   allowed=['block','human'] if variant=='quantity_mismatch' else [target]
   cases.append({'id':cid,'source_image_id':image_id,'scenario':variant,'expected_action':target,'acceptable_actions':allowed,'reference_visible_count':1,'reference_rationale':rationale,'reference_author':'Assistant visual inspection before verification; not independent human annotation of acceptance','spoken_script':spoken,'order':{'number':'PO-'+cid,'supplier':'Controlled Fixture Supplier','require_supplier':True,'product':product,'unit':'carton','ordered':qty,'received':0},'files':{k:{'path':str(p.resolve()),'sha256':digest(p)} for k,p in {'note':note,'camera':Path(source['path']),'audio':audio}.items()}})
 manifest={'frozen_at':datetime.now().astimezone().isoformat(),'source_selection':json.loads((ROOT/'selection.json').read_text()),'scope':'5 previously unused public SCD photos, 15 authored controls. Original images, no selected area. Synthetic audio and notes/orders. Existing full_checks workflow with exact product-description matching, supplier, object cross-check, receiver, second reader and audit. No structured brand/article/model identity in orders: this is NOT strict SKU validation. No ERP writer. Not independent shipments, model-training holdout or field accuracy.','protocol':'Single first application run per case, no outcome-based changes or retries; existing provider SDK transport retries remain enabled. Every selected image and case retained, including errors. Quantity mismatch changes note and open order to 2; speech remains 1. Receiver uncertainty changes only speech. Earlier gate rules can mask injected faults. No measured worker baseline or total billing cost.','code_sha256':{str(p):digest(p) for p in sorted(Path('cbyp').glob('*.py'))},'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'cases':cases}
 write(ROOT/'manifest.json',manifest)
 print('FROZEN',len(cases),'cases; SHA256',digest(ROOT/'manifest.json'),flush=True)
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
   r.update(action='error',error_type=type(e).__name__)
   if run:r['partial']={'failed_step':run.failed_step,'timings':run.timings,'note':run.session.note,'camera':run.session.look,'trace':run.session.trace}
  r['seconds']=round(time.monotonic()-start,3);r['exact_target_met']=r['action']==c['expected_action'];r['acceptable_action_met']=r['action'] in c['acceptable_actions']
  write(OUT/(c['id']+'.json'),r)
  print(json.dumps({k:v for k,v in r.items() if k not in ('evidence','partial')},ensure_ascii=False),flush=True)
  return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,manifest['cases']))
 write(OUT/'results.json',{'manifest_sha256':digest(source),'rows':rows})
 print('ALL CASES FINISHED',flush=True)
if __name__=='__main__':
 import sys
 {'prepare':prepare,'run':run}[sys.argv[1]]()
