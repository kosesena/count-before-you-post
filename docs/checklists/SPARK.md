> 27 Ekim 2026 durumu. O gün düzeltilenler (çift kayıt, argüman doğrulama, zaman aşımı, JPG, SAM hata akışı, ajanın SAM kelimesi seçmesi, maskeler, nokta istemleri) için bkz. [docs/JOURNAL.md](../JOURNAL.md).

# Muse Spark kontrol listesi (27 Eki 2026)

Proje: `~/Desktop/count-before-you-post`. Model: `muse-spark-1.3`.
Kaynak: dev.meta.ai belgeleri (27 Eki'de okundu). Kod sadece okundu, hiçbir şey çalıştırılmadı.
`UNVERIFIED` = belgede açıkça yazmıyor.

Kısa sonuç: Spark'ı doğru ve ölçülü kullanıyoruz (şemalı okuma, Responses ajan döngüsü, effort ölçümü).
Eksik olan iki şey var: ajan döngüsü sağlam değil (henüz hiç çalışmadı) ve Spark'ın
"neden" dediği (reasoning özeti) hiç görünmüyor. README'de Glimmer ve Voice rol alıyor ama kodda yoklar.

## Özellik tablosu

Belge kökü: `https://dev.meta.ai/docs/`

| Özellik | Belge ne diyor | Kullanıyor muyuz | Doğru mu | Eklemeye değer mi |
|---|---|---|---|---|
| **Görsel anlama** | Responses'ta `input_image` (`image_url` düz metin), Chat Completions'ta `image_url: {url}`. Base64 data URL olur. Görsel başına 50 MB, istek başına 50 görsel. Görseli sadece `user` rolüne koy. [image-understanding](https://dev.meta.ai/docs/image-understanding) | Evet. İrsaliye `delivery_note.py:76`, palet `perception.py:39-41` | Evet. `user` rolünde, base64. Küçük kusur: `perception.py:34` MIME'ı hep `image/png` yazıyor; JPG fotoğrafta uyuşmaz. | Zaten var. |
| **Sayım: "önce işaretle, sonra say"** | Sayı için çıplak sayı isteme; modelden her nesneyi işaretlemesini iste, sonra say. Koordinatlar 0–1000 ızgara, sınırı biraz aşabilir (1001), sıkıştır. [image-understanding](https://dev.meta.ai/docs/image-understanding) | Kısmen. İlk deneyde noktalar kullanıldı (ARASTIRMA §6.7). Üründe `perception.py:17` sadece çıplak `cartons_visible` sayısı istiyor. | Belgeye göre zayıf. Çıplak sayı istiyoruz. | **Orta-yüksek.** Noktalar gelirse SAM kutularıyla nesne nesne eşleşme yapılır. Dağınık sahnede toplam tuttu ama sadece 37/59 kutu eşleşti; bu "kapı neden insana sordu" anını kanıtlar. |
| **Yapılandırılmış çıktı (JSON şema)** | Chat Completions: `response_format.json_schema`. Responses: `text.format`. Karıştırırsan çalışmaz. `strict` varsayılan `false`. Strict'te kök obje, her objede `additionalProperties:false`, bütün anahtarlar `required`. Çıktı her durumda şemaya bağlı. [structured-output](https://dev.meta.ai/docs/structured-output) | Evet. `delivery_note.py:67-70`, `perception.py:37-38` | Evet. Doğru endpoint'te doğru parametre, strict kurallarına uyuyor. 8/8 geçerli JSON ölçüldü. | Zaten var. |
| **Akıl yürütme düzeyi (effort)** | `minimal, low, medium, high, xhigh, max` (`max` sadece 1.3'te). `none` → 400. Chat Completions'ta `reasoning_effort`, Responses'ta `reasoning.effort`. Arama/biçim işleri için `low`. [reasoning](https://dev.meta.ai/docs/reasoning) | Evet. Hepsi `medium`: `delivery_note.py:59`, `perception.py:36`, `agent.py:111,125` | Evet. İrsaliye için medium = high ölçüldü (16/16), medium seçildi. `look` ve ajan için effort ölçülmedi. | **Düşük.** Ajan için `low` vs `medium` tur sayısı ölçülebilir. Belge, düşük effort'un tur sayısını artırabildiğini söylüyor ([cookbook](https://dev.meta.ai/docs/cookbook/interleaved-reasoning-tool-use)). |
| **Çıktı bütçesi (max tokens)** | Reasoning token'ları çıktı bütçesinden yer. Yetmezse cevap boş/kesik gelir. Chat Completions'ta asıl ad `max_completion_tokens`; `max_tokens` eski takma ad. Responses'ta `max_output_tokens` (en az 16). [reasoning](https://dev.meta.ai/docs/reasoning), [chat-completions](https://dev.meta.ai/docs/protocols/chat-completions) | Kısmen. `delivery_note.py:66` 16000, `perception.py:36` 8000. Ajanda **hiç yok**: `agent.py:110,124`. | Okumada evet: ölçülen en yüksek 1.849 çıktı token'ı, 16000 bol. `max_tokens` eski ad (çalışır). Ajanda varsayılan değer belgede yok (UNVERIFIED). | Düzeltme olarak gerekli (aşağıda). |
| **finish_reason / status kontrolü** | Bütçe biterse `finish_reason: length` (Chat) veya `status: incomplete` (Responses). [reasoning](https://dev.meta.ai/docs/reasoning), [error-handling](https://dev.meta.ai/docs/error-handling) | Kısmen. `delivery_note.py:83-84` kontrol ediyor. `perception.py:43` ve `agent.py:113-116` etmiyor. | Hayır, iki yerde eksik. | Düzeltme olarak gerekli. |
| **Araç çağırma (tool calling)** | Responses'ta düz tanım (`name`, `parameters` üstte). `tool_choice` sadece `"auto"`. `parallel_tool_calls` varsayılan `true`. Sonuç `function_call_output` + aynı `call_id`. `strict` çıktıyı garanti etmez: **argümanları kendi kodunda doğrula.** Model araç çağırmadan düz metinle de bitirebilir. [tool-calling](https://dev.meta.ai/docs/tool-calling) | Evet. `agent.py:28-45, 107-127` (yeni, hiç çalışmadı). | Kısmen. Tanım biçimi ve `call_id` doğru. Argüman doğrulaması yok, çift kayıt engeli yok, aracın hatası döngüyü düşürüyor, "karar vermeden bitti" durumu ele alınmıyor. | Zaten var; düzeltmeler aşağıda. |
| **Responses durum zinciri (`previous_response_id`)** | Reasoning'i araç turları arasında korur. `instructions`, `tools`, `reasoning.effort` taşınmaz: **her istekte yeniden gönder.** `store` varsayılan `true`. [protocols/responses](https://dev.meta.ai/docs/protocols/responses) | Evet. `agent.py:124-126` | Evet. Üçü de her turda yeniden gönderiliyor. Chat Completions yerine Responses seçimi doğru (Chat Completions reasoning'i turlar arasında taşımaz). | Zaten var. |
| **Reasoning özeti (`reasoning.summary`)** | Sadece Responses. `"auto" / "concise" / "detailed"`. `reasoning` çıktı öğesinin `summary` dizisinde gelir. Garanti değil, boş olabilir. Ham reasoning verilmez. [reasoning](https://dev.meta.ai/docs/reasoning) | Hayır. `agent.py:111,125` sadece `effort` veriyor; trace'e reasoning yazılmıyor (`agent.py:121`). | — | **Yüksek.** Bir satır. Ajanın her araç seçiminden önceki "neden"i trace'e ve demo ekranına girer. "Verifiable agents" anlatısı ve Best Agentic bonusu için en ucuz kanıt. |
| **Şifreli reasoning ile durumsuz tekrar** | `store:false` + `include:["reasoning.encrypted_content"]`, reasoning öğelerini geri gönder. `previous_response_id` ile birlikte → 400. [protocols/responses](https://dev.meta.ai/docs/protocols/responses) | Hayır. | — | **Düşük.** Gizlilik anlatısı ("ERP verisi sunucuda saklanmaz") için var ama demoya bir şey katmaz. |
| **Video anlama (Spark)** | Sadece `video/mp4`. Files API + `input_file`/`input_video` (`file_id`) ya da `input_video` + `video_url`. Çıktı bütçesi en az 4000. Uzun klipte `stream:true`. Boyut/süre sınırı yazmıyor. [video-understanding](https://dev.meta.ai/docs/video-understanding) | Hayır. Video sadece SAM'e gidiyor (`sam.py:69-87`). | — | **Orta.** SAM videoda en fazla 16 nesne izliyor. Spark aynı klibi izleyip "kaç koli indi, hasar var mı" derse videoda da iki bağımsız algı olur. Ama yeni bir ölçüm seti ister. |
| **PDF / dosya girişi** | Responses'ta `input_file` (`file_data`, `file_url`, `file_id`). İlk 100 sayfanın metni, ilk 50 sayfanın görüntüsü. [file-handling](https://dev.meta.ai/docs/file-handling) | Hayır. İrsaliye hep PNG. | — | **Orta.** Gerçek dünyada irsaliye çoğu zaman PDF (e-İrsaliye). `read_note`'a PDF yolu eklemek kolay; "gerçek kullanılır" puanına yarar. |
| **Files API** | `purpose="user_data"`, 1 GiB'e kadar, `file_id` tekrar kullanılır. [file-handling](https://dev.meta.ai/docs/file-handling) | Evet, ama sadece SAM videosu için (`sam.py:64-66`). | Evet. | **Düşük.** Aynı kamera karesi hem SAM'e hem Spark'a base64 gidiyor; bir kez yüklemek küçük tasarruf. |
| **Prompt önbelleği** | Otomatik. Sabit içerik başa, değişken sona. İsteğe bağlı `prompt_cache_key`; Responses'ta `prompt_cache_retention: "24h"`. Önbellekli girdi 0,15 $ / 1M (normal 1,25 $). [prompt-caching](https://dev.meta.ai/docs/prompt-caching), [pricing](https://dev.meta.ai/docs/pricing-rate-limits) | Dolaylı. İstemler zaten önde, görsel sonda (`delivery_note.py:75-76`). Anahtar verilmiyor. | Evet, sıra doğru. | **Düşük.** Görsel her seferinde farklı; kazanç az. |
| **Web arama (`web_search`)** | Sadece Responses ve Messages. `url_citation` ile kaynak. Model gerekmezse aramaz. [search-grounding](https://dev.meta.ai/docs/search-grounding) | Hayır. | — | **Düşük.** Mal kabul akışında dış bilgiye ihtiyaç yok. Zorla eklemek "gösteriş" gibi durur. |
| **Tool search (`defer_loading`)** | Yüzlerce araçlı ajanlar için. Yapılandırılmış çıktıyla birleşmez. [tool-search](https://dev.meta.ai/docs/tool-search) | Hayır (5 araç var). | — | **Düşük.** 5 araçta anlamsız. |
| **Computer use** | Sadece Responses, `{"type":"computer"}`. Ortamı, sürücüyü, ekran görüntüsünü biz sağlarız. `pending_safety_checks` insan kararıdır. [computer-use](https://dev.meta.ai/docs/computer-use) | Hayır. | — | **Düşük.** ERP'ye API'den, kapının arkasından yazmak tasarımın özü. Ekrana tıklayan ajan bu güvenceyi bozar. |
| **Akış (streaming) / background** | `stream:true` olay akışı. Akışsız istekler süre sınırına takılırsa 504. `background:true` kuyruğa alır, akışla birleşmez. [protocols/responses](https://dev.meta.ai/docs/protocols/responses) | Spark'ta hayır (sadece SAM akışlı, `sam.py:59`). | Sorun yok; Spark çağrıları 6–16 sn. | **Orta (demo için).** Ajan adımlarını canlı göstermek demo puanına yarar, Meta araç puanına az. |
| **Hata yönetimi / tekrar** | 429/500/503 → üstel bekleme + jitter, 3–5 deneme. 504'ü olduğu gibi tekrarlama. [error-handling](https://dev.meta.ai/docs/error-handling) | Hayır. `meta.py:28` zaman aşımı ve tekrar ayarı vermiyor (OpenAI SDK kendi varsayılanlarıyla çalışıyor). | Eksik. JOURNAL:167'de SAM akışı 11 dk asıldı; "timeout ile tekrar" denmiş ama kodda timeout yok. | Düzeltme olarak gerekli (canlı demo 4–9 Kas ayakta kalmalı). |
| **Token sayımı** | `POST /v1/responses/input_tokens`. [token-counting](https://dev.meta.ai/docs/token-counting) | Hayır. `usage` kaydediliyor (`delivery_note.py:85`). | Evet. | **Düşük.** Maliyet tablosu için `usage` yeterli. |
| **`safety_identifier`** | Son kullanıcı için sabit, gizli kimlik (≤64 karakter). [protocols/responses](https://dev.meta.ai/docs/protocols/responses) | Hayır. | — | **Düşük.** Tek kullanıcılı demo. |
| **Contributor sürümü** | `muse-spark-1.3-contributor`: girdi 0,10 $ / çıktı 0,20 $ (normal 1,25 / 4,25), ama içerik Meta eğitiminde kullanılır; 150 RPM; `max` effort yok. [pricing](https://dev.meta.ai/docs/pricing-rate-limits) | Hayır. | — | **Düşük-orta.** Veri sentetik; 150 $ kredi biterse toplu ölçümler için 10 kat ucuz yol. Gerçek müşteri verisiyle kullanılmaz. |
| **Muse Spark Open (açık ağırlık)** | 816B MoE, 42B aktif, Muse Model License. Barındıran sağlayıcılar OpenAI uyumlu: Together, Fireworks, Baseten, Groq (`meta-models/muse-spark-open`), Nebius. Groq: araç çağırma + yapılandırılmış çıktı + görsel; Fireworks: görsel + araç; Baseten: görsel/video/ses. Groq kurumsal onay istiyor. [muse-spark-open](https://dev.meta.ai/docs/muse-spark-open), [deploy](https://dev.meta.ai/docs/muse-spark-open/deploy) | Hayır. | — | **Yüksek.** Açık ağırlık bonusu (10k). İrsaliyeyi ikinci, bağımsız okuyucu olarak okur; iki okuma ayrışırsa kapı insana sorar. `meta.py`'ye ikinci istemci + `read_note` parametresi yeterli. Not: KURALLAR Baseten kredisi için `meta-models/muse-spark-open-1026` diyor, belge `-1026`'sız; ikisini de dene. |
| **Muse Glimmer (açık ağırlık)** | 30B, Apache 2.0, metin+görsel, 128K. vLLM/SGLang/llama.cpp/Ollama/LM Studio ile yerel. Donanım şartı yazmıyor (UNVERIFIED Mac'te sığar mı). [muse-glimmer](https://dev.meta.ai/docs/muse-glimmer) | Hayır, ama README:15 "Glimmer ikinci okumayı yapar" diyor. | **Hayır: README kodda olmayan bir şey söylüyor.** | Spark Open ile aynı bonus. Yerel çalışırsa "veri depodan çıkmaz" anlatısı güçlü. Sığmazsa README'yi düzelt. |
| **Muse Code** | Terminal/CI kod ajanı, `muse exec "<istem>"` headless. [muse-code](https://dev.meta.ai/docs/muse-code) | Evet. `cbyp/erpnext.py` Muse Code'la yazıldı, görev `docs/muse-code/erpnext-client.md`, JOURNAL:173-187. | Evet. Görev metni repoda, sonuç ölçülü (13/13 test). | **Düşük-orta.** Bir GitHub Action'da `muse exec` ile kapı testlerini gözden geçirtmek ikinci bir kanıt olur; zorunlu değil. |
| **Ses (Spark 1.3)** | 1.3'te ses "tam desteklenmiyor", kalite düşebilir; Spark 1.2 veya Muse Voice Transcribe öneriliyor. [models](https://dev.meta.ai/docs/models) | Hayır. README:15 "Voice dinler" diyor, kodda yok. | README yine fazla söylüyor. | Spark ile yapma; ses gerekiyorsa Voice Transcribe. Yoksa README'den çıkar. |

## En değerli 3 ekleme (jüri etkisi / emek)

1. **Ajanı sağlamlaştır, reasoning özetini aç, kapılı/kapısız koştur.** (Emek: yarım gün.)
   `reasoning={"effort":"medium","summary":"auto"}` + `resp.output` içindeki `reasoning` öğelerinin `summary` metnini trace'e yaz. Aşağıdaki 1–5 numaralı düzeltmeleri yap. Sonra 6 vakada `run_agent.py` ve `--no-gate` ile koştur.
   Neden: ajan henüz hiç çalışmadı. Meta araç puanında "basit entegrasyonun ötesi" tam olarak bu: Spark kendi araçlarını seçiyor, kapı onu durduruyor, ekranda Spark'ın kendi gerekçesi görünüyor. Best Agentic bonusunun ana kanıtı.
2. **Muse Spark Open'ı ikinci irsaliye okuyucusu yap.** (Emek: 2–4 saat + sağlayıcı hesabı.)
   Aynı şema ve istem, OpenAI uyumlu sağlayıcı (Baseten krediyle; olmazsa Fireworks/Together). Kapıya bir kural: iki okuma farklıysa → insan. 8+6 irsaliyede uyuşma oranını ölç.
   Neden: açık ağırlık bonusu (10k) ve README'deki "ikinci okuyucu" iddiası gerçek olur. Not: Groq dışındaki sağlayıcılarda yapılandırılmış çıktı belgede yazmıyor (UNVERIFIED); ilk çağrıda dene.
3. **`look` şemasına nokta ekle (önce işaretle, sonra say).** (Emek: 1–2 saat.)
   `points: [{x, y}]` (0–1000, sıkıştır) + `cartons_visible = len(points)`. Kapıda SAM kutusu ↔ Spark noktası eşleşmesi: eşleşmeyen nokta/kutu varsa → insan.
   Neden: belgenin kendi önerisi. Toplam sayının tesadüfen tutmasını yakalar (dağınık depoda 56 vs 59 ama 37 eşleşme). "İki Meta modeli birbirini nesne nesne denetliyor" görseli videoda güçlü.

Değerlendirilip elenenler: web arama, tool search, computer use (ürüne katkısı yok, eklemek gösteriş olur).

## Yanlış / riskli kullanım (somut düzeltmeler)

1. **Çift kayıt mümkün.** `cbyp/agent.py:76-95`
   Ajan `post_goods_receipt`'i iki kez çağırırsa (paralel çağrı varsayılan açık, ya da tekrar) kapı ikisini de onaylar, ERP'ye iki fiş gider.
   Düzeltme: başta `if self.posted: return {"posted": False, "gate": "already posted"}`. Bir test ekle.
2. **Argümanlar doğrulanmıyor.** `cbyp/agent.py:101-104, 119`
   `json.loads` bozuk JSON'da, `**args` fazla/eksik anahtarda (TypeError) döngüyü düşürür. `quantity` int değilse (ör. `"12"`, `true`) sessizce reddedilir ya da kapısız modda olduğu gibi yazılır. Belge: "argümanları kendi kodunda doğrula", `strict` garanti değil.
   Düzeltme: `call()` içinde try/except; `isinstance(q, int) and not isinstance(q, bool) and q > 0`; hatayı `{"error": ...}` olarak modele geri ver.
3. **Araç hatası ajanı öldürüyor.** `cbyp/agent.py:63-74`
   `read_note` `finish_reason != "stop"` olunca `RuntimeError` atıyor (`delivery_note.py:83-84`); API hataları da yukarı çıkıyor. Ajan "insana sor" diyemeden süreç çöküyor.
   Düzeltme: araç içinde yakala, `{"error": "...", "hint": "ask_supervisor"}` döndür.
4. **Ajan çağrılarında çıktı bütçesi ve durum kontrolü yok.** `cbyp/agent.py:110-112, 124-126, 113-116`
   `max_output_tokens` verilmiyor (varsayılan belgede yok). `resp.status` kontrol edilmiyor; `incomplete` gelirse `output_text` boş döner ve bu "son cevap" sanılır.
   Düzeltme: `max_output_tokens=16000`; `if resp.status != "completed":` → kayıt yok, insana devret.
5. **"Karar vermeden bitti" ele alınmıyor.** `cbyp/agent.py:115-116`, `experiments/run_agent.py:41-49`
   `tool_choice` sadece `auto`; model ne `post` ne `ask_supervisor` çağırmadan metinle bitebilir.
   Düzeltme: `posted` ve `escalated` boşsa otomatik `ask_supervisor("agent ended without a decision")`; sonuç tablosunda ayrı say.
6. **`look` kesik cevabı kontrol etmiyor; MIME sabit.** `cbyp/perception.py:34, 43`
   `finish_reason` bakılmıyor (`delivery_note.py:83` bakıyor). Kesik JSON `json.loads`'ta patlar. `image/png` sabit; gerçek JPG fotoğrafta yanlış.
   Düzeltme: `delivery_note._data_url` kullan, `finish_reason` kontrolünü ekle.
7. **Zaman aşımı ve tekrar ayarı yok.** `cbyp/meta.py:28`
   SAM akışı bir kez 11 dk asıldı (JOURNAL:167). Kodda timeout yok. Canlı demo 4–9 Kas arası ayakta kalmalı.
   Düzeltme: `OpenAI(..., timeout=60, max_retries=3)`; SAM akışına ayrıca süre sınırı. Belgeye göre 504'ü aynen tekrarlama.
8. **README kodda olmayanı söylüyor.** `README.md:15`
   "Glimmer ikinci okumayı yapar, Voice dinler" yazıyor; kodda ikisi de yok. Jüri bunu kontrol ederse güven kaybı.
   Düzeltme: ya ekle (Ekleme 2) ya da "planned" diye işaretle.
9. **Küçük: eski parametre adı.** `cbyp/delivery_note.py:66`, `cbyp/perception.py:36`
   `max_tokens` eski takma ad; belge `max_completion_tokens` diyor. Çalışıyor, acil değil.

Doğru yapılanlar (dokunma): Responses + `previous_response_id` ve her turda `instructions/tools/reasoning` yeniden gönderme; strict şemalar; görsel `user` rolünde; effort seçimi ölçümle yapıldı; kapı model çıktısına değil araçların topladığı kanıta bakıyor (`agent.py:85`); Muse Code görevi ve sonucu repoda.
