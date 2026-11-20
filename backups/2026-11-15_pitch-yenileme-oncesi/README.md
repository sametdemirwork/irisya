# İrisya Clinic — Tek Sayfa Web Sitesi (Göz Rengi Değiştirme)

Vors Dental sitesinin yapısı (bölümler, animasyonlar, etkileşimler) korunarak İrisya Clinic markasına ve **göz rengi değiştirme tedavisine** göre baştan yazıldı. Site dili İngilizce; hedef pazarlar Avrupa, Körfez, ABD/Kanada ve Romanya.

Önizleme: `.claude/launch.json` → **irisya-site** (`python -m http.server 5510 --directory irisya-clinic`). Build adımı yoktur; klasörü olduğu gibi herhangi bir statik hostinge yükleyebilirsiniz.

```
index.html               → tüm sayfa
assets/css/style.css     → stiller (renk değişkenleri en üstte)
assets/js/main.js        → etkileşimler + yer tutucu sistemi
assets/img/brand/        → logonuzdan kesilen dosyalar (kullanımda)
assets/img/content/      → sitenin tüm fotoğraf/videoları (Higgsfield ile üretildi, aşağıya bakın)
```

## Higgsfield ile üretilen görseller (2026-11-15)

Hero video/posterleri dışında eksik olan 73 görselin tamamı (hikâyeler, avatarlar, ekip, yolculuk, paketler, tedaviler, 8 ton, footer, `og-image.jpg`) Higgsfield ile üretildi; sitede boş/yer tutuculu alan kalmadı.

