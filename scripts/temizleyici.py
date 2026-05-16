import sys, io, json, hashlib
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_PATH    = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"
BLACKLIST_DIR = SCRIPT_DIR / "blacklist"

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def main():
    print("=== TEMIZLIK OPERASYONU ===")

    if not BLACKLIST_DIR.exists():
        print("[X] 'blacklist' klasoru bulunamadi!")
        return

    bad_hashes = set()
    for f in BLACKLIST_DIR.iterdir():
        if f.is_file():
            bad_hashes.add(get_file_hash(f))
    print(f"[i] Kara listede {len(bad_hashes)} parmak izi")

    # Disk'ten sil
    silinen = 0
    for img in IMG_DIR.iterdir():
        if img.is_file() and get_file_hash(img) in bad_hashes:
            img.unlink()
            silinen += 1
            print(f"  [-] Silindi: {img.name}")
    print(f"[+] {silinen} resim silindi")

    # JSON'dan temizle
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        machines = json.load(f)

    for m in machines:
        resimler = m['diller']['tr']['resimler']
        temiz = []
        for url in resimler:
            # Lokal yol mu? Disk'te var mı kontrol et
            if url.startswith('/images/'):
                dosya_adi = url.split('/')[-1]
                if (IMG_DIR / dosya_adi).exists():
                    temiz.append(url)
            else:
                # CDN URL - lokal degil, oldugu gibi birak
                temiz.append(url)
        m['diller']['tr']['resimler'] = temiz

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(machines, f, ensure_ascii=False, indent=2)

    print("[+] yilmaz.json guncellendi!")

if __name__ == "__main__":
    main()
