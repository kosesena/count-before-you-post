"""Freeze all unused single-annotation SCD validation photos before downloading or model calls."""
import collections, hashlib, json, zipfile
from datetime import datetime
from pathlib import Path
from evaluation.download_scd_sample import Remote
ROOT=Path('evaluation/inputs/unseen-single-2026-11-03')
def main():
 ROOT.mkdir(exist_ok=False)
 ann=json.loads(Path('evaluation/inputs/scd/instances_val2017.json').read_text())
 used={str(c['id']) for c in json.loads(Path('evaluation/real-images-selection.json').read_text())['cases']}
 used.update(str(c['id']) for c in json.loads(Path('evaluation/acceptance-selection-2026-11-02.json').read_text())['candidates'])
 # Conservatively exclude every source image already downloaded locally, including screened-only candidates.
 local_names={p.name for p in Path('evaluation/inputs').rglob('*.jpg')}
 used.update(str(im['id']) for im in ann['images'] if Path(im['file_name']).name in local_names)
 counts=collections.Counter(a['image_id'] for a in ann['annotations'])
 images=sorted([im for im in ann['images'] if counts[im['id']]==1 and str(im['id']) not in used],key=lambda im:im['id'])
 selection={'frozen_at':datetime.now().astimezone().isoformat(),'selection':'ALL SCD validation images with exactly one carton annotation, excluding all 38 prior benchmark/screening IDs and any already downloaded filename. No replacement or outcome filtering.','excluded_ids':sorted(used,key=int),'scope':'Previously unused in this repository, not necessarily unseen in model training. Single-annotation convenience stratum, not warehouse accuracy. All selected images will be reported even if unsuitable for acceptance.','source':'https://github.com/yancie-yjr/scd.github.io','license':'CC BY-NC-SA 4.0','images':images}
 (ROOT/'selection.json').write_text(json.dumps(selection,indent=2))
 print('Frozen IDs:',[im['id'] for im in images],flush=True)
 z=zipfile.ZipFile(Remote()); rows=[]
 for im in images:
  p=ROOT/Path(im['file_name']).name;p.write_bytes(z.read('images/val2017/'+p.name))
  rows.append(dict(im,path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),annotations=[a for a in ann['annotations'] if a['image_id']==im['id']]))
  (ROOT/'downloaded.json').write_text(json.dumps(rows,indent=2));print('Downloaded',im['id'],flush=True)
if __name__=='__main__':main()
