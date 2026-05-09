import sys
import os
import json
import time
import requests
import urllib3
from pathlib import Path

# SSL Uyarılarını Kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_PER_RUN = 150  # Full run: gocmaksan (~44) + machines (~74) = ~118 eksik BG

# AYARLAR (GitHub Güvenliği İçin .env Dosyasından Okuma)
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                os.environ['GEMINI_API_KEY'] = line.strip().split('=', 1)[1]

API_KEY = os.environ.get("GEMINI_API_KEY")

def cevir(makine_adi, aciklama, hedef_dil):
    """Gemini API kullanarak teknik tercüme yapar."""
    dil_haritasi = {"bg": "Bulgarian", "tr": "Turkish"}
    hedef = dil_haritasi.get(hedef_dil, hedef_dil)

    prompt = f"""
Sen endüstriyel metal işleme makineleri konusunda uzman bir çevirmensin.
Aşağıdaki makine adını ve açıklamasını {hedef} diline teknik terimleri koruyarak estetik bir şekilde çevir.
Yanıtı sadece şu formatta ver (Tırnak kullanma, sadece metinleri bas):
ISIM: [çeviri]
ACIKLAMA: [çeviri]

MAKINE: {makine_adi}
ACIKLAMA: {aciklama}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        res = requests.post(url, json=payload, timeout=15, verify=False)
        resp_json = res.json()

        if "error" in resp_json:
            msg = resp_json['error'].get('message', '')
            print(f"❌ API Hatası: {msg}")
            if any(kw in msg.lower() for kw in ("quota", "exceeded", "limit: 0")):
                print("🛑 Quota tükendi — daha fazla istek atılmıyor, exit(0)")
                sys.exit(0)
            return None, None

        text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
        satirlar = [s for s in text.strip().split('\n') if s.strip()]
        y_isim = satirlar[0].replace('ISIM:', '').strip()
        y_aciklama = satirlar[1].replace('ACIKLAMA:', '').strip() if len(satirlar)>1 else ""
        time.sleep(6)  # gemini-2.5-flash free tier ~10 RPM → 6sn güvenli aralık
        return y_isim, y_aciklama
    except Exception as e:
        print(f"❌ Hata ({makine_adi} - {hedef_dil}): {e}")
        return None, None

def dosya_isl_yap(json_adi, kalan_limit):
    yol = Path(f"src/data/{json_adi}")
    if not yol.exists(): return kalan_limit
    print(f"\n🚀 {json_adi} isleniyor...")

    with open(yol, 'r', encoding='utf-8') as f:
        makineler = json.load(f)

    degisiklik = False
    neksik = 0
    basarili = 0
    hedef_diller = ["bg"] # Şimdilik sadece Bulgarca eksikleri tamamlıyoruz

    for m in makineler:
        if kalan_limit <= 0:
            break

        # Hangi JSON formatındayız bakalım (en mi var, tr mi?)
        ref = None
        if "en" in m["diller"] and m["diller"]["en"].get("name"):
            r = m["diller"]["en"]
            ref = {"isim": r.get("name"), "aciklama": r.get("description", ""), "images": r.get("images", [])}
        elif "tr" in m["diller"] and m["diller"]["tr"].get("isim"):
            r = m["diller"]["tr"]
            ref = {"isim": r.get("isim"), "aciklama": r.get("aciklama", ""), "images": r.get("resimler", [])}

        if not ref or not ref["isim"]: continue

        for d in hedef_diller:
            if kalan_limit <= 0:
                break
            d_obj = m["diller"].get(d, {})
            isim_var_mi = bool(d_obj.get("name") or d_obj.get("isim"))

            # Açıklaması veya ismi hiç yoksa çevir
            if not isim_var_mi or (not d_obj.get("description") and not d_obj.get("aciklama") and ref["aciklama"]):
                neksik += 1
                kalan_limit -= 1
                print(f"   🔄 Bulgarca çeviriye gönderildi: {ref['isim']} (Gemini düşünürken lütfen bekleyin...)")
                y_isim, y_aciklama = cevir(ref["isim"], ref["aciklama"], d)

                if y_isim:
                    basarili += 1
                    # Tüm şemayı uluslararası formata (name/description) uygun tut
                    m["diller"][d] = {
                        "name": y_isim,
                        "description": y_aciklama,
                        "images": ref.get("images", [])
                    }

                    # Eğer spesifikasyonlar (specs) varsa onları da taşı
                    if "en" in m["diller"] and "specs" in m["diller"]["en"]:
                        m["diller"][d]["specs"] = m["diller"]["en"]["specs"]

                    degisiklik = True
                else:
                    print(f"   ⚠️  API hatası — {ref['isim']} atlandı")

    if degisiklik:
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(makineler, f, ensure_ascii=False, indent=2)
        print(f"✅ {json_adi} güncellendi: {basarili}/{neksik} yeni BG çevirisi eklendi.")
    elif neksik == 0:
        print(f"🟢 {json_adi}: tüm makinelerin Bulgarcaları zaten mevcut.")
    else:
        print(f"⚠️  {json_adi}: {neksik} eksik BG vardı, {basarili} çevrildi, {neksik - basarili} BASARISIZ — API hatasi kontrol edilmeli.")

    return kalan_limit

if __name__ == "__main__":
    if not API_KEY or API_KEY == "BURAYA_GEMINI_API_KEY_GELECEK":
        print("\n================================")
        print("❗ DUR YOLCU!")
        print("LÜTFEN .env DOSYASINA GEMINI_API_KEY GİRİN veya ORTAM DEĞİŞKENİ OLARAK AYARLAYIN :)")
        print("https://aistudio.google.com/")
        print("================================\n")
        sys.exit(1)

    print("\n🌐 TERCÜME MERKEZİ AKTİF")
    kalan = MAX_PER_RUN
    kalan = dosya_isl_yap("gocmaksan.json", kalan)
    kalan = dosya_isl_yap("machines.json", kalan)
    print("\n🎉 Tüm işlemler bitti!")
