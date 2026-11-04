"""Publish all preregistered mixed-control results without changing prior experiments."""
import collections,hashlib,html,json,statistics,shutil
from pathlib import Path
ROOT=Path('evaluation/inputs/preregistered-mixed-2026-11-03');OUT=Path('evaluation/private/preregistered-mixed-2026-11-03');DEST=Path('site/preregistered-mixed')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 m=json.loads((ROOT/'manifest.json').read_text());r=json.loads((OUT/'results.json').read_text());refs=json.loads((ROOT/'references.json').read_text())
 assert r['manifest_sha256']==digest(ROOT/'manifest.json')
 assert m==json.loads((OUT/'manifest.json').read_text())
 assert m['references_sha256']==digest(ROOT/'references.json')
 rows=r['rows'];assert len(rows)==21 and len({x['id'] for x in rows})==21
 assert {x['id'] for x in rows}=={x['id'] for x in m['cases']}
 byid={x['id']:x for x in rows}
 for p,h in m['code_sha256'].items():assert digest(ROOT/'runtime'/p)==h
 for c in m['cases']:
  for k,f in c['files'].items():
   assert digest(f['path'])==f['sha256']
   if byid[c['id']].get('evidence'):assert byid[c['id']]['evidence']['input_sha256'][k]==f['sha256']
  assert byid[c['id']]['expected_action']==c['expected_action']
  assert byid[c['id']]['started_at']>=m['frozen_at']
 counts=collections.Counter(x['action'] for x in rows);targets=collections.Counter(x['expected_action'] for x in rows)
 summary={'distinct_photos':7,'controls':21,'actions':dict(counts),'targets':dict(targets),'exact_targets_met':sum(x['exact_target_met'] for x in rows),'broad_safe_actions_met':sum(x['acceptable_action_met'] for x in rows),'clean_candidates':targets['post'],'accepted_clean_candidates':sum(x['expected_action']=='post' and x['action']=='post' for x in rows),'unexpected_accepts':sum(x['expected_action']!='post' and x['action']=='post' for x in rows),'technical_errors':counts['error'],'erp_writes':sum(bool(x.get('evidence',{}).get('erp_written')) for x in rows),'median_seconds':round(statistics.median(x['seconds'] for x in rows),1),'median_seconds_completed_decisions':round(statistics.median(x['seconds'] for x in rows if x['action']!='error'),1) if any(x['action']!='error' for x in rows) else None,'billing_cost':None,'labor_savings':None,'scope':'21 correlated authored controls on 7 project-unused public photos, one clean acceptance candidate. Not field accuracy or unseen-in-model-training evidence.'}
 assert summary['erp_writes']==0
 public=json.loads(json.dumps({'summary':summary,'manifest_sha256':r['manifest_sha256'],'manifest':m,'visual_references':refs,'rows':rows}))
 for c in public['manifest']['cases']:
  for f in c['files'].values():f['filename']=Path(f.pop('path')).name
 DEST.mkdir(exist_ok=True);(DEST/'img').mkdir(exist_ok=True)
 text=json.dumps(public,ensure_ascii=False,indent=2);(DEST/'results.json').write_text(text);Path('evaluation/preregistered-mixed-2026-11-03.json').write_text(text)
 e=html.escape;labels={'post':'Kabul','block':'Ret','human':'İnsan incelemesi','error':'Teknik hata'};variants={'baseline':'Temel belge','quantity_mismatch':'Yanlış miktar','receiver_uncertain':'Kararsız ses'}
 photos=[]
 for src in json.loads((ROOT/'downloaded.json').read_text()):
  # Keep original bytes; no crop or image alteration.
  filename=f"scd-train-{src['id']}.jpg";shutil.copyfile(src['path'],DEST/'img'/filename)
  ref=refs[str(src['id'])]
  photos.append(f'<figure><a href="img/{filename}"><img loading="lazy" src="img/{filename}" alt="SCD train {src["id"]}"></a><figcaption><code>{src["id"]}</code> · {labels[ref["target"]]}<p>{e(ref["reason"])}</p></figcaption></figure>')
 table=[];details=[]
 for x in rows:
  c=next(c for c in m['cases'] if c['id']==x['id']);ev=x.get('evidence',{});reason='; '.join(ev.get('decision',{}).get('reasons',[])) or x.get('error_type','')
  table.append(f'<tr><td><code>{x["source_image_id"]}</code></td><td>{variants[x["scenario"]]}</td><td>{labels[x["expected_action"]]}</td><td class="{x["action"]}">{labels[x["action"]]}</td><td><code>{e(x.get("rule",x.get("error_type","")))}</code></td><td>{x["seconds"]:.1f} sn</td><td>{"✓" if x["exact_target_met"] else "✗"}</td></tr>')
  details.append(f'<details><summary><code>{e(x["id"])}</code> · {labels[x["action"]]}</summary><p data-original-evidence>{e(reason)}</p><pre>{e(json.dumps(x,ensure_ascii=False,indent=2))}</pre></details>')
 page='''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Yeni karma test · Count Before You Post</title><style>body{margin:0;background:#f5f4ee;color:#17313e;font:16px/1.6 system-ui}main{max-width:1150px;margin:auto;padding:32px 22px}h1{font-size:clamp(28px,4vw,44px);line-height:1.15}a{color:#175bdb}.notice{padding:20px;background:#e7eef9;border-left:4px solid #345ad7}.photos{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}figure{margin:0;background:white;padding:12px}img{width:100%;height:190px;object-fit:contain}figcaption{font-size:13px}table{width:100%;border-collapse:collapse;background:white}th,td{padding:12px;border-bottom:1px solid #ddd;text-align:left}.scroll{overflow:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;background:white;padding:16px}details{margin:12px 0}summary{cursor:pointer}.post{color:#17673f}.block,.error{color:#a22030}</style><script src="../i18n/ui.js" defer data-ui-i18n></script></head><body><main><nav><a href="../jury/">← Jüri demosu</a> · <a href="../unseen-validation/">İlk fotoğraf testi</a> · <a href="../unseen-regression/">Önceki düzeltme testi</a></nav><h1>7 yeni fotoğraf.<br>21 önceden sabitlenmiş kontrol.</h1><p>3 Kasım 2026 · Üretimdeki 39042b9 koduyla yeni girdilerde ilk koşular.</p>'''
 page+=f'<section class="notice"><strong>{counts["post"]} kabul · {counts["block"]} ret · {counts["human"]} insan incelemesi · {counts["error"]} teknik hata.</strong><p>Kesin hedef eşleşmesi: {summary["exact_targets_met"]}/21. Temiz kabul adayı: {summary["accepted_clean_candidates"]}/{summary["clean_candidates"]}. Kabul beklenmeyen kontrollerde kabul: {summary["unexpected_accepts"]}/20.</p><p>Tüm denemelerde medyan: {summary["median_seconds"]} sn. Karar üretenlerde medyan: {summary["median_seconds_completed_decisions"]} sn. ERP yazımı: 0. Maliyet ve çalışan zamanı ölçülmedi.</p></section>'
 unexpected=[x for x in rows if x['expected_action']!='post' and x['action']=='post']
 page+='<h2>Teknik hataların sınırı</h2><p>Üç kontrol karar aşamasında RuntimeError, dokuz kontrol belge okuma aşamasında APIConnectionError ile durdu. Sonraki erişim kontrolünde GitHub çalışırken Meta HTTPS bağlantısı zaman aşımına uğradı. Karar aşamasındaki üç hatanın kök nedeni kesinleşmedi. Temiz adayın üç kontrolü de bağlantı hatası nedeniyle sonuçsuzdur. Bu hatalar doğru ret veya insan incelemesi sayılmaz.</p>'
 page+='<h2>Beklenmeyen kabuller</h2>'
 if unexpected:
  page+='<p>Önceden ret veya inceleme hedeflenen şu kontroller kabul edildi. Bunlar test hedeflerine göre başarısızlıktır; gerçek ERP kaydı veya doğrulanmış fiziksel stok hatası değildir.</p><ul>'+''.join('<li><code>'+e(x['id'])+'</code></li>' for x in unexpected)+'</ul>'
 else:page+='<p>Önceden ret veya inceleme hedeflenen kontrollerde kabul oluşmadı.</p>'
 page+='<h2>Temiz adayın üç kontrolü</h2><ul>'+''.join('<li>'+variants[x['scenario']]+': '+labels[x['expected_action']]+' → '+labels[x['action']]+' (<code>'+e(x.get('rule',x.get('error_type','')))+')</code></li>' for x in rows if x['source_image_id']==3690)+'</ul>'
 page+='''<h2>Hedefler sonuçlardan önce belirlendi</h2><p>Canlıdaki kodun sabit kopyası, fotoğraflar, hazırlanmış belgeler, sesler ve karar hedefleri ilk model çağrısından önce SHA-256 özetleriyle kaydedildi. Sonuç sonrası fotoğraf eleme, hedef değiştirme veya uygulama koşusu tekrarı yoktur. SDK aktarım tekrarları mevcut ayarında kaldı. Her hata rapora dahildir.</p><p>Önceki tüm indirilmiş fotoğraf adları dışlandı; seçilen dosyaların özetleri de önceki dosyalardan farklı. SCD train2017 kümesinde tek koli anotasyonlu, kenarlardan uzak beş uygun fotoğrafın tamamı ve hash sırasındaki ilk iki kenar fotoğrafı kullanıldı. Başlangıçtaki altı iç-kadraj hedefi, indirme ve model çağrılarından önce yalnızca beş aday bulunduğu için beşe indirildi. Bu değişiklik seçim kaydında korunur.</p><h2>Temiz, kusurlu ve belirsiz ne demek?</h2><p>3690 numaralı fotoğraf tek temiz kabul adayıdır. Aynı fotoğrafın belgesinde miktar ikiye çıkarılınca hedef ret; teslim alan sesinde sayım belirsizleşince hedef insan incelemesidir. Diğer altı fotoğraf, açık/hasarlı ambalaj, belirsiz ürün veya eksik kadraj nedeniyle temel durumda da insan incelemesi hedefidir. Bunlar temiz teslimat olarak sayılmaz.</p><p>5545, 5199 ve 5623 için okunabilir ürün adı yoktur. Boş veya uydurulmuş bir ürün adı yerine belgede açıkça “Unverified contents” iddiası kullanıldı. Bunlar ürün belirsizliği kontrolleridir; doğru ürün adı okuma başarısını ölçmez. Miktar kusuru belirsiz fotoğraflarda da denenir; erken ret veya inceleme miktar kontrolünü maskeleyebilir. Ret veya insan incelemesi biçimindeki geniş güvenli duruş, kesin hedef eşleşmesi değildir.</p><h2>Yorumlama sınırları</h2><p>Yedi fotoğrafın her birinden üç kontrol üretildi; 21 bağımsız fiziksel teslimat yoktur. Yalnızca bir temiz aday olduğundan genel otomatik kabul oranı çıkarılamaz. Fotoğraflar bu projede yenidir; modellerin eğitiminde görülmediği iddia edilmez. Veri kümesinin train2017 bölümü kullanılmıştır. Hedefler asistanın ön incelemesine dayanır; bağımsız saha doğrusu değildir.</p><p>Gerçek fotoğraflara sentetik belgeler ve sesler eşlik eder. Ürün açıklaması profili kullanıldı; kesin SKU veya içerik doğrulaması değildir. Hiçbir ERP kaydı yazılmadı. Süreler iş gücü tasarrufu değildir. Başka çalışmada tamamlanan 20 fotoğraflık test bu setten ayrıdır ve seçime dahil edilmedi.</p><p>Kaynak: <a href="https://github.com/yancie-yjr/scd.github.io">SCD / LSCD, Jinrong Yang ve diğerleri</a> · CC BY-NC-SA 4.0. Görseller modele değiştirilmeden verildi.</p><h2>Yedi fotoğraf ve önceden verilen hedefler</h2><div class="photos">'''+''.join(photos)+'</div><h2>21 sonucun tamamı</h2><div class="scroll"><table><thead><tr><th>Fotoğraf</th><th>Kontrol</th><th>Önceden hedef</th><th>Karar</th><th>Kural / hata</th><th>Süre</th><th>Kesin hedef</th></tr></thead><tbody>'+''.join(table)+'</tbody></table></div>'
 page+=f'<h2>Ham sonuçlar ve sabit manifest</h2><p><a href="results.json">Tüm 21 sonuç ve protokol (JSON)</a></p><p>Manifest SHA-256: <code>{r["manifest_sha256"]}</code></p>'+''.join(details)+'</main></body></html>'
 (DEST/'index.html').write_text(page)
 print(json.dumps(summary,ensure_ascii=False,indent=2));print('All input, target, code and manifest hashes verified.')
if __name__=='__main__':main()
