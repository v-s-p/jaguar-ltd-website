# Yedek Inject Raporu

**Tarih:** 2026-05-24 14:10:27  
**Mod:** `apply`  
**Kaynak:** `yilmaz_yedek.json` (90 makine)  
**Hedef:** `src/data/machines/yilmaz/` (88 makine)  
**Süre:** 0.1s

## Özet

| Metrik | Değer |
|---|---|
| Hedef makine | 88 |
| RU inject yapıldı | **88** |
| EN description inject yapıldı | **2** |
| Mismatch (yedekte yok) | 0 |
| Ambiguous match | 1 |
| Hata | 0 |
| Spec key rename ('STANDART ACCESORIES' vb.) | 86 dosyada |
| Yazılan dosya | **88** |
| Backup (.bak) | 88 |
| **DURUM** | ✅ **TAMAMLANDI** |

## EN Description Inject Listesi (Partial Makineler)

| Slug | Önce (chr) | Sonra (chr) | Kaynak |
|---|---|---|---|
| `aim-4420` | 0 chr | 887 chr | yedek EN aciklama |
| `aim-7420` | 0 chr | 887 chr | yedek EN aciklama |

## Spec Key Rename Özeti

| Yedek key | → | Normalize edilen key | Adet |
|---|---|---|---|
| `STANDART ACCESORIES` | → | `STANDARD ACCESSORIES` | (bkz. sayı yukarıda) |
| `OPTIONAL ACCESORIES` | → | `OPTIONAL ACCESSORIES` | |
| RU `GENERAL FEATURES` | → | `ОБЩИЕ ХАРАКТЕРИСТИКИ` | (Karar B) |

## Technical_data Key Dönüşümü (piktogramlar → technical_data)

| TR key (yedek) | → | EN key (inject) |
|---|---|---|
| `elektrik` | → | `Power` |
| `matkap_donus_hizi` | → | `Drill Rotation Speed` |
| `donus_hizi` | → | `Saw Rotation Speed` |
| `cap` | → | `Saw Diameter` |
| `debi` | → | `Flow Rate` |
| `basinc` | → | `Pressure` |
| `boyutlar` | → | `Dimensions (cm)` |
| `urun_agirligi` | → | `Weight` |
| `kesme_hizi` | → | `Cutting Speed` |
| `motor_gucu` | → | `Motor Power` |
| `devir` | → | `Rotation Speed` |
| `voltaj` | → | `Voltage` |
| `frekans` | → | `Frequency` |
| `hava_tuketimi` | → | `Air Consumption` |
| `kesim_acisi` | → | `Cutting Angle` |
| `min_kesim_acisi` | → | `Min Cutting Angle` |
| `max_kesim_acisi` | → | `Max Cutting Angle` |
| `is_uzunlugu` | → | `Working Length` |
| `kapasite` | → | `Capacity` |
| `pnomatik_basinc` | → | `Pneumatic Pressure` |
| `kesim_kapasitesi` | → | `Cutting Capacity` |
| `mil_hizi` | → | `Spindle Speed` |
| `tabla_boyutu` | → | `Table Dimensions` |
| `min_profil_boyu` | → | `Min Profile Length` |
| `max_profil_boyu` | → | `Max Profile Length` |
| `step_motor` | → | `Step Motor` |
| `kesici_sayisi` | → | `Number of Cutters` |
| `kaynak_gucu` | → | `Welding Power` |
| `sicaklik` | → | `Temperature` |
| `piston_kuvveti` | → | `Piston Force` |
| `profil_genisligi` | → | `Profile Width` |
| `profil_yuksekligi` | → | `Profile Height` |
| `freze_alani` | → | `Milling Area` |
| `kose_pres` | → | `Corner Press Force` |
| `profil` | → | `Profile` |

## Ambiguous Match (İlk Aday Seçildi)

| Current slug | Seçilen yedek slug |
|---|---|
| `sm-201-single-head-reinforcement-stell-screwdriver` | `sm-201-sd` |

## Makine Detay Tablosu

