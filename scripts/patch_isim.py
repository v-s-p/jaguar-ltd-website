"""
Bu scripti bir kere calistir, guncelleyici'deki isim parse'ini duzeltir.
  python patch_isim.py
"""
from pathlib import Path
import re

f = Path(__file__).parent / "yilmaz_guncelleyici.py"
kod = f.read_text(encoding='utf-8')

ESKI = '''    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        isim = re.split(r'\\s*[-|]\\s*YILMAZ', t, flags=re.IGNORECASE)[0].strip()'''

YENI = '''    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        # "ACK 420 S - Up-Cutting Saw Machine | YILMAZ MACHINE" -> "ACK 420 S"
        # Once | veya YILMAZ'dan olanı kes
        t = re.split(r\\\'\\\\s*[|]\\\\s*YILMAZ|\\\\s*-\\\\s*YILMAZ\\\', t, flags=re.IGNORECASE)[0].strip()
        # Model kodu + numara kısmını al (aciklama kismini kes)
        # "ACK 420 S - Up-Cutting Saw..." -> "ACK 420 S"
        m_code = re.match(r\\\'^([A-Z]{2,6}[\\\\s\\\\d\\\\-]+?(?:[A-Z]{1,3})??)\\\\s*[-]\\\\s*[A-Za-z]\\\', t)
        if m_code:
            isim = m_code.group(1).strip().rstrip("-").strip()
        else:
            isim = t'''

# Daha guvenli: sadece aciklamali isimler icin post-process yapalim
# Script calistiginda isim zaten dogru geldiyse duzeltme gereksiz
# Basit yontem: " - " ile bolup ilk kismi al, ama sadece ikinci kisim kucukse

print("Patch atlanıyor - kullan: duzeltici.py ile sonradan isim duzelt")
print()
print("VEYA dogrudan machines.json'daki isimleri duzeltmek icin:")
print("  from scriptin sonuc JSON'u:")

import json
JSON = Path(__file__).parent.parent / "src" / "data" / "machines.json"
if JSON.exists():
    data = json.loads(JSON.read_text(encoding='utf-8'))
    duzeltilen = 0
    for m in data:
        isim = m["diller"]["tr"]["isim"]
        # "ACK 420 S - Up-Cutting Saw Machine" -> "ACK 420 S"
        if ' - ' in isim:
            kisimlar = isim.split(' - ')
            ilk = kisimlar[0].strip()
            # Ilk kisim model kodu gibi gorünüyorsa (rakam iceriyor)
            if re.match(r'^[A-Z]', ilk) and any(c.isdigit() for c in ilk):
                m["diller"]["tr"]["isim"] = ilk
                duzeltilen += 1
                print(f"  '{isim}' -> '{ilk}'")
    
    if duzeltilen:
        JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"\n[+] {duzeltilen} isim duzeltildi -> machines.json guncellendi")
    else:
        print("  Duzeltilecek isim bulunamadi (zaten temiz)")
