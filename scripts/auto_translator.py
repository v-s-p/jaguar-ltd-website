import os
import json
import time

STATUS_FILE = "translation_status.json"
DATA_FILES = ["src/data/machines.json", "src/data/gocmaksan.json"]
LANGUAGES = ["en", "tr", "ru", "es", "ro", "bcs"] # bg is default

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_items": []}

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def translate_item(item, lang):
    # Mock translation function to simulate API call
    # Replace with actual API integration (e.g., Google Translate, Gemini)
    time.sleep(0.1) # Simulate network delay
    return {"status": "success", "data": {"translated": True}}

def main():
    print("Otonom Çeviri Betiği Başlatıldı...")
    status = load_status()
    completed_items = set(status["completed_items"])
    
    try:
        for file_path in DATA_FILES:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for idx, item in enumerate(data):
                item_id = item.get("slug", str(idx))
                
                for lang in LANGUAGES:
                    task_id = f"{file_path}_{item_id}_{lang}"
                    if task_id in completed_items:
                        continue
                        
                    print(f"Çevriliyor: {task_id}")
                    # API Call Simulation
                    response = translate_item(item, lang)
                    
                    if response.get("error") == "RATE_LIMIT" or response.get("status") == 429:
                        print("API Limiti aşıldı, durum kaydedildi.")
                        save_status(status)
                        return
                    
                    if response.get("status") == "success":
                        status["completed_items"].append(task_id)
                        completed_items.add(task_id)
                        # Here you would actually update the data object
                        # and write back to the JSON file
            
            # Save progress after each file
            save_status(status)
            
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
        print("Mevcut durum güvenle kaydediliyor...")
        save_status(status)
        
    print("Çeviri işlemi tamamlandı veya durduruldu.")

if __name__ == "__main__":
    main()
