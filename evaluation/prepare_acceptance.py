"""Reproduce authored acceptance fixtures on macOS, after downloading source photos.
Usage: python evaluation/prepare_acceptance.py initial|controls
The literal-label variant is post-hoc; the oil camera is synthetic. Not a field benchmark.
"""
from pathlib import Path
import json,hashlib,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
mode=sys.argv[1] if len(sys.argv)>1 else 'initial'
if mode not in ('initial','controls'):raise SystemExit('Use initial or controls')
root=Path('evaluation/inputs/clean-acceptance' if mode=='initial' else 'evaluation/inputs/acceptance-controls');root.mkdir(exist_ok=False)
fixtures=([('haier',Path('evaluation/inputs/scd/1 (411).jpg'),'Haier HRO6H22-4',2,'374'),('deli',Path('evaluation/inputs/clean-candidates/1 (87).jpg'),'deli No.770 TELEPHONE',1,'822')] if mode=='initial' else [('deli-literal',Path('evaluation/inputs/clean-candidates/1 (87).jpg'),'固定无线电话机',1,'822'),('synthetic-oil',Path('site/img/ok-camera.jpg'),'Ayçiçek yağı 5 L',12,'synthetic-ok')])
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32);cases=[]
for name,camera,product,n,source in fixtures:
 d=root/name;d.mkdir();note=d/'note.png';audio=d/'receiver.wav'
 lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Delivery note: CLEAN-'+name,'Supplier: Controlled Fixture Supplier','Purchase order: PO-CLEAN-'+name,'Product: '+product,f'Quantity: {n}','Unit: carton']
 im=Image.new('RGB',(1500,700),'white');draw=ImageDraw.Draw(im)
 for j,line in enumerate(lines):draw.text((40,45+70*j),line,fill='black',font=font)
 im.save(note)
 spoken=f'I am the receiving clerk. I counted {n} cartons. The supplier is Controlled Fixture Supplier.'
 subprocess.run(['say','-v','Samantha','-o',str(d/'receiver.aiff'),spoken],check=True)
 subprocess.run(['afconvert','-f','WAVE','-d','LEI16@16000','-c','1',str(d/'receiver.aiff'),str(audio)],check=True)
 cases.append({'id':'clean-'+name,'scenario':'clean_candidate','expected_constraint':None,'source_image_id':source,'order':{'number':'PO-CLEAN-'+name,'supplier':'Controlled Fixture Supplier','product':product,'unit':'carton','ordered':n,'received':0},'files':{k:{'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in dict(note=note,camera=camera,audio=audio).items()},'annotation_count':n,'product_source':'Visual reading of visible label before this run; authored test order, not verified contents','audio_source':'macOS Samantha synthetic','spoken_script':spoken})
(root/'manifest.json').write_text(json.dumps({'scope':'Acceptance development fixtures. Authored notes/orders and synthetic voice. Controls include a post-hoc literal-label variant and a synthetic camera; not independent accuracy.','cases':cases},indent=2))
