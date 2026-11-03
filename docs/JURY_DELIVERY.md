# Jüri demosu ve yeni girdi çekim planı

3 Kasım 2026. Bu belge sunum hazırlığıdır; yeni deney sonucu içermez.

## Üç dakikalık sunum

Güncel çekim ve İngilizce metin: [DEMO_VOICEOVER_EN.md](DEMO_VOICEOVER_EN.md).
Açılış tercihi README'deki LEGO kutusudur: çocuk kutuyu sessizce açar → Glimmer
yakın çekiminde çocuk yalnızca “Wow!” der → gece depoyu kuran karakterler.
İlk 25 saniyede anlatıcı yoktur; gece depo kurulur ve kamyon gelir. Anlatıcı 0:25'te,
gerçek fotoğraf kanıtı 0:33'te başlar. Aşağıdaki tablo önceki
kanıt odaklı taslaktır; çekimde güncel saniyeli metni kullan.

| Süre | Ekran | Anlatım |
| --- | --- | --- |
| 0:00–0:20 | `/jury/` açılışı | “Bir AI ajanı irsaliyeyi okuyup mal kabul kaydı oluşturabilir. Ama belge yanlışsa stok da yanlış olur. Count Before You Post, yazma iznini fiziksel kanıta bağlar.” |
| 0:20–0:55 | Correct note | “Bu gerçek fotoğrafta operatörün seçtiği alanı kontrol ediyoruz. Test belgesi bir koli diyor. Kamera, belge, sipariş ve alıcı sayısı uyuşuyor; ikinci okuyucu ve denetim de geçiyor. Tam akış kuru koşuda onay veriyor.” |
| 0:55–1:20 | Wrong quantity | “Aynı fotoğrafta belge ve test siparişi iki koli söylüyor. Fiziksel kanıt bir. Kayıt reddediliyor.” |
| 1:20–1:40 | Wrong article code | “Adet doğru olsa bile ürün kodu uyuşmuyorsa kayıt yine reddediliyor.” |
| 1:40–2:05 | Tarihsel Ask a person örneği | “Kamera kesin karar veremediğinde sistem insana yönlendiriyor. Bu bölüm ayrı, sentetik bir tarihsel kayıt; önceki örnekle aynı deney değil.” |
| 2:05–2:35 | Karar izi, ardından kanıt sayfası | “Kararı dil modeli değil, yazma aracındaki kod kuralları uyguluyor. Ajanın isteği tek başına yeterli değil. Ayrı tarihsel ERPNext deneylerimiz var; bu ekrandaki gerçek fotoğraf denemeleri ERP’ye yazmadı.” |
| 2:35–3:00 | Gerçek fotoğrafın kapsam notu | “Bir gerçek fotoğraftaki kontrollü kabul ve ret yolunu gösterdik. Henüz saha başarı oranı veya zaman tasarrufu iddia etmiyoruz. Sonraki ölçüm, önceden görmediğimiz teslimatlarda doğru kabul ve gereksiz insan incelemesi.” |

Prova sırasında süreyi ölç. 91,8 saniyelik kayıt süresini canlı bekleme gibi sunma:
sayfa önceden kaydedilmiş sonuçları gösterir ve model çağrısı yapmaz.
Simülatör gerekirse soru-cevapta açılabilir; üç dakikalık ana anlatımı bölmek zorunda değil.

## Yeni fiziksel örnekler için çekim listesi

Yeni girdi çalışması mevcut Deli fotoğrafından ayrı tutulacak. Bu küçük çalışma saha
pilotu değildir. Sonuçları görmeden girdileri ve beklenen koşulları sabitle.

1. Üzerinde gerçek, okunabilir marka ve ürün kodu bulunan kapalı ürün kutuları seç.
   Hayalî etiketle ürün kimliği başarısı üretme. Her örnekte tek ürün türü kullan.
2. Üç ayrı fiziksel düzen hazırla: örneğin bir, iki ve üç kutu. Aynı kutular yeniden
   kullanılıyorsa ortak ürün/kutu grubunu kaydet; bunları bağımsız teslimatlar sayma.
3. Her düzen için bir geniş fotoğraf ve etiketi okuyabileceğimiz bir yakın fotoğraf çek.
   Etiket yakın fotoğrafı insanın referans kaydı içindir; tek kamera girdisi kullanan
   mevcut akışın ek görüntüyü analiz ettiğini iddia etme.
4. Her düzenin gerçek adedini, marka/kodunu, varyantını ve görünür hasar durumunu
   model çağrısından önce yaz. Kamera alanı seçilecekse baştan seçip tüm ilgili
   kontrollerde aynı alanı kullan; tam fotoğrafı da koru.
5. Gerçek sesinle kısa kayıt yap: “Teslimatı ben saydım. [N] koli var.” Sayıdan
   emin değilsen bunu açıkça söyle. Ses dosyasının özgün kopyasını sakla.
6. Her düzen için doğru belgeyi hazırla. Ardından aynı fotoğraf üzerinde ayrı
   miktar (+1) ve ürün kodu kontrol belgeleri hazırla. Bunlar aynı fiziksel örneğin
   kontrollü varyantlarıdır; yeni teslimat değildir. Belgeleri TEST olarak işaretle.

İlk etapta 3 fiziksel düzen × 3 belge = 9 kontrollü koşu. Güvenilir sipariş, alıcı
sayımı ve fotoğraf sabit kalır; negatif kontrollerde yalnızca irsaliye değişir.
Bu nedenle bir hata kamera aşamasından önce sipariş eşleşmesinde yakalanabilir;
hangi kontrolün durdurduğunu raporla. Her negatif örneğin bütün aşamaları sınadığını söyleme.

## Koşu ve raporlama

- İlk çağrıdan önce tüm girdilerin hash’lerini ve beklenen koşulu kaydet.
- Doğru örnek için hedef kabul; yanlış miktar/kod için hedef otomatik kabul olmaması.
- Her koşuyu ilk denemesiyle raporla: post/block/human, tetiklenen kural, teknik hata,
  model süresi, insan hazırlığı ve müdahalesi ayrı alanlarda tutulsun.
- Teknik hatayı güvenlik başarısı sayma. Gereksiz insan incelemesini de başarıya katma.
- Tekrarları ilk sonucu silmeden ayrı kaydet. Sonuca göre değiştirilen istem veya
  eşik varsa sonraki koşuları geliştirme denemesi olarak ayır.
- Tam iş akışı kuru koşu kullan; gerçek ERP kaydı oluşturma. Yeni sonuçlar olmadan
  mevcut başarı tablolarını veya jüri iddialarını artırma.
- Doğru koşularda kabul sayısını; kusurlu koşularda yanlış kabul sayısını; human,
  block ve teknik hata sayılarını ayrı ver. Küçük, tekrar kullanılan örneklerden
  genel depo doğruluğu ya da zaman tasarrufu çıkarma.

## Teslim öncesi kontrol

- `/jury/`: gerçek fotoğrafın üç kontrolü, tarihsel üç karar ve dört dil açılıyor.
- Kayıt tekrarı, seçilmiş alan, hazırlanmış belgeler, sentetik ses ve sıfır ERP yazımı
  açıkça görünüyor.
- `/review/` ve `/verify/` bağlantıları mevcut. Erişim kodu isteyen canlı doğrulama
  ekranı, kayıtsız jüri ziyaretçisinin zorunlu ilk adımı yapılmıyor.
- Yayımdan sonra canlı `/jury/` yeniden kontrol edilmeli; yerel önizleme yayım değildir.
