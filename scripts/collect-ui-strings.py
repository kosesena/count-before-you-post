import json,re,hashlib,os
from html.parser import HTMLParser
from pathlib import Path
strings={}
def add(text,source,force=False):
 text=re.sub(r'\s+',' ',text).strip()
 if not text or len(text)>5000 or not re.search(r'[A-Za-zÀ-ž\u4e00-\u9fff]',text):return
 if re.match(r'^(?:https?://|\.?\.?/|data:|#[\w-]+$)',text):return
 if not force and not (' ' in text or re.search(r'[^\x00-\x7f]',text) or re.match(r'^[A-Z][a-z]',text)):return
 if re.search(r'(?:=>|document\.|\bfunction\b|querySelector|\breturn\b.*[;{}])',text):return
 key=hashlib.sha256(text.encode()).hexdigest()[:16]
 strings.setdefault(key,{'id':key,'text':text,'sources':[]})
 if source not in strings[key]['sources']:strings[key]['sources'].append(source)
class Extract(HTMLParser):
 def __init__(self,source):super().__init__();self.source=source;self.skip=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style','pre','code','textarea','svg'):self.skip.append(tag)
  if not self.skip:
   for k,v in attrs:
    if k in ('title','alt','placeholder','aria-label') and v:add(v,self.source)
 def handle_endtag(self,tag):
  if tag in self.skip:self.skip.remove(tag)
 def handle_data(self,data):
  if not self.skip:add(data,self.source,True)
for p in Path('site').rglob('*.html'):Extract(str(p)).feed(p.read_text())
for r in json.load(open(os.environ.get('CBYP_I18N_EXTRACT','/tmp/cbyp-i18n-extract.json'))):
 t=r['text']
 if '<' in t and '>' in t:Extract(r['file']).feed(t)
 else:add(t,r['file'])
def walk(value,source):
 if isinstance(value,str):add(value,source)
 elif isinstance(value,list):
  for v in value:walk(v,source)
 elif isinstance(value,dict):
  for k,v in value.items():
   if k not in ('id','name','model','colour','src','portrait','avatar','bg','avatar_large','image','file'):walk(v,source)
for p in Path('site').glob('data*.json'):
 data=json.loads(p.read_text())
 for key in ('characters','rules'):walk(data.get(key,[]),str(p))
 for c in data.get('cases',[]):
  for key in ('title','what'):walk(c.get(key,''),str(p))
  walk(c.get('gate',{}).get('reason',''),str(p))
for c in json.loads(Path('site/validation.json').read_text()).get('counting_area_controls',{}).get('rows',[]):
 walk(c.get('evidence',{}).get('decision',{}).get('reasons',[]),'site/validation.json')
for text in ['camera','masks','carton','cartons','{{0}} carton','{{0}} cartons','{{0}} koli','Original report (archived)','Interface language','Language catalog could not load. Reload to retry. Original interface shown.']:add(text,'shared UI',True)
Path('site/i18n/source.json').write_text(json.dumps(list(strings.values()),ensure_ascii=False,indent=2))
print('strings',len(strings),'characters',sum(len(x['text']) for x in strings.values()))
