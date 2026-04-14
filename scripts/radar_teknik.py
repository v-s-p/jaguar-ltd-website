import requests
from bs4 import BeautifulSoup

url = "https://www.yilmazmachine.com.tr/urunler/aim-7420/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

print("Hedefe 'Teknik Özellikler' radarı atılıyor...")
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.content, 'html.parser')

print("\n--- TEKNİK VERİ BÖLÜMÜ HTML YAPISI ---\n")
# Sayfadaki "TEKNİK ÖZELLİKLER" başlığını buluyoruz
teknik_baslik = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'TEKNİK' in tag.text.upper())

if teknik_baslik:
    # Başlığın hemen altındaki veri bloğunu (tablo veya liste) buluyoruz
    kapsayici = teknik_baslik.find_next(['table', 'ul', 'div', 'p'])
    # HTML kodunun ilk 1500 karakterini ekrana basıyoruz ki yapıyı çözelim
    print(kapsayici.prettify()[:1500]) 
else:
    print("Makinede Teknik Özellikler başlığı bulunamadı. Farklı bir HTML yapısı var.")