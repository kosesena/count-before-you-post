import sys,json,zipfile,hashlib,collections,subprocess
from pathlib import Path
from datetime import datetime
REPO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(REPO))
from evaluation.download_scd_sample import Remote
ROOT=REPO/'evaluation/inputs/preregistered-mixed-2026-11-03'
ROOT.mkdir(exist_ok=True)
assert not (ROOT/"selection.json").exists()
z=zipfile.ZipFile(Remote())
member=next(i.filename for i in z.infolist() if i.filename.endswith('instances_train2017.json'))
raw=(ROOT/'annotations.json').read_bytes() if (ROOT/'annotations.json').exists() else z.read(member);(ROOT/'annotations.json').write_bytes(raw);ann=json.loads(raw)
names={p.name for p in (REPO/'evaluation/inputs').rglob('*.jpg')};groups=collections.defaultdict(list)
for a in ann['annotations']:groups[a['image_id']].append(a)
def edge(im):
 w,h=im['width'],im['height'];return any(x<=.02*w or y<=.02*h or x+bw>=.98*w or y+bh>=.98*h for x,y,bw,bh in [a['bbox'] for a in groups[im['id']]])
key=lambda im:hashlib.sha256(('cbyp-new-mixed-v1:'+str(im['id'])).encode()).hexdigest()
pool=[im for im in ann['images'] if Path(im['file_name']).name not in names and len(groups[im['id']])==1]
inside=sorted([im for im in pool if not edge(im)],key=key)[:5];boundary=sorted([im for im in pool if edge(im)],key=key)[:2]
assert len(inside)==5 and len(boundary)==2,(len(inside),len(boundary))
selected=[dict(im,stratum='interior' if im in inside else 'boundary') for im in inside+boundary]
selection={'frozen_at':datetime.now().astimezone().isoformat(),'source':'https://github.com/yancie-yjr/scd.github.io','license':'CC BY-NC-SA 4.0','dataset_split':'train2017','excluded_filenames':sorted(names),'selection':'All five eligible interior and two boundary single-carton annotation photographs sorted by SHA256(cbyp-new-mixed-v1:ID). Exclude all previously downloaded filenames. No replacements or outcome filtering.','scope':'Previously unused by this project, NOT unseen in model training. Metadata strata are not cleanliness guarantees. Assistant visual review before model calls fixes targets; synthetic documents/audio, no real shipment truth or ERP writes.','metadata_feasibility_note':'Initial planned six interior singleton photographs reduced to all five available before photo download or any model call; two boundary photographs retained. No outcome filtering.', 'images':selected}
(ROOT/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2));print('FROZEN',[(i['id'],i['stratum']) for i in selected],flush=True)
rows=[]
for im in selected:
 name=Path(im['file_name']).name;p=ROOT/name;p.write_bytes(z.read('images/train2017/'+name));rows.append(dict(im,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),annotations=groups[im['id']]))
 (ROOT/'downloaded.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('Downloaded',im['id'],flush=True)
