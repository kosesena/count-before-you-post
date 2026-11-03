"""Audit and summarize the complete first-run holdout; never omit failed cases."""
import collections,hashlib,html,json,statistics
from urllib.parse import quote
from pathlib import Path
ROOT=Path('evaluation/inputs/holdout20-2026-11-03');OUT=Path('evaluation/private/holdout20-2026-11-03')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 m=json.loads((OUT/'manifest.json').read_text());r=json.loads((OUT/'results.json').read_text());rows=r['rows'];cases={c['id']:c for c in m['cases']}
 assert r['manifest_sha256']==digest(OUT/'manifest.json')==digest(ROOT/'manifest.json')
 assert len(rows)==len(cases)==20 and {r['id'] for r in rows}==set(cases)
 assert len({c['source_image_id'] for c in cases.values()})==20
 assert not ({c['source_image_id'] for c in cases.values()}&set(m['source_selection']['excluded_ids']))
 for c in cases.values():
  for v in c['files'].values():assert digest(v['path'])==v['sha256']
 for p,h in m['code_sha256'].items():assert digest(ROOT/'runtime'/p)==h
 for x in rows:
  c=cases[x['id']];assert x['expected_action']==c['expected_action'];assert x['exact_target_met']==(x['action']==c['expected_action'])
  if 'evidence' in x:
   e=x['evidence'];assert e['decision']['action']==x['action'];assert not e['erp_written'];assert e['input_sha256']=={k:v['sha256'] for k,v in c['files'].items()}
 counts=collections.Counter(x['action'] for x in rows);pos=[x for x in rows if x['expected_action']=='post'];neg=[x for x in rows if x['expected_action']!='post']
 summary={'distinct_photos':20,'cases':20,'actions':dict(counts),'targets':dict(collections.Counter(x['expected_action'] for x in rows)),'exact_targets_met':sum(x['exact_target_met'] for x in rows),'acceptable_actions_met':sum(x['acceptable_action_met'] for x in rows),'acceptance_candidates':len(pos),'accepted_candidates':sum(x['action']=='post' for x in pos),'nonpost_targets':len(neg),'unexpected_accepts':sum(x['action']=='post' for x in neg),'technical_errors':counts['error'],'median_seconds_all_attempts':round(statistics.median(x['seconds'] for x in rows),1),'erp_writes':0,'total_cost_usd':None,'worker_time_saved':None,'missing_product_reference_cases':[c['id'] for c in cases.values() if not c['order']['product']],'fully_specified_controls':sum(bool(c['order']['product']) for c in cases.values())}
 public=json.loads(json.dumps(m))
 for c in public['cases']:
  for v in c['files'].values():v['filename']=Path(v.pop('path')).name
 payload={'summary':summary,'manifest_sha256':r['manifest_sha256'],'manifest':public,'rows':rows}
 dest=Path('evaluation/holdout20-2026-11-03.json');dest.write_text(json.dumps(payload,ensure_ascii=False,indent=2))
 esc=lambda x:html.escape(str(x));labels={'post':'Kabul','block':'Ret','human':'İnsan incelemesi','error':'Teknik hata'}
 table=[];details=[]
 for x in rows:
  c=cases[x['id']];e=x.get('evidence',{});reason=' '.join(e.get('decision',{}).get('reasons',[])) or x.get('error_type','')
  table.append(f"<tr><td>{c['source_image_id']}</td><td>{esc(c['scenario'])}</td><td>{labels[x['expected_action']]}</td><td>{labels[x['action']]}</td><td>{esc(x.get('rule',x.get('error_type','')))}</td><td>{x['seconds']:.1f}</td></tr>")
  photo=quote(str(Path(c['files']['camera']['path']).relative_to(Path('evaluation').resolve())))
  note=quote(str(Path(c['files']['note']['path']).relative_to(Path('evaluation').resolve())))
  details.append(f"<details><summary>{esc(x['id'])}: {labels[x['action']]}</summary><p><a href='{photo}'>Orijinal fotoğraf</a> · <a href='{note}'>Hazırlanan belge</a></p><p>Önceden hedef gerekçesi: {esc(c['reference_rationale'])}</p><p>Gerçek karar: {esc(reason)}</p><pre>{esc(json.dumps(x,ensure_ascii=False,indent=2))}</pre></details>")
 page='''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>20 yeni fotoğraf — ilk koşu</title><style>body{font:16px/1.6 system-ui;color:#172647;background:#f8f5ed;margin:0}main{max-width:1100px;margin:auto;padding:32px 24px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:450px;overflow:auto;font-size:12px}details{padding:15px;border-bottom:1px solid #ddd}.scroll{overflow:auto}.notice{padding:20px;background:#e8eef8;border-radius:12px}summary{cursor:pointer}a{color:#2458ce}</style><main><h1>20 yeni fotoğraf.<br>İlk koşuların tamamı.</h1>'''
 page+=f"<div class='notice'><strong>{counts['post']} kabul · {counts['block']} ret · {counts['human']} insan incelemesi · {counts['error']} teknik hata</strong><p>Kesin hedef: {summary['exact_targets_met']}/20. Kabul adayları: {summary['accepted_candidates']}/{len(pos)}. Otomatik kabul verilmemesi gereken {len(neg)} örnekte beklenmeyen kabul: {summary['unexpected_accepts']}. Medyan: {summary['median_seconds_all_attempts']} saniye. ERP yazımı: 0.</p></div>"
 page+='<h2>Ne ölçüldü?</h2><p>Önceden kullanılan 43 fotoğraf dışlandı. Model çağrılarından önce sabitlenen 20 farklı SCD görüntüsü seçildi. Veri anotasyonlarına göre 2–8 kolili, 15 iç kadraj ve 5 kenar kadraj örneği. Seçim hash sırasına göre; sonuç sonrası eleme veya örnek değiştirme yok. 2–4 ve 2–6 aralıklarında yeterli iç kadraj adayı olmadığı, indirme ve model çağrılarından önce saptandı; nihai aralık 2–8 olarak sabitlendi.</p><p>Görsel inceleme sonrasında, model çağrılarından önce hedefler ve ürün metinleri kaydedildi. Kabul adayı, görüntüde sayım/ürün eşleşmesi elverişli görünen örnektir; tüm fiziksel teslimatın doğrulandığı anlamına gelmez. Karışık veya belirsiz fotoğraflar korunur. Hedefler asistan incelemesi; bağımsız insan etiketlemesi değildir.</p><p>Tek fotoğraf başına tek kontrol; gerçek fotoğraflara hazırlanmış belge/sipariş ve sentetik ses eşlik eder. Miktar kusuru varsa belge ve sipariş bir fazla, ses anotasyon sayısında. Bu ürün-adı profili testidir; kesin SKU doğrulaması değildir. Tüm kod izole kopyadan çalıştı; girdilerin ve kodun SHA-256 özetleri doğrulandı. Sonuç sonrası düzeltme veya yeniden koşu yapılmadı. Mevcut SDK ağ tekrarları etkin.</p><h2>Referans kalitesi</h2><p>410, 162 ve 599 fotoğraflarında tam ürün adı güvenilir biçimde okunamadı. İsim uydurmak yerine belge/sipariş ürün alanı boş bırakıldı. Bunların güvenli durması, kameranın ürünü doğru okuduğu veya yeni görsel riskini yakaladığı anlamına gelmez. 778 üzerindeki SKÅDIS okuması da belirsizdir ve kabul hedefi değildir. Bu örnekler toplam 20 içinde korunur; otomasyon başarısı olarak sayılmaz.</p><p>Beş miktar kusuru örneği aynı zamanda karışık/örtülü yükler içerir; bu set miktar kusurunu diğer etkenlerden bağımsız ölçemez. Kabul adayları 541, 330, 320 ve 340 numaralı görüntülerdir. Bunlarda görünür yüzler tutarlı olsa da üst üste istif vardır; mevcut katı istif kuralının otomatik kabulü durdurması olasıdır. Hedefler model sonuçlarından önce belirlenmiş işletim beklentisidir; kapı kurallarını aynalamak için sonradan değiştirilmez.</p><h2>Sınırlar</h2><p>Fotoğrafların model eğitiminde bulunmadığı bilinmiyor. Farklı dosyalar bağımsız teslimatlar değildir; 659 ve 629 gibi aynı sahnenin farklı açıları vardır. Arka plan, örtülme ve karışık ürünler nedeniyle 10 temiz kabul kotası zorlanmadı. Bu deney saha doğruluğu veya iş gücü tasarrufu değildir. Model süresi ölçüldü, çalışan aktif süresi ve toplam API faturası ölçülmedi. Hatalar tabloda korunur ve başarı sayılmaz. Erken kapı kuralları, enjekte edilen miktar kusurunun kontrolüne ulaşılmasını önleyebilir.</p>'
 page+='<h2>20 sonucun tamamı</h2><div class="scroll"><table><thead><tr><th>Fotoğraf</th><th>Senaryo</th><th>Hedef</th><th>Sonuç</th><th>Kural/hata</th><th>Saniye</th></tr></thead><tbody>'+''.join(table)+'</tbody></table></div>'
 page+='<p><a href="holdout20-2026-11-03.json">Tam manifest ve ham sonuçlar</a></p><p>Kaynak: <a href="https://github.com/yancie-yjr/scd.github.io">SCD / LSCD, Jinrong Yang ve diğerleri</a>, CC BY-NC-SA 4.0. Fotoğraflar modele orijinal haliyle verildi.</p><h2>Her kararın kanıtı</h2>'+''.join(details)+'</main></html>'
 Path('evaluation/holdout20-report.html').write_text(page)
 print(json.dumps(summary,indent=2));print('All hashes, targets, counts and outcomes verified.')
if __name__=='__main__':main()
