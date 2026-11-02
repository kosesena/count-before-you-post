# Gerçek veri, saha ölçümü ve API maliyeti

Durum: 2 Kasım 2026. Kullanıcının tercihiyle üçüncü taraf pilotuna bağlı kalmadan, açık gerçek fotoğraflarla kontrollü testler yürütülüyor. Sonuçlar: [kontrollü doğrulama raporu](CONTROLLED_VALIDATION.md). Gerçek teslimat ölçümü ve tam fatura mutabakatı henüz yok. Aşağıdaki işletmeler yalnızca gelecekteki adaylardır; kimseye mesaj gönderilmedi.

## İnternetten bulunan kaynaklar

| Kaynak | Doğrulanan kanal | Kullanım |
| --- | --- | --- |
| OPLOG | partnerships@oplog.io — https://www.oplog.io/tr/iletisim | Fulfillment işletmesi; partnerlik kanalından anonim teslimat örneği / uzaktan pilot talebi. Uygunluk bir öneridir, kabul garantisi yoktur. |
| Bonolog | info@bonolog.com.tr — https://bonolog.com.tr/tr/iletisim | Fulfillment deposu olan işletme; mal kabul ekibine yönlendirme talebi. |
| SCD araştırmacıları | https://github.com/yancie-yjr/scd.github.io | Gerçek depo ve internet koli görüntüleri, instance etiketleri. Görsel bileşen değerlendirmesi için aday. Veri lisansı CC BY-NC-SA 4.0; repo kod lisansı ile karıştırılmamalı. |
| Amazon Bin Image Dataset | https://registry.opendata.aws/amazon-bin-imagery/ | Gerçek fulfillment kutu içi ürün görüntüleri ve metadata. Koli teslimatından farklı görev; ana teslimat doğrulama seti olarak kullanılmayacak. CC BY-NC-SA 3.0 US. |

SCD görüntülerine uydurma irsaliye/ses eklemek gerçek uçtan uca saha verisi üretmez. Görsel testte yalnızca görünür etiketli nesneler değerlendirilebilir; gizli koli adedi çıkarılamaz. Aynı yükün farklı açılarını bağımsız teslimat saymayın. Yayımlanmış verinin model eğitiminde görülmediği garanti edilemez. SCD doğrulama kümesinden önceden belirlenmiş 30 görüntü indirildi ve değerlendirildi. Ham fotoğraflar Git ve site dışında tutuluyor; ticari demo içinde yeniden yayımlama izni varsayılmıyor.

## Gönderime hazır pilot talebi (henüz gönderilmedi)

Konu: Mal kabul kontrolü için 20–30 anonim örnekle uzaktan araştırma pilotu

Merhaba,

Count Before You Post, koli fotoğrafı, irsaliye ve teslim alan kişinin sayımını karşılaştırarak stok kaydı öncesinde uyuşmazlıkları insan incelemesine yönlendiren bir prototip. Gerçek operasyonlarda doğruluğunu ve zaman etkisini henüz ölçmedik.

Mal kabul ekibinizle önce kısa bir uygunluk görüşmesi, uygunsa 20–30 bağımsız tek ürünlü teslimat üzerinde uzaktan değerlendirme yapmak istiyoruz. Aynı teslimata ait anonim irsaliye, yük fotoğrafı, bağımsız doğrulanmış koli adedi/ürün bilgisi ve mümkünse izinli alıcı ses kaydı gerekiyor. Gerçek ERP sisteminize yazma veya bağlantı istemiyoruz. Ses/veri toplanması ve harici model servislerinde işlenmesi kapsamı önceden birlikte belirlenecek.

Manuel kontrol süresi, yanlış kabul ve insan incelemesi ihtiyacını ölçeceğiz; sonuçları başarılı/başarısız tüm örneklerle paylaşacağız. Başlangıçta veri paylaşmadan kısa bir görüşme mümkün mü? İlgili operasyon veya inovasyon ekibine yönlendirebilir misiniz?

Teşekkürler,
Sena

## Ölçüm protokolü

