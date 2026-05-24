# Yılmaz BG Recovery — Apply Report

**Tarih:** 2026-05-23 19:31:31  
**Mod:** `apply`  
**Kaynak:** `d6b5cc8:src/data/machines.json`  
**Hedef dizin:** `src/data/machines/yilmaz/`

## Özet

| Metrik | Değer |
|---|---|
| Başarılı (will-write/written) | 42 |
| Hatalı | 0 |
| Atlanan / Hariç tutuldu | 1 |
| Yazılan dosya | 42 |
| Backup (.bak) oluşturulan | 42 |
| Toplam byte değişimi | +115660 bytes |
| **DURUM** | ✅ **TAMAMLANDI** |

## Özel Notlar

- **`alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi`**: **KAYIP** — individual dosya yok, inject hedefi bulunamadı. Bu makinenin BG çevirisi kurtarılamaz.
- **`vce-3500`**, **`vce-4000`**: ghost BG skeleton (`name: ""`, `description: ""`, `images: []`, boş specs) gerçek içerikle **REPLACE** edildi (`[ghost replaced]` notu ile işaretli).
- BG `specs` anahtarları Kiril alfabesiyle bırakıldı (RENAME YOK): `СТАНДАРТНИ АКСЕСОАРИ` / `ОПЦИОНАЛНИ АКСЕСОАРИ` / `ОБЩИ ХАРАКТЕРИСТИКИ`.
- `ТЕХНИЧЕСКИ ДАННИ` key'i kaynak veride her zaman boş `{}` olduğundan DROP edildi.
- `diller.en`, `diller.ru`, top-level field'lar **değiştirilmedi**.

## Makine Detay Tablosu

| # | Slug | Sonuç | Bytes Önce→Sonra | Not |
|---|---|---|---|---|
| 1 | `alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi` | **excluded** | — | no individual file — BG content lost (alm-6510) |
| 2 | `ack-420-s-up-cutting-saw-machine` | **written** | 3452 → 6515 | OK |
| 3 | `aim-4420` | **written** | 3155 → 8911 | OK |
| 4 | `aim-7420` | **written** | 3591 → 9534 | OK |
| 5 | `ca-603-pvc-corner-cleaning-machine-4-6-cutters` | **written** | 2481 → 5270 | OK |
| 6 | `ccl-1661-pvc-corner-cleaning-machine` | **written** | 3915 → 9269 | OK |
| 7 | `cnc-609` | **written** | 3038 → 6350 | OK |
| 8 | `cnc-611` | **written** | 3070 → 6367 | OK |
| 9 | `crm-201-s-template-copy-router-machine-with-triple-hole-water-slot-drilling` | **written** | 3375 → 7308 | OK |
| 10 | `crm-250-s-template-copy-router-machine` | **written** | 2844 → 6224 | OK |
| 11 | `dc-421-psd-double-head-mitre-saw-machine-full-automatic` | **written** | 2840 → 5993 | OK |
| 12 | `dc-550-pb-double-head-mitre-saw-machines` | **written** | 3810 → 7528 | OK |
| 13 | `dc-550-skh-double-head-mitre-saw-machine-full-automatic` | **written** | 4752 → 8851 | OK |
| 14 | `dkn-300-450-600-302-452-602-roller-conveyor-with-manual-stop-display-unit` | **written** | 1676 → 3012 | OK |
| 15 | `fr-223-fr-223s-portable-template-copy-router` | **written** | 2595 → 4705 | OK |
| 16 | `fr-226-s-automatic-copy-router-machine` | **written** | 2208 → 4621 | OK |
| 17 | `gas-301` | **written** | 1625 → 3181 | OK |
| 18 | `kd-350-d-miter-saw-machine` | **written** | 2545 → 4588 | OK |
| 19 | `kd-350-m-miter-saw-machine` | **written** | 2127 → 3640 | OK |
| 20 | `kd-400-d-miter-saw-machine` | **written** | 2829 → 5181 | OK |
| 21 | `kd-400-m-mitre-saw-machine` | **written** | 1678 → 3234 | OK |
| 22 | `km-215-s-semi-automatic-end-milling-machine` | **written** | 2629 → 5636 | OK |
| 23 | `mca-801` | **written** | 2154 → 4711 | OK |
| 24 | `mk-420-mk-420ps-mk-450-manual-up-cutting-saw-machine` | **written** | 3816 → 6717 | OK |
| 25 | `mkn-serisi-150-300-301` | **written** | 1562 → 2687 | OK |
| 26 | `nsm-352-nsm-353-kanat-isleme-merkezi` | **written** | 1805 → 2921 | OK |
| 27 | `pim-6508-se` | **written** | 3825 → 8698 | OK |
| 28 | `pwb-4100` | **written** | 1697 → 3427 | OK |
| 29 | `pye-101-pye-102-pye-103-pye-104-manual-punch-press` | **written** | 2325 → 3738 | OK |
| 30 | `rs-1000` | **written** | 999 → 1827 | OK |
| 31 | `ryk-420-w-radial-saw-machine` | **written** | 2616 → 5750 | OK |
| 32 | `scm-420-l4-scm-420-l7-servo-controlled-serial-cutting-machine` | **written** | 4251 → 8005 | OK |
| 33 | `sdt-275` | **written** | 1317 → 2533 | OK |
| 34 | `sk-500-d-automatic-sawing-and-drilling-machine` | **written** | 3746 → 8724 | OK |
| 35 | `skn-300-450-600-digital-roller-conveyor-with-automatic-length-stop` | **written** | 2263 → 4175 | OK |
| 36 | `sm-201-sd` | **written** | 2596 → 5597 | OK |
| 37 | `st-264-pvc-automatic-water-slot-machine` | **written** | 2288 → 4549 | OK |
| 38 | `tk-503-pvc-tek-kose-kaynak-makinesi` | **written** | 2174 → 4591 | OK |
| 39 | `vce-1570` | **written** | 1672 → 3842 | OK |
| 40 | `vce-3500` | **written** | 2321 → 2905 | OK [ghost replaced] |
| 41 | `vce-4000` | **written** | 3919 → 7155 | OK [ghost replaced] |
| 42 | `vk-420-v-cutting-90-end-notching-machine` | **written** | 3359 → 6074 | OK |
| 43 | `wgm-202` | **written** | 2018 → 4074 | OK |

