from google import genai
import sys
import os

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Hata: GEMINI_API_KEY ortam değişkeni bulunamadı.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

def otonom_mudahale(dosya_yolu, talimat):
    print(f"[*] Hedef: {dosya_yolu}")
    print(f"[*] Talimat: {talimat}")
    
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            mevcut_kod = f.read()
    except FileNotFoundError:
        print(f"Hata: {dosya_yolu} bulunamadı!")
        return
    
    # ✅ Token tasarrufu: Dosya boyutu 50KB üstüyse warning ver
    if len(mevcut_kod) > 50000:
        print(f"⚠️ Warning: Dosya {len(mevcut_kod)} bytes. Token maliyeti yüksek olabilir.")
    
    prompt = f"""Sen rasyonel bir yazılımcısın. Bu koda sadece şu talimatı uygula: "{talimat}"
Çıktı: SADECE güncellenmiş kod. Markdown yok, açıklama yok, "İşte kodunuz" yok.
KOD:
{mevcut_kod}"""
    
    print("[*] Gemini çalışıyor...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # ✅ Markdown cleanup improved
        yeni_kod = response.text
        for marker in ["```astro\n", "```typescript\n", "```javascript\n", "```html\n", "```python\n", "```\n"]:
            yeni_kod = yeni_kod.replace(marker, "")
        yeni_kod = yeni_kod.strip()
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(yeni_kod)
        
        print("[+] Başarılı! Dosya güncellendi.")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python ajan.py <dosya_yolu> <talimat>")
        sys.exit(1)
    
    otonom_mudahale(sys.argv[1], sys.argv[2])