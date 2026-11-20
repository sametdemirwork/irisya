# İrisya Clinic: kurtarma notu (20 Kasım 2026)

Klasör 16-19 Kasım arasında masaüstünden kalıcı olarak silinmişti. Çöp Kutusu'nda değildi.
Bu klasördeki metin dosyaları eski Claude oturum kayıtlarından yeniden oluşturuldu:
her yazma ve düzenleme adımı ile Bash üzerinden yapılan sed/Python değişiklikleri sırayla yeniden uygulandı.

## Siteyi çalıştırma
- `siteyi-ac.bat` dosyasına çift tıklayın: site http://localhost:5510 adresinde açılır (Python gerekir, bilgisayarda kurulu).
- Ya da PowerShell'de: `cd irisya-clinic` ve ardından `python -m http.server 5510`.
- Claude içinden önizleme ayarı `.claude/launch.json` dosyasında (`irisya-site`, `vors-site`).
- Kod, düzen ve etkileşimler çalışıyor. Görseller gelene kadar fotoğraf alanları boş görünür.
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

## Geri gelmeyenler: görseller ve videolar
Oturum kayıtlarında görsellerin yalnızca adı geçiyor. Sitenin kullandığı ve şu an eksik olan dosyalar
(`irisya-clinic/` içine bu yollarla geri konmalı):

- assets/img/brand/apple-touch-icon.png
- assets/img/brand/favicon-192.png
- assets/img/brand/favicon-32.png
- assets/img/brand/logo-navy.webp
- assets/img/brand/mark-light.webp
- assets/img/brand/wordmark-white.webp
- assets/img/content/${file}`;
- assets/img/content/<file>.
- assets/img/content/clinic.webp
- assets/img/content/footer-portrait.webp
- assets/img/content/footer.webp
- assets/img/content/hero
- assets/img/content/hero-720
- assets/img/content/hero-portrait
- assets/img/content/hero-portrait.webp
- assets/img/content/hero-still-portrait.webp
- assets/img/content/hero-still.webp
- assets/img/content/hero.webp
- assets/img/content/journey-1.webp
- assets/img/content/journey-2.webp
- assets/img/content/journey-3.webp
- assets/img/content/journey-4.webp
- assets/img/content/journey-5.webp
- assets/img/content/moment-1.webp
- assets/img/content/moment-2.webp
- assets/img/content/moment-3.webp
- assets/img/content/moment-4.webp
- assets/img/content/moment-5.webp
- assets/img/content/og-image.jpg
- assets/img/content/quote-1.webp
- assets/img/content/quote-2.webp
- assets/img/content/quote-3.webp
- assets/img/content/quote-4.webp
- assets/img/content/quote-5.webp
- assets/img/content/quote-6.webp
- assets/img/content/quote-7.webp
- assets/img/content/quote-8.webp
- assets/img/content/quote-9.webp
- assets/img/content/riders.webp
- assets/img/content/shade-1-detail.webp
- assets/img/content/shade-1.webp
- assets/img/content/shade-2-detail.webp
- assets/img/content/shade-2.webp
- assets/img/content/shade-3-detail.webp
- assets/img/content/shade-3.webp
- assets/img/content/shade-4-detail.webp
- assets/img/content/shade-4.webp
- assets/img/content/shade-5-detail.webp
- assets/img/content/shade-5.webp
- assets/img/content/shade-6-detail.webp
- assets/img/content/shade-6.webp
- assets/img/content/shade-7-detail.webp
- assets/img/content/shade-7.webp
- assets/img/content/shade-8-detail.webp
- assets/img/content/shade-8.webp
- assets/img/content/shade-preview-1.webp
- assets/img/content/shade-preview-2.webp
- assets/img/content/shade-preview-3.webp
- assets/img/content/story-1-after.webp
- assets/img/content/story-1-before.webp
- assets/img/content/story-1.webp
- assets/img/content/story-2-after.webp
- assets/img/content/story-2-before.webp
- assets/img/content/story-2.webp
- assets/img/content/story-3-after.webp
- assets/img/content/story-3-before.webp
- assets/img/content/story-3.webp
- assets/img/content/story-4-after.webp
- assets/img/content/story-4-before.webp
- assets/img/content/story-4.webp
- assets/img/content/story-5-after.webp
- assets/img/content/story-5-before.webp
- assets/img/content/story-5.webp
- assets/img/content/tx-1.webp
- assets/img/content/tx-2.webp
- assets/img/content/tx-3.webp
- assets/img/content/tx-4-after.webp
- assets/img/content/tx-4.webp
- assets/img/content/why.webp

## Görsel kurtarma (20 Kasım 2026, bulut oturumu)
Higgsfield hesabının üretim geçmişinde 121 görsel bulundu ve indirildi. Bunlar `irisya-tools/hf/jobs.json` istemleriyle
eşleştirildi. Eşleşmeler `process.py` ve `ba.py` içindeki göz/iris koordinatlarıyla doğrulandı
(9 quote ve 5 story portresinde koordinatlar irislere birebir oturuyor). Seçilen kaynaklar `irisya-tools/hf/sources.json`
dosyasında. `python irisya-tools/hf/fetch_raw.py` bunları `raw/` klasörüne yeniden indirir, ardından `process.py` çalıştırılır.

Geri gelen 51 dosya (`assets/img/content/`):
story-1…5, moment-1…5, journey-1…5, riders, footer, footer-portrait, clinic, tx-1…4,
shade-1…8, shade-1…8-detail, shade-preview-1…3, quote-1…9.

Hâlâ eksik olanlar:
- **brand/** (logo-navy, mark-light, wordmark-white, favicon-32, favicon-192, apple-touch-icon):
  `brand.py` kaynak logo dosyalarını (`irisya-tools/logo-src/irisya-logo-navy.webp`, `irisya-logo-white.webp`) istiyor.
  Bunlar kayıp. Logo dosyaları bulunursa `python irisya-tools/brand.py` hepsini yeniden üretir.
- **hero.webp, hero-portrait.webp, hero-still.webp, hero-still-portrait.webp ve hero / hero-720 / hero-portrait (.mp4 / .webm)**:
  Higgsfield video geçmişi boş. Kling klipleri (`hero-film/irisya/raw/*.mp4`) bulunamadı.
- **why.webp**: kaynağı `why-shade-c` (GPT Image 2.6). Bu modelin sonuçları geçmiş listesinde yok.
- **tx-4-after.webp**: kaynağı `tx-4-after` (GPT Image 2.6 düzenlemesi), geçmişte yok.
- **story-1…5-before.webp / story-1…5-after.webp** (önce/sonra şeritleri): `ba.py`, GPT ile düzenlenmiş
  `story-N-before` görsellerini istiyor. Bunlar da geçmişte yok.
- `og-image.jpg` repoda zaten vardı. Mevcut dosya farklı bir tasarım olduğu için değiştirilmedi.