## Backup Dosyaları

- `ack-420-s-up-cutting-saw-machine.json.bak`
- `aim-4420.json.bak`
- `aim-7420.json.bak`
- `ca-603-pvc-corner-cleaning-machine-4-6-cutters.json.bak`
- `ccl-1661-pvc-corner-cleaning-machine.json.bak`
- `cnc-609.json.bak`
- `cnc-611.json.bak`
- `crm-201-s-template-copy-router-machine-with-triple-hole-water-slot-drilling.json.bak`
- `crm-250-s-template-copy-router-machine.json.bak`
- `dc-421-psd-double-head-mitre-saw-machine-full-automatic.json.bak`
- `dc-550-pb-double-head-mitre-saw-machines.json.bak`
- `dc-550-skh-double-head-mitre-saw-machine-full-automatic.json.bak`
- `dkn-300-450-600-302-452-602-roller-conveyor-with-manual-stop-display-unit.json.bak`
- `fr-223-fr-223s-portable-template-copy-router.json.bak`
- `fr-226-s-automatic-copy-router-machine.json.bak`
- `gas-301.json.bak`
- `kd-350-d-miter-saw-machine.json.bak`
- `kd-350-m-miter-saw-machine.json.bak`
- `kd-400-d-miter-saw-machine.json.bak`
- `kd-400-m-mitre-saw-machine.json.bak`
- `km-215-s-semi-automatic-end-milling-machine.json.bak`
- `mca-801.json.bak`
- `mk-420-mk-420ps-mk-450-manual-up-cutting-saw-machine.json.bak`
- `mkn-serisi-150-300-301.json.bak`
- `nsm-352-nsm-353-kanat-isleme-merkezi.json.bak`
- `pim-6508-se.json.bak`
- `pwb-4100.json.bak`
- `pye-101-pye-102-pye-103-pye-104-manual-punch-press.json.bak`
- `rs-1000.json.bak`
- `ryk-420-w-radial-saw-machine.json.bak`
- `scm-420-l4-scm-420-l7-servo-controlled-serial-cutting-machine.json.bak`
- `sdt-275.json.bak`
- `sk-500-d-automatic-sawing-and-drilling-machine.json.bak`
- `skn-300-450-600-digital-roller-conveyor-with-automatic-length-stop.json.bak`
- `sm-201-sd.json.bak`
- `st-264-pvc-automatic-water-slot-machine.json.bak`
- `tk-503-pvc-tek-kose-kaynak-makinesi.json.bak`
- `vce-1570.json.bak`
- `vce-3500.json.bak`
- `vce-4000.json.bak`
- `vk-420-v-cutting-90-end-notching-machine.json.bak`
- `wgm-202.json.bak`

---
*Generated by `tools/recover_yilmaz_bg.py` — 2026-05-23 19:31:31*
