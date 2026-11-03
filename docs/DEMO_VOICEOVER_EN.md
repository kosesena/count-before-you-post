# Count Before You Post — 3:00 video planı

3 Kasım 2026. Önceki taslağın yerine geçer. İlk anlatıcı 0:25'te; gerçek
kanıt 0:33'te başlar. Çocuk sadece Glimmer yakın çekiminde “Wow!” der.
Zamanlar kurgu hedefidir; seslendirme henüz kaydedilmedi veya ölçülmedi.

## Açılış: 0:00–0:33

| Süre | Görüntü | Ses |
| --- | --- | --- |
| 0:00–0:03 | Mavi kutu çocuğun ellerinde, proje adı okunur. | Oda sesi, hafif müzik. |
| 0:03–0:07 | Çocuk kutuyu açar; oyuncaklar görünür. | Ambalaj hışırtısı, konuşma yok. |
| 0:07–0:10 | Glimmer yakın çekimi. | Çocuk, yaklaşık 0:08'de: **“Wow!”** |
| 0:10–0:13 | Açık kutudan geceye geçiş. | Müzik, konuşma yok. |
| 0:13–0:17 | Glimmer ışıldar; karakterler canlanır. | Hafif hareket sesleri. |
| 0:17–0:21 | Karakterler depoyu kurar. | Parça yerleştirme sesleri. |
| 0:21–0:25 | Kamyon mal kabul alanına gelir. | Kamyon sesi; müzik alçalır. |
| 0:25–0:29 | İrsaliye yakın çekimi. | Anlatıcının ilk cümlesi. |
| 0:29–0:33 | Koliler ve karar kapısı. | Anlatıcının ikinci cümlesi. |

**Voiceover · 0:25–0:33**

At this little warehouse, paperwork is only a claim. Before an AI agent updates stock, the evidence must agree.

## Gerçek fotoğraf: 0:33–0:54

| Süre | Görüntü |
| --- | --- |
| 0:33–0:40 | Oyuncak koliden gerçek Deli fotoğrafına kesme. Tam orijinal fotoğrafı göster. |
| 0:40–0:46 | Operatörün seçtiği alan; tam fotoğrafla farkı belli olsun. |
| 0:46–0:54 | `/jury/`: test belgesi ve seçilmiş alan yan yana. |

**Voiceover · 0:33–0:40**

Here is a real photograph, tested through our verification workflow. These are recorded results.

**Voiceover · 0:40–0:54**

An operator selected this counting area and confirmed it contains the delivery. Outside goods were not checked. The documents are test inputs, the receiver voice is synthetic, and no ERP records were written.

Ekran etiketi: **Controlled real-photo test · Recorded replay · No ERP write**.

## Doğru belge: 0:54–1:17

| Süre | Görüntü |
| --- | --- |
| 0:54–1:00 | “01 · Correct note”: **1 carton · No.770**. |
| 1:00–1:07 | Kamera ve belge yan yana. |
| 1:07–1:14 | **APPROVE · dry run**, ikinci okuyucu ve audit tamamlandı satırı. |
| 1:14–1:17 | Yeşil kararı tut; kısa durak. |

**Voiceover · 0:54–1:17**

The correct note claims one carton. Muse Spark reads the document and the camera image. SAM checks the carton. The order, product identity and receiver count agree. Spark Open rereads the note, and Wonder audits it. All required checks pass. One carton is approved in a dry run.

## Yanlış miktar: 1:17–1:34

| Süre | Görüntü |
| --- | --- |
| 1:17–1:21 | “02 · Wrong quantity”: belgede **2 cartons**. |
| 1:21–1:27 | Aynı kamera görüntüsünde **1 carton**. |
| 1:27–1:34 | **BLOCK · no receipt**. |

**Voiceover · 1:17–1:34**

Same photograph, different claim. This note and its test order say two cartons. The camera evidence still shows one. The receipt is blocked. Agreement between documents cannot override a conflicting physical count.

## Yanlış ürün: 1:34–1:49

| Süre | Görüntü |
| --- | --- |
| 1:34–1:40 | “03 · Wrong article code”: belgede **No.999**, kamerada **No.770**. |
| 1:40–1:49 | Kırmızı karar ve ürün kimliği uyuşmazlığı açıklaması. |

**Voiceover · 1:34–1:49**

Now the quantity matches, but the document and order specify a different article code. The camera reads the original code. The gate blocks this receipt too. A matching count is not enough.

## İnsan incelemesi: 1:49–2:06

