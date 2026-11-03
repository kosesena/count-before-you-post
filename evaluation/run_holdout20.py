"""Prepare frozen 20-photo controls; run once using an isolated code snapshot."""
import hashlib,json,os,shutil,subprocess,sys
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('evaluation/inputs/holdout20-2026-11-03')
OUT=Path('evaluation/private/holdout20-2026-11-03')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def prepare():
 if (ROOT/'manifest.json').exists():raise ValueError('Manifest already frozen')
 refs=json.loads((ROOT/'references.json').read_text());sources=json.loads((ROOT/'downloaded.json').read_text());assert len(sources)==20
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32);cases=[]
 for src in sources:
  ref=refs[str(src['id'])];cid=f"scd-{src['id']}-{ref['scenario']}";d=ROOT/cid;d.mkdir(exist_ok=False)
  count=src['annotated_visible_count'];qty=count+(1 if ref['scenario']=='quantity_mismatch' else 0)
  product=ref['product'];note=d/'note.png';audio=d/'receiver.wav'
  lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: '+cid,'Product: '+product,'Quantity: '+str(qty)+' cartons','Unit: carton']
  im=Image.new('RGB',(1800,800),'white');draw=ImageDraw.Draw(im)
  for i,line in enumerate(lines):draw.text((40,40+95*i),line,font=font,fill='black')
  im.save(note)
  words={2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight'}
  spoken=f'I am the receiving clerk. I counted {words[count]} cartons. The supplier is Controlled Fixture Supplier.'
  subprocess.run(['say','-v','Samantha','-o',str(d/'receiver.aiff'),spoken],check=True)
  subprocess.run(['afconvert','-f','WAVE','-d','LEI16@16000','-c','1',str(d/'receiver.aiff'),str(audio)],check=True)
  cases.append({'id':cid,'source_image_id':src['id'],'scenario':ref['scenario'],'expected_action':ref['target'],'acceptable_actions':[ref['target']] if ref['target']=='post' else ['human','block'],'reference_visible_count':count,'reference_rationale':ref['reason'],'reference_author':'Assistant visual review before calls; dataset visible-carton annotation count, not physical shipment ground truth','spoken_script':spoken,'order':{'number':'PO-'+cid,'supplier':'Controlled Fixture Supplier','require_supplier':True,'product':product,'unit':'carton','ordered':qty,'received':0},'files':{k:{'path':str(p.resolve()),'sha256':digest(p)} for k,p in {'note':note,'camera':Path(src['path']),'audio':audio}.items()}})
 runtime=ROOT/'runtime';shutil.copytree('cbyp',runtime/'cbyp',ignore=shutil.ignore_patterns('__pycache__'))
 manifest={'frozen_at':datetime.now().astimezone().isoformat(),'source_selection':json.loads((ROOT/'selection.json').read_text()),'references_sha256':digest(ROOT/'references.json'),'scope':'20 distinct previously unused SCD validation photos; metadata-stratified convenience sample. Original unmodified photos, authored single-line notes/orders, synthetic receiver audio, exact product-description profile, no trusted SKU identifiers, no ERP writer. Not independent field ground truth, model-training holdout or worker-time study. Mixed/unclear photos remain included; no forced clean labels.','protocol':'One application run per frozen case. No outcome-based input/target/code edits or trial retries. SDK transport retries remain enabled. Every outcome retained, including errors. Count is visible dataset annotations, not hidden contents. Quantity mismatch raises note AND order by one; voice keeps reference count. Earlier gate rules may mask injected faults.','execution':'All cbyp imports from isolated frozen runtime. No credentials copied. Three concurrent cases.','code_sha256':{str(p.relative_to(runtime)):digest(p) for p in sorted((runtime/'cbyp').glob('*.py'))},'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'cases':cases}
 write(ROOT/'manifest.json',manifest);print('FROZEN',len(cases),'SHA256',digest(ROOT/'manifest.json'),flush=True)
def run():
 # Load credential only into environment, never logs or archived snapshot.
 for line in Path('.env').read_text().splitlines():
  k,sep,v=line.partition('=')
  if sep and k.strip() and k.strip() not in os.environ:os.environ[k.strip()]=v.strip()
 runtime=(ROOT/'runtime').resolve();sys.path.insert(0,str(runtime))
 from evaluation import run_unseen_controls as runner
 import cbyp.workflow
 assert Path(cbyp.workflow.__file__).is_relative_to(runtime)
 def frozen_digest(p):
  p=Path(p);return digest(runtime/p if not p.is_absolute() and p.parts[0]=='cbyp' else p)
 runner.digest=frozen_digest;runner.ROOT=ROOT;runner.OUT=OUT
 runner.run()
if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
