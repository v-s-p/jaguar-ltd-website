# S8 Professor Monorepo

AI destekli mac analizi urunu icin iOS + Android (tek kod tabani) ve guvenli backend monorepo yapisi.

## Current State
- Mobile: Expo SDK 54, auth + plan akisi calisiyor
- Backend: JWT auth, RevenueCat webhook, freemium/premium server-side enforce
- Storage: provider abstraction hazir (`memory` / `supabase`)

## Monorepo Yapisi
- `apps/mobile`: Expo React Native (iOS + Android)
- `apps/backend`: API, AI orchestration, entitlement
- `packages/shared`: ortak tipler, schema, utility
- `docs`: mimari, guvenlik, compliance, operasyon, planlama

## Cloud-Only Hedefi
- Mobil uygulama sadece cloud backend ile konusur
- Prompt, AI orkestrasyonu, kupon motoru ve plan kontrolu backendde kalir
- Mobilde secret bulunmaz

## Local Run
1. Backend:
   - `npm run build:backend`
   - `node apps/backend/dist/server.js`
2. Mobile:
   - `set EXPO_PUBLIC_API_BASE_URL`
   - `npm run dev:mobile -- --tunnel`

## Cloud Run
Detayli adimlar: `docs/operations/cloud-only-deploy.md`
Render icin hizli yol: `docs/operations/render-deploy.md`
Subscription + forgot-password go-live: `docs/operations/subscription-auth-go-live.md`
EAS mobile build pipeline: `docs/operations/eas-build-pipeline.md`

## Webhook Test (PowerShell)
RevenueCat webhookunu tek komutla smoke-test etmek icin:

```powershell
cd "C:\Users\Kenan\Desktop\S8 Professor"
.\scripts\test-webhook.ps1 `
  -BaseUrl "https://s8-professor-app.onrender.com" `
  -WebhookSecret "RENDER_ENV_REVENUECAT_WEBHOOK_SECRET" `
  -AppUserId "kullanici@email.com"
```

Not: Premium -> Free downgrade testi icin `-DowngradeToFree` ekleyebilirsin.

## Webhook Test (PowerShell)
RevenueCat webhookunu tek komutla smoke-test etmek icin:

```powershell
cd "C:\Users\Kenan\Desktop\S8 Professor"
.\scripts\test-webhook.ps1 `
  -BaseUrl "https://s8-professor-app.onrender.com" `
  -WebhookSecret "RENDER_ENV_REVENUECAT_WEBHOOK_SECRET" `
  -AppUserId "kullanici@email.com"
```

Not: Premium -> Free downgrade testi icin `-DowngradeToFree` ekleyebilirsin.

## Provider Portability
Detayli model: `docs/architecture/provider-abstraction.md`
