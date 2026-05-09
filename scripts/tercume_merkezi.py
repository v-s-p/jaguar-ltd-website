import sys
import os
import json
import time
import requests
import urllib3
from pathlib import Path

# SSL Uyarılarını Kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        res = requests.post(url, json=payload, timeout=15, verify=False)
        resp_json = res.json()
        
        if "error" in resp_json:
            print(f"❌ API Hatası: {resp_json['error']['message']}")
            return None, None
            
        text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
        satirlar = [s for s in text.strip().split('\n') if s.strip()]
        y_isim = satirlar[0].replace('ISIM:', '').strip()
        y_aciklama = satirlar[1].replace('ACIKLAMA:', '').strip() if len(satirlar)>1 else ""
        return y_isim, y_aciklama
    except Exception as e:
        print(f"❌ Hata ({makine_adi} - {hedef_dil}): {e}")
        return None, None

def dosya_isl_yap(json_adi):
    yol = Path(f"src/data/{json_adi}")
    if not yol.exists(): return
    print(f"\n🚀 {json_adi} isleniyor...")
    
    with open(yol, 'r', encoding='utf-8') as f:
        makineler = json.load(f)

    degisiklik = False
    hedef_diller = ["bg"] # Şimdilik sadece Bulgarca eksikleri tamamlıyoruz

    for m in makineler:
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
            d_obj = m["diller"].get(d, {})
            isim_var_mi = bool(d_obj.get("name") or d_obj.get("isim"))
            
            # Açıklaması veya ismi hiç yoksa çevir
            if not isim_var_mi or (not d_obj.get("description") and not d_obj.get("aciklama") and ref["aciklama"]):
                print(f"   🔄 Bulgarca çeviriye gönderildi: {ref['isim']} (Gemini düşünürken lütfen bekleyin...)")
                y_isim, y_aciklama = cevir(ref["isim"], ref["aciklama"], d)
                
                if y_isim:
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
                    time.sleep(4.5)

    if degisiklik:
        with open(yol, 'w', encoding='utf-8') as f:
            json.dump(makineler, f, ensure_ascii=False, indent=2)
        print(f"✅ {json_adi} başarıyla güncellendi! Çeviriler eklendi.")
    else:
        print(f"🟢 {json_adi} dosyasındaki tüm makinelerin Bulgarcaları mevcut.")

if __name__ == "__main__":
    if not API_KEY or API_KEY == "BURAYA_GEMINI_API_KEY_GELECEK":
        print("\n================================")
        print("❗ DUR YOLCU!")
        print("LÜTFEN .env DOSYASINA GEMINI_API_KEY GİRİN veya ORTAM DEĞİŞKENİ OLARAK AYARLAYIN :)")
        print("https://aistudio.google.com/")
        print("================================\n")
        sys.exit(1)
        
    print("\n🌐 TERCÜME MERKEZİ AKTİF")
    dosya_isl_yap("gocmaksan.json")
    dosya_isl_yap("machines.json")
    print("\n🎉 Tüm işlemler bitti!")