"""Fetch 30 fixed validation images using HTTP ranges; run from repo root.
Dataset CC BY-NC-SA 4.0, https://github.com/yancie-yjr/scd.github.io.
Downloads only data, executes no downloaded content.
"""
import io,json,urllib.request,zipfile,hashlib
from pathlib import Path
BASE='https://drive.usercontent.google.com/download?id=1JRk_YjPpGcTCB-bvlJ37KsI5Sx1tfbUc&export=download&confirm=t'
class Remote(io.RawIOBase):
 def __init__(self):self.pos=0;self.size=15617058890
 def seek(self,off,whence=0):
  self.pos=off if whence==0 else self.pos+off if whence==1 else self.size+off
  return self.pos
 def tell(self):return self.pos
 def seekable(self):return True
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  if not n:return b''
  start=self.pos;end=min(self.size-1,start+n-1)
  req=urllib.request.Request(BASE+'&range_start='+str(start),headers={'Range':f'bytes={start}-{end}'})
  with urllib.request.urlopen(req,timeout=60) as r:
   if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-'):raise ValueError('range not respected')
   b=r.read()
  self.pos+=len(b);return b
def main():
    root=Path('evaluation/inputs/scd')
    root.mkdir(parents=True, exist_ok=False)
    z=zipfile.ZipFile(Remote());infos=z.infolist()
    (root/'archive-index.json').write_text(json.dumps([{'name':i.filename,'size':i.file_size} for i in infos],indent=2))
    print('entries',len(infos),flush=True)
    print('annotations',[(i.filename,i.file_size) for i in infos if i.filename.endswith('.json')],flush=True)
    print('examples',[i.filename for i in infos[:12]],flush=True)
    ann=json.loads(z.read('annotations/instances_val2017.json'))
    (root/'instances_val2017.json').write_text(json.dumps(ann))
    images=sorted(ann['images'],key=lambda i:hashlib.sha256(('cbyp-2026-11-02:'+str(i['id'])).encode()).hexdigest())[:30]
    rows=[]
    for i in images:
     name=i['file_name'];member='images/val2017/'+Path(name).name
     data=z.read(member);dest=root/Path(name).name;dest.write_bytes(data)
     labels=[a for a in ann['annotations'] if a['image_id']==i['id']]
     rows.append({'id':str(i['id']),'file':str(dest),'sha256':hashlib.sha256(data).hexdigest(),'annotated_visible_count':len(labels),'annotations':labels,'width':i['width'],'height':i['height']})
     print('downloaded',len(rows),name,len(labels),flush=True)
     (root/'sample.json').write_text(json.dumps({'source':'https://github.com/yancie-yjr/scd.github.io','license':'CC BY-NC-SA 4.0','selection':'First 30 validation images sorted by SHA256(cbyp-2026-11-02:IMAGE_ID); no outcome-based filtering','scope':'Visible annotated cartons, not independent deliveries or physical total','cases':rows},indent=2))

if __name__ == "__main__":
    main()