| # | Slug | Match | RU | EN partial | Bytes | Not |
|---|---|---|---|---|---|---|
| 1 | `ack-420-s-up-cutting-saw-machine` | exact | ✅ | — | 6515→9957 | bak=ack-420-s-up-cutting-saw-machine.json.bak.2 |
| 2 | `ack-550-up-cutting-saw-machine` | code-only | ✅ | — | 5777→9328 | bak=ack-550-up-cutting-saw-machine.json.bak.2 |
| 3 | `ack-700-up-cutting-saw-machine` | code-only | ✅ | — | 5823→9403 | bak=ack-700-up-cutting-saw-machine.json.bak.2 |
| 4 | `aim-3410-aluminium-profile-machining-center` | exact | ✅ | — | 10820→10955 | bak=aim-3410-aluminium-profile-machining-center.json.bak.2 |
| 5 | `aim-4420` | exact | ✅ | +887chr | 8911→16037 | bak=aim-4420.json.bak.2 |
| 6 | `aim-7420` | exact | ✅ | +887chr | 9534→16779 | bak=aim-7420.json.bak.2 |
| 7 | `aim-7510-aluminium-profile-processing-centers` | exact | ✅ | — | 11562→18524 | bak=aim-7510-aluminium-profile-processing-centers.json.bak.3 |
| 8 | `ca-601-semi-automatic-pvc-single-corner-cleaning-machine` | exact | ✅ | — | 5946→9193 | bak=ca-601-semi-automatic-pvc-single-corner-cleaning-machine.json.bak.2 |
| 9 | `ca-603-pvc-corner-cleaning-machine-4-6-cutters` | exact | ✅ | — | 5270→8333 | bak=ca-603-pvc-corner-cleaning-machine-4-6-cutters.json.bak.2 |
| 10 | `ccl-1661-pvc-corner-cleaning-machine` | exact | ✅ | — | 9269→14912 | bak=ccl-1661-pvc-corner-cleaning-machine.json.bak.2 |
| 11 | `cdc-600-compound-angle-double-head-saw-cutting-machine` | exact | ✅ | — | 8459→13677 | bak=cdc-600-compound-angle-double-head-saw-cutting-machine.json.bak.2 |
| 12 | `ck-412-pvc-glazing-bead-saw` | exact | ✅ | — | 4681→7422 | bak=ck-412-pvc-glazing-bead-saw.json.bak.2 |
| 13 | `cnc-609` | exact | ✅ | — | 6350→9834 | bak=cnc-609.json.bak.2 |
| 14 | `cnc-611` | exact | ✅ | — | 6367→10042 | bak=cnc-611.json.bak.2 |
| 15 | `cpm-4150-s` | exact | ✅ | — | 8158→13424 | bak=cpm-4150-s.json.bak.2 |
| 16 | `cpm-6161-double-station-composite-panel-processing-machine` | exact | ✅ | — | 10081→16498 | bak=cpm-6161-double-station-composite-panel-processing-machine.json.bak.2 |
| 17 | `crm-201-s-template-copy-router-machine-with-triple-hole-water-slot-drilling` | exact | ✅ | — | 7308→11430 | bak=crm-201-s-template-copy-router-machine-with-triple-hole-water-slot-drilling.json.bak.2 |
| 18 | `crm-250-s-template-copy-router-machine` | exact | ✅ | — | 6224→10005 | bak=crm-250-s-template-copy-router-machine.json.bak.2 |
| 19 | `dc-421-pbs-double-head-mitre-saw-machine-full-automatic` | exact | ✅ | — | 6363→10263 | bak=dc-421-pbs-double-head-mitre-saw-machine-full-automatic.json.bak.2 |
| 20 | `dc-421-psd-double-head-mitre-saw-machine-full-automatic` | exact | ✅ | — | 5993→9611 | bak=dc-421-psd-double-head-mitre-saw-machine-full-automatic.json.bak.2 |
| 21 | `dc-550-pb-double-head-mitre-saw-machines` | exact | ✅ | — | 7528→11737 | bak=dc-550-pb-double-head-mitre-saw-machines.json.bak.2 |
| 22 | `dc-550-skh-double-head-mitre-saw-machine-full-automatic` | exact | ✅ | — | 8851→13311 | bak=dc-550-skh-double-head-mitre-saw-machine-full-automatic.json.bak.2 |
| 23 | `dk-502-double-corner-pvc-welding-machine` | code-only | ✅ | — | 6090→9453 | bak=dk-502-double-corner-pvc-welding-machine.json.bak.2 |
| 24 | `dk-540-four-corner-pvc-welding-machine` | exact | ✅ | — | 5665→9104 | bak=dk-540-four-corner-pvc-welding-machine.json.bak.2 |
| 25 | `dkn-300-450-600-302-452-602-roller-conveyor-with-manual-stop-display-unit` | exact | ✅ | — | 3012→4591 | bak=dkn-300-450-600-302-452-602-roller-conveyor-with-manual-stop-display-unit.json.bak.2 |
| 26 | `fr-221-s-pneumatic-template-copy-router` | exact | ✅ | — | 4129→6584 | bak=fr-221-s-pneumatic-template-copy-router.json.bak.2 |
| 27 | `fr-222-portable-template-copy-router` | exact | ✅ | — | 3256→5113 | bak=fr-222-portable-template-copy-router.json.bak.2 |
| 28 | `fr-223-fr-223s-portable-template-copy-router` | exact | ✅ | — | 4705→7212 | bak=fr-223-fr-223s-portable-template-copy-router.json.bak.2 |
| 29 | `fr-226-s-automatic-copy-router-machine` | exact | ✅ | — | 4621→7343 | bak=fr-226-s-automatic-copy-router-machine.json.bak.2 |
| 30 | `gas-301` | exact | ✅ | — | 3181→4988 | bak=gas-301.json.bak.2 |
| 31 | `gpt-1000-glass-window-trolley` | code-only | ✅ | — | 2681→4196 | bak=gpt-1000-glass-window-trolley.json.bak.2 |
| 32 | `gt-1000-gasket-trolley` | exact | ✅ | — | 2111→3330 | bak=gt-1000-gasket-trolley.json.bak.2 |
| 33 | `hdl-400-hdl-700-servo-controlled-automatic-length-stops` | exact | ✅ | — | 5794→8850 | bak=hdl-400-hdl-700-servo-controlled-automatic-length-stops.json.bak.2 |
| 34 | `hp-1000-horizontal-profile-troley` | exact | ✅ | — | 2368→3705 | bak=hp-1000-horizontal-profile-troley.json.bak.2 |
| 35 | `kd-305-portable-miter-saw-machine` | exact | ✅ | — | 3152→4854 | bak=kd-305-portable-miter-saw-machine.json.bak.2 |
| 36 | `kd-350-d-miter-saw-machine` | exact | ✅ | — | 4588→6795 | bak=kd-350-d-miter-saw-machine.json.bak.2 |
| 37 | `kd-350-m-miter-saw-machine` | exact | ✅ | — | 3640→5379 | bak=kd-350-m-miter-saw-machine.json.bak.2 |
| 38 | `kd-350-p-miter-saw-machine` | exact | ✅ | — | 4232→6670 | bak=kd-350-p-miter-saw-machine.json.bak.2 |
| 39 | `kd-400-d-miter-saw-machine` | exact | ✅ | — | 5181→7647 | bak=kd-400-d-miter-saw-machine.json.bak.2 |
| 40 | `kd-400-m-mitre-saw-machine` | exact | ✅ | — | 3234→4994 | bak=kd-400-m-mitre-saw-machine.json.bak.2 |
| 41 | `kd-400-p-miter-saw-machine` | exact | ✅ | — | 4143→6518 | bak=kd-400-p-miter-saw-machine.json.bak.2 |
| 42 | `kd-402-s-double-mitre-saw-machine` | exact | ✅ | — | 6322→10013 | bak=kd-402-s-double-mitre-saw-machine.json.bak.2 |
| 43 | `km-211-manual-end-milling-machine` | exact | ✅ | — | 3719→5865 | bak=km-211-manual-end-milling-machine.json.bak.2 |
| 44 | `km-212-portable-end-milling-machine` | exact | ✅ | — | 3159→4913 | bak=km-212-portable-end-milling-machine.json.bak.2 |
| 45 | `km-215-s-semi-automatic-end-milling-machine` | exact | ✅ | — | 5636→8946 | bak=km-215-s-semi-automatic-end-milling-machine.json.bak.2 |
| 46 | `kp-110-pneumatic-aluminum-corner-crimping-machine` | exact | ✅ | — | 5269→8239 | bak=kp-110-pneumatic-aluminum-corner-crimping-machine.json.bak.2 |
| 47 | `kp-130-cnc-cnc-automatic-corner-crimping-machine` | exact | ✅ | — | 6452→6587 | bak=kp-130-cnc-cnc-automatic-corner-crimping-machine.json.bak.2 |
| 48 | `kp-180-hydraulic-aluminium-corner-crimping-machine` | exact | ✅ | — | 7748→11400 | bak=kp-180-hydraulic-aluminium-corner-crimping-machine.json.bak.2 |
| 49 | `ky-305-portable-miter-saw-machine` | exact | ✅ | — | 3142→4839 | bak=ky-305-portable-miter-saw-machine.json.bak.2 |
| 50 | `mca-801` | exact | ✅ | — | 4711→7259 | bak=mca-801.json.bak.2 |
| 51 | `mk-420-mk-420ps-mk-450-manual-up-cutting-saw-machine` | exact | ✅ | — | 6717→9872 | bak=mk-420-mk-420ps-mk-450-manual-up-cutting-saw-machine.json.bak.2 |
| 52 | `mkn-serisi-150-300-301` | exact | ✅ | — | 2687→3782 | bak=mkn-serisi-150-300-301.json.bak.2 |
| 53 | `ncr-300-4-axis-nc-controlled-router-machine` | exact | ✅ | — | 7532→11974 | bak=ncr-300-4-axis-nc-controlled-router-machine.json.bak.2 |
| 54 | `nsm-352-nsm-353-kanat-isleme-merkezi` | exact | ✅ | — | 2921→4162 | bak=nsm-352-nsm-353-kanat-isleme-merkezi.json.bak.2 |
| 55 | `pc-4000-profile-carry-cart` | exact | ✅ | — | 2211→3373 | bak=pc-4000-profile-carry-cart.json.bak.2 |
| 56 | `pim-6508-se` | exact | ✅ | — | 8698→13727 | bak=pim-6508-se.json.bak.2 |
| 57 | `pim-6509-pvc-profile-processing-center` | exact | ✅ | — | 9503→15452 | bak=pim-6509-pvc-profile-processing-center.json.bak.2 |
| 58 | `pt-1000-product-transportation-troley` | exact | ✅ | — | 2276→3475 | bak=pt-1000-product-transportation-troley.json.bak.2 |
| 59 | `pt-2000-product-transportation-trolley-two-sided` | exact | ✅ | — | 2502→3717 | bak=pt-2000-product-transportation-trolley-two-sided.json.bak.2 |
| 60 | `pwb-4100` | exact | ✅ | — | 3427→5215 | bak=pwb-4100.json.bak.2 |
| 61 | `pye-101-pye-102-pye-103-pye-104-manual-punch-press` | exact | ✅ | — | 3738→5299 | bak=pye-101-pye-102-pye-103-pye-104-manual-punch-press.json.bak.2 |
| 62 | `rs-1000` | exact | ✅ | — | 1827→2740 | bak=rs-1000.json.bak.2 |
| 63 | `rt-1000-rotating-table` | exact | ✅ | — | 2622→4108 | bak=rt-1000-rotating-table.json.bak.2 |
| 64 | `ryk-420-radial-saw-machine` | exact | ✅ | — | 5928→9442 | bak=ryk-420-radial-saw-machine.json.bak.2 |
| 65 | `ryk-420-w-radial-saw-machine` | exact | ✅ | — | 5750→9054 | bak=ryk-420-w-radial-saw-machine.json.bak.2 |
| 66 | `scm-420-l4-scm-420-l7-servo-controlled-serial-cutting-machine` | exact | ✅ | — | 8005→12128 | bak=scm-420-l4-scm-420-l7-servo-controlled-serial-cutting-machine.json.bak.2 |
| 67 | `sdt-275` | exact | ✅ | — | 2533→3982 | bak=sdt-275.json.bak.2 |
| 68 | `sdt-280-semi-automatic-multi-reinforcement-and-profile-cutting-machine` | exact | ✅ | — | 6547→9745 | bak=sdt-280-semi-automatic-multi-reinforcement-and-profile-cutting-machine.json.bak.2 |
| 69 | `sk-500-automatic-sawing-machine` | exact | ✅ | — | 7441→11809 | bak=sk-500-automatic-sawing-machine.json.bak.2 |
| 70 | `sk-500-d-automatic-sawing-and-drilling-machine` | exact | ✅ | — | 8724→14068 | bak=sk-500-d-automatic-sawing-and-drilling-machine.json.bak.2 |
| 71 | `skn-300-450-600-digital-roller-conveyor-with-automatic-length-stop` | exact | ✅ | — | 4175→6612 | bak=skn-300-450-600-digital-roller-conveyor-with-automatic-length-stop.json.bak.2 |
| 72 | `sm-201-sd` | exact | ✅ | — | 5597→8757 | bak=sm-201-sd.json.bak.2 |
| 73 | `sm-201-single-head-reinforcement-stell-screwdriver` | ambiguous | ✅ | — | 4814→7974 | bak=sm-201-single-head-reinforcement-stell-screwdriver.json.bak.2 |
| 74 | `sm-206-fully-automatic-double-head-reinforcement-steel-screwdriver` | code-only | ✅ | — | 6790→10164 | bak=sm-206-fully-automatic-double-head-reinforcement-steel-screwdriver.json.bak.2 |
| 75 | `snm-560-m-aluminium-facade-notching-machine-manual` | exact | ✅ | — | 6966→11174 | bak=snm-560-m-aluminium-facade-notching-machine-manual.json.bak.2 |
| 76 | `snm-560-srv-servo-controlled-aluminium-facade-notching-machine` | exact | ✅ | — | 6633→10524 | bak=snm-560-srv-servo-controlled-aluminium-facade-notching-machine.json.bak.2 |
| 77 | `st-264-pvc-automatic-water-slot-machine` | exact | ✅ | — | 4549→7110 | bak=st-264-pvc-automatic-water-slot-machine.json.bak.2 |
| 78 | `tk-503-pvc-tek-kose-kaynak-makinesi` | exact | ✅ | — | 4591→7316 | bak=tk-503-pvc-tek-kose-kaynak-makinesi.json.bak.2 |
| 79 | `tk-505-single-corner-pvc-welding-machine` | code-only | ✅ | — | 4362→7010 | bak=tk-505-single-corner-pvc-welding-machine.json.bak.2 |
| 80 | `vce-1570` | exact | ✅ | — | 3842→5954 | bak=vce-1570.json.bak.2 |
| 81 | `vce-3500` | exact | ✅ | — | 2905→2587 | bak=vce-3500.json.bak.2 |
| 82 | `vce-4000` | exact | ✅ | — | 7155→6837 | bak=vce-4000.json.bak.2 |
| 83 | `vk-420-v-cutting-90-end-notching-machine` | exact | ✅ | — | 6074→9172 | bak=vk-420-v-cutting-90-end-notching-machine.json.bak.2 |
| 84 | `vp-1000-vertica-profile-troley` | exact | ✅ | — | 2406→3792 | bak=vp-1000-vertica-profile-troley.json.bak.2 |
| 85 | `vp-2000-vertica-profile-troley` | exact | ✅ | — | 3048→4485 | bak=vp-2000-vertica-profile-troley.json.bak.2 |
| 86 | `was-1000-window-assembly-station` | exact | ✅ | — | 2369→3646 | bak=was-1000-window-assembly-station.json.bak.2 |
| 87 | `wb-4000-work-bench` | exact | ✅ | — | 3039→4898 | bak=wb-4000-work-bench.json.bak.2 |
| 88 | `wgm-202` | exact | ✅ | — | 4074→6129 | bak=wgm-202.json.bak.2 |

---
*Generated by `tools/inject_yilmaz_from_yedek.py` — 2026-05-24 14:10:27*
