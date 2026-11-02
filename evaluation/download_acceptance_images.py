"""Download the eight acceptance candidates; python -m evaluation.download_acceptance_images.
Requires the original SCD annotation manifest. CC BY-NC-SA 4.0, not redistributed.
"""
from pathlib import Path
import json,hashlib,zipfile
from evaluation.download_scd_sample import Remote
ann=json.loads(Path('evaluation/inputs/scd/instances_val2017.json').read_text());used={c['id'] for c in json.loads(Path('evaluation/inputs/scd/sample.json').read_text())['cases']};candidates=[]
for im in sorted(ann['images'],key=lambda i:hashlib.sha256(('clean:'+str(i['id'])).encode()).hexdigest()):
 labels=[a for a in ann['annotations'] if a['image_id']==im['id']]
 if str(im['id']) in used or not 1<=len(labels)<=4:continue
 if not all(a['bbox'][0]>im['width']*.02 and a['bbox'][1]>im['height']*.02 and a['bbox'][0]+a['bbox'][2]<im['width']*.98 and a['bbox'][1]+a['bbox'][3]<im['height']*.98 for a in labels):continue
 candidates.append((im,labels))
 if len(candidates)==8:break
root=Path('evaluation/inputs/clean-candidates');root.mkdir(exist_ok=False);z=zipfile.ZipFile(Remote());rows=[]
for im,labels in candidates:
 p=root/Path(im['file_name']).name;p.write_bytes(z.read('images/val2017/'+p.name));rows.append({'id':str(im['id']),'path':str(p),'count':len(labels),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print(rows[-1],flush=True)
(root/'manifest.json').write_text(json.dumps(rows,indent=2))
