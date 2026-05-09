# S8 Professor - Weekly Spor Toto Prediction App

## Project
- **Name:** S8 Professor
- **Type:** Sports prediction app (Spor Toto weekly matches)
- **Repo:** https://github.com/v-s-p/s8-professor-app
- **Branch:** chore/eas-build-pipeline

## Architecture
**Backend (Express + Supabase)**
- Every Friday: Admin endpoint triggers
- Fetches 15 matches from Spor Toto official API
- Generates AI analysis per match using Gemini 2.5 Flash
- Saves predictions to Supabase

**Mobile (React Native / Expo)**
- User reads data from Supabase
- No backend running on device

## Business Model
- **Free:** First 3 match analyses + 3-match coupon
- **Premium:** 15 match analyses + 3-4 combined coupons (RevenueCat)

## Status
- Backend: ✅ DONE (Gemini integration complete)
- Mobile: ⏳ TO START (React Native/Expo next)

## Dev Commands
```bash
# Backend start
cd apps/backend && npm run dev

# Admin endpoint test
Invoke-WebRequest -Uri "http://localhost:4000/v1/admin/process-weekly-toto" -Method POST -Headers @{"X-Admin-Secret"="H9bIduYyNLUZK1Q2R4VtaAWSnJgCTqc8"}

# Check predictions
Invoke-WebRequest -Uri "http://localhost:4000/v1/predictions/latest"

# Git push
git add . && git commit -m "msg" && git push
```

## Notes
- DEVLOG.md = Session continuity (read at start, update at end)
- Persist this file during compacting

## 🤖 Claude Code Master Directives
**Purpose:** Fast autonomous work, minimal questions, sensible defaults.

### Decision Rules
- **Default to YES** unless safety-critical
- Ask ONLY if truly blocking
- Use project patterns/conventions (no custom reinventions)
- Move fast, iterate on feedback

### Code Style
- TypeScript over JavaScript
- Expo/React Native (mobile-first)
- Express.js (backend)
- Consistent with existing codebase

### Git Workflow
- Feature branches (feat/*, fix/*, chore/*)
- Meaningful commit messages
- PRs for major changes
- `/devlog` at session end

### Automation Rules
- If task is routine: proceed autonomously
- If task is exploratory: ask 1 clarifying question max
- If ambiguous: pick most common pattern from codebase
- When in doubt: reference existing similar code

### DO NOT ASK
- "Should I use X or Y?" → Use Y if it's in codebase
- "Is this design okay?" → Match existing patterns
- "Should I add comments?" → Add if complex, sparse otherwise
- "Commit now?" → Yes, after each logical chunk

### JUST DO IT

---

## DEVLOG System ✅ Automation ready
- Run `/devlog` at the end of every session to auto-generate + commit an entry
- See `.claude/DEVLOG-GUIDE.md` for full usage and examples
- Command definition: `.claude/commands/devlog.md`

---

## 📚 WIKI AGENT — HAFIZA YÖNETİMİ

### Görev
`/docs/wiki` klasörü bu projenin derlenmiş hafızasıdır.
Kodu değiştirme. Sadece analiz et ve wiki'ye yaz.

### TARAMA DIŞI TUTULACAKLAR (INGEST'te kesinlikle atla)
- `node_modules/`, `dist/`, `build/`, `.expo/`, `.git/`
- `*.lock` dosyaları (`package-lock.json`, `yarn.lock`)
- `*.config.js/ts` (babel, metro, jest) — sadece gerekirse oku
- Test dosyaları (`*.test.ts`, `*.spec.ts`) — ayrı node olarak işle

### OPERASYON: INGEST
Tetikleyici: "Wiki INGEST yap" komutu

1. Şu klasörleri tara: `apps/backend/src/`, `apps/mobile/src/` ve root `package.json`
2. Her modül/servis için `/docs/wiki/` altında ayrı `.md` dosyası oluştur
3. Her dosya formatı ZORUNLU:

\`\`\`
# ModulAdı

## Özet
(Max 3 cümle — ne yapar, neden var, nereye bağlı)

## Teknolojiler
- (Supabase, Gemini, Express vs.)

## Bağlantılar
- [[Index]] | [[İlgili_Modül]] | [[Diğer_Modül]]

## Son Değişiklik
(Git log'dan al veya "INGEST tarihinde oluşturuldu" yaz)
\`\`\`

4. **Node adlandırma kuralı:** Her modül için TEK canonical isim seç. Class adı dosya/modül adından farklıysa (örn: class `SupabaseUserRepository` → file `userStore.ts`), tüm referanslar canonical adla yapılmalı. Bu, VERIFY adımında link kırılmasını engeller.
5. Her INGEST sonrası `[[Index.md]]`'yi güncelle — tüm node'ları listele
6. INGEST tamamlanınca **otomatik VERIFY çalıştır**
7. INGEST + VERIFY tamamlanınca DEVLOG.md'ye tek satır not düş: `[tarih] Wiki INGEST tamamlandı — N node, M tutarsızlık düzeltildi`

### OPERASYON: QUERY
Tetikleyici: Session başı veya "Wiki'den bak" komutu

1. ÖNCE `DEVLOG.md` oku (son session özeti)
2. SONRA `/docs/wiki/Index.md` oku
3. İlgili 2-3 wiki dosyasını oku
4. Ancak bunlar yetersizse kod taramasına gir
5. Kodu taramak yerine wiki'den cevapla — daha hızlı, daha az token

### OPERASYON: UPDATE
Tetikleyici: Yeni özellik eklendikten sonra

1. Sadece değişen modüllerin wiki dosyasını güncelle
2. Index.md'yi kontrol et, yeni node varsa ekle
3. `[[bağlantı]]` tutarlılığını koru
4. UPDATE sonrası **VERIFY çalıştır**
5. DEVLOG.md'ye not düş: `[tarih] Wiki UPDATE — hangi node'lar güncellendi`

### OPERASYON: VERIFY
Tetikleyici: INGEST/UPDATE sonrası otomatik veya "Wiki VERIFY" komutu

1. Her node için kod tarafında karşılığı var mı kontrol et
2. Class/factory adı ile node adı uyuşuyor mu? (örn: `SupabaseUserRepository` class'ı → `UserStore` node'una map'lenmiş olabilir, referanslar tek canonical adla olmalı)
3. Bir node X başka bir Y'ye link veriyorsa, Y'de de X'e backlink olmalı (çift yönlü simetri)
4. **Düzeltme politikası:**
   - **Küçük düzeltmeler** (link adı, eksik backlink, yanlış referans) → otomatik yap ve raporla
   - **Yapısal değişiklikler** (node ekle/sil, birleştir/böl) → öner, onay bekle
5. VERIFY tamamlanınca DEVLOG.md'ye not düş: `[tarih] Wiki VERIFY — N tutarsızlık bulundu, M otomatik düzeltildi, K onay bekliyor`