| Süre | Görüntü |
| --- | --- |
| 1:49–1:55 | Tarihsel bölüm, İngilizce kayıt: “03 · Ask a person”. |
| 1:55–2:00 | “Object match” görünümü ve uyuşmayan nesneler. |
| 2:00–2:06 | **ASK A PERSON · no automatic receipt**. |

**Voiceover · 1:49–2:06**

What if the evidence is uncertain? In this separate synthetic example, the models disagree about the cartons. The system asks a person. This historical recording uses the earlier core checks, rather than the full workflow.

Ekran etiketi: **Separate historical recording · Synthetic scene · Core checks**.

## Teknik fark: 2:06–2:26

| Süre | Görüntü |
| --- | --- |
| 2:06–2:13 | Editörde `cbyp/gate.py` karar kuralları. |
| 2:13–2:19 | `cbyp/agent.py`: `post_goods_receipt` kontrolü. |
| 2:19–2:26 | Jüri sayfası, tarihsel “02 · Block”; araç izinde reddedilen yazma sonucu. |

**Voiceover · 2:06–2:26**

Models provide observations. Plain code controls the write. The verification gate sits inside the agent's receipt-writing tool, so asking to post is not authorization. Separate historical experiments also created actual ERPNext receipts. The real-photo tests you just saw were dry runs.

## Kanıt ve sınırlar: 2:26–2:43

| Süre | Görüntü |
| --- | --- |
| 2:26–2:34 | `/review/#validation`: “30 real photos” ve “24 controlled scenarios” kartları. |
| 2:34–2:43 | Seçilmiş alanın kapsam notu ve önceki başarısızlıklara bağlantı. |

**Voiceover · 2:26–2:43**

We publish failures alongside successful checks. This comparison uses one previously inspected photograph, not three independent deliveries. Real-photo counting remains challenging. Accuracy on new warehouses and worker time savings still need to be measured.

## Kapanış: 2:43–3:00

| Süre | Görüntü |
| --- | --- |
| 2:43–2:50 | `/jury/`: tekrar doğru belgenin yeşil kabul kararı. |
| 2:50–2:55 | Sabah görseli; karakterler yeniden oyuncak halinde. |
| 2:55–2:57 | Proje adı; seslendirmede “Count Before You Post.” |
| 2:57–3:00 | İsim, doğrulanmış proje bağlantısı, krediler. Sabit kare; müzik söner. |

**Voiceover · 2:43–2:57**

My SAP internship showed me why stock records matter. This is my approach to AI receiving: require evidence, stop on contradictions, and ask a person when uncertain. Count Before You Post.

## Kurgu ve kayıt notları

- İlk 25 saniyede anlatıcı yok. Tek çocuk repliği Glimmer yakın çekimindeki “Wow!”.
- Mevcut hikâye referansları: `assets/readme/toybox.jpg`, `toybox-open.jpg`,
  `night.jpg`, `morning-wink.jpg`. Kutu açma, canlanma ve kamyon hareketleri çekim/
  animasyon hedefleridir; hazır video veya ses üretildiği iddia edilmez.
- Görseller arasında geçişleri ve ekran tıklamalarını seslendirme aralıklarına
  yerleştir. Konuşmayı yaklaşık 130–145 kelime/dakika hızında prova et. Sığmayan
  kısmı hızlandırmak yerine kısalt; son üç saniyeyi sessiz kapanışa bırak.
- Konuşma sırasında müziği alçalt. Karar kutularını altyazıyla kapatma.
- Gerçek fotoğrafın 91.8 / 58.7 / 56.3 saniyelik süreleri geçmiş koşulara aittir.
  Kurgu geçişleri canlı model hızı değildir. Yeni API çağrısı veya ERP yazımı gerekmez.
- Fotoğraf kredisi: “Photo: Jinrong Yang et al. · SCD / LSCD · CC BY-NC-SA 4.0 · Cropped”.
- Mevcut kutu/gece/sabah görselleri: “Box and story artwork: ChatGPT (OpenAI),
  based on the Muse Image cast.” Yeni animasyon üretilirse kullanılan aracı ekle.
- Yerel sayfa: http://127.0.0.1:8771/jury/. Sunucu gerekirse repo kökünden
  `python3 -m http.server 8771 --bind 127.0.0.1 --directory site`.
- Kapanışta canlı proje bağlantısı kullan ve yayımdan sonra doğrula. Yerel adresi
  yarışma bağlantısı diye kullanma. Ortam dosyaları ve kişisel sekmeler görünmesin.
