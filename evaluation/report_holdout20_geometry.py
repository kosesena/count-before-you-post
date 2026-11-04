"""Audited before/after comparison; every case, error and change is preserved."""
import collections,html,json,statistics
from pathlib import Path
from urllib.parse import quote
from evaluation.run_holdout20 import digest
ROOT=Path('evaluation/inputs/holdout20-geometry-regression-v2-2026-11-03')
OUT=Path('evaluation/private/holdout20-geometry-regression-v2-2026-11-03')
def object_summary(row):
    entries=[t['gate_cross_check'] for t in row.get('evidence',{}).get('trace',[]) if 'gate_cross_check' in t]
    return {k:entries[-1].get(k) for k in ['agreed','sam_only','spark_only','doubled']} if entries else None

def summarize(rows):
 pos=[r for r in rows if r['expected_action']=='post'];neg=[r for r in rows if r['expected_action']!='post'];counts=collections.Counter(r['action'] for r in rows)
 completed=[r for r in rows if r['action']!='error'];completed_negative=[r for r in neg if r['action']!='error']
 return {'cases':len(rows),'completed_decisions':len(completed),'completed_nonpost_targets':len(completed_negative),'median_seconds_completed':round(statistics.median(r['seconds'] for r in completed),1) if completed else None,'actions':{k:counts[k] for k in ['post','block','human','error']},'exact_targets_met':sum(r['action']==r['expected_action'] for r in rows),'accepted_candidates':sum(r['action']=='post' for r in pos),'acceptance_candidates':len(pos),'unexpected_accepts':sum(r['action']=='post' for r in neg),'nonpost_targets':len(neg),'median_seconds':round(statistics.median(r['seconds'] for r in rows),1),'erp_writes':sum(bool(r.get('evidence',{}).get('erp_written')) for r in rows)}
