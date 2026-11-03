"""Focused document-only audit of the two historical OCR mismatches. Not full receipt trials."""
import json,os,sys,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def main():
 root=Path('evaluation/private/unseen-regression-v2-frozen-2026-11-03/runtime').resolve()
 sys.path.insert(0,str(root))
 for line in Path('.env').read_text().splitlines():
  k,sep,v=line.partition('=')
  if sep and k.strip() and k.strip() not in os.environ:os.environ[k.strip()]=v.strip()
 from cbyp.second_reader import read_note,SPARK_OPEN
 from cbyp.wonder import audit_note
 out=Path('evaluation/private/ocr-regression-2026-11-03');out.mkdir(exist_ok=False)
 m=json.loads(Path('evaluation/inputs/unseen-single-2026-11-03/manifest.json').read_text())
 def one(variant):
  cid='scd-711-'+variant;case=next(c for c in m['cases'] if c['id']==cid)
  original=json.loads(Path('evaluation/private/unseen-single-2026-11-03',cid+'.json').read_text())
  primary=original['evidence']['note'];note=case['files']['note']['path'];start=time.monotonic()
  r={'id':cid,'scope':'Focused document-only regression, historical first-reader output plus fresh independent reading/audit; no receipt decision or write.','original_primary':primary,'input_sha256':case['files']['note']['sha256']}
  try:
   r['second']=read_note(note,model=SPARK_OPEN)['claim'];r['audit']=audit_note(note,primary)
  except Exception as e:r['error_type']=type(e).__name__
  r['seconds']=round(time.monotonic()-start,3)
  (out/(cid+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(cid, 'error' if 'error_type' in r else 'completed',flush=True);return r
 with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(one,['quantity_mismatch','receiver_uncertain']))
 (out/'results.json').write_text(json.dumps({'rows':rows},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
