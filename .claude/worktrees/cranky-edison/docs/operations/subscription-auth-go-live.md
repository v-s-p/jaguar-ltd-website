# Subscription + Auth Go-Live Checklist

Bu dokuman, Free -> Premium satin alma ve forgot password akislarini productiona hazirlamak icindir.

## 1) Mobile Env (Expo)
- `EXPO_PUBLIC_API_BASE_URL=https://s8-professor-app.onrender.com`
- `EXPO_PUBLIC_SUPABASE_URL=...`
- `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...`
- `EXPO_PUBLIC_PASSWORD_RESET_REDIRECT_URL=s8professor://reset-password`
- `EXPO_PUBLIC_REVENUECAT_API_KEY_IOS=appl_...`
- `EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID=goog_...`
- `EXPO_PUBLIC_REVENUECAT_ENTITLEMENT_ID=premium`

## 2) Supabase Auth Ayarlari
- Auth URL Configuration altinda redirect URL ekle:
  - `s8professor://reset-password`
- Email templates aktif olsun (signup + reset password).

## 3) Backend Env (Render)
- `USER_REPOSITORY_PROVIDER=supabase`
- `SUPABASE_URL=...`
- `SUPABASE_SERVICE_ROLE_KEY=...`
- `JWT_SECRET=...`
- `REVENUECAT_WEBHOOK_SECRET=<strong-random-secret>`
- `ALLOW_DEV_LOGIN=false`

## 4) RevenueCat
- Webhook URL:
  - `https://s8-professor-app.onrender.com/v1/webhooks/revenuecat`
- Authorization/Bearer secret:
  - Render'daki `REVENUECAT_WEBHOOK_SECRET` ile birebir ayni.
- `app_user_id` olarak email kullan (mobile login email ile ayni format).

## 5) Mobile UI Kontrol
- Login / Sign Up calisiyor.
- `Forgot Password` tiklayinca reset mail gidiyor.
- Reset linkten app aciliyor ve `Set New Password` ekrani gorunuyor.
- `Restore Access` plani backendden yeniliyor.
- `Upgrade to Premium` satin alma ekranini aciyor ve purchase tamamliyor.
- `Manage Subscription` iOS/Android store sayfasini aciyor.

## 6) Build Notu (Onemli)
- `react-native-purchases` Expo Go icinde test edilemez.
- RevenueCat purchase/restore testi icin EAS development build veya store build kullan.

## 7) SQL Dogrulama
```sql
select id, email, plan
from profiles
order by created_at desc;
```

Premium satin alma testinde ilgili kullanicinin `plan='premium'` olmasi gerekir.