def main():
 m=json.loads((OUT/'manifest.json').read_text());r=json.loads((OUT/'results.json').read_text());before_payload=json.loads(Path('evaluation/holdout20-final-2026-11-03.json').read_text());before=before_payload['valid_first_model_runs'];after=r['rows'];old={x['id']:x for x in before};cases={c['id']:c for c in m['cases']}
 first_attempt_rows=list(after)
 recovery=None
 recovery_dir=Path('evaluation/private/holdout20-geometry-recovery-2026-11-03')
 if (recovery_dir/'results.json').exists():
  recovery=json.loads((recovery_dir/'results.json').read_text())
  rm=json.loads((recovery_dir/'manifest.json').read_text())
  assert recovery['manifest_sha256']==digest(recovery_dir/'manifest.json')==digest('evaluation/inputs/holdout20-geometry-recovery-2026-11-03/manifest.json')
  assert rm['code_sha256']==m['code_sha256']
  for path,h in rm['protected_files'].items():assert digest(path)==h,path
  errors={x['id'] for x in after if x['action']=='error'}
  assert len(errors)==17 and {x['id'] for x in recovery['rows']}==errors
  assert {c['id'] for c in rm['cases']}==errors
  for c in rm['cases']:assert c==cases[c['id']]
  replacements={x['id']:x for x in recovery['rows']}
  after=[replacements.get(x['id'],x) for x in after]
  recovery['manifest']=json.loads(json.dumps(rm))
  for c in recovery['manifest']['cases']:
   for f in c['files'].values():f['filename']=Path(f.pop('path')).name
 assert r['manifest_sha256']==digest(ROOT/'manifest.json')==digest(OUT/'manifest.json')
 assert len(after)==len(cases)==len(old)==20 and {x['id'] for x in after}==set(old)
 for p,h in m['protected_files'].items():assert digest(p)==h,p
 for p,h in m['code_sha256'].items():assert digest(ROOT/'runtime'/p)==h,p
 for x in after:
  c=cases[x['id']];o=old[x['id']];assert x['expected_action']==o['expected_action']==c['expected_action'];assert x['acceptable_actions']==o['acceptable_actions']
  for f in c['files'].values():assert digest(f['path'])==f['sha256']
  expected={k:v['sha256'] for k,v in c['files'].items()};assert o['evidence']['input_sha256']==expected
  if 'evidence' in x:
   e=x['evidence'];assert e['input_sha256']==expected;assert e['decision']['action']==x['action'];assert not e['erp_written']
   if x['action']=='post':
    assert e['result']['posted'] and e['result'].get('document') is None
    assert e['second_opinions'].get('audit',{}).get('ok') is True
 bs,ats=summarize(before),summarize(after)
 public=json.loads(json.dumps(m))
 for c in public['cases']:
  for f in c['files'].values():f['filename']=Path(f.pop('path')).name
 changes=[{'id':x['id'],'expected':x['expected_action'],'before':old[x['id']]['action'],'before_rule':old[x['id']].get('rule'),'after':x['action'],'after_rule':x.get('rule'),'before_seconds':old[x['id']]['seconds'],'after_seconds':x['seconds'],'before_objects':object_summary(old[x['id']]),'after_objects':object_summary(x)} for x in after]
 payload={'before_summary':bs,'after_summary':ats,'comparison':changes,'manifest_sha256':r['manifest_sha256'],'manifest':public,'before_rows':before,'after_rows':after,'network_interrupted_first_attempt_rows':first_attempt_rows,'recovery':recovery,'recovery_connection_interruptions':[json.loads(p.read_text()) for p in sorted(Path('evaluation/private').glob('holdout20-geometry-recovery-2026-11-03-connection-interrupted-*/interrupted-results.json'))],'interrupted_attempt':json.loads(Path(m['interrupted_attempt']['path']).read_text()),'scope':'Post-hoc same-input regression, not new holdout accuracy. Fresh model outputs can differ; changes cannot all be attributed to code.'}
 Path('evaluation/holdout20-geometry-regression-2026-11-03.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
 esc=lambda s:html.escape(str(s));labels={'post':'Kabul','block':'Ret','human':'İnsan incelemesi','error':'Teknik hata'}
 table=[];details=[]
 for x in after:
  o=old[x['id']];c=cases[x['id']];e=x.get('evidence',{});reason=' '.join(e.get('decision',{}).get('reasons',[])) or x.get('error_type','')
  table.append(f"<tr><td>{c['source_image_id']}</td><td>{esc(c['scenario'])}</td><td>{labels[x['expected_action']]}</td><td>{labels[o['action']]}<br><small>{esc(o.get('rule',''))}</small></td><td>{labels[x['action']]}<br><small>{esc(x.get('rule',x.get('error_type','')))}</small></td><td>{o['seconds']:.1f} → {x['seconds']:.1f}</td></tr>")
  links=' · '.join(f"<a href='{quote(str(Path(c['files'][k]['path']).relative_to(Path('evaluation').resolve())))}'>{label}</a>" for k,label in [('camera','Orijinal fotoğraf'),('note','Değişmeyen belge'),('audio','Değişmeyen ses')])
  details.append(f"<details><summary>{esc(x['id'])}: {labels[o['action']]} → {labels[x['action']]}</summary><p>{links}</p><p>Önceden hedef: {esc(c['reference_rationale'])}</p><p>Yeni karar: {esc(reason)}</p><h3>Önce</h3><pre>{esc(json.dumps(o,ensure_ascii=False,indent=2))}</pre><h3>Sonra</h3><pre>{esc(json.dumps(x,ensure_ascii=False,indent=2))}</pre></details>")
 page='''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kutu eşleştirme ve kadraj — 20 örnek regresyonu</title><style>body{font:16px/1.6 system-ui;color:#172647;background:#f8f5ed;margin:0}main{max-width:1150px;margin:auto;padding:32px 24px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:450px;overflow:auto;font-size:12px}details{padding:15px;border-bottom:1px solid #ddd}.scroll{overflow:auto}.notice{padding:20px;background:#e8eef8;border-radius:12px}summary{cursor:pointer}a{color:#2458ce}</style><main><h1>Aynı 20 örnek.<br>Kutu eşleştirme ve kadraj düzeltmesinden sonra.</h1>'''
 stats=[('Kabul',bs['actions']['post'],ats['actions']['post']),('Ret',bs['actions']['block'],ats['actions']['block']),('İnsan incelemesi',bs['actions']['human'],ats['actions']['human']),('Çözülemeyen teknik hata',bs['actions']['error'],ats['actions']['error']),('Kabul adaylarında kabul',f"{bs['accepted_candidates']}/4",f"{ats['accepted_candidates']}/4"),('Kabul verilmemesi hedeflenenlerde kabul',f"{bs['unexpected_accepts']}/16",f"{ats['unexpected_accepts']}/{ats['completed_nonpost_targets']} tamamlanan"),('Kesin hedef eşleşmesi',f"{bs['exact_targets_met']}/20",f"{ats['exact_targets_met']}/20"),('Karar üreten örnek sayısı',bs['completed_decisions'],ats['completed_decisions']),('Tamamlanan kararlarda medyan süre (sn)',bs['median_seconds_completed'],ats['median_seconds_completed']),('ERP yazımı',bs['erp_writes'],ats['erp_writes'])]
 if ats['actions']['error']:
  page+=f"<div class='notice'><strong>Karşılaştırma tamamlanamadı: {ats['completed_decisions']}/20 karar, {ats['actions']['error']} teknik hata.</strong><p>Hatalar başarı veya güvenli ret sayılmaz. Hızlı bağlantı hataları tüm-deneme medyanını düşürür; bu hız iyileşmesi değildir. Beklenmeyen kabul sayısı yalnızca karar üreten örnekleri kapsar; eksik sonuçlar güvenlik başarısı olarak yorumlanamaz.</p></div>"
 if recovery is not None:
  page+="<div class='notice'><strong>Bağlantı sonrası toparlama:</strong> 3 önceki karar korundu; yalnızca 17 teknik hata aynı kod ve girdilerle yeniden çalıştırıldı. İlk hata denemeleri saklıdır. Süreler farklı bağlantı koşullarından geldiği için saf bir hız karşılaştırması değildir.</div>"
 page+='<table><tr><th>Ölçüt</th><th>Önce</th><th>Sonra</th></tr>'+''.join(f'<tr><td>{label}</td><td>{b}</td><td>{a}</td></tr>' for label,b,a in stats)+'</table>'
 page+='''<h2>Ne düzeltildi?</h2><ul><li>Tüm Spark ve SAM görüntü çağrıları EXIF yönü uygulanmış, yön metaverisi kaldırılmış kayıpsız PNG piksellerini alıyor. Özgün dosyalar değiştirilmedi; model girdilerinde kırpma/yeniden boyutlandırma yapılmadı. Böylece nokta, maske ve kenar kontrolleri aynı piksel koordinatlarını kullanıyor.</li><li>Nokta okuyucu artık tavan kamerası veya düzenli ızgara varsaymıyor. Her görünür kutunun gerçek yüzünde, bant/etiket/kenardan uzakta tek nokta işaretliyor. Tanısal 541 koşusunda eski istem, iki sütun/üç sıra yerine üç sütun/iki sıra noktalar üretmişti.</li><li>Eşleşmede rastgele ilk örtüşen kutu seçilmiyor. Aynı kimlikli birden fazla nokta maskesi veya birden fazla uyumlu kutu varsa karar belirsiz kalıyor. Nokta maskesi kendi istem noktasını da içermek zorunda. Koordinat aralığı hataları sessizce kırpılmıyor.</li><li>Kadraj kontrolü dolu maske piksellerini kullanıyor. Yalnızca kutunun sınırlayıcı dikdörtgenindeki boş dolgu kenara değiyorsa bu gerçek nesne teması sayılmıyor. Gerçek maske kenara değerse, küçük veya düşük güvenli olsa bile inceleme sürüyor.</li><li>Maske boyutu, boş maske veya görüntü dışı koordinat hatası kabulü durduruyor. Güven eşikleri, %1 kenar bandı, %80 maske kapsaması ve 1,5 büyüme sınırı değiştirilmedi. Ürün/miktar/ses/ikinci okuyucu/denetim kontrolleri gevşetilmedi.</li><li>İz kayıtları nokta koordinatlarını, eşleşme adaylarını ve maske sınırlarını saklıyor.</li></ul><h2>Korunan ara koşu</h2><p>Yalnızca istemi düzelten ilk ara koşuda EXIF yön uyuşmazlığı fark edildi. Üç karar tamamlanmıştı; üç çağrı sürüyordu ve 14 örnek başlamamıştı. Süreç durduruldu; bu kayıtlar silinmedi ve başarı sayılmadı. Ardından EXIF düzeltmeli koşuda üç karar tamamlandı, 17 örnek teknik hatayla durdu. Bağlantı geri geldikten sonra yalnızca bu 17 örnek aynı sabit sürümle bir kez daha çalıştırıldı; tamamlanan üç karar değiştirilmedi. Toparlama sonuçları varsa tablodaki sonuçlar iki aşamanın birleşimidir; bağlantı nedeniyle toparlama da durduysa ilk teknik hatalar tabloda kalır. Toparlamanın kesinti kayıtları recovery_connection_interruptions alanındadır; ilk 17 hata JSON dosyasında network_interrupted_first_attempt_rows alanında, toparlama denemeleri recovery alanında korunur. Ara kayıtlar JSON dosyasında interrupted_attempt alanındadır.</p><h2>Karşılaştırma dürüstlüğü</h2><p>Aynı 20 geçerli girdi kullanıldı: ilk koşudaki 17 geçerli belge ve daha önce ayrıca sabitlenmiş üç yanlış-ürün ek belgesi. İlk hazırlıkta boş ürünle durdurulan üç kayıt eski raporda kalır; burada tekrar çalıştırılmaz. Fotoğraf, belge, ses, sipariş, hedef ve kabul edilebilir kararlar değişmedi. Dosya özetleri doğrulandı; önceki sonuçlar korunuyor.</p><p>Yeni kod çağrıdan önce izole kopyaya alındı. Tamamlanmış model kararları yeniden denenmedi. İlk koşuda teknik hata veren 17 örnek, ağ geri geldikten sonra aynı girdilerle ayrı toparlama koşusunda çalıştırıldı. Hatalar silinmedi; bu protokol sapması açıkça raporlandı. SDK ağ tekrarları değişmedi. Eski istemi inceleyen 541 tanısal geometri çağrısı bu 20 karara dahil değil.</p><p>Bu, daha önce görülen örnekler üzerinde düzeltme sonrası regresyondur; yeni veri doğruluğu değildir. Taze model çağrıları farklı çıktılar verebilir, bu nedenle değişimin tamamı koda bağlanamaz. Dört kabul adayı bağımsız saha doğrusu değildir. İnsan iş yükü tasarrufu ve toplam API faturası ölçülmedi. ERP yazımı yok.</p>'''
 page+='<h2>Dört kabul adayının nesne eşleştirmesi</h2><p>Sıra: eşleşen / yalnız SAM / yalnız Spark / çift nokta. Bu aşamanın düzelmesi, bağımsız istif, ürün veya denetim kurallarını geçersiz kılmaz.</p><table><tr><th>Fotoğraf</th><th>Önce</th><th>Sonra</th><th>Son karar kuralı</th></tr>'+''.join(f"<tr><td>{x['source_image_id']}</td><td>{esc(object_summary(old[x['id']]))}</td><td>{esc(object_summary(x))}</td><td>{esc(x.get('rule',x['action']))}</td></tr>" for x in after if x['expected_action']=='post')+'</table>'
 page+='<h2>20 örneğin tamamı</h2><div class="scroll"><table><tr><th>Fotoğraf</th><th>Senaryo</th><th>Hedef</th><th>Önce</th><th>Sonra</th><th>Saniye</th></tr>'+''.join(table)+'</table></div><p><a href="holdout20-geometry-regression-2026-11-03.json">Tüm önce/sonra kayıtları ve sabit manifest</a> · <a href="holdout20-final-report.html">Önceki rapor</a></p><h2>Örnek başına kanıt</h2>'+''.join(details)+'</main></html>'
 Path('evaluation/holdout20-geometry-comparison.html').write_text(page)
 print(json.dumps({'before':bs,'after':ats},ensure_ascii=False,indent=2));print('All protected files, input hashes, frozen code, targets and rows verified.')
if __name__=='__main__':main()
