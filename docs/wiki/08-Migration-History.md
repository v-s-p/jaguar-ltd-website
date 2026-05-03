---
title: Migration History
type: decision
status: active
last_verified: 2026-05-03
---

## Purpose

Veri formatının v1 (Türkçe alan adları) → v2 (İngilizce, marka-aware) 
geçişinin gerekçesi ve yapılan kararlar.

## Key Facts

- **Sorun:** `machines.json` Türkçe alan isimleri (`isim`, `aciklama`, 
  `resimler`, `kategoriler`, `alt_kategoriler`) ile eski formattaydı; 
  `gocmaksan.json` zaten yeni formatta İngilizce
- **Karışıklık:** `KategoriPage` ve `MachinePage` iki farklı yapıyı 
  okumaya çalışıyordu → PVC sayfasında slug ismi, bozuk resimler
- **Karar:** Tüm veri İngilizce alan adlarına standardize edilecek 
  (`name`, `description`, `images`, `categories`, `subcategory`)
- **Migration script:** `scripts/migrate_v2.py` (CLAUDE_MASTER kaynaklı)
- **Kategori dönüşüm tablosu:** `Aluminyum → Aluminium`, `KESIM → Cutting`, 
  `KOSE PRES → Corner Crimping`, vb. (15+ eşleşme)
- **İsim temizliği:** `"ACK 420 S - Up-Cutting Saw Machine"` → `"ACK 420 S"` 
  regex ile
- **Marka alanı:** Her kayda `brand: "yilmaz"` veya `brand: "gocmaksan"` 
  eklendi
- **Dil dizisi düzeltmesi:** `siteMetadata.ts` 10 dilden 7 dile indirildi 
  (26 Nisan 2026)
- **Tip standardı:** `src/types/Machine.ts` oluşturuldu, 
  `subcategory: string[]`, `specs` 4 standart anahtar
- **Görsel temizlik:** Çöp resimler (`logo`, `toolquaz`, `uvaga`, 
  `banner`) JSON'lardan temizlendi

## Connections

- [[Data-Layer]] — Migration'ın hedef şeması
- [[Page-Components]] — Migration sonrası fix edilen render katmanı
- [[scraper-pipeline]] — Standardın geriye doğru uygulanması

## Source Files

- `CLAUDE_MASTER.md` — Migration protokolü (proje kökünde)
- `JAGUAR_DEV_LOG.md` — Karar ve uygulama timeline'ı
- `BUTON_FIX.md` — UI fix notları
- `PDF_FIX.md` — PDF render fix notları
- `SPECS_KATALOG_FIX.md` — Specs gösterim fix notları
- `scripts/migrate_v2.py` — Migration betiği

## Open Questions

- Migration tamamen yapıldı mı yoksa kısmî mi? (Üretim verisinde 
  doğrulanması gerekir)
- 3 FIX.md dosyasının özetleri henüz wiki'ye yansıtılmadı