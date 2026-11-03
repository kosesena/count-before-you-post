"""Author explicit-identifier development controls; not independent field evidence."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path('evaluation/inputs/explicit-identity-controls');root.mkdir(exist_ok=False)
base=json.loads(Path('evaluation/inputs/clean-acceptance/manifest.json').read_text())['cases'][1]
cases=[]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32)
for name,variant in [('explicit-deli-black','黑'),('explicit-deli-wrong-colour','白')]:
 d=root/name;d.mkdir();note=d/'note.png'
 im=Image.new('RGB',(1600,900),'white');draw=ImageDraw.Draw(im)
 lines=['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: '+name,'Product: Telephone','Brand: deli','Article code: No.770','Colour: '+variant,'Quantity: 1 carton']
 for i,line in enumerate(lines):draw.text((40,40+95*i),line,font=font,fill='black')
 im.save(note)
 files={k:dict(v) for k,v in base['files'].items()};files['note']={'path':str(note.resolve()),'sha256':hashlib.sha256(note.read_bytes()).hexdigest()}
 cases.append({'id':name,'scenario':'explicit_identifier_control','expected_constraint':'not_post' if variant=='白' else None,'source_image_id':'822','order':{'number':'PO-'+name,'supplier':'Controlled Fixture Supplier','require_supplier':True,'product':'Telephone','product_identity':{'brand':'deli','product_code':'No.770','model':'','variant':variant},'unit':'carton','ordered':1,'received':0},'files':files})
(root/'manifest.json').write_text(json.dumps({'scope':'Post-hoc development controls on previously inspected SCD image 822. Authored explicit article/colour notes and orders, reused synthetic speech. Black matches visually read label; white is a deliberate negative control. Not unseen-data accuracy, genuine shipment or field validation.','cases':cases},ensure_ascii=False,indent=2))
