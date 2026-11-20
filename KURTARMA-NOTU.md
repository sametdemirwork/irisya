# İrisya Clinic: kurtarma notu (20 Kasım 2026)

Klasör 16-19 Kasım arasında masaüstünden kalıcı olarak silinmişti. Çöp Kutusu'nda değildi.
Bu klasördeki metin dosyaları eski Claude oturum kayıtlarından yeniden oluşturuldu:
her yazma ve düzenleme adımı ile Bash üzerinden yapılan sed/Python değişiklikleri sırayla yeniden uygulandı.

## Siteyi çalıştırma
- `siteyi-ac.bat` dosyasına çift tıklayın: site http://localhost:5510 adresinde açılır (Python gerekir, bilgisayarda kurulu).
- Ya da PowerShell'de: `cd irisya-clinic` ve ardından `python -m http.server 5510`.
- Claude içinden önizleme ayarı `.claude/launch.json` dosyasında (`irisya-site`, `vors-site`).
- Kod, düzen ve etkileşimler çalışıyor. Fotoğraflar ve hero filmi 20 Kasım'da Higgsfield'den geri yüklendi (aşağıda).
  Yalnızca logo dosyaları hâlâ eksik.
- `og-image.jpg` eski bir oturumun geçici klasöründen geri alındı.

## Doğrulama
- `irisya-clinic/index.html`, `assets/css/style.css`, `assets/js/main.js`, `README.md`:
  15 Kasım 21:45'teki (UTC) tam okumalarla birebir eşleştirildi. Sonraki tüm değişiklikler hatasız uygulandı
  ve kayıtlardaki son komut çıktılarıyla karşılaştırıldı (style.css 1188 satır, `?v=15` / `?v=10`, 35 tipografik ’ vb.).
  Bu dört dosya, silinmeden önceki son hâliyle aynı olmalı.
- `irisya-tools/*.py`, `irisya.css`, `hero-film/irisya/build.py`, `prompts.md`: Claude'un dosya geçmişindeki tam kopyalarla eşleşti.
- Daha az kesin olanlar: `irisya-tools/hf/jobs.json`, `irisya-responsive.css`, `restyle.py` ve
  `backups/2026-11-15_pitch-yenileme-oncesi/` yalnızca komutların yeniden çalıştırılmasıyla oluştu. Bunlar tam bir okumayla doğrulanamadı.
- `backups/2026-11-16_ai-rotus-oncesi/`: 21:45'te doğrulanan hâlin 21:51'deki kopyası, güvenilir.
- `vors-dental-clinic/`: İrisya klasörünün içindeki 14 Kasım tarihli referans kopya (yalnızca 3 kod dosyası).

## Görseller ve video: Higgsfield'den geri yükleme (20 Kasım 2026)

Sitenin kullandığı fotoğrafların hepsi Higgsfield hesabındaki üretimlerden yeniden oluşturuldu.
Hesaptaki 121 görsel tek tek incelendi; her site dosyasının hangi üretimden geldiği
`irisya-tools/hf/sources.json` içinde (üretim kimliği ve tarihiyle) yazılı. Aynı görsel için birden fazla deneme
varsa, son ve istemle uyuşan deneme seçildi. Portreler ayrıca `process.py` / `ba.py` içindeki göz koordinatlarıyla
piksel düzeyinde doğrulandı: 5 hikâye portresi ve 9 yorum fotoğrafında kayıtlı iris konumları gözlere tam oturuyor.

Yeniden üretmek için (Python, numpy, pillow):
1. `irisya-tools/hf/` içinde `HF_CDN` ortam değişkenine Higgsfield sonuç adresinin `/hf_...` öncesindeki kısmını verin,
   `python fetch.py` çalıştırın (ham PNG'ler `raw/` içine iner, git'e girmez).
2. `python recolour.py`, `python ba.py`, ardından `process.py` içinde siteye giren adlarla `python process.py ...`.
   `og-image` adını vermeyin: mevcut `og-image.jpg` daha yeni tasarım, `process.py` eski sürümünü üretir.
3. Hero filmi: `hero-film/irisya/` içinde `python -E stills.py` (`pip install imageio-ffmpeg`).

### Birebir aynı kaynaktan gelenler (51 dosya)
story-1…5, moment-1…5, quote-1…9, journey-1…5, riders, footer, footer-portrait, clinic, tx-1…4,
shade-1…8 ve shade-N-detail, shade-preview-1…3: eski oturumdaki aynı Higgsfield üretimleri ve aynı `process.py` ayarları.
`ba.py` şeritlerinin "sonra" tarafı da (story-N-after) aynı portrelerden.

