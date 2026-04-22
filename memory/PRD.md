# Fire Compliance OS — PRD

## Original Problem
Build "Fire Compliance OS" — enterprise SaaS fully owned by SSPL (Securrise Solution Pvt Ltd). Multi-tenant fire-safety compliance OS with asset management, inspection, audits, risk, revenue and client lock-in.

## User Choices
- MVP core web platform (deep, not wide); rule-based scoring (no AI); manual wallet recharge + usage deduction; JWT email/password auth; in-app + email (Resend log-only until key provided).
- Phase-3 confirmed: no feature expansion beyond 7 listed tasks — focus on revenue/usability/automation.

## Architecture (v1.2.0)
```
backend/
├── server.py            # thin entrypoint (mounts 13 routers, starts scheduler)
├── seed.py              # idempotent seed (Acme demo tenant)
├── core/
│   ├── config.py  · db.py · security.py · deps.py
│   ├── emailer.py (Resend + log fallback + templates)
│   ├── wallet_service.py (charge + credit + grace-mode)
│   ├── notify.py (severity-aware in-app + audit)
│   └── scheduler.py (AsyncIOScheduler daily cron)
└── routers/
    ├── auth · admin · assets · compliance · wallet · documents · users · notifications
    └── amc · reports · onboarding · support · demo
frontend/src/
├── pages/   Landing · Login (+ demo) · SuperAdmin · Clients · Dashboard · Assets · AssetDetail ·
│           Inspections · Maintenance · Incidents · Compliance (+ Book Service) · RiskMap ·
│           Wallet · Documents · Notifications (severity) · Sites · Users · Support
├── components/ AppShell (demo reset) · ui-kit
└── context/AuthContext
```

## Timeline
- **v1.0 (MVP)** · 2026-04-22 · 34 tests green
- **v1.0.1 stabilization** · NOC leak + invoice collision + amount validation · 52 green
- **v1.1 Phase-2** · wallet deduction, email, upload, logout revocation, revenue dashboard, refactor · 65 green
- **v1.2 Phase-3** · AMC Book Service · Daily scheduler · Onboarding · PDF report · Demo mode · Severity · Support requests · **86 green**

## Env Vars
`MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `FRONTEND_URL`,
`RESEND_API_KEY` (optional), `EMAIL_FROM`,
`COST_PER_ASSET=10`, `COST_PER_INSPECTION=5`, `COST_PER_USER=20`, `WALLET_LOW_THRESHOLD=500`,
`UPLOAD_DIR=/app/backend/uploads`

## Phase-3 Deliverables (all shipped, all tested)
1. **AMC Book Service** — `POST /api/amc/book-service`: creates maintenance task, auto-assigns technician, generates PRO-YYYYMMDDHHMMSS invoice, debits wallet, logs `amc.book_service`. 402 w/ shortfall if insufficient.
2. **Scheduler** — APScheduler daily 03:00 UTC; `scan_and_alert()` raises `expired_assets` (critical) + `maintenance_due` (warning) per-client with dedup via `scheduler_runs` collection.
3. **Onboarding** — `GET /api/onboarding/progress` returns 3-step checklist + progress %; widget auto-hides on completion.
4. **PDF reports** — `GET /api/reports/compliance` (reportlab) with SSPL header/footer, score block, summary table, NOC per site, expired list, recent failed inspections.
5. **Demo mode** — `POST /api/demo/login` (unauthenticated OK) + `POST /api/demo/reset` (demo/super only, tenant-scoped wipe).
6. **Severity** — every notification carries `severity ∈ {critical, warning, info}` mapped by kind; frontend filters + color-coded borders.
7. **Support requests** — `/api/support-requests` CRUD; creation notifies all SSPL super_admins (severity from priority).

## Known Limitations (v1.2)
1. Resend sends live only when `RESEND_API_KEY` set (templates all wired; falls back to `[EMAIL:log-only]`)
2. Uploads on local disk; migrate to S3/GCS for scale
3. No mobile/offline technician app
4. No WhatsApp/SMS channels
5. Risk map uses coord-plot, not real tiles
6. Brute-force key uses ingress proxy IP (NAT users share bucket on same email)
7. Wallet recharge is SSPL-manual only (no client self-serve / Stripe)
8. Daily scheduler is in-process — won't fire if backend down at 03:00 UTC (no distributed scheduler)

## Backlog
### P0
- [ ] Drop `RESEND_API_KEY` to go live on email
- [ ] Distributed cron or at-least-once run guarantee
### P1
- [ ] Stripe/Razorpay self-serve recharge
- [ ] Object-storage migration for Document Vault
- [ ] Bulk asset CSV import
- [ ] PDF customisation (logo upload per client for white-label)
- [ ] Audit log UI for super_admin
### P2 (deferred by user)
- [ ] Predictive AI risk engine
- [ ] Android + offline sync
- [ ] WhatsApp/SMS (Twilio)
- [ ] Voice-note Hindi/English
- [ ] White-label partner portal

## Credentials
See `/app/memory/test_credentials.md`.
