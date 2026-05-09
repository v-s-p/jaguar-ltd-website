# Session Notes - 2026-02-24

## Context
Bu not, VS Code sohbeti kaybolsa bile proje baglamini korumak icin olusturuldu.

## Decisions
1. Tek monorepo ile iOS + Android yonetimi
2. Mobile app kabuk, tum kritik mantik backendde
3. Freemium/Premium yetkilendirme server-side enforce
4. Repo private kalacak
5. Branch protection aktif olacak (PR + check zorunlu)

## Completed Work
1. Repo olusturuldu: `v-s-p/s8-professor-app` (private)
2. Monorepo iskeleti olusturuldu
3. Security/compliance dokumanlari eklendi
4. CI workflowlari eklendi
5. `main` branch protection aktif edildi
6. `NEXT.md` eklendi (resume guide)

## Technical Notes
- Node/NPM mevcut ama PATH sorunu olabilir.
- Gerekirse PowerShell'de gecici PATH:
  - `$env:Path='C:\Program Files\nodejs;'+$env:Path`

## Active Branch / PR
- Branch: `docs/next-md-resume`
- PR: `https://github.com/v-s-p/s8-professor-app/pull/1`

## Next Focus
1. Backend JWT auth middleware
2. Plan bazli endpoint korumasi (`/v1/me/plan`, `/v1/analyze`)
3. RevenueCat webhook iskeleti
4. Mobile login + token + backend entegrasyonu
