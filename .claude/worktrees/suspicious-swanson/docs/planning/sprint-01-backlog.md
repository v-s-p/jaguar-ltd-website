# Sprint 01 Backlog (2 weeks)

## Goal
Monorepo iskeleti, guvenli auth/entitlement omurgasi ve ilk analiz ekraninin calisir hale gelmesi.

## Must
1. Monorepo bootstrap (`apps/mobile`, `apps/backend`, `packages/shared`)
2. Mobile app shell + auth guard
3. Backend auth middleware + JWT
4. `GET /v1/me/plan` endpoint
5. `POST /v1/analyze` endpoint (mock AI response ile)
6. Freemium policy: ilk 3 mac response shaping
7. Premium policy: tum mac + 4 kupon output shaping
8. Audit log tablosu ve temel event logging

## Should
1. RevenueCat webhook receiver (staging)
2. Store purchase test senaryolari
3. Basic rate limit
4. Sentry entegrasyonu

## Nice
1. Feature flag altyapisi
2. Request signing prototype
3. On-device anti-tamper sinyal toplama

## Definition of Done
1. Free user: 3 mactan fazlasini goremez
2. Premium user: tum maclari ve 4 kuponu gorur
3. Prompt ve API key client bundle icinde bulunmaz
4. Smoke tests pass
