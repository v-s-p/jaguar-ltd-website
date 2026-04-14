import requests
from bs4 import BeautifulSoup

url = "https://www.yilmazmachine.com.tr/urunler/aim-7420/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

print("Hedefe teknik radar atışı yapılıyor...")
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.content, 'html.parser')

print("\n--- SAYFADAKİ TÜM BAŞLIKLAR (h2, h3, h4) ---")
for tag in soup.find_all(['h2', 'h3', 'h4']):
    print(f"<{tag.name} class='{tag.get('class', [])}'> {tag.text.strip()}")

print("\n--- SAYFADAKİ LİSTELER (ul, ol) Sınıfları ---")
for lst in soup.find_all(['ul', 'ol']):
    print(f"<{lst.name} class='{lst.get('class', [])}'>")

print("\n--- SAYFADAKİ AÇIKLAMA PARAGRAFLARI (p) Sınıfları ---")
p_etiketleri = soup.find_all('p')
for p in p_etiketleri[:10]: # Sadece ilk 10'unu alalım kalabalık yapmasın
    if p.text.strip():
        print(f"<p class='{p.get('class', [])}'> {p.text.strip()[:50]}...")