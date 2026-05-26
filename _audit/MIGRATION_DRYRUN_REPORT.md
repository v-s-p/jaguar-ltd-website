# Gocmaksan Schema Migration — Dry-Run Report

**Tarih:** 2026-05-26 12:48  
**Toplam makine:** 47  
**Degisecek makine:** 47 / 47  
**Anomali:** 0  

## A. Coklu Subcategory'li Makineler

Toplam: **9 makine** subcategory array'i 2+ eleman iceriyor (array KORUNUYOR, degistirilmiyor).

| Kombinasyon | Makine |
|---|---|
| `Spiral + Steel Factory` | `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi` |
| `Standard + Light Construction` | `gms-bcz-600-gocmaksan-tugla-kesme-makinasi` |
| `Standard + Steel Factory` | `gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi`, `gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi`, `gms-matrix-55-gocmaksan-demir-demir-kesme-hatti`, `gms-matrix-55s-gocmaksan-demir-kesme-hatti`, `gms-mh-8c-gocmaksan-hasir-kesme-makinasi`, `gms-synclone-45s-gocmaksan-demir-bukme-hatti` |
| `Stirrup + Steel Factory` | `gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi` |

## B. Empty Cleanup ile Kaldirilan Key'ler

**38 makinede** empty cleanup tetiklendi:

| Makine | Kaldirilan |
|---|---|
| `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-b-26-gocmaksan-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-b-36-gocmaksan-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-b-50-gocmaksan-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-bcz-600-gocmaksan-tugla-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-bt-24x5-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-bt-26-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-h-26-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-h-36-s-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-h-38-s-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-h-45-s-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-h-55-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-kalip-sokmeler-gocmaksan` | specs: all keys empty after processing — diller.en.specs not written |
| `gms-kompaktor` | TECHNICAL DATA: empty dict — discarded (not written) |
| `gms-m-36-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-m-45-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-m-55-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-matrix-55-gocmaksan-demir-demir-kesme-hatti` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-matrix-55s-gocmaksan-demir-kesme-hatti` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-max-40-gocmaksan-insaat-demiri-kesme-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-mg-20b-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-mg-26-junior-portatif-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-mh-8c-gocmaksan-hasir-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-perdah-makinasi` | TECHNICAL DATA: empty dict — discarded (not written); pdf_catalog top-level removed (diller.en already has it) |
| `gms-power-24-gocmaksan-portatif-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-rl-2000-gocmaksan-cift-tamburlu-silindir` | TECHNICAL DATA: empty dict — discarded (not written) |
| `gms-sh-45-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sh-60-gocmaksan-insaat-demiri-kesme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sl-30-gocmaksan-etriye-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sl-36-gocmaksan-etriye-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sx-26-gocmaksan-spiral-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sx-36-gocmaksan-spiral-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-sx-40-gocmaksan-spiral-demir-bukme-makinasi` | pdf_catalog top-level removed (diller.en already has it) |
| `gms-synclone-45s-gocmaksan-demir-bukme-hatti` | pdf_catalog top-level removed (diller.en already has it) |

## C. Spec Key Kapsamı (GENERAL FEATURES / CAPACITIES / SUPPLIED EQUIPMENT)

**46 makinede** en az 1 spec key eksik:

