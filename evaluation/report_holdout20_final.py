"""Combine 17 initially valid cases and 3 first-model-call addendum fixtures.
Keep all 23 attempted fixtures and both manifests; do not hide invalid inputs.
"""
import collections,hashlib,html,json,statistics
from pathlib import Path
from urllib.parse import quote
from evaluation.run_holdout20 import digest
BASE=Path('evaluation/private/holdout20-2026-11-03');ADD=Path('evaluation/private/holdout20-input-addendum-2026-11-03')
def main():
 m=json.loads((BASE/'manifest.json').read_text());a=json.loads((ADD/'manifest.json').read_text());orig=json.loads((BASE/'results.json').read_text());extra=json.loads((ADD/'results.json').read_text())
 assert orig['manifest_sha256']==digest(BASE/'manifest.json')
 assert extra['manifest_sha256']==digest(ADD/'manifest.json')
 assert a['parent_manifest_sha256']==orig['manifest_sha256']
 by_id={r['id']:r for r in orig['rows']};cases={c['id']:c for c in m['cases']};replacement={}
 for c in a['cases']:
  old=by_id[c['replaces_invalid_fixture']]
  assert old['action']=='error' and old['error_type']=='ValueError' and 'evidence' not in old and 'partial' not in old
  assert not cases[old['id']]['order']['product']
  replacement[c['source_image_id']]=c['id'];cases[c['id']]=c
 rows=[r for r in orig['rows'] if r['source_image_id'] not in replacement]+extra['rows']
 assert len(orig['rows'])==20 and len(extra['rows'])==3 and len(rows)==20 and len({r['source_image_id'] for r in rows})==20
 for r in rows:
  c=cases[r['id']];assert c['order']['product'];assert r['expected_action']==c['expected_action']
  for f in c['files'].values():assert digest(f['path'])==f['sha256']
  if 'evidence' in r:
   e=r['evidence'];assert e['decision']['action']==r['action'];assert not e['erp_written'];assert e['input_sha256']=={k:v['sha256'] for k,v in c['files'].items()}
 counts=collections.Counter(r['action'] for r in rows);pos=[r for r in rows if r['expected_action']=='post'];neg=[r for r in rows if r['expected_action']!='post']
 s={'distinct_photos':20,'valid_fixtures':20,'fixture_attempts_including_invalid':23,'pre_model_invalid_fixtures_retained':3,'actions':dict(counts),'exact_targets_met':sum(r['action']==r['expected_action'] for r in rows),'acceptable_actions_met':sum(r['action'] in cases[r['id']]['acceptable_actions'] for r in rows),'acceptance_candidates':len(pos),'accepted_candidates':sum(r['action']=='post' for r in pos),'nonpost_targets':len(neg),'unexpected_accepts':sum(r['action']=='post' for r in neg),'model_workflow_errors':counts['error'],'median_seconds_valid_attempts':round(statistics.median(r['seconds'] for r in rows),1),'erp_writes':0,'human_labor_savings':None,'total_cost_usd':None}
 def public(x):
  x=json.loads(json.dumps(x))
  for c in x['cases']:
   for f in c['files'].values():f['filename']=Path(f.pop('path')).name
  return x
 payload={'summary':s,'initial_manifest_sha256':orig['manifest_sha256'],'addendum_manifest_sha256':extra['manifest_sha256'],'initial_manifest':public(m),'addendum_manifest':public(a),'valid_first_model_runs':rows,'all_initial_attempts':orig['rows'],'all_addendum_attempts':extra['rows']}
 Path('evaluation/holdout20-final-2026-11-03.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
 esc=lambda s:html.escape(str(s));labels={'post':'Kabul','block':'Ret','human':'İnsan incelemesi','error':'Teknik hata'}
 table=[];details=[]
 for r in sorted(rows,key=lambda r:r['source_image_id']):
  c=cases[r['id']];e=r.get('evidence',{});reason=' '.join(e.get('decision',{}).get('reasons',[])) or r.get('error_type','')
  table.append(f"<tr><td>{r['source_image_id']}</td><td>{esc(r['scenario'])}</td><td>{labels[r['expected_action']]}</td><td>{labels[r['action']]}</td><td>{esc(r.get('rule',r.get('error_type','')))}</td><td>{r['seconds']:.1f}</td></tr>")
  links=' · '.join(f"<a href='{quote(str(Path(c['files'][k]['path']).relative_to(Path('evaluation').resolve())))}'>{label}</a>" for k,label in [('camera','Orijinal fotoğraf'),('note','Test belgesi'),('audio','Sentetik ses')])
  details.append(f"<details><summary>{r['source_image_id']} — {labels[r['action']]}</summary><p>{links}</p><p>Önceden hedef: {esc(c['reference_rationale'])}</p><p>Gerçek karar: {esc(reason)}</p><pre>{esc(json.dumps(r,ensure_ascii=False,indent=2))}</pre></details>")
 page='''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>20 yeni fotoğraf — doğrulanmış sonuçlar</title><style>body{font:16px/1.6 system-ui;color:#172647;background:#f8f5ed;margin:0}main{max-width:1100px;margin:auto;padding:32px 24px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:450px;overflow:auto;font-size:12px}details{padding:15px;border-bottom:1px solid #ddd}.scroll{overflow:auto}.notice{padding:20px;background:#e8eef8;border-radius:12px}summary{cursor:pointer}a{color:#2458ce}</style><main><h1>20 yeni fotoğraf.<br>Geçerli girdilerle ilk model koşuları.</h1>'''
 page+=f"<div class='notice'><strong>{counts['post']} kabul · {counts['block']} ret · {counts['human']} insan incelemesi · {counts['error']} model akışı hatası</strong><p>Kabul adayları: {s['accepted_candidates']}/{s['acceptance_candidates']}. Otomatik kabul verilmemesi gereken {len(neg)} örnekte beklenmeyen kabul: {s['unexpected_accepts']}. Kesin hedef eşleşmesi: {s['exact_targets_met']}/20. Medyan: {s['median_seconds_valid_attempts']} saniye. ERP yazımı yok.</p></div>"
 page+='''<h2>Üç hazırlık hatası saklanmadı</h2><p>İlk 20 girdiden 410, 162 ve 599 için ürün adı okunamadığından boş bırakıldı. Uygulama bu üç geçersiz siparişi model çağrısı öncesinde reddetti. Bunlar uygulamanın görsel başarısızlığı değil, test hazırlama hatasıdır. İlk 20 satır değiştirilmeden saklandı.</p><p>Aynı üç fotoğraf için ayrıca sabitlenen belgelerde bilerek yanlış “Sunflower oil 5 L” iddiası kullanıldı; fotoğraflar ilaç kolileri gösteriyor. Amaç, doğru ilaç adını uydurmadan yanlış ürün iddiasını sınamak. Bu üçü için ilk model çağrıları ek koşuda yapıldı; sonuç alınmış hiçbir model kararı yeniden denenmedi. Toplam 23 girdi denemesi ve 20 farklı fotoğrafa ait 20 geçerli ilk model koşusu vardır. Bu protokol sapması raporda açıkça korunur.</p><h2>Önceden sabitlenen seçim</h2><p>Önceki 43 fotoğraf dışlandı; 20 yeni dosyanın SHA-256 özetleri de önceki fotoğraflardan farklı. SCD doğrulama kümesinde 2–8 koli anotasyonlu fotoğraflar arasından sabit hash sırasıyla 15 iç kadraj, 5 kenar kadraj görüntüsü seçildi. Daha dar 2–4 ve 2–6 aralıklarında yeterli aday bulunmadığı, indirme/model çağrısı öncesinde tespit edildi. Sonuç sonrası fotoğraf eleme yok.</p><p>Görsel inceleme dört kabul adayı belirledi: 541, 330, 320 ve 340. Hepsinde görünür etiketler ve sayımlar tutarlı görünse de istif ve gizli derinlik riski var. Hedefler bağımsız saha doğrusu değil, asistanın model çağrısı öncesi değerlendirmesidir. Bazı fotoğraflar aynı sahnenin farklı açılarıdır; 20 dosya, 20 bağımsız fiziksel teslimat anlamına gelmez.</p><h2>Yorumlama sınırları</h2><p>Bu set 10 temiz kabul hedefli dengeli test değildir. Beş miktar kusuru örneğinde karışık/örtülü ürünler de vardır; miktar hatasını diğer kusurlardan bağımsız ölçmez. Üç ek örnek ise bilerek yanlış ürün iddiasını sınar. Erken kapı kuralları daha sonraki kontrolleri maskeleyebilir. Geniş güvenli duruş (ret veya insan incelemesi), kesin hedefle aynı değildir.</p><p>Ürün adı eşleştirme profili kullanıldı; kesin SKU doğrulaması değil. Gerçek fotoğraflar, hazırlanmış not/siparişler ve sentetik seslerle sınandı. Modellerin bu fotoğrafları eğitimde görmediği bilinmiyor. Kod izole kopyadan çalıştı. Girdi ve karar hash'leri doğrulandı. ERP yazımı yapılmadı. Çalışanın aktif zamanı ve toplam API faturası ölçülmedi; süreler iş gücü tasarrufu değildir.</p><p>Kaynak: <a href="https://github.com/yancie-yjr/scd.github.io">SCD / LSCD, Jinrong Yang ve diğerleri</a>, CC BY-NC-SA 4.0. Orijinal görüntüler modele kırpılmadan verildi.</p><h2>Tüm geçerli ilk model sonuçları</h2>'''
 page+='<h2>Kabul adaylarında ne oldu?</h2><ul>'+''.join(f"<li>{r['source_image_id']}: {labels[r['action']]} — {esc(r.get('rule','error'))}. {esc(' '.join(r.get('evidence',{}).get('decision',{}).get('reasons',[])))}</li>" for r in pos)+'</ul><p>541 ve 320 örneklerinde SAM ve Spark toplam altı kolide anlaşırken nesne eşleştirmesi anlaşamadı. 340 örneğinde altı güçlü tespite ek olarak, sol kenarda yaklaşık 0,789 güvenli küçük bir tespit kadraj kontrolünü tetikledi. Bunun gerçekten teslimata ait koli olup olmadığı bu testte bağımsız doğrulanmadı. 330 ise örtülme/istif kuralında durdu. Bu nedenler otomatik kabul faydasını sınırlıyor; eşikleri gevşetmek için tek başına yeterli kanıt değiller.</p>'
 page+='<div class="scroll"><table><thead><tr><th>Fotoğraf</th><th>Kontrol</th><th>Hedef</th><th>Karar</th><th>Kural/hata</th><th>Saniye</th></tr></thead><tbody>'+''.join(table)+'</tbody></table></div><p><a href="holdout20-final-2026-11-03.json">Tüm 23 deneme ve iki sabit manifest (JSON)</a> · <a href="holdout20-report.html">İlk 20 denemenin değişmemiş raporu</a></p><h2>Kararların kanıtları</h2>'+''.join(details)+'</main></html>'
 Path('evaluation/holdout20-final-report.html').write_text(page)
 print(json.dumps(s,ensure_ascii=False,indent=2));print('Both manifests, all inputs and first-model-run integrity verified.')
if __name__=='__main__':main()
