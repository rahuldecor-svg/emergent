# Fire Compliance OS — PRD

## Original Problem
"Fire Compliance OS" — enterprise SaaS owned by SSPL (Securrise Solution Pvt Ltd). Multi-tenant fire-safety compliance OS.

## User Choices
- Core web platform (deep, not wide); rule-based scoring (no AI); manual wallet recharge + usage deduction; JWT email/password; in-app + email (Resend log-only fallback).
- Phase-2/3/4 explicitly: no feature expansion beyond listed tasks — focus on revenue, security, usability, bilingual training/legal.

## Architecture (v1.2)
```
backend/
├── server.py            # thin entrypoint, 15 routers, APScheduler
├── seed.py
├── core/ → config · db · security (JWT + revocation) · deps · emailer · wallet_service · notify · scheduler
└── routers/ → auth · admin · assets · compliance · wallet · documents · users · notifications
              · amc · reports · onboarding · support · demo · asset_master · qr
frontend/src/
├── pages/ → Landing · Login (+demo) · Terms (public) · SuperAdmin · ClientsAdmin
│          · Dashboard · Assets (master picker + QR sheet) · AssetDetail (+QR PDF)
│          · Inspections · Maintenance · Incidents · Compliance (+Book Service)
│          · RiskMap · Wallet · Documents · Sites · Users · Support · HelpCenter
│          · NotificationsPage (severity)
├── components/ → AppShell (+NeedHelpFab) · ui-kit · NeedHelpFab
├── lib/ → api · i18n (EN+HI friendly errors) · helpContent (all bilingual copy)
└── context/AuthContext
```

## Timeline
- **v1.0 MVP** → 34 tests
- **v1.0.1 stabilisation** → 52 tests (NOC leak · invoice collision · amount validation)
- **v1.1 Phase-2** → 65 tests (wallet deduction · email · upload · revocation · revenue dashboard · router refactor)
- **v1.2 Phase-3** → 86 tests (AMC Book Service · scheduler · onboarding · PDF · demo · severity · support)
- **v1.2 Phase-4** → **100/100 tests** (asset master · QR PDF print · Help Center EN/HI · Terms · FAB · friendly errors)

## Known Limitations (v1.2)
1. Resend sends live only when `RESEND_API_KEY` set — **MOCKED/log-only** today
2. Uploads on local disk — single-node
3. No mobile/offline · No WhatsApp/SMS · No real map tiles
4. Wallet recharge is SSPL-manual only (no self-serve)
5. Scheduler in-process (won't fire if backend down at 03:00 UTC)
6. Brute-force lock key uses ingress proxy IP

## Backlog
### P0
- [ ] Provide RESEND_API_KEY → email channel goes live
- [ ] Distributed cron / at-least-once run guarantee
### P1
- [ ] Self-serve recharge (Stripe/Razorpay)
- [ ] Object-storage for Document Vault
- [ ] White-label PDF / client logo upload
- [ ] CSV bulk asset import
- [ ] Password reset flow (currently SSPL-assisted)
### P2 (deferred by user)
- [ ] Predictive AI risk engine
- [ ] Android + offline sync
- [ ] WhatsApp/SMS (Twilio)
- [ ] Voice notes Hindi/English inspection
- [ ] White-label partner portal

See `/app/memory/test_credentials.md` for demo accounts.
