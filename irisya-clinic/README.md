# İrisya Clinic · Tek Sayfa Web Sitesi (Göz Rengi Değiştirme)

İstanbul'da göz rengi değiştirme (lazer keratopigmentasyon) yapan İrisya Clinic için tek sayfalık site. Site dili İngilizce; hedef pazarlar Avrupa, Körfez, ABD/Kanada ve Romanya.

Önizleme: `.claude/launch.json` → **irisya-site** (port 5510). Build adımı yoktur; `irisya-clinic/` klasörünü olduğu gibi herhangi bir statik hostinge yükleyebilirsiniz.

```
index.html               → tüm sayfa
assets/css/style.css     → stiller (renkler ve yazı ölçüleri en üstte)
assets/js/main.js        → etkileşimler (en üstte WhatsApp numarası)
assets/img/brand/        → logo dosyaları
assets/img/content/      → sitede kullanılan fotoğraflar ve hero filmi (74 dosya, ~17 MB; ~14 MB'ı video,
                           ziyaretçi bunlardan yalnızca ekranına uyan tek dosyayı indirir)
```

## 2026-11-16 rötuşu: kalan yapay zekâ izleri

Genel tasarım (renkler, sayfa akışı, bölümler) aynı kaldı; görsel ve videolara dokunulmadı. Önceki hâl git geçmişinde (`0fc5d22` commit'inde `backups/2026-11-16_ai-rotus-oncesi/`).

- **Yazı:** başlık üstü etiketler artık Space Mono değil, Figtree 700 / 14 px / geniş harf aralığı. Space Mono yalnızca gerçekte de tek aralıklı olacak yerlerde: kalkış panosu, biniş kartı, film zaman kodu. Gövde metinlerindeki eksi harf aralığı kaldırıldı, başlıklarda hafifletildi; paragraflarda ve başlıklarda tek kelime kalan satırlar önlendi; düz kesme işaretleri tipografik ’ oldu.
- **Renk ve gölge:** arka plandaki bulanık renk lekeleri (Why, paket kartı, bento, hikâye sahnesi) düz zemin oldu; mavi "parıltı" gölgeleri nötr gölgeye çevrildi; ufuk geçişindeki ışık halesi yumuşatıldı; gövde metni grisi lacivert tonlu yapıldı.
- **Butonlar:** hepsi aynı hap (pill) biçiminde. WhatsApp'a gönderen butonlarda sohbet uygulaması "gönder" oku yerine WhatsApp simgesi var. Aynı forma giden butonlar tek etikette toplandı ("Get a free shade plan").
- **Süsleme:** paket kartındaki sahte "gönder" butonu ve eğik uygulama ikonları, footer'daki sahte tasarım programı seçim kutusu (köşe tutamakları, oynayan imleç), sonsuz sallanan çerçeveler, eğik selam baloncukları ve "Your pick" etiketi, buzlu cam efektleri, "+" düğmesinin dönmesi ve "(01)" tarzı parantezli numaralar kaldırıldı.
- **Düzeltilen hatalar:** Dubai örnek gezisi (4 gece) "4-day plan" yazıyordu, artık "5-day plan". "Noor H." hem yorum şeridinde hem heterokromi alıntısında farklı tedavilerle geçiyordu, ikinci alıntı başka bir isimle değişti; iki ayrı "Sophie" da ayrıldı. Telefonda "Before you fly" satırı ikiye bölünüyordu; biniş kartındaki 9.5 px yazılar 10 px oldu. 1024–1199 px arası ekranlarda (küçük dizüstü) menüdeki "How it works" üç satıra bölünüyordu, menü sıkılaştırıldı.

## 2026-11-15 yenilemesi: neler değişti

Site, Pitch tarzı tasarım sistemine göre baştan yazıldı ve "yapay zekâ yapmış" izlenimi veren her şey temizlendi. Önceki sürümün tamamı git geçmişinde (`0fc5d22` commit'inde `backups/2026-11-15_pitch-yenileme-oncesi/`).

**Tasarım dili**
- Yazı: yalnızca **Figtree** 400 / 700 / 800 ve **Space Mono** (2026-11-16 rötuşundan beri yalnızca pano, biniş kartı ve film zaman kodunda). Arada kalan 500/600 ağırlıkları ve her köşeye serpiştirilmiş mono etiketler kaldırıldı.
- Renk: logodan lacivert `#021E44`, iris mavisi `#2E63B8`, gök `#A8C7E3`, açık tonlar `#E4EEF8` / `#F6F9FC`. Tek sıcak vurgu **bal rengi `#F2C46D`** (eski "buz mavisi" vurgu hiçbir şeyi öne çıkarmıyordu; her şey maviydi).
- Fotoğraf kuralı: **insan ve mekân fotoğrafları siyah-beyaz, renk yalnızca gözlerde ve ton örneklerinde.** Yapay zekâ portrelerinin parlak, plastik cilt görüntüsü bu sayede editoryal bir seriye dönüştü.
- **Çizilmiş iris örnekleri:** sekiz ton (IR-01 … IR-08) artık CSS ile çizilen irislerle gösteriliyor (`.iris` sınıfı, `--c` rengi). Menüde, hikâye seçicide, paket kartında, ton listesinde ve tedavi kartlarında kullanılıyor. Yüz avatarlarının yerini aldılar.
- Sayfa akışı Pitch sırasına getirildi: hero → paket → neden İrisya → nasıl işler (deste) → hastalar nereden geliyor → hikâyeler → paket içeriği (bento) → ufuk geçişi → tedaviler → tonlar → SSS → kapanış.

**Kaldırılan yapay zekâ izleri**
- Hero'daki "prompt" kutusu (yazı yazan placeholder, "Examples" karıştırma düğmesi) yerine **cümle şeklinde bir form** ("My eyes are [dark brown] and I'd like [Hazel], flying in from [London].") → WhatsApp.
- **Hero filmi** (16 sn döngü: göz, İstanbul, havalimanı karşılaması, muayene, göz) arka planda duruyor. İlk yenilemede kaldırılmıştı, aynı gün isteğe göre geri eklendi. Üzerinde lacivert bir perde var, beyaz sayfaya geçiş şehir listesinden başlıyor; alt köşede bir bölüm etiketi ("03 — Airport pickup") ve duraklat düğmesi var. 21 Kasım 2026'da istek üzerine hızlı kurgulu, efektli sürüme geçildi (17 kesme, hız rampaları, zoom-blur, whip pan, ışık sızıntısı, flaş, RGB ayrışması, kısa montaj).
- Paket bölümünde kendi kendine yazan "ajan" kutusu ve "Building your package" animasyonu yerine üç **örnek gezi** düğmesi (Londra / Dubai / Bükreş); kartlar, gün planı ve fiyat kartı seçilen geziye göre değişiyor.
- Anlamsız sahte arayüzler (transfer için yükselen grafik, "Pg / Ring" çubuğu, merkezde logolu bağlantı şeması, yıldız ikonu) yerine gerçek bilgi taşıyan kartlar: kornea şeması, kendi fotoğrafınızda ton önizlemesi, havalimanı karşılama panosu, koordinatör yazışması, tedavi pasaportu, dört dilde selam, takip takvimi.
- Metinler: "reimagined", "Welcome to a new era", "nothing falls through the cracks", "We'll handle the rest", "Ready when you are" gibi kalıplar ve uzun tireler kaldırıldı. "40+ countries" ve bayrak sıraları sayfada altı kez tekrarlanıyordu, sadeleştirildi. Ana başlık: **"Choose your eye colour."**
- Yorum kartlarındaki 5 yıldız sıraları ve 9 yapay zekâ yüz avatarı kaldırıldı. Aynı alıntının iki yerde geçmesi ve aynı kişinin iki farklı tedaviyle anılması düzeltildi.
- Kodda Vors Dental'dan kalan sınıf ve yorumlar ("smile", "implant", "X-ray", "riders", `--purple` = mavi gibi yanıltıcı değişken adları) temizlendi; CSS sıfırdan, okunur şekilde yazıldı (2050 → ~1100 satır).
- Sosyal medya görseli (`og-image.jpg`) eski slogan ve parlak göz yerine yeni başlık, logo ve sekiz çizilmiş irisle yeniden üretildi.
- Kullanılmayan 99 dosya (yüz avatarları, ekip fotoğrafları, eski kompozitler vb.) siteden kaldırıldı.

**Düzeltilen hatalar**
- Örnek gezilerde gece/gün tutarsızlığı (4 gece yazıp 4 günlük plan gösteriyordu).
- SSS'de bir cevap açılınca soruların sütunlar arasında kayması; kapalı cevaplardaki bağlantılara klavyeyle odaklanılabilmesi.
- Telefonda tedavi kartının fotoğrafın üstüne binmesi.
- Sayfa yenilenince menü çubuğunun şeffaf kalabilmesi, mobil menü simgesinin kapanış "×" olmaması.

## Yayına almadan önce MUTLAKA değiştirin

| Ne | Nerede |
|---|---|
| WhatsApp numarası | `assets/js/main.js` → en üstteki `WHATSAPP_NUMBER` (ülke kodu ile, sadece rakam) |
| Telefon, e-posta, adres | `index.html` → footer `#contact` + `<head>` JSON-LD |
| Alan adı | `canonical`, `og:image`, JSON-LD içindeki `https://www.irisyaclinic.com/` |
| **Hasta hikâyeleri ve yorumlar** | Hikâyeler, yorum şeridi ve tedavi sekmelerindeki alıntılar **örnek metindir**; isimler, şehirler, uçuşlar ve ton kodları gerçek değildir. Gerçek ve yazılı izinli yorumlarla değiştirin. |
| **Yapay zekâ ile üretilmiş kişi fotoğrafları ve hero filmi** | `story-1…5`, `story-1…5-before/-after` (önce/sonra göz şeritleri), `moment-1…5`, `journey-1…5`, `why`, `quote-1…9`, `tx-1`, `tx-2`, `tx-4`/`tx-4-after`, `clinic`, `riders`, `footer*`, göz yakın çekimleri ve hero filmi (`hero*.mp4/webm`, Kling ile) Higgsfield ile üretildi. Filmdeki doktor, hasta, araç ve otel gerçek değil. Siyah-beyaz işlem onları daha doğal gösteriyor ama **gerçek hasta değiller**; hasta sonucu gibi sunulmamalı. Gerçek fotoğrafları aynı dosya adıyla koymanız yeterli, kod değişmez. |
| **Rakamlar ve iddialar** | "about 20 minutes", "3–5 days", "8 shades", "within 24 hours", örnek gezilerdeki ve "Patients worldwide" bölgelerindeki uçuş süreleri (Avrupa 1.5–4 sa, Ortadoğu 3.5–4.5 sa, ABD 10–13 sa; şehir bazında süreler `main.js` → `HOURS`) ve koordinatör dilleri (İngilizce, Arapça, Almanca, Romence) kliniğin gerçek verileriyle kontrol edilmeli. |
| Sosyal medya | footer `.socials` içindeki `href="#"` değerleri |
| Yasal sayfalar | Gizlilik politikası / KVKK ve çerez metni henüz yok; ayrı sayfa olarak eklenip footer'a bağlanmalı. |

> **Hukuki not:** Göz rengi değiştirme elektif bir tıbbi işlemdir. Türkiye'de sağlık hizmeti tanıtımı (hasta yorumu, önce/sonra görseli, fiyat ve "garanti" ifadeleri) ile hedef ülkelerin reklam kuralları kısıtlayıcı olabilir. SSS'deki risk ve uygunluk metinleri genel bilgi olarak yazıldı. Yayın öncesi kliniğin göz doktorlarına ve bir hukukçuya kontrol ettirin.

## Fotoğraf değiştirme

Her görsel alanı `assets/img/content/` içindeki bir dosyayı bekler. Dosya yoksa alanda lacivert, kesik çerçeveli bir yer tutucu çıkar ve üzerinde beklenen dosya adı yazar. Dosyayı **aynı adla** koyduğunuzda kod değişmeden yerine oturur.

| Dosya | Boyut | Nerede |
|---|---|---|
| `shade-1` … `shade-8.webp`, `shade-N-detail.webp` | 800×500 | Ton listesi (gün ışığı + yakın çekim) |
| `shade-preview-1…3.webp` | 300×300 | "A preview on your own eyes" kartı (IR-01, IR-07, IR-05) |
| `why.webp` | 1500×2000 | "Why İrisya" fotoğrafı: gün ışığında yanağa tutulan IR-07 Hazel ton diski. Siyah-beyaz işlem **dosyanın içinde** (yalnızca iki göz ve disk renkli; `../irisya-tools/hf/process.py` → `COLOUR_SPOTS`), CSS filtre uygulamaz. Gerçek fotoğrafla değiştirirseniz siyah-beyazı kendiniz yapın. Masaüstünde 16:9, telefonda 4:3 kırpılır. |
| `journey-1` … `journey-5.webp` | 1680×840 | "How it works" destesi (siyah-beyaz gösterilir) |
| `story-1` … `story-5.webp` | 1100×1467 | Hasta hikâyesi portreleri (siyah-beyaz) |
| `moment-1` … `moment-5.webp` | 600×750 | Hikâyelerdeki eğik fotoğraf |
| `quote-1` … `quote-9.webp` | 640×840 | Yorum şeridindeki fotoğraflı kartlar (siyah-beyaz gösterilir). Her kartın fotoğrafı alıntısına uygun sahne: telefonda ton önizlemesi, Arapça konuşan koordinatörle anne-kız, vapurda güneş gözlüğü, havalimanı karşılaması vb. Kartın rengi `t-navy / t-iris / t-honey / t-white` sınıfıyla seçilir. |
| `riders.webp` | 1200×1800 | "Patients worldwide" İstanbul görseli (lacivert çift ton) |
| `tx-1` … `tx-4.webp`, `tx-4-after.webp` | 1400×1050 | Tedavi sekmeleri (`tx-1`, `tx-2` siyah-beyaz; `tx-3` ve heterokromi renkli) |
| `footer.webp` / `footer-portrait.webp` | 2400×1030 / 900×1125 | Kapanış bölümü arka planı |
| `clinic.webp` | 600×375 | Footer'daki klinik kartı |
| `og-image.jpg` | 1200×630 | Sosyal medya paylaşım görseli |
| `hero.mp4/webm`, `hero-720.*`, `hero-portrait.*` | 1920×1080 / 1280×720 / 608×1080, 16 sn | Hero filmi: geniş ekran, dizüstü/tablet, telefon. Kaynak ve kurgu: `../hero-film/irisya/build.py` (Higgsfield hesabındaki 6 Kling 4.0 klibi; `python -E build.py fetch` indirir). Yeniden üretince `index.html`'deki `data-v` ve poster `?v=` değerlerini artırın. |
| `hero.webp`, `hero-portrait.webp` | 1920×1080 / 608×1080 | Film yüklenene kadar görünen kare (filmin 1. saniyesi) |
| `hero-still.webp`, `hero-still-portrait.webp` | 1920×1080 / 608×1080 | "Hareketi azalt" açıkken görünen sabit kare |

## Sayfa bölümleri

- **Hero:** "Choose your eye colour." Arkada film (ekran görünürken oynar, kaydırınca durur; duraklat düğmesi sağ altta). Cümle formu (şu anki göz rengi, istenen ton, kalkış şehri, isteğe bağlı fotoğraf) → WhatsApp mesajı. WhatsApp bağlantıyla dosya taşıyamadığı için fotoğraf seçilirse kullanıcıya sohbette eklemesi söylenir.
- **All-inclusive:** Üç örnek gezi; prosedür, otel, transfer, koordinatör kartları, gün planı, sabit fiyat kartı.
- **Why İrisya:** Kaydırdıkça kelime kelime dolan cümle ("Plenty of clinics start with the colour. We start with your cornea…"), altında gün ışığında ton denemesini gösteren fotoğraf ("IR-07 Hazel, checked in daylight") ve üç sayı.
- **How it works:** Plan → Arrive → Examine → Colour → Fly home destesi (sürüklenebilir, oklarla gezilebilir, 6 sn'de bir ilerler).
- **Patients worldwide:** Avrupa / Ortadoğu / ABD satırları (şehirler ve direkt uçuş süreleri). Seçili bölge görseldeki çerçeveyi bal rengine çevirir; rota kartı o bölgenin şehirlerini döndürür. Kimse tıklamazsa bölgeler sırayla değişir, tıklanınca seçilen bölgede kalır. Koordinatör dilleri.
- **Patient stories:** 5 hikâye (biniş kartı özetli, her hikâyede sürüklenebilir önce/sonra göz şeridi: önce doğal kahverengi, sonra hikâyenin tonu; `../irisya-tools/hf/ba.py` ile üretilir) ve kayan yorum şeridi; şeritteki 9 kartın hepsi fotoğraflı ve göz rengi değişimiyle ilgili (fotoğraf siyah-beyaz, yalnızca kişinin irisleri kendi tonunda renkli), her kartta tonun çizilmiş irisi var.
- **What's included:** 7 kartlık bento.
- **Treatments:** 4 sekme (keratopigmentasyon, lazerle iris açma, kişiye özel ton, heterokromi + önce/sonra düğmesi).
- **Shades (8):** Büyük harfli ton listesi; her satır gün ışığı, çizilmiş iris ve yakın çekim gösterir.
- **FAQ:** 28 soru, 5 konu süzgeci.
- **Kapanış (Free shade plan):** "Two photos. One quote." Formda ton seçici (8 ton + "Not sure"), "Flying in from" (Europe / Middle East / USA / Elsewhere) ve not alanı; seçimler WhatsApp mesajına satır olarak eklenir. Altında fotoğraf ipuçları ve üç adım (fotoğrafları gönder → 24 saatte ton planı → tek sabit fiyat). Geniş ekranda yanlarda uçuş süresi çerçeveleri, footer.

Tüm animasyonlar "hareketi azalt" ayarı açık olan cihazlarda kapanır; hero filmi bu cihazlarda ve veri tasarrufu modunda kendiliğinden oynamaz, sabit kare ve oynat düğmesi görünür. İçerik JavaScript çalışmasa da görünür kalır.