"""Addendum: three blank-reference fixtures fail input validation before any model call.
Preserve original run. Replace only those fixtures in a separately frozen protocol
with a deliberate, non-pharmaceutical product claim; no historical decisions retried.
"""
import json,shutil,subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from evaluation.run_holdout20 import digest,write
SOURCE=Path('evaluation/inputs/holdout20-2026-11-03')
ROOT=Path('evaluation/inputs/holdout20-input-addendum-2026-11-03')
def prepare():
 ROOT.mkdir(exist_ok=False);m=json.loads((SOURCE/'manifest.json').read_text());cases=[]
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32)
 for original in m['cases']:
  if original['order']['product']:continue
  c=json.loads(json.dumps(original));cid=f"scd-{c['source_image_id']}-wrong_product_addendum";d=ROOT/cid;d.mkdir()
  qty=c['reference_visible_count'];note=d/'note.png'
  lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: '+cid,'Product: Sunflower oil 5 L','Quantity: '+str(qty)+' cartons','Unit: carton']
  im=Image.new('RGB',(1800,800),'white');draw=ImageDraw.Draw(im)
  for i,line in enumerate(lines):draw.text((40,40+95*i),line,font=font,fill='black')
  im.save(note)
  c.update(id=cid,scenario='wrong_product_addendum',expected_action='block',acceptable_actions=['block','human'],reference_rationale='Deliberately false sunflower-oil claim against visibly pharmaceutical cartons. Full pharmaceutical label transcription is unavailable; no true product identity is invented. Reject or review, never automatically accept.',replaces_invalid_fixture=original['id'])
  c['order'].update(number='PO-'+cid,product='Sunflower oil 5 L');c['files']['note']={'path':str(note.resolve()),'sha256':digest(note)};cases.append(c)
 assert len(cases)==3
 shutil.copytree(SOURCE/'runtime',ROOT/'runtime')
 m.update(frozen_at=datetime.now().astimezone().isoformat(),cases=cases,execution='First model runs for three images whose initial fixtures fail local product-required validation. Same isolated runtime, no credential copy.',protocol='Input-validation repair addendum. Original 20-row run including all three invalid inputs remains unchanged. Three deliberately false product fixtures frozen separately before any model calls on these photographs. No completed model decision retried or replaced.',parent_manifest_sha256=digest(SOURCE/'manifest.json'))
 write(ROOT/'manifest.json',m);print('FROZEN ADDENDUM',digest(ROOT/'manifest.json'))
def run():
 from evaluation import run_holdout20 as runner
 runner.ROOT=ROOT;runner.OUT=Path('evaluation/private/holdout20-input-addendum-2026-11-03');runner.run()
if __name__=='__main__':
 import sys
 {'prepare':prepare,'run':run}[sys.argv[1]]()
