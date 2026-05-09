# Provider Abstraction Guide

## Goal
Keep the business logic independent from the backing service so the app can run on Supabase today and move to Firebase or another provider later.

## Current Pattern
1. API/business logic uses `UserRepository` interface only.
2. Runtime picks provider via `USER_REPOSITORY_PROVIDER`.
3. Adapters:
- `memory` adapter for local/dev.
- `supabase` adapter for cloud production.

## Why This Helps Migration
1. Endpoint contracts stay stable (`/v1/auth/dev-login`, `/v1/me/plan`, `/v1/analyze`).
2. Storage-specific code is isolated in adapter files.
3. Moving to Firebase becomes adding `firebase-user-repository.ts` and switching env.

## Required Contracts
Adapter must implement:
- `getUserById(userId)`
- `getOrCreateByEmail(email, requestedPlan)`
- `setUserPlanByIdentifier(identifier, plan)`

## Add A New Provider (Example: Firebase)
1. Create `apps/backend/src/store/firebase-user-repository.ts`.
2. Implement `UserRepository`.
3. Add provider branch in `apps/backend/src/store/index.ts`.
4. Set env `USER_REPOSITORY_PROVIDER=firebase`.
5. Run backend build and smoke tests.

## Deployment Principle
Mobile client never carries provider credentials.
All provider keys stay in cloud runtime environment.