1. 20–30 bağımsız yük; en az yarısı temiz, kalanlarda eksik/yanlış ürün, hasar ve görünürlük sorunu. Geliştirmede kullanılan yükleri hariç tutun. Doğal hata oranını bu zenginleştirilmiş örneklemden tahmin etmeyin.
2. İnsan gerçekliği model çalışmadan önce yazılır: fiziksel adet, ürün, hasar, beklenen karar. Aynı yükün görüntüleri tek load_id altında kalır. Manifest ve dosyalar mevcut run_heldout --freeze ile mühürlenir.
3. Manuel ve destekli kontrol için aynı kapsamı kullanın: sayım + belge karşılaştırma + kayıt hazırlama. Yükleme/taşıma süresini karıştırmayın. İki ayrı değerlendirici kullanın; model sonucuna ve birbirinin sonucuna kör olsunlar. Görev sırasını dönüşümlü dağıtın; değerlendirici/sıra etkisini raporlayın.
4. evaluation/field-observation.example.json dosyasını her yük için doldurun. Aktif çalışma, kesinti ve toplam geçen süre ayrı; model süresi insan çalışma süresi değildir. Destekli aktif süreye fotoğraf/ses hazırlama, inceleme, düzeltme ve veri girişi dahildir.
5. Eşleşmiş yükler için manuel aktif süre eksi destekli aktif süre farkını raporlayın; negatif farkı saklamayın. Eksik ölçümü sıfır saymayın. İnceleme oranı = insan incelemesi gereken / tüm denemeler; teknik başarısızlıkları ayrıca gösterin. Manuel ve destekli yanlış kabulü aynı bağımsız gerçekle karşılaştırın.
6. Küçük pilotta sıfır hata üretim güvenliği kanıtı değildir. Sonuç seçmeyin; bütün denemeleri, başarısız çağrıları ve tekrarları koruyun. ERPNext belge zaman damgalarını aktif iş süresi yerine koymayın.

## Fatura teslim listesi

Meta ve Baseten için aynı başlangıç/bitiş tarihi ve saat diliminde usage/billing dışa aktarımı veya ekran görüntüsü gerekiyor:

- Proje/workspace ve model/endpoint bazında çağrı sayıları, varsa request ID ve zaman damgası.
- Girdi/çıktı tokenları; görüntü, ses, GPU/saniye gibi ayrıca ücretlenen birimler.
- İndirim/kredi öncesi kullanım bedeli, uygulanan indirim/ücretsiz kredi, net kullanım bedeli, para birimi. Vergi ve abonelik/altyapı bedelleri ayrı.
- Başlangıç/bitiş kredi bakiyesi yalnızca kontrol içindir; tek başına çağrı maliyeti değildir.
- Başarısız çağrı ve tekrarlar dahil; aynı hesaptaki diğer projeler hariç. Görsel/ses/ikinci okuyucu/ajan tüm aşamalar hesaba katılmalı.

API anahtarı, kart bilgisi veya giriş şifresi gerekmiyor. İhracatları ignored evaluation/private/ altında tutun; faturayı site/ içine veya Git'e koymayın.

Önce sağlayıcı toplamlarını kendi satırlarıyla uzlaştırın, ardından request ID ile koşuya eşleyin. Eşlenmeyen bedeli saklayın; tahmini dağılımı ölçülmüş koşu maliyeti diye göstermeyin. Krediyle net ödeme sıfır olabilir; brüt tüketim ayrıca raporlanır. Tüm sağlayıcılar ve çağrılar kapsanmadan toplam maliyet bilinmiyor olarak kalır. evaluation/billing.example.json muhasebe şablonudur, fiyat tahmini içermez.

## Sonraki bağımlılıklar

- İşletmeyle iletişim için açık gönderim talimatı ve veri paylaşmayı kabul eden muhatap gerekir. Bu belge tek başına pilot başlatmaz.
- Fatura dışa aktarımları gelince maliyet hesaplanabilir.
- Gerçek teslimatlar gelince mühürleme ve API değerlendirmesi yapılabilir; şu anda saha başarısı iddiası yoktur.

## 2 Kasım maliyet incelemesi

Meta 27 Ekim–2 Kasım kullanım CSV’si alındı; gösterilen net harcama 0 TRY. Bu, ücretsiz kredi öncesi tüketimin veya bu projeye ait tüm çağrıların maliyetinin sıfır olduğunu kanıtlamaz. Özel dökümler `evaluation/private/` altında tutulur.

Baseten için ayrı kullanıcı hesabı yok: 28 Ekim hackathon e-postası 100 USD başlangıç kredisi, API anahtarı ve Muse Spark Open erişimi sağlıyor. E-posta kalan bakiyeyi göstermiyor. Mevcut anahtarla resmi salt okunur `GET /v1/billing/model_apis` isteği 403 döndürdü; çıkarım erişimi fatura erişimi anlamına gelmiyor. Hesap açılması veya tek kullanımlık anahtar bağlantısının yeniden açılması gerekmiyor. Tam API maliyeti doğrulanamadı; tahmin gerçek fatura diye sunulmayacak.
