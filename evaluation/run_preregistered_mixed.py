"""Seven previously unused photographs; pre-registered controls on frozen production code."""
import hashlib,json,os,subprocess,sys,tarfile,io
from pathlib import Path
from datetime import datetime
ROOT=Path('evaluation/inputs/preregistered-mixed-2026-11-03')
OUT=Path('evaluation/private/preregistered-mixed-2026-11-03')
COMMIT='39042b925056d546183aa94058b363ec2562d886'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare():
 from PIL import Image,ImageDraw,ImageFont
 assert not (ROOT/'manifest.json').exists()
 refs=json.loads((ROOT/'references.json').read_text());sources=json.loads((ROOT/'downloaded.json').read_text());assert len(sources)==7
 # Freeze committed runtime rather than concurrently modified working-tree code.
 runtime=ROOT/'runtime';runtime.mkdir(exist_ok=False)
 archive=subprocess.check_output(['git','archive',COMMIT,'cbyp'])
 with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(runtime,filter='data')
 prior={digest(p) for p in Path('evaluation/inputs').rglob('*.jpg') if not p.is_relative_to(ROOT)}
 assert all(src['sha256'] not in prior for src in sources),'Duplicate previous photograph'
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32);cases=[]
 for src in sources:
  ref=refs[str(src['id'])];assert ref['product'] and ref['target'] in ['post','human']
  for variant in ['baseline','quantity_mismatch','receiver_uncertain']:
   cid=f"scd-train-{src['id']}-{variant}";d=ROOT/cid;d.mkdir(exist_ok=False);qty=2 if variant=='quantity_mismatch' else 1
   note=d/'note.png';audio=d/'receiver.wav'
   lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: '+cid,'Product: '+ref['product'],'Quantity: '+str(qty)+' carton','Unit: carton']
   im=Image.new('RGB',(1800,800),'white');draw=ImageDraw.Draw(im)
   for i,line in enumerate(lines):draw.text((40,40+95*i),line,font=font,fill='black')
   im.save(note)
   spoken='I am the receiving clerk. '+('I am not sure how many cartons arrived. I could not complete the count.' if variant=='receiver_uncertain' else 'I counted one carton.')+' The supplier is Controlled Fixture Supplier.'
   subprocess.run(['say','-v','Samantha','-o',str(d/'receiver.aiff'),spoken],check=True);subprocess.run(['afconvert','-f','WAVE','-d','LEI16@16000','-c','1',str(d/'receiver.aiff'),str(audio)],check=True)
   target='human' if variant=='receiver_uncertain' else ('block' if variant=='quantity_mismatch' and ref['target']=='post' else ref['target'])
   cases.append({'id':cid,'source_image_id':src['id'],'scenario':variant,'expected_action':target,'acceptable_actions':[target] if target=='post' else ['human','block'],'reference_visible_count':1,'reference_rationale':ref['reason'],'reference_author':'Assistant visual inspection before tested-model calls; not independent shipment ground truth','spoken_script':spoken,'order':{'number':'PO-'+cid,'supplier':'Controlled Fixture Supplier','require_supplier':True,'product':ref['product'],'unit':'carton','ordered':qty,'received':0},'files':{k:{'path':str(p.resolve()),'sha256':digest(p)} for k,p in {'note':note,'camera':Path(src['path']),'audio':audio}.items()}})
 manifest={'frozen_at':datetime.now().astimezone().isoformat(),'source_selection':json.loads((ROOT/'selection.json').read_text()),'references_sha256':digest(ROOT/'references.json'),'scope':'Seven project-unused SCD train2017 photographs and 21 authored controls. NOT unseen in model training, independent shipments, strict SKU validation or field accuracy. Original photos, synthetic notes and receiver audio, exact product-description profile. No ERP writer.','protocol':'Targets and all inputs fixed before first tested-model call. One application run per case, no outcome-based selection, edits or retries. Provider SDK transport retries remain enabled. Technical failures retained. Baseline is only an acceptance candidate when visually supported; uncertain baseline images stay human targets. Quantity mismatch changes both note and order to two, voice remains one. Earlier gates can mask injected faults. Broad safe-stop (block/human) is not exact target correctness. No labor savings or billing measurement.','execution':'Isolated runtime from live commit 39042b9; concurrent working-tree edits cannot enter this test.','code_sha256':{str(p.relative_to(runtime)):digest(p) for p in sorted((runtime/'cbyp').glob('*.py'))},'git_head':COMMIT,'cases':cases}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('FROZEN',len(cases),'manifest',digest(ROOT/'manifest.json'),flush=True)
def run():
 for line in Path('.env').read_text().splitlines():
  k,sep,v=line.partition('=')
  if sep and k.strip() and k.strip() not in os.environ:os.environ[k.strip()]=v.strip()
 runtime=(ROOT/'runtime').resolve();sys.path.insert(0,str(runtime))
 from evaluation import run_unseen_controls as runner
 import cbyp.workflow
 assert Path(cbyp.workflow.__file__).is_relative_to(runtime)
 def frozen_digest(p):
  p=Path(p);return digest(runtime/p if not p.is_absolute() and p.parts[0]=='cbyp' else p)
 runner.digest=frozen_digest;runner.ROOT=ROOT;runner.OUT=OUT;runner.run()
if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