### Higgsfield geçmişinde olmadığı için yerine konanlar
Higgsfield bağlantısı yalnızca Soul / Soul Cinematic / Soul Location görsellerini listeliyor. **GPT Image 2.6 düzenlemeleri
ve Kling 4.0 videoları geçmişte görünmüyor** (video listesi boş geliyor). Bunların yerine:

| Dosya | Eskiden | Şimdi |
|---|---|---|
| `why.webp` | `why-shade-c` (GPT Image) | Aynı istemin Soul Cinematic sürümü `why-shade-b`; renkli bölgeler (`COLOUR_SPOTS`) ona göre yeniden ölçüldü. Sahne aynı: pencere önünde yanağa tutulan IR-07 Hazel diski. |
| `story-1…5-before.webp`, `story-3/5-after` | GPT Image ile kahverengi / düzeltilmiş göz düzenlemeleri | `irisya-tools/hf/recolour.py`: iris çemberi bulunur, göz kapağı ayrılır, yalnızca iris pikselleri yeniden renklenir (doku korunur). `ba.py` artık bu aracın kaydettiği iris maskesini kullanıyor; `BEFORE_TONE` boşaltıldı. |
| `tx-4-after.webp` | GPT Image (kahverengi gözü mavi yapan düzenleme) | `recolour.py`: kahverengi iris, diğer gözün açık gri-mavisine eşlendi. |
| `hero*.mp4/webm`, `hero*.webp` | 8 Kling klibi + `build.py` | **Geçici:** `hero-film/irisya/stills.py`, `build.py`'nin kurgusunu (16 sn, aynı geçişler, renk, bölüm zamanları, telefon kırpması, posterler) Higgsfield fotoğraflarıyla kuruyor: ela iris → Boğaz (mavi saat) → Galata → transfer aracı → karşılama şoförü → otel → buz mavisi iris → muayene → iris. Plaka, Mercedes rozeti ve karşılama kartındaki anlamsız yazı bulanıklaştırıldı. Kling klipleri bulunursa `raw/` içine koyup `python -E build.py` çalıştırmak hepsinin yerine gerçek filmi koyar. |

### Hâlâ eksik: logo dosyaları (Higgsfield'den gelmiyordu)
Bunlar size verilen logo dosyalarından `irisya-tools/brand.py` ile kesiliyordu; kaynakları (`irisya-tools/logo-src/irisya-logo-navy.webp`
ve `irisya-logo-white.webp`) da silinenler arasında. Bu iki dosyayı geri koyup `python -E irisya-tools/brand.py` çalıştırmak hepsini üretir:

- assets/img/brand/mark-light.webp, wordmark-white.webp (menü), logo-navy.webp (footer, JSON-LD)
- assets/img/brand/favicon-32.png, favicon-192.png, apple-touch-icon.png

## Uçtan uca kontrol (20 Kasım 2026)
Site yerelde (`python -m http.server`) Chromium ile masaüstü 1440×900, dizüstü 1280×720, tablet 820×1180 ve telefon
(iPhone 13) boyutlarında açıldı, sayfa baştan sona kaydırıldı, 5 hikâye sekmesi, 4 tedavi sekmesi, heterokromi
"Today / Matched" düğmesi, önce/sonra kaydırıcısı ve ton satırları tıklandı.
- 75 içerik görselinin hepsi yükleniyor ve dosya boyutları HTML'deki width/height değerleriyle birebir aynı.
  `<picture>` kaynakları (telefon posteri, footer portresi) da doğru boyutta. Yer tutucu çıkan görsel yok.
- Hero filmi her ekranda oynuyor ve doğru dosyayı seçiyor: masaüstü/tablet `hero.webm`, dizüstü `hero-720.webm`,
  telefon `hero-portrait.webm`; bölüm etiketi filmle birlikte ilerliyor. "Hareketi azalt" açıkken `hero-still.webp`
  görünüyor ve film indirilmiyor. Videolar 16 sn, 24 fps, sessiz, yuv420p (H.264 + VP9).
- Konsolda JavaScript hatası yok. Tek hata: logo dosyalarının 404'ü (yukarıda, "Hâlâ eksik").
- Hikâye portreleri, gezi fotoğrafları ve yorum fotoğrafları metinlerle eşleşiyor (ör. Layla / Dubai / IR-07 Hazel,
  "Galata at sunset", Noor / Kuveyt / annesiyle).
