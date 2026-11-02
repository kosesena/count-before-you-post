# Gerçek fotoğraflarla kontrollü doğrulama — 2 Kasım 2026

Bu çalışma gerçek teslimat pilotu değildir. Başka bir işletmeye bağlı kalmadan gerçek fotoğraflarda görsel bileşenleri, ardından yazılmış irsaliye/sipariş ve sentetik alıcı sesiyle entegrasyonu dener. Gerçek ERP kaydı oluşturulmadı.

## 30 görüntülük görsel değerlendirme

Kaynak: [SCD araştırmacılarının deposu](https://github.com/yancie-yjr/scd.github.io), LSCD validation görüntüleri ve instance etiketleri. Veri lisansı CC BY-NC-SA 4.0. Ham fotoğraflar dağıtılmıyor; yerel ignored dizinde tutuluyor.

Seçim, sonuçlara bakılmadan `SHA256("cbyp-2026-11-02:" + image_id)` sırasındaki ilk 30 validation görüntüsü olarak sabitlendi. Kimlikler, SHA256 özetleri ve referans adetler [manifestte](../evaluation/real-images-selection.json). Geliştirme tabanı: `71f6c22`.

| Ölçüm | SAM | Spark |
| --- | ---: | ---: |
| Tamamlanan görüntü | 30/30 | 30/30 |
| Etiketli adetle tam eşleşme | 12/30 (%40) | 17/30 (%56,7) |
| Ortalama mutlak adet hatası | 1,20 | 1,77 |
| Teknik çağrı hatası | 0 | 0 |

Modeller: `sam-3.1` ve `muse-spark-1.3`; sesli entegrasyonda `muse-voice-transcribe-1.0`. SAM sayımı mevcut 0,70 güven eşiğini kullanır. Spark'ın adet çıktısı doğrudan karşılaştırılır. Tam sonuçlar ve bütün hatalı sayımlar [sonuç dosyasında](../evaluation/real-images-2026-11-02.json). Tek görüntü için sıralı SAM + Spark işlem süresinin medyanı 30,611 saniye; üç görüntü eşzamanlı çalıştırıldı. Bu sayı insan çalışma süresi veya zaman tasarrufu değildir.

Referans yalnızca görünür etiketli kutu sayısıdır; fiziksel toplamı, kapalı kutuların içeriğini veya bağımsız teslimat sayısını göstermez. Modelin eğitimde bu açık veriyi görmediği garanti edilemez. Görüntüler küçük ve zor bir örneklem oluşturur; gerçek depolardaki doğal hata oranına genellenemez. Bu sonuçlar otomatik stok kabulünün görsel toplam eşitliğine dayanamayacağını gösteriyor.

## 24 kontrollü entegrasyon senaryosu

Aynı seçimin ilk 24 görüntüsünde altı türden dörder senaryo: temel durum, eksik adet, yanlış ürün, belgeye eklenmiş talimat, birim uyuşmazlığı ve belirsiz alıcı ifadesi. Sipariş/irsaliye üretilmiştir; ses macOS Samantha ile sentezlenmiştir. Ürün isimleri Spark ön okumasından alındığı için bağımsız ürün doğruluğu iddiası yoktur. Bu bir geliştirme testi; kör veya bağımsız saha testi değildir.

20 kusurlu durumda beklenen güvenlik koşulu otomatik kayıt yapmamaktır. Dört temel durumda bağımsız doğru karar etiketi yoktur. Bir erken kontrol başka bir kusuru örtebilir: örneğin görünürlük nedeniyle insan incelemesine yönlendirme, eklenmiş talimatın ayrıca yakalandığını kanıtlamaz. Teknik hata başarılı engelleme sayılmaz.

İlk koşu büyük fotoğraflarda SAM maskelerinin kendi piksel boyutuyla kaynak fotoğraftaki sınırlarının farklı olabileceğini ortaya çıkardı. Kod bunları aynı varsayıp indis hatasına düşüyordu. Düzeltme maskeyi kaynak sınırlarına nearest-neighbour ile eşler; geçersiz boyut ve henüz desteklenmeyen kesirli sınırlar işlemi durdurur. Düşük çözünürlüklü maskenin kaybolmuş detayını geri getirmez. İlk koşu korunur, düzeltme sonrası tekrar ayrı kaydedilir. İlk ve tekrar koşularında telefon fotoğraflarının EXIF dönüşü nedeniyle kaynak boyutlarının ters kullanıldığı da görüldü. İki girdide gerçek dönüş metadata’sı vardı. Spark noktalarının piksele çevrilmesi ve SAM nokta istemi artık görüntülenen yönün boyutlarını kullanıyor; bu iki girdi ayrı regresyon tekrarında teknik hatasız tamamlandı. Birinde ürün uyuşmazlığı, diğerinde sayım uyuşmazlığı kararı çıktı.

## Tekrar üretme

Repo ortamı ve mevcut sağlayıcı erişimleriyle, repo kökünde:

```sh
.venv/bin/python evaluation/download_scd_sample.py
.venv/bin/python -m evaluation.run_real_images evaluation/inputs/scd/sample.json evaluation/private/scd-run-2026-11-02
.venv/bin/python evaluation/prepare_controlled.py
.venv/bin/python -m evaluation.run_controlled evaluation/inputs/hybrid-2026-11-02/manifest.json evaluation/private/hybrid-fixed-2026-11-02
.venv/bin/python -m unittest discover -s tests
```

Hazırlayıcı macOS `say`, `afconvert` ve Arial Unicode fontu kullanır. İndirici sabit kaynak arşiv boyutuna bağlıdır; kaynak değişirse yeniden incelenmelidir. Mevcut çıktı dizinlerini ezmezler. Yeni tekrar için koşucuya yeni bir çıktı dizini verin. API çalıştırmaları kredi tüketir. Dosya özetleri çağrılardan önce doğrulanır. Ham veri, sesler ve sağlayıcı dökümleri Git dışında kalır.

## Maliyet ve saha faydası

Meta'nın 27 Ekim–2 Kasım dışa aktarımında 6.542 istek ve net 0 TRY görünüyor; ücretsiz kredi aktif. Bu, kredi öncesi bedelin sıfır olduğunu veya tüm hesap çağrılarının bu projeye ait olduğunu kanıtlamaz. Döküm yeni koşulardan önce alınmıştır; bu koşuların nihai faturası değildir.

Baseten'in 28 Ekim hackathon e-postası 100 USD başlangıç kredisi ve Muse Spark Open erişimini doğrular; kalan bakiye değildir. Ayrı kullanıcı hesabı bulunmuyor. Mevcut hackathon anahtarıyla resmi [Model APIs maliyet endpoint'i](https://docs.baseten.co/reference/management-api/billing/gets-model-apis-costs) 403 döndürdü. Anahtar veya tek kullanımlık bağlantı rapora alınmadı. Çıkarım yetkisi fatura okuma yetkisi sağlamıyor.

**Toplam gerçek API maliyeti bilinmiyor.** Sağlayıcı brüt/net tüketim ve koşu eşleştirmesi olmadan tahmin gerçek fatura diye sunulmaz. **Ölçülmüş insan zamanı tasarrufu da yok.** Gerçek operasyon gözlemi olmadan ERPNext kayıt saatleri veya model çalışma süresi bunun yerine kullanılamaz. Bu iki açık kalem testlerin tamamlanmasıyla otomatik olarak kapanmaz.

## Korunan denemeler

| Deneme | Girdi | Teknik hata | Tamamlanan kusurlu durumlarda otomatik kaydı reddetme |
| --- | ---: | ---: | ---: |
| [İlk koşu](../evaluation/controlled-initial-2026-11-02.json) | 24 | 20 (18 maske, 2 dönüş) | 4/20 |
| [Maske düzeltmesi sonrası](../evaluation/controlled-mask-fixed-2026-11-02.json) | 24 | 9 (1 dönüş, 8 bağlantı) | 13/20 |
| [Dönüş regresyonu](../evaluation/controlled-exif-fixed-2026-11-02.json) | 2 | 0 | 1/1 |
| [Bağlantı tekrarı](../evaluation/controlled-connection-retry-2026-11-02.json) | 7 | 1 (ses zaman aşımı) | 6/6 |

İki dönüş girdisi sonuç seçilerek değil EXIF metadata’sıyla seçildi. Bağlantı tekrarları ayrı raporlanır. Bu denemelerde hatalı otomatik kayıt gözlenmemesi, teknik başarısızlıkların veya gereksiz insan yönlendirmelerinin başarı olduğu anlamına gelmez. Tekrarlar model çıktıları değişebileceğinden birebir aynı karar garantisi vermez.

Bu kontrollü kümede erken kontroller bütün tamamlanan girdileri durdurdu; ikinci okuyucu/audit aşamasına ulaşılmadı. Dolayısıyla Baseten üzerinden ikinci görüşün başarılı kabul yolunu bu deneyin test ettiği iddia edilmez. Mevcut nokta istemi çağrı başına en fazla 16 nesne kullanır; daha kalabalık görüntülerde tam nesne eşleşmesi bu uygulamada sınırlıdır.

## Son durum

[Sonuçların tanısal birleşimi](../evaluation/controlled-latest-2026-11-02.json): 24 farklı senaryodan 23 karar, 1 ses servisinde zaman aşımı. Otomatik kayıt yapılmaması gereken 20 durumun 20’si tamamlandı ve kayıt yapmadı. Bu, birden fazla düzeltme/tekrarın birleşimidir; tek seferlik 24/24 başarı veya bağımsız doğruluk sonucu değildir. Baseline hybrid-19 zaman aşımı açık kalır. Hiçbir gerçek ERP kaydı yazılmadı.

Yerel doğrulama: 119 Python testi geçti; kaynak boyutundan farklı raster ve EXIF yönlü koordinatlar için regresyon testleri eklendi. Sağlayıcı gecikmesi/erişimi ve gereksiz insan incelemesi ihtiyacı üretim öncesi açık konulardır.
