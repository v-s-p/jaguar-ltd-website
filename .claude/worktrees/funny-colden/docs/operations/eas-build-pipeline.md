# EAS Build Pipeline

Bu dokuman Android ve iOS buildlerini local bilgisayardan bagimsiz sekilde EAS cloud uzerinden almak icindir.

## 1) Once bir kere
1. Expo account ac.
2. Asagidaki komutla login ol:
   - `npx eas-cli@latest login`
3. Mobile klasorunde EAS project bagla:
   - `cd apps/mobile`
   - `npx eas-cli@latest project:init`

## 2) EAS Secrets / Env
Asagidaki public env degerlerini EAS ortamina gir:
- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `EXPO_PUBLIC_REVENUECAT_API_KEY_IOS`
- `EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID`
- `EXPO_PUBLIC_PASSWORD_RESET_REDIRECT_URL=s8professor://reset-password`
- `EXPO_PUBLIC_REVENUECAT_ENTITLEMENT_ID=premium`

Ornek:
- `npx eas-cli@latest env:create --name EXPO_PUBLIC_API_BASE_URL --value https://s8-professor-app.onrender.com --scope project`

## 3) Build Profilleri
`apps/mobile/eas.json` icindeki profiller:
- `development`: Dev client APK/IPA
- `preview`: Internal test build
- `production`: Store release build

## 4) Build Komutlari
Android development:
- `cd apps/mobile`
- `npx eas-cli@latest build --platform android --profile development`

Android production:
- `cd apps/mobile`
- `npx eas-cli@latest build --platform android --profile production`

iOS development:
- `cd apps/mobile`
- `npx eas-cli@latest build --platform ios --profile development`

iOS production:
- `cd apps/mobile`
- `npx eas-cli@latest build --platform ios --profile production`

## 5) Store Submit (Opsiyonel)
Android:
- `npx eas-cli@latest submit --platform android --profile production`

iOS:
- `npx eas-cli@latest submit --platform ios --profile production`

## 6) Notlar
- RevenueCat satin alma/restore testleri icin Expo Go degil, EAS development build kullan.
- iOS build icin local Mac gerekmiyor (EAS cloud build yeterli).
- Supabase reset link redirect degeri ile app scheme ayni olmalidir:
  - `s8professor://reset-password`

