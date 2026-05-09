#!/usr/bin/env python3
"""
Jaguar Tercüme Test Scripti
Sadece ilk 5 makiney i Bulgarcaya tercüme etmek için.
Gemini 1.5 Flash kullanır (hızlı + ucuz).
"""

import json
import os
import sys
from pathlib import Path
import google.generativeai as genai

# ============================================================================
# 1. API SETUP
# ============================================================================

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ HATA: GEMINI_API_KEY ortam değişkeni bulunamadı!")
    print("   Linux/Mac: export GEMINI_API_KEY='your-key-here'")
    print("   Windows:   $env:GEMINI_API_KEY='your-key-here'")
    sys.exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ============================================================================
# 2. TERCÜME FONKSİYONU (Gemini Flash ile)
# ============================================================================

def tercume_et(makine_adi, aciklama):
    """
    Makine adı + açıklaması Bulgarcaya çevirir.
    Teknik terminolojiyi korur.
    """
    
    prompt = f"""Sen endüstriyel metal işleme makineleri konusunda uzman bir çevirmensin.
Aşağıdaki makine adını ve açıklamasını Bulgarcaya çevir.
Teknik terimleri koruyarak doğru bir şekilde çevir.

Yanıtı ŞU FORMATta ver (tırnak yok, sadece metinler):
ISIM: [Bulgarca tercüme]
ACIKLAMA: [Bulgarca tercüme]

MAKINE: {makine_adi}
ACIKLAMA: {aciklama}
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Parse yanıt
        satirlar = [s.strip() for s in text.split('\n') if s.strip()]
        
        isim = ""
        aciklama_ceviri = ""
        
        for satir in satirlar:
            if satir.startswith("ISIM:"):
                isim = satir.replace("ISIM:", "").strip()
            elif satir.startswith("ACIKLAMA:"):
                aciklama_ceviri = satir.replace("ACIKLAMA:", "").strip()
        
        if not isim:
            print(f"   ⚠️  Parse hatası: {text[:100]}")
            return None, None
        
        return isim, aciklama_ceviri
        
    except Exception as e:
        print(f"   ❌ Gemini Hatası: {e}")
        return None, None

# ============================================================================
# 3. TEST LOJİK (İlk 5 makine)
# ============================================================================

def test_yap():
    """
    machines.json yükle, ilk 5 makineyi tercüme et, çıktı göster.
    """
    
    json_yolu = Path("src/data/machines.json")
    
    if not json_yolu.exists():
        print(f"❌ HATA: {json_yolu} bulunamadı!")
        print(f"   Lütfen Jaguar-ltd klasöründe çalışan olduğundan emin ol.")
        sys.exit(1)
    
    # JSON yükle
    with open(json_yolu, 'r', encoding='utf-8') as f:
        makineler = json.load(f)
    
    print(f"✅ {len(makineler)} makine yüklendi. İlk 5'i test edilecek.\n")
    
    test_makineler = makineler[:5]  # İlk 5
    basarili = 0
    basarisiz = 0
    
    for idx, m in enumerate(test_makineler, 1):
        slug = m.get("slug", "unknown")
        
        # İngilizceden çek
        en_data = m.get("diller", {}).get("en", {})
        isim_en = en_data.get("name", "")
        aciklama_en = en_data.get("description", "")
        
        if not isim_en or not aciklama_en:
            print(f"{idx}. {slug}")
            print(f"   ⚠️  İngilizce veri eksik. Skip.\n")
            continue
        
        print(f"{idx}. {slug}")
        print(f"   EN: {isim_en[:50]}...")
        
        # Tercüme et
        isim_bg, aciklama_bg = tercume_et(isim_en, aciklama_en)
        
        if isim_bg and aciklama_bg:
            print(f"   ✅ BG: {isim_bg[:50]}...")
            print(f"   Açıklama: {aciklama_bg[:60]}...\n")
            basarili += 1
            
            # Çıktıya kaydet (opsiyonel)
            m["diller"]["bg"] = {
                "name": isim_bg,
                "description": aciklama_bg,
                "images": en_data.get("images", [])
            }
        else:
            print(f"   ❌ Tercüme başarısız\n")
            basarisiz += 1
    
    # ============================================================================
    # 4. SONUÇ & KAYDET
    # ============================================================================
    
    print("=" * 60)
    print(f"📊 TEST SONUCU:")
    print(f"   ✅ Başarılı: {basarili}")
    print(f"   ❌ Başarısız: {basarisiz}")
    print(f"   💰 Tahmini maliyet: ~$0.001-0.005 (5 makine)")
    
    # Opsiyonel: test sonuçlarını kaydet
    output_path = Path("tercume_test_sonuc.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(makineler[:5], f, ensure_ascii=False, indent=2)
    
    print(f"   📁 Sonuçlar kaydedildi: {output_path}\n")
    
    return basarili, basarisiz

# ============================================================================
# ÇALIŞTIR
# ============================================================================

if __name__ == "__main__":
    print("🚀 JAGUAR TERCÜME TEST (İlk 5 Makine, Gemini Flash)\n")
    
    success, failed = test_yap()
    
    if success > 0:
        print("✅ Test başarılı! Full çalıştırma için tercume_merkezi.py kullanabilirsin.")
    else:
        print("❌ Test başarısız. API key'i ve ağ bağlantısını kontrol et.")
