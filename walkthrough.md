# Çok Dilli (i18n) Altyapı Kurulumu - Walkthrough

Sitenin global bir platforma dönüşmesi için gereken çok dilli yapı (Internationalization - i18n) başarıyla kuruldu.

## Yapılan Temel Değişiklikler

### 1. Sözlük ve Yardımcı Fonksiyonlar
`src/i18n/` dizini altında merkezi bir yönetim sistemi kuruldu.
- **`ui.ts`**: Site üzerindeki tüm statik metinlerin (Navigasyon, Butonlar, Alt Bilgi) 7 dildeki karşılıkları tanımlandı.
- **`utils.ts`**: URL'den dil algılama ve SEO uyumlu dil-spesifik URL üretme fonksiyonları eklenecek.

### 2. Bileşen Tabanlı Mimari (Refactor)
Astro'nun statik derleme gücünü verimli kullanmak için sayfalar bileşenlere (`src/components/pages/`) dönüştürüldü:
- **`HomePage.astro`**, **`KategoriPage.astro`**, **`MachinePage.astro`** vb.
- Bu sayede aynı içerik hem `/` (Bulgarca) hem de `/en/`, `/tr/` gibi yollarda kod tekrarı olmadan render edilebiliyor.

### 3. Dinamik Dil Seçici (Language Picker)
Header ve Footer alanlarına kullanıcının dil değiştirebileceği şık bir dropdown eklendi. Seçilen dile göre site anında (yeniden yüklenerek) ilgili dile bürünür.

### 4. Makine Verileri Entegrasyonu
`machines.json` ve `gocmaksan.json` verileri artık aktif dile göre filtreleniyor:
- Eğer makinenin seçilen dilde (örneğin Rusça) bir çevirisi varsa o gösterilir.
- Çeviri yoksa otomatik olarak İngilizce'ye veya orijinal Bulgarca veriye geri döner (Fallback).

## Test ve Doğrulama
- `npm run build` komutu çalıştırılarak tüm diller için statik sayfaların (Örn: `/bg/about`, `/en/about`, `/tr/about`) hatasız üretildiği doğrulandı.
- Import yollarındaki kırılmalar ve dosya hiyerarşisi hataları giderildi.

## Önemli Dosyalar
- [ui.ts](file:///c:/Users/Kenan/Desktop/AI/Jaguar-ltd/src/i18n/ui.ts)
- [utils.ts](file:///c:/Users/Kenan/Desktop/AI/Jaguar-ltd/src/i18n/utils.ts)
- [LanguagePicker.astro](file:///c:/Users/Kenan/Desktop/AI/Jaguar-ltd/src/components/LanguagePicker.astro)
- [CLAUDE_MASTER.md](file:///c:/Users/Kenan/Desktop/AI/Jaguar-ltd/CLAUDE_MASTER.md)

---
*Hazırlayan: Antigravity AI*
