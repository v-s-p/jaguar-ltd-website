# NEXT

## Current State (2026-02-24)
- Repo: `https://github.com/v-s-p/s8-professor-app`
- Branch: `main`
- Branch protection aktif (PR + 1 review + required check: `build-and-check`)
- CI workflows eklendi:
  - `.github/workflows/ci.yml`
  - `.github/workflows/dependency-audit.yml`

## What Is Already Done
1. Monorepo scaffold (`apps/mobile`, `apps/backend`, `packages/shared`)
2. Security/compliance docs
3. Mobile shell app (Expo TS)
4. Backend skeleton (`/health`, `/v1/me/plan`, `/v1/analyze` mock)
5. Local install + build/typecheck + backend smoke test

## Next Implementation Steps
1. Backend JWT auth middleware ekle
2. Mock user store ile `plan` bilgisini auth user'a bagla
3. `POST /v1/analyze` endpointinde auth zorunlu yap
4. RevenueCat webhook endpoint iskeleti ekle
5. Mobile app'te login + token + `/me/plan` ve `/analyze` entegrasyonu

## Resume Commands (PowerShell)
```powershell
cd "C:\Users\Kenan\Desktop\S8 Professor"
git pull
```

Node PATH sorunu olursa:
```powershell
$env:Path='C:\Program Files\nodejs;'+$env:Path
```

Run backend:
```powershell
npm run build:backend
node apps/backend/dist/server.js
```

Run mobile:
```powershell
npm run dev:mobile
```

## Notes
- Private repo'da kal.
- Prompt/AI key asla mobile client'a koyma.
- Free vs Premium kontrolu sadece backend'de enforce edilmeli.
