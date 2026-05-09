# Render Deploy Guide

## Scope
Deploy only backend to cloud so mobile app is fully PC-independent.

## 1) Connect Repo
1. Open Render dashboard.
2. Create `Web Service` from GitHub repo `v-s-p/s8-professor-app`.
3. Render can read `render.yaml` automatically.

## 2) Required Environment Variables
Set these in Render service settings:
- `PORT` (Render usually sets this automatically)
- `JWT_SECRET`
- `REVENUECAT_WEBHOOK_SECRET`
- `USER_REPOSITORY_PROVIDER=supabase`
- `ALLOW_DEV_LOGIN=false`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_ORIGINS` (comma-separated, e.g. `https://expo.dev,https://your-app-domain.com`)

## 3) Verify Deployment
1. Open `https://<render-service>.onrender.com/health`
2. Expect response:
   - `ok: true`
   - `repository: "supabase"`

## 4) Mobile App Configuration
Use backend URL as API base:
- `EXPO_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com`

## 5) RevenueCat Webhook
In RevenueCat dashboard webhook URL:
- `https://<render-service>.onrender.com/v1/webhooks/revenuecat`
Authorization header:
- `Bearer <REVENUECAT_WEBHOOK_SECRET>`

## 6) Production Smoke Test
1. Dev login free -> analyze returns max `3/2`.
2. Send webhook premium event.
3. Analyze returns full matches and `4` coupons.
