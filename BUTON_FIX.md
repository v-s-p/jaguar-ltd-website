# FİLTRE BUTON TASARIM TUTARSIZLIĞI — FİX TALİMATI

## SORUN
Kategori sayfalarındaki filtre butonları tutarsız görünüyor:
- Pasif buton: beyaz bg, gri yazı ✅
- Aktif buton (ALU/PVC): turkuaz bg ama yazı da beyaz oluyor — kayboluyor ❌
- Göçmaksan butonları daha küçük font, farklı padding ❌
- Boyut/font/padding/renk tutarsız ❌

## HEDEF TASARIM (Göçmaksan baz alınsın, tüm kategorilere uygulansın)

### Pasif buton:
- bg: white
- border: 1px solid #e5e7eb (gray-200)
- text: #6b7280 (gray-500)
- font: font-semibold (600)
- padding: px-4 py-2
- border-radius: rounded-full
- font-size: text-sm
- hover: border-[#00A8B5], text-[#00A8B5]

### Aktif buton:
- bg: #00A8B5 (turkuaz)
- border: border-[#00A8B5]
- text: WHITE (#ffffff) — ALU/PVC için
- text: #1a1a1a (koyu) — Göçmaksan için (turuncu tema)
- font: font-bold (700)
- padding: px-4 py-2
- border-radius: rounded-full

## DÜZELTME YAPILACAK DOSYA
`src/components/pages/KategoriPage.astro`

## YAPILACAK DEĞİŞİKLİK

### 1. HTML — Buton class'larını düzelt:

**"Виж всички / Всички" butonu (başlangıç aktif):**
```html
<button
  class="filter-btn font-bold px-4 py-2 rounded-full text-sm border transition-all duration-200 text-white border-[#00A8B5]"
  style="background:#00A8B5"
  data-filter="all">
  {t('btn.viewall')} / Всички
</button>
```

**Alt kategori butonları (başlangıç pasif):**
```html
<button
  class="filter-btn bg-white text-gray-500 border border-gray-200 font-semibold px-4 py-2 rounded-full text-sm hover:border-[#00A8B5] hover:text-[#00A8B5] transition-all duration-200"
  data-filter={sub.id}>
  {sub.label}
</button>
```

### 2. JavaScript — applyFilter fonksiyonunu düzelt:

Mevcut `applyFilter` fonksiyonu class replace ile çalışıyor ama güvenilmez.
Tüm style/class manipülasyonunu şu şekilde yaz:

```javascript
const applyFilter = (val) => {
  buttons.forEach(b => {
    const isActive = b.getAttribute('data-filter') === val;
    if (isActive) {
      b.style.background = '#00A8B5';
      b.style.color = 'white';
      b.style.borderColor = '#00A8B5';
      b.classList.remove('bg-white', 'text-gray-500', 'border-gray-200');
    } else {
      b.style.background = 'white';
      b.style.color = '#6b7280';
      b.style.borderColor = '#e5e7eb';
      b.classList.remove('text-white');
    }
  });

  let visible = 0;
  cards.forEach(card => {
    const s = card.getAttribute('data-subcategories') || '';
    const show = val === 'all' || s === val || s.includes(val);
    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  if (empty) empty.style.display = visible === 0 ? 'block' : 'none';
};
```

## TEST EDİLECEK SAYFALAR
1. http://localhost:4321/tr/kategori/aluminyum
   - "Виж всички" aktif → turkuaz bg, beyaz yazı ✓
   - "Рязане" aktif → turkuaz bg, beyaz yazı ✓
   - Pasif butonlar → beyaz bg, gri yazı ✓
   
2. http://localhost:4321/tr/kategori/pvc
   - Aynı kontrol ✓

3. http://localhost:4321/tr/kategori/gocmaksan
   - BENDING, CUTTING vs → aynı boyut ve stil ✓
   - Aktif buton → turkuaz bg, beyaz yazı ✓

## EKSTRA (isteğe bağlı iyileştirme)
Göçmaksan sayfasında başlık rengi turuncu (#f59e0b) olabilir, 
Yılmaz sayfalarında turkuaz (#00A8B5) kalır.
Bunu catName'e göre ayarla:
```
const accentColor = catName === 'Gocmaksan' ? '#f59e0b' : '#00A8B5';
```
