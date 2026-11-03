"""Freeze and fetch 20 unused SCD photographs without model-outcome filtering."""
import collections,hashlib,json,zipfile
from pathlib import Path
from datetime import datetime
from evaluation.download_scd_sample import Remote
ROOT=Path('evaluation/inputs/holdout20-2026-11-03')
def main():
 ROOT.mkdir(exist_ok=True)
 if (ROOT/"selection.json").exists():raise ValueError("Selection already frozen")
 ann=json.loads(Path('evaluation/inputs/scd/instances_val2017.json').read_text())
 local={p.name for p in Path('evaluation/inputs').rglob('*.jpg')}
 used={im['id'] for im in ann['images'] if Path(im['file_name']).name in local}
 groups=collections.defaultdict(list)
 for a in ann['annotations']:groups[a['image_id']].append(a)
 def edge(im):
  w,h=im['width'],im['height']
  return any(x<=.02*w or y<=.02*h or x+bw>=.98*w or y+bh>=.98*h for x,y,bw,bh in [a['bbox'] for a in groups[im['id']]])
 pool=[im for im in ann['images'] if im['id'] not in used and 2<=len(groups[im['id']])<=8]
 key=lambda im:hashlib.sha256(('cbyp-holdout20-v1:'+str(im['id'])).encode()).hexdigest()
 clear=sorted([im for im in pool if not edge(im)],key=key)[:15]
 boundary=sorted([im for im in pool if edge(im)],key=key)[:5]
 assert len(clear)==15 and len(boundary)==5
 selected=[dict(im,stratum='interior' if im in clear else 'boundary',annotated_visible_count=len(groups[im['id']])) for im in clear+boundary]
 manifest={'frozen_at':datetime.now().astimezone().isoformat(),'source':'https://github.com/yancie-yjr/scd.github.io','license':'CC BY-NC-SA 4.0','excluded_ids':sorted(used),'selection':'Unused validation images with 2–8 annotated cartons. First 15 interior and first 5 boundary images sorted by SHA256(cbyp-holdout20-v1:ID). Boundary means an annotation bbox within 2% of image edge. Frozen before download or tested-model calls. No replacements. Interior is a metadata stratum, NOT a clean-delivery guarantee.','scope':'20 distinct public photographs with authored notes/orders and synthetic speech. Not model-training holdout, field ground truth, SKU validation or labor-savings measurement. Visual references and targets to be frozen before model calls; uncertain images will not be forced into acceptance targets.','images':selected}
 (ROOT/'selection.json').write_text(json.dumps(manifest,indent=2))
 print('FROZEN',[(im['id'],im['stratum'],im['annotated_visible_count']) for im in selected],flush=True)
 z=zipfile.ZipFile(Remote());rows=[]
 for im in selected:
  p=ROOT/Path(im['file_name']).name;p.write_bytes(z.read('images/val2017/'+p.name))
  rows.append(dict(im,path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),annotations=groups[im['id']]))
  (ROOT/'downloaded.json').write_text(json.dumps(rows,indent=2));print('Downloaded',im['id'],flush=True)
if __name__=='__main__':main()
