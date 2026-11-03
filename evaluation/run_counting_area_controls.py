"""Three disclosed development controls on one operator-selected area, not field validation."""
import base64, hashlib, json, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from api.verify import process
from cbyp.counting_area import select_area

ROOT=Path(__file__).resolve().parents[1]
BOX=[820,560,3330,2580]  # Chosen visually before calls; retains the complete foreground Deli carton.

def run(destination):
    out=Path(destination);out.mkdir(parents=True,exist_ok=False)
    base=json.loads((ROOT/'evaluation/inputs/explicit-identity-controls/manifest.json').read_text())['cases'][0]
    camera=Path(base['files']['camera']['path']);audio=Path(base['files']['audio']['path'])
    selection={'box':BOX,'confirmed':True}
    crop,area=select_area(camera,selection,out)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',32)
    cases=[]
    for name,qty,code in [('correct',1,'No.770'),('quantity-mismatch',2,'No.770'),('wrong-article',1,'No.999')]:
        note=out/(name+'-note.png');im=Image.new('RGB',(1600,900),'white');draw=ImageDraw.Draw(im)
        for i,line in enumerate(['CONTROLLED TEST DOCUMENT - NOT A REAL DELIVERY','Supplier: Controlled Fixture Supplier','Delivery note: area-'+name,'Product: Telephone','Brand: deli','Article code: '+code,'Colour: 黑','Quantity: '+str(qty)+' carton']):
            draw.text((40,40+95*i),line,font=font,fill='black')
        im.save(note)
        order=json.loads(json.dumps(base['order']));order.update(number='PO-area-'+name,ordered=qty)
        order['product_identity']['product_code']=code
        cases.append({'id':name,'expected_constraint':None if name=='correct' else 'not_post','order':order,'note':note.name})
    manifest={'scope':'Previously inspected SCD 822 real photo, manually selected foreground area, authored notes/orders, synthetic receiver audio. Post-hoc development controls, not unseen deliveries or field validation. All three cases share the same area and audio. No weakening of gate rules.', 'selection':selection,'original_sha256':area['original']['sha256'],'analyzed_sha256':area['analyzed']['sha256'],'cases':cases}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    if '--prepare-only' in sys.argv:return
    rows=[]
    for case in cases:
        payload={'consent':True,'language':'English','order':case['order'],'counting_area':selection}
        for k,p in [('note',out/case['note']),('camera',camera),('audio',audio)]:payload[k]={'name':p.name,'base64':base64.b64encode(p.read_bytes()).decode()}
        started=time.monotonic()
        try:
            result=process(payload)
            row={'id':case['id'],'expected_constraint':case['expected_constraint'],'evidence':result,'seconds':round(time.monotonic()-started,3)}
            print(case['id'],result['decision']['action'],result['decision']['rule'],flush=True)
        except Exception as e:
            row={'id':case['id'],'expected_constraint':case['expected_constraint'],'error_type':type(e).__name__,'seconds':round(time.monotonic()-started,3)}
            print(case['id'],row['error_type'],flush=True)
        (out/(case['id']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2));rows.append(row)
    (out/'results.json').write_text(json.dumps({'manifest':manifest,'rows':rows},ensure_ascii=False,indent=2))
if __name__=='__main__':run(sys.argv[1])