| Makine | Mevcut | Eksik |
|---|---|---|
| `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-ayarli-kosebentler-gocmaksan` | `CAPACITIES` | `GENERAL FEATURES`, `SUPPLIED EQUIPMENT` |
| `gms-b-26-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-b-36-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-b-50-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bcz-600-gocmaksan-tugla-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bs-36-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi-sy0wu` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bs-50-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bs-60-gocmaksan-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bt-24x5-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-bt-26-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-demirci-anahtarlari-gocmaksan` | `CAPACITIES` | `GENERAL FEATURES`, `SUPPLIED EQUIPMENT` |
| `gms-el-makaslari-gocmaksan` | `CAPACITIES` | `GENERAL FEATURES`, `SUPPLIED EQUIPMENT` |
| `gms-etriye-kollari-gocmaksan` | `CAPACITIES` | `GENERAL FEATURES`, `SUPPLIED EQUIPMENT` |
| `gms-h-26-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-h-36-s-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-h-38-s-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-h-45-s-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-h-55-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-kalip-sokmeler-gocmaksan` | — | `GENERAL FEATURES`, `CAPACITIES`, `SUPPLIED EQUIPMENT` |
| `gms-kompaktor` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-m-36-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-m-45-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-m-55-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-matrix-55-gocmaksan-demir-demir-kesme-hatti` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-matrix-55s-gocmaksan-demir-kesme-hatti` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-max-40-gocmaksan-insaat-demiri-kesme-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-mg-20b-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-mg-26-junior-portatif-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-mh-8c-gocmaksan-hasir-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-oturak-makaslari-gocmaksan` | `CAPACITIES` | `GENERAL FEATURES`, `SUPPLIED EQUIPMENT` |
| `gms-perdah-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-power-24-gocmaksan-portatif-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-rl-2000-gocmaksan-cift-tamburlu-silindir` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sh-45-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sh-60-gocmaksan-insaat-demiri-kesme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sl-30-gocmaksan-etriye-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sl-36-gocmaksan-etriye-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sx-26-gocmaksan-spiral-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sx-36-gocmaksan-spiral-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-sx-40-gocmaksan-spiral-demir-bukme-makinasi` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |
| `gms-synclone-45s-gocmaksan-demir-bukme-hatti` | `CAPACITIES`, `GENERAL FEATURES` | `SUPPLIED EQUIPMENT` |

## D. Beklenmedik Spec Key'ler

Hicbir makinede beklenmedik spec key yok. Temiz.

## F. Makine Bazinda Ozet

| Makine | Log satiri | Degisti? | Subcat | Spec keys |
|---|---|---|---|---|
| `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi` | 8 | YES | ['Spiral', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-ayarli-kosebentler-gocmaksan` | 6 | YES | ['Hand Tools'] | CAPACITIES |
| `gms-b-26-gocmaksan-insaat-demiri-bukme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-b-36-gocmaksan-insaat-demiri-bukme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-b-50-gocmaksan-insaat-demiri-bukme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-bcz-600-gocmaksan-tugla-kesme-makinasi` | 8 | YES | ['Standard', 'Light Construction'] | GENERAL FEATURES, CAPACITIES |
| `gms-bs-36-gocmaksan-insaat-demiri-bukme-makinasi` | 7 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi-sy0wu` | 7 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-bs-50-gocmaksan-insaat-demiri-bukme-makinasi` | 7 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-bs-60-gocmaksan-insaat-demiri-bukme-makinasi` | 7 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-bt-24x5-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | 8 | YES | ['Portable'] | GENERAL FEATURES, CAPACITIES |
| `gms-bt-26-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | 8 | YES | ['Portable'] | GENERAL FEATURES, CAPACITIES |
| `gms-demirci-anahtarlari-gocmaksan` | 6 | YES | ['Hand Tools'] | CAPACITIES |
| `gms-el-makaslari-gocmaksan` | 6 | YES | ['Hand Tools'] | CAPACITIES |
| `gms-etriye-kollari-gocmaksan` | 6 | YES | ['Hand Tools'] | CAPACITIES |
| `gms-h-26-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-h-36-s-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-h-38-s-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-h-45-s-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-h-55-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-kalip-sokmeler-gocmaksan` | 5 | YES | ['Hand Tools'] | — |
| `gms-kompaktor` | 8 | YES | ['Light Construction'] | GENERAL FEATURES, CAPACITIES |
| `gms-m-36-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-m-45-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-m-55-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-matrix-55-gocmaksan-demir-demir-kesme-hatti` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-matrix-55s-gocmaksan-demir-kesme-hatti` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-max-40-gocmaksan-insaat-demiri-kesme-bukme-makinasi` | 8 | YES | ['Combined'] | GENERAL FEATURES, CAPACITIES |
| `gms-mg-20b-gocmaksan-portatif-insaat-demiri-bukme-makinasi` | 8 | YES | ['Portable'] | GENERAL FEATURES, CAPACITIES |
| `gms-mg-26-junior-portatif-bukme-makinasi` | 8 | YES | ['Portable'] | GENERAL FEATURES, CAPACITIES |
| `gms-mh-8c-gocmaksan-hasir-kesme-makinasi` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
| `gms-oturak-makaslari-gocmaksan` | 6 | YES | ['Hand Tools'] | CAPACITIES |
| `gms-perdah-makinasi` | 8 | YES | ['Light Construction'] | GENERAL FEATURES, CAPACITIES |
| `gms-power-24-gocmaksan-portatif-insaat-demiri-kesme-makinasi` | 8 | YES | ['Portable'] | GENERAL FEATURES, CAPACITIES |
| `gms-rl-2000-gocmaksan-cift-tamburlu-silindir` | 8 | YES | ['Light Construction'] | GENERAL FEATURES, CAPACITIES |
| `gms-sh-45-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-sh-60-gocmaksan-insaat-demiri-kesme-makinasi` | 8 | YES | ['Standard'] | GENERAL FEATURES, CAPACITIES |
| `gms-sl-30-gocmaksan-etriye-bukme-makinasi` | 8 | YES | ['Stirrup'] | GENERAL FEATURES, CAPACITIES |
| `gms-sl-36-gocmaksan-etriye-bukme-makinasi` | 8 | YES | ['Stirrup'] | GENERAL FEATURES, CAPACITIES |
| `gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi` | 9 | YES | ['Stirrup', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES, SUPPLIED EQUIPMENT |
| `gms-sx-26-gocmaksan-spiral-demir-bukme-makinasi` | 8 | YES | ['Spiral'] | GENERAL FEATURES, CAPACITIES |
| `gms-sx-36-gocmaksan-spiral-demir-bukme-makinasi` | 8 | YES | ['Spiral'] | GENERAL FEATURES, CAPACITIES |
| `gms-sx-40-gocmaksan-spiral-demir-bukme-makinasi` | 8 | YES | ['Spiral'] | GENERAL FEATURES, CAPACITIES |
| `gms-synclone-45s-gocmaksan-demir-bukme-hatti` | 8 | YES | ['Standard', 'Steel Factory'] | GENERAL FEATURES, CAPACITIES |
