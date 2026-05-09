# Release & Incident Runbook

## Release Workflow
1. Feature branch -> PR -> review -> merge main
2. CI: lint + test + security scan
3. Backend deploy (staging)
4. Mobile EAS build (internal)
5. Smoke test (auth, plan, analyze, purchase)
6. Production deploy + phased rollout

## iOS Release Steps
1. App Store Connect build upload
2. Metadata ve subscription references kontrolu
3. TestFlight validation
4. Production submit ve review takibi

## Android Release Steps
1. Play Console AAB upload
2. Internal/closed testing validation
3. Rollout yuzu belirleme (or. %10 -> %50 -> %100)
4. Crash ve ANR takibi

## Incident Severity
- Sev1: tum analiz servis disi / odeme dogrulama tamamen bozuk
- Sev2: premium policy partial fail
- Sev3: tek endpoint gecici hata

## Incident Response
1. Triage owner ata
2. Etki alani tespit et
3. Gecici mitigasyon uygula (feature flag / rate limit)
4. Geri alma (rollback) gerekiyorsa tetikle
5. Postmortem yaz: root cause + aksiyonlar

## Monitoring Baseline
1. API error rate
2. p95 latency
3. payment verification failure rate
4. suspicious request rate
5. premium entitlement mismatch alerts
