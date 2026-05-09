# Cloud-Only Deploy

## Outcome
After this setup, mobile app and backend run fully in cloud. Local PC is needed only for development.

## Backend Deploy (Recommended: Railway/Render/Fly)
1. Build command: `npm run build:backend`
2. Start command: `node apps/backend/dist/server.js`
3. Required env:
- `PORT`
- `JWT_SECRET`
- `REVENUECAT_WEBHOOK_SECRET`
- `USER_REPOSITORY_PROVIDER=supabase`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Supabase Setup
1. Create project in Supabase.
2. Run migration `apps/backend/supabase/migrations/0001_init.sql`.
3. Insert initial users or let `dev-login` create rows by email.

## Mobile Runtime
1. Set `EXPO_PUBLIC_API_BASE_URL` to deployed backend URL.
2. Set Supabase public vars for mobile auth:
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
3. Build app with EAS (or distribute internal preview build).
4. Do not ship localhost URLs in production profile.

## Smoke Checklist
1. `GET /health` returns `repository=supabase`.
2. `POST /v1/auth/dev-login` returns token.
3. `POST /v1/webhooks/revenuecat` updates plan.
4. Free account returns max 3 matches and 2 coupons.
5. Premium account returns full matches and 4 coupons.
