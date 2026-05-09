# Staging Secrets Template

Bu dosya dokumantasyon amaclidir. Degerleri GitHub Environments > staging > Secrets altinda tanimla.

## Backend Secrets
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_SECRET`
- `REVENUECAT_API_KEY`
- `SENTRY_DSN`

## Mobile Public Vars (staging)
- `EXPO_PUBLIC_API_BASE_URL`
- `EXPO_PUBLIC_SENTRY_DSN`

## Notes
1. `EXPO_PUBLIC_*` degiskenleri client bundle'a girer; secret olamaz.
2. OpenAI ve servis role key sadece backend environmentta tutulur.
3. Her secret icin rotasyon sahibi ve rotasyon tarihi tutulmalidir.
