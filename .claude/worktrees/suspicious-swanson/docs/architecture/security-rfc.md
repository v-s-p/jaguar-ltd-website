# Security & Architecture RFC

## Scope
Bu dokuman S8 Professor urunu icin iOS + Android mobil istemci ve backend mimarisinin guvenlik esaslarini tanimlar.

## System Boundaries
- Mobile App (Expo React Native): UI, session state, response rendering
- Backend API: auth guard, entitlement, AI orchestration, coupon generation
- Data Store: users, subscriptions, analyses, audit logs
- Third-party: OpenAI, RevenueCat/App Store/Play Billing, Supabase/Firebase

## Non-Negotiables
1. Prompt ve model anahtarlari mobilde tutulmaz.
2. Freemium/Premium karar mekanizmasi frontendde degil backendde calisir.
3. Tum kritik endpointler auth + rate limit altinda olur.
4. Minimum veri prensibi: freemium icin sadece gerekli alanlar doner.

## Reference Architecture
1. `POST /v1/auth/login` -> token alimi
2. `GET /v1/me/plan` -> free/premium entitlement
3. `POST /v1/analyze` -> mac listesi bazli analiz
4. `GET /v1/analyses/:id` -> daha once uretilmis sonuc

## Entitlement Policy
- Free: ilk 3 mac + temel istatistik + sinirli kupon seti
- Premium: tum maclar + genisletilmis istatistik + 4 kupon seti
- Policy backend response shaping ile enforce edilir.

## Threat Model (Top Risks)
1. Reverse engineering ile prompt sizdirma
2. API abuse ve key harvesting
3. Fake premium unlock (client-side bypass)
4. Token replay ve oturum ele gecirme
5. Prompt injection ile system instruction exposure

## Security Controls
- JWT (kisa omurlu) + refresh token rotation
- Device/IP aware rate limiting
- Signed request metadata (nonce/timestamp) for sensitive endpoints
- Secret manager (runtime injection)
- Structured audit logging
- Output filter: system prompt ve internal chain disclosure bloklama

## Mobile Platform Requirements
### iOS
- Sign in with Apple gerekliligi (uygunsa)
- App Tracking Transparency kararina uyum
- In-App Purchase disclosure ve restore flow
- Keychain ile secure token saklama

### Android
- Play Billing Library uyumu
- Data Safety formuna uygun veri beyanlari
- Keystore signing + R8 obfuscation
- EncryptedSharedPreferences / secure storage

## Privacy by Design
- PII siniflandirma
- Loglarda PII masking
- Veri saklama suresi tanimi
- Kullanici talebiyle veri silme akisi

## Release Gates
1. Security checklist pass
2. Store compliance checklist pass
3. Incident rollback plani hazir
4. Critical test suites green
