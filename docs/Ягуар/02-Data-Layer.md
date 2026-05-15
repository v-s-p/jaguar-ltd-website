---
title: Data Layer
type: data
status: active
last_verified: 2026-05-03
---

## Purpose

İki ayrı JSON dosyasında tutulan 121 makinenin veri yapısını ve ortak 
TypeScript tipini tanımlar. Format v2'ye migrate edilmiş hâli.

## Key Facts

- **yilmaz.json** — 74 Yılmaz makinesi (alüminyum + PVC işleme)
- **gocmaksan.json** — 47 Göçmaksan makinesi (büküm, makaslar)
- **Type tanımı:** `src/types/Machine.ts` — `subcategory: string[]`, `specs?: MachineSpecs`
- **MachineSpecs 4 anahtarı:** `"STANDART AKSESUARLAR"?: string[]`, 
  `"OPSIYONEL AKSESUARLAR"?: string[]`, `"GENEL OZELLIKLER"?: string[]`, 
  `"TEKNIK_TABLO"?: Record<string, string>`
- **Marka ayrımı:** Her makinede `brand: "yilmaz"` veya `"gocmaksan"`
- **Yılmaz şeması:** `categories: string[]` (Aluminium, PVC), 
  `subcategory: string` (Cutting, Routing, vb.)
- **Göçmaksan şeması:** `category: string` (Bending Machines), 
  `subcategory: string` (Standard, vb.)
- **Dil yapısı:** `diller.{en|tr|ru|es|ro|bg|bcs}` — `name`, `description`, 
  `images`, `specs`
- **Migration:** Eski format (`isim`, `aciklama`, `resimler`, `kategoriler`) 
  v2'de İngilizce alan adlarına dönüştürüldü

## Connections

- [[Architecture-Overview]] — Üst seviye sistem bağlamı
- [[Page-Components]] — Bu veriyi tüketen render katmanı
- [[Migration-History]] — v1→v2 geçişinin tarihçesi
- [[scraper-pipeline]] — Veriyi üreten pipeline
- [[translation-pipeline]] — `diller.*` alanlarını dolduran süreç

## Source Files

- `src/data/yilmaz.json` — Yılmaz veri seti (74 kayıt)
- `src/data/gocmaksan.json` — Göçmaksan veri seti (47 kayıt)
- `src/types/Machine.ts` — Ortak TypeScript interface

## Open Questions

_(Tüm kritik sorular kapatıldı — 2026-05-03)_