- **Modeller:** Soul 2.0 (kişiler), Soul Cinematic (göz yakın çekimleri, klinik sahneleri), Soul Location (İstanbul, otel, klinik). Görsel başına ~0,12 kredi. Heterokromi "sonra" görseli GPT Image 2.6 ile "önce" karesinden düzenlendi (iki kare birebir hizalı). Toplam harcama ≈ 10,7 kredi.
- **Aynı kişi:** `face-1…5` avatarları `story-1…5` portrelerinden kırpıldı; `shade-preview-1…3` ve `tx-4-detail` ilgili göz fotoğraflarından kırpıldı. `og-image.jpg` = üretilmiş göz görseli + beyaz logo.
- **Araçlar:** `../irisya-tools/hf/`. `build_jobs.py` promptları (`jobs.json`) üretir, `gen.py [ad…] [--force]` Higgsfield'da üretip `raw/` içine indirir, `process.py [ad…]` kırpıp WebP olarak buraya yazar, `sheet.py` inceleme için kontak baskı çıkarır. `bin/hf.exe`, Higgsfield CLI'ının kopyasıdır (Windows Store Python, AppData içindeki CLI'ı göremediği için); CLI'ı güncellerseniz yeniden kopyalayın.
- **Tek bir görseli değiştirmek için:** `build_jobs.py` içindeki promptu düzenleyin, sonra `python build_jobs.py`, `python gen.py --force <ad>` ve `python process.py <ad>` çalıştırın.

> **Önemli:** Hasta hikâyeleri, yorum avatarları, "Why İrisya" portresi ve heterokromi önce/sonra görseli **yapay zekâ ile üretilmiş temsili kişilerdir, gerçek hasta değildir.** Yayına almadan önce bunları gerçek ve yazılı izinli hasta fotoğraflarıyla değiştirin ya da açıkça "temsili görsel" olarak işaretleyin (aşağıdaki hukuki nota bakın).

## Marka sistemi

| | |
|---|---|
| Renkler (logodan) | Lacivert `#021E44` · mürekkep `#04132B` · iris mavisi `#2D6BA6` · gök `#A8C7E3` · sis `#E7EFF7` · buz `#CFE7F8` |
| Yazı tipleri | Pitch sistemi: **Figtree** (başlık 800/700, sıkı harf aralığı; metin 400) · **Space Mono** (büyük harfli başlık üstü etiketler) |
| Logo | Navigasyonda beyaz kapaklı + renkli irisli göz işareti ve IRISYA yazısı, footer'da tam lacivert logo, favicon'da renkli iris |

CSS'teki değişken adları eski rolleri korur: `--deep` = marka laciverti, `--purple` = iris mavisi (aksiyon rengi), `--lilac` = gök, `--pale` = sis, `--lime` = buz (vurgu).

## Fotoğraf ve video ekleme (yer tutucular)

Sitedeki her görsel alanı `assets/img/content/` içindeki bir dosyayı bekler. Dosya yokken alanda **lacivert, kesik çerçeveli bir yer tutucu** görünür; üzerinde içeriğin ne olması gerektiği, dosya adı ve önerilen boyut yazar. Dosyayı **aynı adla** klasöre koyduğunuzda kod değişikliği gerekmeden yerine oturur. Farklı en-boy oranı da çalışır, görsel alana kırpılarak yerleşir.

> Format: `.webp` (adlar bu uzantıyla bekleniyor). JPG/PNG kullanmak isterseniz `index.html` içindeki ilgili `src` uzantısını değiştirin.

| Dosya | Boyut | Nerede |
|---|---|---|
| `hero.webp` | 1920×1080 | Hero arka planı (videonun başladığı kare) |
| `hero.mp4` / `.webm`, `hero-720.*`, `hero-portrait.*` | 1920×1080, 1280×720, 608×1080 · sessiz döngü | Hero videosu: ekran boyutuna göre doğru sürüm yüklenir, sağ altta durdur düğmesi ve bölüm yazısı çıkar. Kaynak ve kurgu: `../hero-film/irisya/` (`python -E build.py`) |
| `hero-portrait.webp`, `hero-still.webp`, `hero-still-portrait.webp` | 608×1080 / 1920×1080 | Telefon posteri; "hareketi azalt" açık olanlar için durağan kare |
| `story-1` … `story-5.webp` | 1100×1467 (dikey) | Hasta hikâyeleri, büyük portre |
| `moment-1` … `moment-5.webp` | 600×750 | Hikâyelerdeki eğik polaroid "an" fotoğrafı |
| `face-1` … `face-5.webp` | 200×200 | Hikâye seçici avatarları + başlıktaki 4 yuvarlak avatar |
| `review-1` … `review-9.webp` | 200×200 | Yorum şeridi avatarları |
| `vision-bg.webp` | 1600×1000 | Paket kartının bulanık arka planı |
| `package-procedure.webp`, `package-hotel.webp`, `package-transfer.webp` | 600×300 | Paket kartları |
| `why.webp` | 1000×1500 (dikey) | "Why İrisya" portresi (gözler kadrajın ~%30–40 yüksekliğinde olursa seçim kutusu gözlere denk gelir) |
| `team-1.webp` (göz doktoru), `team-2.webp` (koordinatör), `team-3.webp` (ton tasarımcısı) | 400×400 | Doktor/ekip avatarları (Why, paket kutuları, SSS kartı) |
| `journey-1` … `journey-5.webp` | 1680×840 | Yolculuk kartları: 01 göz fotoğrafı/ton önizleme · 02 havalimanı karşılama · 03 göz muayenesi · 04 işlem odası · 05 eve dönüş. Karttaki mesaj balonları sol tarafa biner, ana konuyu sağa yerleştirin |
| `riders.webp` | 1200×1120 | "Patients worldwide" İstanbul görseli |
| `bento-procedure.webp` | 600×320 | Paket kutusu: keratopigmentasyon |
| `shade-preview-1` … `-3.webp` | 300×300 | Paket kutusu: ton önizleme penceresi |
| `bento-aftercare.webp` | 600×400 | Paket kutusu: takip |
| `tx-1` … `tx-4.webp` | 1400×1050 | Tedavi sekmeleri: keratopigmentasyon · lazerle iris açma · kişiye özel ton · heterokromi (önce) |
| `tx-4-after.webp` | 1400×1050 | Heterokromi sekmesi "Matched" düğmesiyle gelen sonra görseli |
| `tx-1-detail` … `tx-4-detail.webp` | 520×650 | Sekmelerdeki eğik detay polaroidi |
| `send-photos.webp` | 960×411 | Ton kütüphanesi "fotoğraf gönder" kartı (göz yakın çekimi) |
| `shade-1` … `shade-8.webp` | 800×500 | Ton kütüphanesi satırları: göz fotoğrafı (IR-01 Glacier … IR-08 Honey) |
| `shade-1-detail` … `shade-8-detail.webp` | 800×500 | Ton kütüphanesi satırları: yakın çekim |
| `footer.webp` | 2400×1030 | Kapanış bölümü arka planı (masaüstü) |
| `footer-portrait.webp` | 900×1125 | Kapanış bölümü arka planı (telefon) |
| `clinic.webp` | 600×375 | Footer'daki klinik kartı (giriş/resepsiyon) |
| `og-image.jpg` | 1200×630 | Sosyal medya paylaşım görseli (`<head>` → `og:image`) |

**Önce/sonra fotoğrafları** (`tx-4` / `tx-4-after`, hikâye portreleri) yalnızca gerçek ve yazılı izni alınmış hasta vakaları olmalıdır. Yapay zekâ ile üretilmiş kişi görselleri hasta sonucu gibi sunulmamalıdır.

## Yayına almadan önce MUTLAKA değiştirin

| Ne | Nerede |
|---|---|
| WhatsApp numarası | `assets/js/main.js` → en üstteki `WHATSAPP_NUMBER` (ülke kodu ile, sadece rakam) |
| Telefon, e-posta, adres | `index.html` → footer `f-contact` + `<head>` JSON-LD |
| Alan adı | `canonical`, `og:image`, JSON-LD içindeki `https://www.irisyaclinic.com/` (örnek alan adı) |
| **Hasta yorumları ve hikâyeleri** | "Patient stories" bölümü, yorum şeridi ve tedavi sekmelerindeki alıntılar **örnek metinlerdir**: isimler, şehirler, uçuşlar, kalış süreleri ve ton kodları gerçek değildir. Gerçek, izinli yorumlarla değiştirin |
| **Rakamlar ve iddialar** | "Patients from 40+ countries", "about 20 minutes", "3–5 days", "8+ shades", "Most replies arrive within minutes" ifadeleri örnektir. Kliniğin gerçek verileriyle güncelleyin |
| **Koordinatör dilleri** | İngilizce, Arapça, Almanca ve Romence yazıyor (paket kartı, ülkeler bölümü, SSS, ekip kutusu). Klinik karşılamıyorsa düzeltin |
| **Hizmet kapsamı** | Heterokromi/iris düzeltme sekmesi ve SSS'deki "iris implantı yapmıyoruz" cevabı kliniğin pratiğine göre kontrol edilmeli |
| Uçuş süreleri | Footer çerçeveleri ve "Patients worldwide" rota kartındaki süreler yaklaşık değerlerdir (`main.js` → `routes`) |
| Sosyal medya | footer `socials` içindeki `href="#"` değerleri |

> **Hukuki not:** Göz rengi değiştirme elektif bir tıbbi işlemdir. Türkiye'de sağlık hizmeti tanıtımı (hasta yorumu, önce/sonra görseli, fiyat ve "garanti" ifadeleri) ile hedef ülkelerin reklam kuralları kısıtlayıcı olabilir. SSS'deki risk ve uygunluk metinleri genel bilgi olarak yazıldı. Yayın öncesi kliniğin göz doktorlarına ve bir hukukçuya kontrol ettirin. Footer'da kısa bir tıbbi uyarı notu bulunur.

## İçerik kurgusu (bölüm bölüm)

- **Hero:** "Your eyes, *reimagined.*". WhatsApp'a giden "Get my shade plan" kutusu, göz fotoğrafı ekleme butonu, göz rengine özel örnek sorular, hedef pazar bayrakları.
- **Patient stories:** "New colours, *flown home*." 5 pazar (BAE, İngiltere, Romanya, Almanya, Kanada), ton kodlu rozet, biniş kartı (kalış · ton · otel).
- **All-inclusive:** Yazılarak oluşan paket senaryoları (Glacier Blue + Dubai'den Hazel + lazerle açma), 4 günlük gezi planı.
- **Why İrisya:** Kelime kelime boyanan metin, istatistikler (ton · dakika · gün) ve animasyonlu kornea diyagramı (pigment halkası + açık merkez).
- **Your journey:** Plan → Arrive → Examine → Colour → Fly home.
- **Patients worldwide:** Dil kartı (English · العربية · Deutsch · Română), bayraklar, pazarlar arasında dönen rota kartı.
- **Paket kutuları (bento):** Keratopigmentasyon, dijital ton önizleme, VIP transfer, koordinasyon, medikal pigmentler, koordinatör, takip.
- **Tedaviler (4 sekme):** Lazer keratopigmentasyon · lazerle iris açma (temkinli dil: kademeli, tam ton seçilemez, geri alınamaz, göz tansiyonu takibi) · kişiye özel ton · heterokromi (önce/sonra düğmesi).
- **Shades (08):** IR-01 Glacier Blue … IR-08 Honey ton kütüphanesi ve fotoğraf gönderme kartı.
- **SSS:** 5 konu, 28 soru: maliyet, işlem, güvenlik/uygunluk, seyahat, bakım. Riskler açıkça yazıldı.

## Kullanılmayan dosyalar

Aşağıdakiler eski bir üretim turundan kalmadır; site bunları kullanmıyor (güncel görseller `assets/img/content/` içinde):

- `assets/img/iris/`: iris çizimleri
- `assets/img/` kökündeki kompozitler ve boyanmış fotoğraflar
- bunları üreten `../irisya-tools/` betikleri

İsterseniz silebilir ya da kendi görsellerinizin yerine kullanabilirsiniz. Logodan kesilen `assets/img/brand/` dosyaları kullanımdadır.
